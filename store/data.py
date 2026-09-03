"""Shared in-memory data for all lab programs.

No database is used. Everything is stored in plain Python lists and
dictionaries, which is allowed by the assignment.
"""

# ---------------------------------------------------------------- Lab 1 data
# Category list. Each category is just a name.
categories = ["Electronics", "Fashion", "Groceries"]

# Item list. Each item is a dictionary that remembers its category.
items = [
    {"id": 1, "name": "Bluetooth Headphone", "price": 2500, "category": "Electronics"},
    {"id": 2, "name": "Power Bank 10000mAh", "price": 1800, "category": "Electronics"},
    {"id": 3, "name": "Smart Watch", "price": 4200, "category": "Electronics"},
    {"id": 4, "name": "Cotton T-Shirt", "price": 900, "category": "Fashion"},
    {"id": 5, "name": "Running Shoes", "price": 3500, "category": "Fashion"},
    {"id": 6, "name": "Basmati Rice 5kg", "price": 1250, "category": "Groceries"},
    {"id": 7, "name": "Sunflower Oil 2L", "price": 640, "category": "Groceries"},
    {"id": 8, "name": "Green Tea 100g", "price": 320, "category": "Groceries"},
]

# ------------------------------------------------------- Labs 2, 3, 4 storage
cart = []       # list of {"id", "name", "price", "qty"}
wishlist = []   # list of items
orders = []     # list of {"order_id", "customer", "address", "items", "total"}
payments = []   # list of sandbox payment records (Lab 5)
events = []     # list of analytics events (Lab 6)


def next_item_id():
    """Small helper so newly added items never reuse an id."""
    return max([item["id"] for item in items], default=0) + 1


def find_item(item_id):
    for item in items:
        if item["id"] == item_id:
            return item
    return None


def cart_total():
    return sum(line["price"] * line["qty"] for line in cart)
