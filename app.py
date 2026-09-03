"""E-Commerce Laboratory - all six lab programs in one small Flask app.

Run with:  python app.py     then open http://127.0.0.1:5000

Student : Abhishek Barali
Roll no : 023bscit003
Section : A        Batch : 2023
"""
from flask import Flask, render_template

from labs.lab1_categories import lab1
from labs.lab2_cart import lab2
from labs.lab3_checkout import lab3
from labs.lab4_wishlist import lab4
from labs.lab5_payment import lab5
from labs.lab6_analytics import lab6
from store import data

app = Flask(__name__)

for blueprint in (lab1, lab2, lab3, lab4, lab5, lab6):
    app.register_blueprint(blueprint)

LABS = [
    ("1", "Product category list", "Create categories, add items to them and display items with their categories.", "/lab1"),
    ("2", "Product list and add to cart", "List products, add them to the cart and display the cart items.", "/lab2"),
    ("3", "Add to cart and checkout", "Check the cart out into an order and display the ordered list of items.", "/lab3"),
    ("4", "Wish list", "Save products to a wish list, display it, and move items to the cart.", "/lab4"),
    ("5", "Payment gateway", "Pay the order amount through a payment gateway running in sandbox mode.", "/lab5"),
    ("6", "Google Analytics", "Install the GA4 tracking snippet and determine the analytics parameters.", "/lab6"),
]


@app.route("/")
def home():
    return render_template("home.html", active="home", labs=LABS,
                           products=len(data.items), categories=len(data.categories))


if __name__ == "__main__":
    app.run(debug=True)
