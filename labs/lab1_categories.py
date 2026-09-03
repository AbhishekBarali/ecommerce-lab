"""Lab 1 - Product category list, add items to a category, display items
with their categories.
"""
from flask import Blueprint, render_template, request, redirect, url_for

from store import data

lab1 = Blueprint("lab1", __name__)


@lab1.route("/lab1")
def page():
    # Group the items under each category for display.
    grouped = {c: [i for i in data.items if i["category"] == c] for c in data.categories}
    return render_template("lab1.html", active="lab1", grouped=grouped,
                           categories=data.categories, msg=request.args.get("msg"))


@lab1.route("/lab1/add-category", methods=["POST"])
def add_category():
    name = request.form.get("category", "").strip()
    if name and name not in data.categories:
        data.categories.append(name)
        return redirect(url_for("lab1.page", msg=f"Category '{name}' created."))
    return redirect(url_for("lab1.page"))


@lab1.route("/lab1/add-item", methods=["POST"])
def add_item():
    name = request.form.get("name", "").strip()
    price = request.form.get("price", "0").strip()
    category = request.form.get("category", "")
    if name and category:
        data.items.append({
            "id": data.next_item_id(),
            "name": name,
            "price": int(price or 0),
            "category": category,
        })
        return redirect(url_for("lab1.page", msg=f"'{name}' added to {category}."))
    return redirect(url_for("lab1.page"))
