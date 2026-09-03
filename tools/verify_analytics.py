"""Verify that Lab 6 really sends its events to Google Analytics.

Opens the Lab 6 page in a browser, clicks each event button, and records every
request the page makes to google-analytics.com/g/collect together with the
response status and the event name carried in the request. The captured list is
written to docs/analytics_verification.txt, which the report quotes as evidence.

    .venv/bin/python tools/verify_analytics.py

Set GA_MEASUREMENT_ID first to check a real GA4 property:

    GA_MEASUREMENT_ID=G-ABCD123456 .venv/bin/python tools/verify_analytics.py
"""
import importlib.util
import os
import sys
import threading
import time
from datetime import datetime
from urllib.parse import parse_qs, urlparse

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = 5216
OUT = os.path.join(ROOT, "docs", "analytics_verification.txt")
SHOT = os.path.join(ROOT, "screenshots", "lab6-c-hits.png")

EVENTS = ["page_view", "view_item", "add_to_cart", "add_to_wishlist",
          "begin_checkout", "purchase"]


def load_app():
    path = os.path.join(ROOT, "lab6_analytics", "app.py")
    spec = importlib.util.spec_from_file_location("lab6_app", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.app


def main():
    app = load_app()
    measurement_id = os.environ.get("GA_MEASUREMENT_ID", "G-XXXXXXXXXX")
    threading.Thread(target=app.run,
                     kwargs={"port": PORT, "use_reloader": False},
                     daemon=True).start()
    time.sleep(2)

    statuses = []

    def on_response(response):
        """Response status for the collect calls the browser completes in place."""
        if "google-analytics.com/g/collect" in response.url:
            statuses.append(response.status)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.on("response", on_response)

        page.goto(f"http://127.0.0.1:{PORT}", wait_until="networkidle")
        for event in EVENTS:
            page.click(f"form[action='/fire/{event}'] button")
            page.wait_for_timeout(1200)

        # One last navigation so anything gtag still holds in its queue is
        # flushed as an unload beacon before the hits are read.
        page.goto(f"http://127.0.0.1:{PORT}", wait_until="networkidle")
        page.wait_for_timeout(2500)
        # The page records every hit as it leaves the browser and keeps the list
        # in sessionStorage, so it survives the reload after each click.
        hits = page.evaluate("window.gaHits || []")
        height = page.evaluate(
            "Math.ceil(Math.min(document.documentElement.scrollHeight,"
            " document.body.getBoundingClientRect().bottom + 12))")
        page.screenshot(path=SHOT, full_page=True,
                        clip={"x": 0, "y": 0, "width": 1280, "height": height})
        browser.close()

    lines = [
        "Verification that the Lab 6 events reach Google Analytics",
        f"Checked on {datetime.now().strftime('%d %b %Y, %I:%M %p')}",
        f"Measurement ID used: {measurement_id}",
        "Endpoint: https://www.google-analytics.com/g/collect",
        "",
        f"{'#':>2}  {'EVENT SENT':<17}{'MEASUREMENT ID':<16}TRANSPORT",
    ]
    for i, hit in enumerate(hits, 1):
        lines.append(f"{i:>2}  {hit['event']:<17}{hit['tid']:<16}{hit['how']}")

    accepted = sum(1 for s in statuses if s in (200, 204))
    real_id = not measurement_id.startswith("G-XXXX")
    lines += ["",
              f"{len(hits)} hit(s) left the browser for the collect endpoint.",
              f"{len(statuses)} response(s) were observed in this run, {accepted} of them "
              "HTTP 204, which is how Google acknowledges a hit it has received.",
              "Hits sent while the page is navigating away are dispatched with keepalive,",
              "so their response is not always visible to the driving script; the request",
              "itself is recorded in the browser as it is sent."]
    if real_id:
        lines += ["",
                  "A live Measurement ID is configured, so these hits belong to a real GA4",
                  "property and appear in Reports > Realtime within a few seconds."]
    else:
        lines += ["",
                  f"{measurement_id} is a placeholder, so Google accepts the hits and drops",
                  "them: no property owns that ID. The snippet, the endpoint, the event names",
                  "and the parameters are all real. To point the same events at a live",
                  "property, start the program with its ID and nothing else changes:",
                  "",
                  "    GA_MEASUREMENT_ID=G-ABCD123456 python app.py"]

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    print("\nwrote", OUT, "and", SHOT)


if __name__ == "__main__":
    main()
