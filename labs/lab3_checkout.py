"""Lab 3 - Add to cart plus checkout, and display of the ordered item list."""
from flask import Blueprint, render_template, request, redirect, url_for

from store import data
from labs.lab2_cart import add_to_cart

lab3 = Blueprint("lab3", __name__)


@lab3.route("/lab3")
def page():
    return render_template("lab3.html", active="lab3", products=data.items,
                           cart=data.cart, total=data.cart_total(),
                           orders=data.orders, msg=request.args.get("msg"))


@lab3.route("/lab3/add/<int:item_id>", methods=["POST"])
def add(item_id):
    item = add_to_cart(item_id)
    msg = f"'{item['name']}' added to cart." if item else None
    return redirect(url_for("lab3.page", msg=msg))


@lab3.route("/lab3/checkout", methods=["POST"])
def checkout():
    if not data.cart:
        return redirect(url_for("lab3.page", msg="Cart is empty, nothing to check out."))

    order = {
        "order_id": 1001 + len(data.orders),
        "customer": request.form.get("customer", "Guest").strip() or "Guest",
        "address": request.form.get("address", "-").strip() or "-",
        "items": [dict(line) for line in data.cart],   # copy the cart lines
        "total": data.cart_total(),
    }
    data.orders.append(order)
    data.cart.clear()                                  # cart is emptied after checkout
    return redirect(url_for("lab3.page", msg=f"Order #{order['order_id']} placed successfully."))
