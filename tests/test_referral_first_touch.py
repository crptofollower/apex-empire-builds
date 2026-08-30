"""Static + first-touch contract tests for apexempire.ai waitlist capture."""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
REF_CODE_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


class FakeStorage:
    def __init__(self):
        self.data = {}

    def getItem(self, key):
        return self.data.get(key)

    def setItem(self, key, value):
        self.data[key] = value


def normalize_referral_code(raw):
    if not isinstance(raw, str):
        return ""
    code = raw.strip()
    if not REF_CODE_RE.match(code):
        return ""
    return code


def capture_first_touch(storage, incoming_raw):
    incoming = normalize_referral_code(incoming_raw or "")
    existing = normalize_referral_code(storage.getItem("herald_referral_code") or "")
    if existing:
        return existing
    if incoming:
        storage.setItem("herald_referral_code", incoming)
        return incoming
    return ""


def waitlist_payload(email, storage, incoming_ref=""):
    payload = {"email": email}
    referral = capture_first_touch(storage, incoming_ref)
    visitor = storage.getItem("herald_visitor_id") or "00000000-0000-4000-8000-000000000001"
    if not storage.getItem("herald_visitor_id"):
        storage.setItem("herald_visitor_id", visitor)
    if referral:
        payload["referral_code"] = referral
    if visitor:
        payload["visitor_id"] = visitor
    return payload


class ReferralCaptureTests(unittest.TestCase):
    def test_live_script_contains_first_touch_contract(self):
        self.assertIn("WAITLIST_URL = 'https://web-production-b4083.up.railway.app/waitlist'", HTML)
        self.assertIn("herald_referral_code", HTML)
        self.assertIn("herald_visitor_id", HTML)
        self.assertIn("crypto.randomUUID", HTML)
        self.assertIn("/^[A-Za-z0-9_-]{1,64}$/", HTML)
        self.assertIn("if (referralCode) payload.referral_code = referralCode", HTML)
        self.assertIn("waitlistPayload(email)", HTML)
        self.assertEqual(HTML.count("data-waitlist novalidate"), 2)
        self.assertIn("We’ll use this email only for Herald early access and invitations.", HTML)

    def test_organic_payload_omits_referral_code(self):
        storage = FakeStorage()
        payload = waitlist_payload("a@example.com", storage, "")
        self.assertEqual(payload["email"], "a@example.com")
        self.assertNotIn("referral_code", payload)
        self.assertIn("visitor_id", payload)

    def test_first_touch_ref_preserved_against_later_ref(self):
        storage = FakeStorage()
        first = capture_first_touch(storage, "EXAMPLE")
        second = capture_first_touch(storage, "OTHER")
        self.assertEqual(first, "EXAMPLE")
        self.assertEqual(second, "EXAMPLE")
        payload = waitlist_payload("b@example.com", storage, "OTHER")
        self.assertEqual(payload["referral_code"], "EXAMPLE")

    def test_malformed_ref_not_stored(self):
        storage = FakeStorage()
        self.assertEqual(capture_first_touch(storage, "no spaces!!"), "")
        self.assertEqual(capture_first_touch(storage, "x" * 65), "")
        self.assertIsNone(storage.getItem("herald_referral_code"))

    def test_payload_keys_match_backend_contract(self):
        storage = FakeStorage()
        payload = waitlist_payload("c@example.com", storage, "EXAMPLE")
        self.assertEqual(set(payload), {"email", "referral_code", "visitor_id"})
        self.assertTrue(REF_CODE_RE.match(payload["referral_code"]))
        self.assertRegex(payload["visitor_id"], r"^[A-Za-z0-9_-]{8,128}$")


if __name__ == "__main__":
    unittest.main()
