"""Capture the screenshots used in the lab report.

Each lab is a separate Flask app, so each one is started on its own port,
driven with Playwright, and screenshotted.

    .venv/bin/python tools/capture_screenshots.py
"""
import importlib.util
import os
import sys
import threading
import time

from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "screenshots")

LABS = [
    ("lab1_categories", 5101),
    ("lab2_cart", 5102),
    ("lab3_checkout", 5103),
    ("lab4_wishlist", 5104),
    ("lab5_payment", 5105),
    ("lab6_analytics", 5106),
]


def load_app(folder):
    """Import the app.py of one lab folder under a unique module name."""
    path = os.path.join(ROOT, folder, "app.py")
    spec = importlib.util.spec_from_file_location(f"{folder}_app", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module.app


def serve_all():
    for folder, port in LABS:
        app = load_app(folder)
        threading.Thread(target=app.run,
                         kwargs={"port": port, "use_reloader": False},
                         daemon=True).start()
    time.sleep(3)


def shot(page, name, full=True):
    """Screenshot trimmed to the real content height, so a short page does not
    leave a band of empty space in the report."""
    height = page.evaluate(
        "Math.ceil(Math.min(document.documentElement.scrollHeight,"
        " document.body.getBoundingClientRect().bottom + 12))")
    if not full:
        height = min(height, 880)
    page.screenshot(path=os.path.join(OUT, name), full_page=True,
                    clip={"x": 0, "y": 0, "width": 1280, "height": height})
    print("saved", name)


def main():
    os.makedirs(OUT, exist_ok=True)
    serve_all()
    base = "http://127.0.0.1:"

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 880})

        # Lab 1 - create a category, then add an item into it
        page.goto(base + "5101")
        shot(page, "lab1-a-start.png")
        page.fill("input[name=category]", "Stationery")
        page.click("form[action='/category'] button")
        page.fill("input[name=name]", "A4 Notebook")
        page.select_option("select[name=category]", "Stationery")
        page.click("form[action='/item'] button")
        shot(page, "lab1-b-added.png")

        # Lab 2 - add products, raise a quantity
        page.goto(base + "5102")
        shot(page, "lab2-a-products.png")
        page.click("form[action='/add/1'] button")
        page.click("form[action='/add/3'] button")
        page.click("form[action='/add/3'] button")
        page.click("form[action='/add/5'] button")
        shot(page, "lab2-b-cart.png")

        # Lab 3 - fill the cart, then check out
        page.goto(base + "5103")
        page.click("form[action='/add/1'] button")
        page.click("form[action='/add/4'] button")
        page.click("form[action='/add/4'] button")
        shot(page, "lab3-a-cart.png")
        page.click("form[action='/checkout'] button")
        shot(page, "lab3-b-order.png")

        # Lab 4 - save to the wish list, then move one item to the cart
        page.goto(base + "5104")
        shot(page, "lab4-a-products.png")
        page.click("form[action='/save/1'] button")
        page.click("form[action='/save/4'] button")
        page.click("form[action='/save/6'] button")
        shot(page, "lab4-b-wishlist.png")
        page.click("form[action='/move/4'] button")
        shot(page, "lab4-c-moved.png")

        # Lab 5 - invoice, sandbox gateway, result
        page.goto(base + "5105")
        shot(page, "lab5-a-invoice.png")
        page.click("form[action='/gateway'] button")
        shot(page, "lab5-b-gateway.png", full=False)
        page.click("form[action='/gateway/verify'] button")
        shot(page, "lab5-c-result.png")

        # Lab 6 - fire the events and read the parameters
        page.goto(base + "5106")
        shot(page, "lab6-a-setup.png")
        for event in ["page_view", "view_item", "add_to_cart",
                      "add_to_wishlist", "begin_checkout", "purchase"]:
            page.click(f"form[action='/fire/{event}'] button")
        shot(page, "lab6-b-events.png")

        browser.close()


if __name__ == "__main__":
    main()
