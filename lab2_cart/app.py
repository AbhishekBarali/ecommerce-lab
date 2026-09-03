"""Lab 2 - Product list and add to cart.

Show a product list, add products to the cart, change quantity, and display
the cart items with a total.

Run:  python app.py      then open http://127.0.0.1:5002

Abhishek Barali - 023bscit003 - Section A - Batch 2023
"""
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

SHOPPER = {"name": "Abhishek Barali", "roll": "023bscit003", "city": "Kathmandu"}

products = [
    {"id": 1, "name": "Basmati Rice", "unit": "5 kg bag", "price": 1250, "shelf": "Grains"},
    {"id": 2, "name": "Sunflower Oil", "unit": "2 litre", "price": 640, "shelf": "Grains"},
    {"id": 3, "name": "Green Tea", "unit": "100 g", "price": 320, "shelf": "Beverages"},
    {"id": 4, "name": "Ground Coffee", "unit": "250 g", "price": 780, "shelf": "Beverages"},
    {"id": 5, "name": "Cheddar Cheese", "unit": "400 g", "price": 910, "shelf": "Dairy"},
    {"id": 6, "name": "Fresh Curd", "unit": "500 ml", "price": 180, "shelf": "Dairy"},
]

cart = []      # each line: {"id", "name", "unit", "price", "qty"}


def find(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def line_for(product_id):
    return next((line for line in cart if line["id"] == product_id), None)


def total():
    return sum(line["price"] * line["qty"] for line in cart)


@app.route("/")
def home():
    shelves = sorted({p["shelf"] for p in products}, key=lambda s: s)
    return render_template("index.html", shopper=SHOPPER, products=products,
                           shelves=shelves, cart=cart, total=total(),
                           items=sum(line["qty"] for line in cart),
                           note=request.args.get("note"))


@app.route("/add/<int:product_id>", methods=["POST"])
def add(product_id):
    product = find(product_id)
    if not product:
        return redirect(url_for("home"))
    line = line_for(product_id)
    if line:
        line["qty"] += 1                       # already in the cart, so raise qty
    else:
        cart.append({"id": product["id"], "name": product["name"],
                     "unit": product["unit"], "price": product["price"], "qty": 1})
    return redirect(url_for("home", note=f"{product['name']} added to the cart."))


@app.route("/less/<int:product_id>", methods=["POST"])
def less(product_id):
    line = line_for(product_id)
    if line:
        line["qty"] -= 1
        if line["qty"] <= 0:
            cart.remove(line)
    return redirect(url_for("home"))


@app.route("/drop/<int:product_id>", methods=["POST"])
def drop(product_id):
    line = line_for(product_id)
    if line:
        cart.remove(line)
        return redirect(url_for("home", note=f"{line['name']} removed from the cart."))
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(port=5002, debug=True)
