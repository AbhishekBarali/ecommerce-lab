"""Lab 4 - Product list and wish list.

Save products to a wish list, display the saved items, remove them, and move
a saved item into the cart.

Run:  python app.py      then open http://127.0.0.1:5004

Abhishek Barali - 023bscit003 - Section A - Batch 2023
"""
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

OWNER = {"name": "Abhishek Barali", "roll": "023bscit003"}

products = [
    {"id": 1, "name": "Acoustic Guitar", "brand": "Cort", "price": 24500},
    {"id": 2, "name": "Noise Cancelling Headphone", "brand": "Sony", "price": 18900},
    {"id": 3, "name": "Fitness Band", "brand": "Mi", "price": 4300},
    {"id": 4, "name": "Espresso Maker", "brand": "Delonghi", "price": 15600},
    {"id": 5, "name": "Trekking Backpack 45L", "brand": "Quechua", "price": 7200},
    {"id": 6, "name": "Instant Camera", "brand": "Fujifilm", "price": 11800},
]

wishlist = []   # each entry: product dictionary plus the time it was saved
cart = []       # products moved out of the wish list


def find(product_id):
    return next((p for p in products if p["id"] == product_id), None)


def saved_ids():
    return [w["id"] for w in wishlist]


@app.route("/")
def home():
    return render_template("index.html", owner=OWNER, products=products,
                           wishlist=wishlist, saved=saved_ids(), cart=cart,
                           value=sum(w["price"] for w in wishlist),
                           note=request.args.get("note"))


@app.route("/save/<int:product_id>", methods=["POST"])
def save(product_id):
    product = find(product_id)
    if not product:
        return redirect(url_for("home"))
    if product["id"] in saved_ids():
        return redirect(url_for("home", note=f"{product['name']} is already on the wish list."))
    entry = dict(product)
    entry["saved_at"] = datetime.now().strftime("%d %b, %I:%M %p")
    wishlist.append(entry)
    return redirect(url_for("home", note=f"{product['name']} saved to the wish list."))


@app.route("/forget/<int:product_id>", methods=["POST"])
def forget(product_id):
    wishlist[:] = [w for w in wishlist if w["id"] != product_id]
    return redirect(url_for("home", note="Item removed from the wish list."))


@app.route("/move/<int:product_id>", methods=["POST"])
def move(product_id):
    """Move a saved item out of the wish list and into the cart."""
    entry = next((w for w in wishlist if w["id"] == product_id), None)
    if entry:
        cart.append(entry)
        wishlist.remove(entry)
        return redirect(url_for("home", note=f"{entry['name']} moved to the cart."))
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(port=5004, debug=True)
