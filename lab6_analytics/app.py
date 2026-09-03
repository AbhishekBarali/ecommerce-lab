"""Lab 6 - Google Analytics setup and analytics parameters.

The GA4 gtag.js snippet is installed in the page head, the standard
e-commerce events are fired with their parameters, and the parameters that
are read from the GA4 reports are listed on the page. Every fired event is
also kept locally so the collected parameters can be seen without opening the
Google Analytics dashboard.

Run:  python app.py      then open http://127.0.0.1:5006

Abhishek Barali - 023bscit003 - Section A - Batch 2023
"""
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

PROPERTY = {
    "account": "Abhishek Barali",
    "roll": "023bscit003",
    "property_name": "Barali Store Web",
    "measurement_id": "G-XXXXXXXXXX",     # from the GA4 web data stream
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
    "begin_checkout": {"items": 2, "value": 6700, "currency": "NPR",
                       "coupon": "none"},
    "purchase": {"transaction_id": "ORD-023BSCIT003-01", "value": 6800,
                 "shipping": 100, "currency": "NPR", "items": 2},
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
    return render_template("index.html", prop=PROPERTY, events=EVENTS,
                           parameters=PARAMETERS, log=list(reversed(log)),
                           counts=counts, fired=len(log))


@app.route("/fire/<name>", methods=["POST"])
def fire(name):
    if name in EVENTS:
        log.append({"name": name, "params": EVENTS[name],
                    "time": datetime.now().strftime("%H:%M:%S")})
    return redirect(url_for("home"))


@app.route("/reset", methods=["POST"])
def reset():
    log.clear()
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(port=5006, debug=True)
