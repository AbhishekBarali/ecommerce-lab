"""Lab 5 - Payment gateway integration in sandbox (test) mode.

The store hands the amount to the gateway, the customer confirms with the
published eSewa sandbox test credentials, and the gateway returns a
transaction reference with a status. No live merchant key is used and no real
money moves, so the flow can be demonstrated offline.

Run:  python app.py      then open http://127.0.0.1:5005

Abhishek Barali - 023bscit003 - Section A - Batch 2023
"""
import random
import string
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

CUSTOMER = {"name": "Abhishek Barali", "roll": "023bscit003",
            "email": "abhishek.barali@example.com"}

# Published eSewa sandbox values. Test environment only.
SANDBOX = {"product_code": "EPAYTEST", "esewa_id": "9806800001",
           "password": "Nepal@123", "token": "123456",
           "success_url": "/gateway/verify", "failure_url": "/gateway/verify"}

ORDER = {
    "number": f"INV-{CUSTOMER['roll'].upper()}-05",
    "lines": [
        {"name": "Annual hosting plan", "qty": 1, "price": 3600},
        {"name": "Domain renewal", "qty": 1, "price": 1400},
    ],
    "delivery": 0,
}

payments = []   # every attempt: reference, amount, status, time


def order_total():
    return sum(l["qty"] * l["price"] for l in ORDER["lines"]) + ORDER["delivery"]


def new_reference():
    tail = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"ESW-{CUSTOMER['roll'][-3:]}-{tail}"


@app.route("/")
def home():
    return render_template("checkout.html", customer=CUSTOMER, order=ORDER,
                           total=order_total(), sandbox=SANDBOX, payments=payments)


@app.route("/gateway", methods=["POST"])
def gateway():
    """Screen shown by the gateway. In production this page is on eSewa's site."""
    return render_template("gateway.html", customer=CUSTOMER, sandbox=SANDBOX,
                           amount=int(request.form.get("amount", 0)),
                           product_code=request.form.get("product_code", ""),
                           order_number=ORDER["number"])


@app.route("/gateway/verify", methods=["POST"])
def verify():
    """Check the credentials, then record the result of the payment."""
    amount = int(request.form.get("amount", 0))
    ok = (request.form.get("esewa_id") == SANDBOX["esewa_id"]
          and request.form.get("password") == SANDBOX["password"]
          and request.form.get("token") == SANDBOX["token"])

    payment = {
        "reference": new_reference(),
        "order": ORDER["number"],
        "payer": CUSTOMER["name"],
        "roll": CUSTOMER["roll"],
        "amount": amount,
        "channel": "eSewa ePay (sandbox)",
        "status": "COMPLETE" if ok else "FAILED",
        "time": datetime.now().strftime("%d %b %Y, %I:%M:%S %p"),
    }
    payments.append(payment)
    return redirect(url_for("result", reference=payment["reference"]))


@app.route("/result")
def result():
    reference = request.args.get("reference")
    payment = next((p for p in payments if p["reference"] == reference), None)
    return render_template("result.html", payment=payment, payments=payments,
                           customer=CUSTOMER)


if __name__ == "__main__":
    app.run(port=5005, debug=True)
