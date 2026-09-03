"""Lab 6 - Google Analytics setup and analytics parameters.

The GA4 gtag.js snippet is installed in the page head, the standard e-commerce
events are fired through gtag so they really are sent to Google Analytics, and
the parameters read from the GA4 reports are listed on the page. Every hit the
browser sends to google-analytics.com is also captured and shown on the page,
so the integration can be checked without opening the GA dashboard.

Run:  python app.py      then open http://127.0.0.1:5006

The Measurement ID comes from the GA_MEASUREMENT_ID environment variable, so a
real GA4 property can be used without editing the code:

    GA_MEASUREMENT_ID=G-ABCD123456 python app.py

Abhishek Barali - 023bscit003 - Section A - Batch 2023
"""
import json
import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

PROPERTY = {
    "account": "Abhishek Barali",
    "roll": "023bscit003",
    "property_name": "Barali Store Web",
    "measurement_id": os.environ.get("GA_MEASUREMENT_ID", "G-XXXXXXXXXX"),
    "stream": "Barali Store - Web stream",
    "user_id": "023bscit003",             # user_id sent with every event
}

# Events the store sends, with the parameters attached to each one.
EVENTS = {
    "page_view": {"page_title": "Barali Store", "page_location": "/lab6",
                  "user_id": PROPERTY["user_id"]},
    "view_item": {"item_id": "SW-03", "item_name": "Smart Watch",
                  "item_category": "Electronics", "value": 4200, "currency": "NPR"},
    "add_to_cart": {"item_id": "BT-01", "item_name": "Bluetooth Headphone",
                    "item_category": "Electronics", "quantity": 1,
                    "value": 2500, "currency": "NPR"},
    "begin_checkout": {"item_count": 2, "value": 6700, "currency": "NPR",
                       "coupon": "none"},
    "purchase": {"transaction_id": "ORD-023BSCIT003-01", "value": 6800,
                 "shipping": 100, "currency": "NPR", "item_count": 2},
    "add_to_wishlist": {"item_id": "RS-05", "item_name": "Running Shoes",
                        "value": 3500, "currency": "NPR"},
}

# What each report parameter tells us about the store.
PARAMETERS = [
    ("Active users", "Different people who opened the store", "Realtime"),
    ("Sessions", "Visits; a session closes after 30 minutes idle", "Acquisition"),
    ("Views", "Pages opened, collected automatically by gtag.js", "Pages and screens"),
    ("Engagement rate", "Visits of 10s or more, 2 views, or an event", "Engagement"),
    ("Average engagement time", "Time the page stayed in the foreground", "Engagement"),
    ("Event count", "How often each event such as add_to_cart fired", "Events"),
    ("Key events", "Events marked as conversions, purchase here", "Admin, Events"),
    ("Total revenue", "Value carried by the purchase event", "Monetisation"),
    ("Session source", "Where the visit came from, e.g. google / organic", "Acquisition"),
    ("Device and country", "Dimensions collected for every visitor", "Tech, Demographics"),
]

log = []        # local copy of the events that were fired


@app.route("/")
def home():
    counts = {name: sum(1 for e in log if e["name"] == name) for name in EVENTS}
    # The event named in ?send= is handed to gtag when the page loads, so the
    # hit is really sent to Google Analytics by the browser.
    send = request.args.get("send")
    pending = {"name": send, "params": EVENTS[send]} if send in EVENTS else None
    return render_template("index.html", prop=PROPERTY, events=EVENTS,
                           parameters=PARAMETERS, log=list(reversed(log)),
                           counts=counts, fired=len(log), pending=pending,
                           live=not PROPERTY["measurement_id"].startswith("G-XXXX"),
                           pending_json=json.dumps(pending["params"]) if pending else "{}")


@app.route("/fire/<name>", methods=["POST"])
def fire(name):
    if name not in EVENTS:
        return redirect(url_for("home"))
    log.append({"name": name, "params": EVENTS[name],
                "time": datetime.now().strftime("%H:%M:%S")})
    return redirect(url_for("home", send=name))


@app.route("/reset", methods=["POST"])
def reset():
    log.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(port=5006, debug=True)
