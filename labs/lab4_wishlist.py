"""Lab 4 - Product list with an add-to-wish-list feature, and display of the
wish list items.
"""
from flask import Blueprint, render_template, request, redirect, url_for

from store import data
from labs.lab2_cart import add_to_cart

lab4 = Blueprint("lab4", __name__)


@lab4.route("/lab4")
def page():
    wished_ids = [i["id"] for i in data.wishlist]
    return render_template("lab4.html", active="lab4", products=data.items,
                           wishlist=data.wishlist, wished_ids=wished_ids,
                           msg=request.args.get("msg"))


@lab4.route("/lab4/add/<int:item_id>", methods=["POST"])
def add(item_id):
    item = data.find_item(item_id)
    if item and item["id"] not in [w["id"] for w in data.wishlist]:
        data.wishlist.append(item)
        return redirect(url_for("lab4.page", msg=f"'{item['name']}' saved to wish list."))
    return redirect(url_for("lab4.page", msg="Item is already in the wish list."))


@lab4.route("/lab4/remove/<int:item_id>", methods=["POST"])
def remove(item_id):
    data.wishlist[:] = [w for w in data.wishlist if w["id"] != item_id]
    return redirect(url_for("lab4.page", msg="Item removed from wish list."))


@lab4.route("/lab4/move/<int:item_id>", methods=["POST"])
def move_to_cart(item_id):
    """Move a saved item from the wish list into the cart."""
    item = add_to_cart(item_id)
    data.wishlist[:] = [w for w in data.wishlist if w["id"] != item_id]
    msg = f"'{item['name']}' moved to cart." if item else None
    return redirect(url_for("lab4.page", msg=msg))
