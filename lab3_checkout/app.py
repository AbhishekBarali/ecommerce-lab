"""Lab 3 - Add to cart and checkout.

Add products to the cart, check out with customer details, and display the
ordered list of items as a receipt.

Run:  python app.py      then open http://127.0.0.1:5003

Abhishek Barali - 023bscit003 - Section A - Batch 2023
"""
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

BUYER = {"name": "Abhishek Barali", "roll": "023bscit003",
         "address": "Baneshwor, Kathmandu", "phone": "98XXXXXX01"}

DELIVERY = 100

products = [
    {"id": 1, "name": "Mechanical Keyboard", "price": 5400},
    {"id": 2, "name": "Wireless Mouse", "price": 1350},
    {"id": 3, "name": "Laptop Stand", "price": 2100},
    {"id": 4, "name": "USB-C Hub", "price": 2950},
    {"id": 5, "name": "Desk Lamp", "price": 1780},
    {"id": 6, "name": "Monitor Riser", "price": 3200},
]

cart = []       # each line: {"id", "name", "price", "qty"}
orders = []     # each order: {"number", "buyer", "roll", "address", "placed",
                #              "lines", "goods", "delivery", "total"}


def find(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def goods_total():
    return sum(line["price"] * line["qty"] for line in cart)


@app.route("/")
def home():
    return render_template("index.html", buyer=BUYER, products=products,
                           cart=cart, goods=goods_total(), delivery=DELIVERY,
                           orders=list(reversed(orders)),
                           note=request.args.get("note"))


@app.route("/add/<int:product_id>", methods=["POST"])
def add(product_id):
    product = find(product_id)
    if not product:
        return redirect(url_for("home"))
    line = next((l for l in cart if l["id"] == product_id), None)
    if line:
        line["qty"] += 1
    else:
        cart.append({"id": product["id"], "name": product["name"],
                     "price": product["price"], "qty": 1})
    return redirect(url_for("home", note=f"{product['name']} is in the cart."))


@app.route("/drop/<int:product_id>", methods=["POST"])
def drop(product_id):
    cart[:] = [line for line in cart if line["id"] != product_id]
    return redirect(url_for("home", note="Item removed from the cart."))


@app.route("/checkout", methods=["POST"])
def checkout():
    """Turn the cart into an order, then empty the cart."""
    if not cart:
        return redirect(url_for("home", note="The cart is empty, so there is nothing to check out."))

    goods = goods_total()
    order = {
        "number": f"ORD-{BUYER['roll'].upper()}-{len(orders) + 1:02d}",
        "buyer": request.form.get("name", BUYER["name"]).strip() or BUYER["name"],
        "roll": BUYER["roll"],
        "address": request.form.get("address", BUYER["address"]).strip() or BUYER["address"],
        "phone": request.form.get("phone", BUYER["phone"]).strip() or BUYER["phone"],
        "placed": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "lines": [dict(line) for line in cart],       # copy of the cart
        "goods": goods,
        "delivery": DELIVERY,
        "total": goods + DELIVERY,
    }
    orders.append(order)
    cart.clear()
    return redirect(url_for("home", note=f"Order {order['number']} placed."))


if __name__ == "__main__":
    app.run(port=5003, debug=True)
