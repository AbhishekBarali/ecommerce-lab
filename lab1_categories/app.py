"""Lab 1 - Product category list and items.

Create product categories, add items into a chosen category, and display
every item together with its category.

Run:  python app.py      then open http://127.0.0.1:5001

Abhishek Barali - 023bscit003 - Section A - Batch 2023
"""
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

STAFF = {"name": "Abhishek Barali", "roll": "023bscit003"}

# Categories are a plain list of names.
categories = ["Electronics", "Fashion", "Groceries"]

# Items are a list of dictionaries; each one remembers its category.
items = [
    {"code": "BT-01", "name": "Bluetooth Headphone", "price": 2500,
     "stock": 12, "category": "Electronics"},
    {"code": "PB-02", "name": "Power Bank 10000mAh", "price": 1800,
     "stock": 7, "category": "Electronics"},
    {"code": "SW-03", "name": "Smart Watch", "price": 4200,
     "stock": 4, "category": "Electronics"},
    {"code": "TS-04", "name": "Cotton T-Shirt", "price": 900,
     "stock": 25, "category": "Fashion"},
    {"code": "RS-05", "name": "Running Shoes", "price": 3500,
     "stock": 9, "category": "Fashion"},
    {"code": "BR-06", "name": "Basmati Rice 5kg", "price": 1250,
     "stock": 30, "category": "Groceries"},
    {"code": "SO-07", "name": "Sunflower Oil 2L", "price": 640,
     "stock": 18, "category": "Groceries"},
]


def next_code(category):
    """Build a short item code from the category name and the item count."""
    return f"{category[:2].upper()}-{len(items) + 1:02d}"


@app.route("/")
def home():
    grouped = [(c, [i for i in items if i["category"] == c]) for c in categories]
    return render_template("index.html", staff=STAFF, categories=categories,
                           grouped=grouped, items=items,
                           note=request.args.get("note"))


@app.route("/category", methods=["POST"])
def add_category():
    name = request.form.get("category", "").strip()
    if not name:
        return redirect(url_for("home"))
    if name in categories:
        return redirect(url_for("home", note=f"Category '{name}' already exists."))
    categories.append(name)
    return redirect(url_for("home", note=f"Category '{name}' created."))


@app.route("/item", methods=["POST"])
def add_item():
    name = request.form.get("name", "").strip()
    category = request.form.get("category", "")
    if not name or category not in categories:
        return redirect(url_for("home"))
    items.append({
        "code": next_code(category),
        "name": name,
        "price": int(request.form.get("price") or 0),
        "stock": int(request.form.get("stock") or 0),
        "category": category,
    })
    return redirect(url_for("home", note=f"'{name}' added under {category}."))


if __name__ == "__main__":
    app.run(port=5001, debug=True)
