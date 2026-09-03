"""Lab 5 - Payment gateway integration (sandbox / test mode).

The flow copies how eSewa's test environment works: the store sends the
amount and a product code to the gateway, the customer confirms with the
published sandbox test credentials, and the gateway sends back a
transaction reference with a status. Nothing here touches real money and no
live API key is used, so the program can be run offline.
"""
import random
import string
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for

from store import data

lab5 = Blueprint("lab5", __name__)

# Published sandbox test credentials (test mode only, not a real account).
SANDBOX = {"merchant_code": "EPAYTEST", "esewa_id": "9806800001",
           "password": "Nepal@123", "token": "123456"}

DELIVERY_CHARGE = 100


def reference():
    return "TXN-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def payable():
    """Amount to pay: cart total plus delivery, or a demo amount if cart is empty."""
    subtotal = data.cart_total() or 2500
    return subtotal, DELIVERY_CHARGE, subtotal + DELIVERY_CHARGE


@lab5.route("/lab5")
def page():
    subtotal, delivery, total = payable()
    return render_template("lab5.html", active="lab5", subtotal=subtotal,
                           delivery=delivery, total=total, sandbox=SANDBOX,
                           payments=data.payments)


@lab5.route("/lab5/gateway", methods=["POST"])
def gateway():
    """The gateway screen. In a live setup this page is hosted by eSewa."""
    return render_template("lab5_gateway.html", active="lab5",
                           amount=int(request.form.get("amount", 0)),
                           sandbox=SANDBOX, error=request.args.get("error"))


@lab5.route("/lab5/verify", methods=["POST"])
def verify():
    """Verify the sandbox credentials and record the payment result."""
    amount = int(request.form.get("amount", 0))
    ok = (request.form.get("esewa_id") == SANDBOX["esewa_id"]
          and request.form.get("password") == SANDBOX["password"]
          and request.form.get("token") == SANDBOX["token"])

    record = {
        "ref": reference(),
        "amount": amount,
        "method": "eSewa (Sandbox)",
        "status": "COMPLETE" if ok else "FAILED",
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    data.payments.append(record)
    return redirect(url_for("lab5.result", ref=record["ref"]))


@lab5.route("/lab5/result")
def result():
    record = next((p for p in data.payments if p["ref"] == request.args.get("ref")), None)
    return render_template("lab5_result.html", active="lab5", record=record,
                           payments=data.payments)
