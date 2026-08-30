"""Static contract tests for the founder growth dashboard page."""
from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "growth.html").read_text(encoding="utf-8")
INDEX = (ROOT / "index.html").read_text(encoding="utf-8")
ADMIN = (ROOT / "admin.html").read_text(encoding="utf-8")


class GrowthDashboardPageTests(unittest.TestCase):
    def test_page_is_unlisted_and_noindex(self):
        self.assertIn('name="robots" content="noindex,nofollow"', HTML)
        self.assertNotIn("growth.html", INDEX)
        self.assertIn("ApexEmpire Operations", HTML)
        self.assertIn("Waitlist Total", HTML)
        self.assertIn("New This Week", HTML)
        self.assertIn("Organic", HTML)
        self.assertIn("Referred", HTML)
        self.assertIn("Top Referral Sources", HTML)
        self.assertIn("Recent Signups", HTML)

    def test_page_contains_no_embedded_secret(self):
        self.assertNotIn("GROWTH_DASHBOARD_SECRET", HTML)
        self.assertNotIn("WEBHOOK_SECRET", HTML)
        self.assertNotIn("HERALD_ACCESS_CODE", HTML)
        self.assertNotRegex(HTML, r"Bearer [A-Za-z0-9_\-]{16,}")
        self.assertNotIn("sessionStorage.setItem(STORAGE_KEY, '", HTML)

    def test_auth_is_header_bearer_not_query_string(self):
        self.assertIn("Authorization", HTML)
        self.assertIn("'Bearer ' + secret", HTML)
        self.assertIn("/growth/summary", HTML)
        self.assertIn("/growth/signups", HTML)
        self.assertIn("/growth/export.csv", HTML)
        self.assertNotIn("?secret=", HTML)
        self.assertNotIn("querySelector('input[name=secret]')", HTML)
        self.assertIn("sessionStorage", HTML)
        self.assertNotIn("localStorage", HTML)

    def test_does_not_reuse_legacy_admin_surface(self):
        self.assertNotIn("/admin/", HTML)
        self.assertNotIn("WEBHOOK_SECRET", HTML)
        self.assertNotIn("admin.html", HTML)
        self.assertNotIn("/waitlist/list", HTML)
        self.assertIn("?secret=", ADMIN)
