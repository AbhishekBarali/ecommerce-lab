"""Lab 6 - Google Analytics setup and analytics parameters.

The GA4 gtag.js snippet lives in templates/base.html, so every page of the
store reports a page_view to the configured Measurement ID. This program
also fires the standard GA4 e-commerce events and keeps a local copy of each
event with its parameters, so the parameters being measured can be seen and
screenshotted without opening the Google Analytics dashboard.
"""
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for

from store import data

lab6 = Blueprint("lab6", __name__)

MEASUREMENT_ID = "G-XXXXXXXXXX"   # replace with the real ID from the GA4 property

# GA4 events fired by this store, with the parameters sent along with them.
EVENT_LIBRARY = {
    "page_view": {"page_title": "Mini E-Commerce Store", "page_location": "/lab6"},
    "view_item": {"item_id": "3", "item_name": "Smart Watch",
                  "item_category": "Electronics", "value": 4200, "currency": "NPR"},
    "add_to_cart": {"item_id": "1", "item_name": "Bluetooth Headphone",
                    "item_category": "Electronics", "quantity": 1,
                    "value": 2500, "currency": "NPR"},
    "begin_checkout": {"items": 2, "value": 4300, "currency": "NPR"},
    "purchase": {"transaction_id": "TXN-DEMO01", "value": 4400,
                 "shipping": 100, "currency": "NPR", "items": 2},
}

# The parameters that are read from the GA4 reports for this store.
PARAMETERS = [
    ("Users / Active users",
     "How many different people opened the store", "Realtime"),
    ("Sessions",
     "Number of visits, a session ends after 30 minutes idle", "Acquisition"),
    ("Views (page_view)",
     "Pages opened, collected automatically by gtag.js", "Engagement > Pages"),
    ("Engagement rate",
     "Sessions of 10s or more, with 2 views or an event", "Engagement"),
    ("Average engagement time",
     "Time the page was actually in the foreground", "Engagement"),
    ("Event count",
     "How many times each event such as add_to_cart was fired", "Events"),
    ("Conversions",
     "Events marked as key events, purchase in this store", "Admin > Events"),
    ("Item revenue / value",
     "Money value sent with the e-commerce events", "Monetisation"),
    ("Traffic source / medium",
     "Where the visitor came from, e.g. google / organic", "Acquisition"),
    ("Device, browser, country",
     "Dimensions collected automatically for each visitor", "Tech reports"),
]


@lab6.route("/lab6")
def page():
    return render_template("lab6.html", active="lab6", measurement_id=MEASUREMENT_ID,
                           library=EVENT_LIBRARY, parameters=PARAMETERS,
                           events=list(reversed(data.events)))


@lab6.route("/lab6/track/<event_name>", methods=["POST"])
def track(event_name):
    params = EVENT_LIBRARY.get(event_name)
    if params:
        data.events.append({
            "name": event_name,
            "params": params,
            "time": datetime.now().strftime("%H:%M:%S"),
        })
    return redirect(url_for("lab6.page"))


@lab6.route("/lab6/clear", methods=["POST"])
def clear():
    data.events.clear()
    return redirect(url_for("lab6.page"))
