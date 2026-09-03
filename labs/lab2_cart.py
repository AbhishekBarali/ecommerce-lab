"""Lab 2 - Product list with an add-to-cart feature, and display of cart
items.
"""
from flask import Blueprint, render_template, redirect, url_for, request

from store import data

lab2 = Blueprint("lab2", __name__)


def add_to_cart(item_id, qty=1):
    """Add an item to the cart list, or increase quantity if already there."""
    item = data.find_item(item_id)
    if not item:
        return None
    for line in data.cart:
        if line["id"] == item_id:
            line["qty"] += qty
            return item
    data.cart.append({"id": item["id"], "name": item["name"],
                      "price": item["price"], "qty": qty})
    return item


@lab2.route("/lab2")
def page():
    return render_template("lab2.html", active="lab2", products=data.items,
                           cart=data.cart, total=data.cart_total(),
                           msg=request.args.get("msg"))


@lab2.route("/lab2/add/<int:item_id>", methods=["POST"])
def add(item_id):
    item = add_to_cart(item_id)
    msg = f"'{item['name']}' added to cart." if item else None
    return redirect(url_for("lab2.page", msg=msg))


@lab2.route("/lab2/remove/<int:item_id>", methods=["POST"])
def remove(item_id):
    data.cart[:] = [line for line in data.cart if line["id"] != item_id]
    return redirect(url_for("lab2.page", msg="Item removed from cart."))
