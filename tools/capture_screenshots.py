"""Capture the screenshots used in the lab report.

Starts the Flask app on a local port, drives it with Playwright, and writes
PNG files into the screenshots/ folder.

    .venv/bin/python tools/capture_screenshots.py
"""
import os
import sys
import threading
import time

from playwright.sync_api import sync_playwright

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app  # noqa: E402

PORT = 5055
BASE = f"http://127.0.0.1:{PORT}"
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "screenshots")


def serve():
    app.run(port=PORT, use_reloader=False)


def shot(page, name, full=True):
    path = os.path.join(OUT, name)
    page.screenshot(path=path, full_page=full)
    print("saved", name)


def main():
    os.makedirs(OUT, exist_ok=True)
    threading.Thread(target=serve, daemon=True).start()
    time.sleep(2)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})

        # Home
        page.goto(BASE)
        shot(page, "01-home.png")

        # Lab 1 - create a category and add an item to it
        page.goto(f"{BASE}/lab1")
        page.fill("input[name=category]", "Stationery")
        page.click("form[action='/lab1/add-category'] button")
        page.fill("input[name=name]", "A4 Notebook")
        page.fill("input[name=price]", "220")
        page.select_option("select[name=category]", "Stationery")
        page.click("form[action='/lab1/add-item'] button")
        shot(page, "02-lab1-categories.png")

        # Lab 2 - add products to the cart
        page.goto(f"{BASE}/lab2")
        shot(page, "03-lab2-products.png")
        page.click("form[action='/lab2/add/1'] button")
        page.click("form[action='/lab2/add/5'] button")
        page.click("form[action='/lab2/add/5'] button")
        shot(page, "04-lab2-cart.png")

        # Lab 3 - checkout
        page.goto(f"{BASE}/lab3")
        page.click("form[action='/lab3/add/6'] button")
        shot(page, "05-lab3-checkout.png")
        page.click("form[action='/lab3/checkout'] button")
        shot(page, "06-lab3-order.png")

        # Lab 4 - wish list
        page.goto(f"{BASE}/lab4")
        page.click("form[action='/lab4/add/3'] button")
        page.click("form[action='/lab4/add/7'] button")
        shot(page, "07-lab4-wishlist.png")

        # Lab 5 - payment gateway in sandbox mode
        page.goto(f"{BASE}/lab2")
        page.click("form[action='/lab2/add/3'] button")
        page.goto(f"{BASE}/lab5")
        shot(page, "08-lab5-payment.png")
        page.click("form[action='/lab5/gateway'] button")
        shot(page, "09-lab5-gateway.png", full=False)
        page.click("form[action='/lab5/verify'] button")
        shot(page, "10-lab5-result.png")

        # Lab 6 - analytics
        page.goto(f"{BASE}/lab6")
        shot(page, "11-lab6-setup.png")
        for event in ["page_view", "view_item", "add_to_cart", "begin_checkout", "purchase"]:
            page.click(f"form[action='/lab6/track/{event}'] button")
        page.locator("h2:has-text('Events collected')").scroll_into_view_if_needed()
        shot(page, "12-lab6-events.png")

        browser.close()


if __name__ == "__main__":
    main()
