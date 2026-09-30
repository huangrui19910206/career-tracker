#!/usr/bin/env python3
"""Build the career-tracker static site.

Reads data/companies.json and writes data.js as `const COMPANIES = [...]`.
Idempotent: re-running produces the same output for the same input.
Usage: python3 build.py   (run from the repo root)
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
DATA_JSON = ROOT / "data" / "companies.json"
DATA_JS = ROOT / "data.js"

REQUIRED_KEYS = {
    "slug", "name", "tagline", "valuation", "valuation_detail", "size",
    "location", "rto", "status", "contacts", "timeline", "intel", "interviews",
}
VALID_STATUSES = {
    "outreach", "connected", "engaged", "interviewing", "scheduling",
    "offer", "paused",
}
VALID_CONTACT_STATUSES = {"invited", "connected", "inbound_pending", "existing"}


def main():
    companies = json.loads(DATA_JSON.read_text(encoding="utf-8"))

    slugs = [c["slug"] for c in companies]
    assert len(slugs) == len(set(slugs)), "duplicate slugs found"

    for c in companies:
        missing = REQUIRED_KEYS - set(c.keys())
        assert not missing, f"{c.get('slug')}: missing keys {missing}"
        assert c["status"] in VALID_STATUSES, f"{c['slug']}: bad status {c['status']}"
        for k in ("contacts", "timeline", "interviews"):
            assert isinstance(c[k], list), f"{c['slug']}: {k} must be a list"
        assert isinstance(c["intel"], dict), f"{c['slug']}: intel must be an object"
        for ct in c["contacts"]:
            assert ct["contact_status"] in VALID_CONTACT_STATUSES, (
                f"{c['slug']}/{ct.get('name')}: bad contact_status"
            )

    # Sort timeline entries chronologically per company (stable).
    for c in companies:
        c["timeline"] = sorted(c["timeline"], key=lambda t: t["date"])
        c["interviews"] = sorted(c["interviews"], key=lambda i: (i["date"], i["time"]))

    # Sort companies by name for a stable build.
    companies = sorted(companies, key=lambda c: c["name"].lower())

    from datetime import date
    payload = "const BUILD_DATE = \"" + date.today().strftime("%b %d, %Y") + "\";\n" + "const COMPANIES = " + json.dumps(companies, ensure_ascii=False, indent=2) + ";\n"
    DATA_JS.write_text(payload, encoding="utf-8")
    print(f"wrote {DATA_JS} ({len(companies)} companies)")


if __name__ == "__main__":
    main()
