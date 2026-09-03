"""Build the E-Commerce Laboratory report as a .docx file.

    .venv/bin/python tools/build_report.py

Body text is Times New Roman 12pt and every run is pure black.
"""
import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SHOTS = os.path.join(ROOT, "screenshots")
OUTDIR = os.path.join(ROOT, "docs")
OUTFILE = os.path.join(OUTDIR, "ECommerce_Lab_Report_Abhishek_Barali_023bscit003.docx")

BLACK = RGBColor(0, 0, 0)
BODY_FONT = "Times New Roman"
CODE_FONT = "Consolas"
MAX_IMG_W = 6.1     # inches
MAX_IMG_H = 7.6     # inches

STUDENT = [
    ("Name", "Abhishek Barali"),
    ("Roll No.", "023bscit003"),
    ("Section", "A"),
    ("Semester / Batch", "2023"),
    ("Subject", "E-Commerce Laboratory"),
    ("Language used", "Python 3 with the Flask micro framework"),
    ("Data storage", "In-memory lists and dictionaries (no database)"),
]

FIG = [0]   # figure counter


# --------------------------------------------------------------- helpers
def set_black(run, font=BODY_FONT, size=12, bold=False, italic=False):
    run.font.name = font
    run.font.size = Pt(size)
    run.font.color.rgb = BLACK
    run.bold = bold
    run.italic = italic
    run._element.rPr.rFonts.set(qn("w:eastAsia"), font)


def para(doc, text="", size=12, bold=False, italic=False, align=None,
         space_after=8, font=BODY_FONT):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if text:
        set_black(p.add_run(text), font=font, size=size, bold=bold, italic=italic)
    return p


def heading(doc, text, level=1):
    sizes = {1: 16, 2: 13.5, 3: 12.5}
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16 if level == 1 else 12)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    set_black(p.add_run(text), size=sizes[level], bold=True)
    if level == 1:
        bottom_border(p)
    return p


def bottom_border(paragraph):
    pPr = paragraph._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "6")
    bottom.set(qn("w:space"), "2")
    bottom.set(qn("w:color"), "000000")
    borders.append(bottom)
    pPr.append(borders)


def shade(cell, hex_fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_fill)
    tcPr.append(shd)


def bullets(doc, lines, numbered=False):
    style = "List Number" if numbered else "List Bullet"
    for line in lines:
        p = doc.add_paragraph(style=style)
        p.paragraph_format.space_after = Pt(4)
        set_black(p.add_run(line))
        mark_black(p)


def mark_black(paragraph):
    """Make the paragraph mark itself Times New Roman black, so list numbers
    and bullets are not rendered in the template's default font/colour."""
    pPr = paragraph._p.get_or_add_pPr()
    rPr = pPr.find(qn("w:rPr"))
    if rPr is None:
        rPr = OxmlElement("w:rPr")
        pPr.append(rPr)
    fonts = OxmlElement("w:rFonts")
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(attr), BODY_FONT)
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "000000")
    size = OxmlElement("w:sz")
    size.set(qn("w:val"), "24")          # half-points, so 12pt
    for element in (fonts, color, size):
        rPr.append(element)


def info_table(doc, rows, widths=(2.0, 4.1), header=None):
    table = doc.add_table(rows=0, cols=len(widths))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    if header:
        cells = table.add_row().cells
        for cell, text in zip(cells, header):
            shade(cell, "EDEDED")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            set_black(p.add_run(text), size=11.5, bold=True)
    for row in rows:
        cells = table.add_row().cells
        for index, (cell, text) in enumerate(zip(cells, row)):
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            set_black(p.add_run(str(text)), size=11.5, bold=(index == 0 and not header))
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            cell.width = Inches(width)
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    return table


def code_block(doc, path, caption=None, first=None, last=None):
    """Insert the source file (or a slice of it) as a shaded monospace block."""
    with open(os.path.join(ROOT, path), encoding="utf-8") as handle:
        lines = handle.read().rstrip("\n").split("\n")
    lines = lines[(first - 1 if first else 0):(last if last else len(lines))]

    table = doc.add_table(rows=1, cols=1)
    table.style = "Table Grid"
    cell = table.cell(0, 0)
    shade(cell, "F5F5F5")
    cell.width = Inches(6.1)
    cell.paragraphs[0]._p.getparent().remove(cell.paragraphs[0]._p)
    for line in lines:
        for piece in soft_wrap(line.replace("\t", "    ")):
            p = cell.add_paragraph()
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            set_black(p.add_run(piece), font=CODE_FONT, size=9)
    para(doc, caption or f"Code: {path}", size=10.5, italic=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)


def soft_wrap(line, limit=86):
    """Break a long code line so it cannot spill outside the page margin."""
    if len(line) <= limit:
        return [line]
    indent = " " * (len(line) - len(line.lstrip()) + 4)
    pieces, rest = [], line
    while len(rest) > limit:
        cut = rest.rfind(" ", 0, limit)
        if cut <= len(indent):
            cut = limit
        pieces.append(rest[:cut])
        rest = indent + rest[cut:].lstrip()
    pieces.append(rest)
    return pieces


def figure(doc, filename, caption):
    path = os.path.join(SHOTS, filename)
    width_px, height_px = Image.open(path).size
    width = MAX_IMG_W
    if width * height_px / width_px > MAX_IMG_H:
        width = MAX_IMG_H * width_px / height_px
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    p.add_run().add_picture(path, width=Inches(width))
    FIG[0] += 1
    para(doc, f"Figure {FIG[0]}: {caption}", size=10.5, italic=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)


def lab_block(doc, number, title, objective, steps, code_files, figures, output_note):
    heading(doc, f"Lab {number}: {title}", level=1)

    heading(doc, "Objective", level=2)
    para(doc, objective)

    heading(doc, "Logic used", level=2)
    bullets(doc, steps, numbered=True)

    heading(doc, "Source code", level=2)
    for path, caption, span in code_files:
        code_block(doc, path, caption, *(span or (None, None)))

    heading(doc, "Output", level=2)
    para(doc, output_note)
    for filename, caption in figures:
        figure(doc, filename, caption)


# --------------------------------------------------------------- document
def build():
    os.makedirs(OUTDIR, exist_ok=True)
    doc = Document()

    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(12)
    normal.font.color.rgb = BLACK
    normal.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)

    for section in doc.sections:
        section.top_margin = section.bottom_margin = Inches(1)
        section.left_margin = section.right_margin = Inches(1)

    # ----- title page
    para(doc, space_after=40)
    para(doc, "E-COMMERCE LABORATORY", size=22, bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    para(doc, "Lab Assignment Report: Programs 1 to 6", size=14,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4)
    para(doc, "A mini e-commerce store built in Python", size=12, italic=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=40)
    info_table(doc, STUDENT, widths=(2.0, 4.1))
    para(doc, space_after=30)
    para(doc, "Source code: https://github.com/AbhishekBarali/ecommerce-lab",
         size=11.5, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)
    doc.add_section(WD_SECTION.NEW_PAGE)

    # ----- contents
    heading(doc, "Contents", level=1)
    bullets(doc, [
        "Introduction",
        "Tools used and how to run the programs",
        "Lab 1: Product category list and items",
        "Lab 2: Product list and add to cart",
        "Lab 3: Add to cart and checkout",
        "Lab 4: Product list and wish list",
        "Lab 5: Payment gateway integration in sandbox mode",
        "Lab 6: Google Analytics setup and analytics parameters",
        "Conclusion",
    ], numbered=True)

    # ----- introduction
    heading(doc, "Introduction", level=1)
    para(doc, "This report covers the six programs of the E-Commerce Laboratory. "
              "All six are parts of one small online store, so the same product data is "
              "reused by every program instead of being written again for each lab. The "
              "store is written in Python using the Flask micro framework, and every "
              "record is held in ordinary Python lists and dictionaries, which the "
              "assignment allows in place of a database.")
    para(doc, "Each lab below is presented with its objective, the logic that was used, "
              "the source code of that program, and a screenshot of the output taken "
              "while the program was running.")

    heading(doc, "Tools used and how to run the programs", level=2)
    info_table(doc, [
        ("Language", "Python 3.12"),
        ("Framework", "Flask 3.1 (routing and HTML templates)"),
        ("Data storage", "Python lists and dictionaries in store/data.py"),
        ("Analytics", "Google Analytics 4 tracking snippet (gtag.js)"),
        ("Payment gateway", "eSewa test mode (sandbox), no live key used"),
        ("Editor / OS", "Visual Studio Code on Linux"),
    ], widths=(2.0, 4.1))

    para(doc, "The whole store runs from a single command:")
    code_block(doc, "docs/run_commands.txt", "Commands used to run the store")

    heading(doc, "Project structure", level=2)
    code_block(doc, "docs/structure.txt", "Files in the project")
    figure(doc, "01-home.png",
           "Home page of the store listing all six lab programs")

    # ----- Lab 1
    lab_block(
        doc, 1, "Product Category List and Items",
        "Create a product category list, add items into the created categories, and "
        "display all items together with their categories.",
        [
            "Categories are kept in a simple list of names, and items in a list of "
            "dictionaries where each item remembers the category it belongs to.",
            "The 'Add Category' form appends a new name to the category list, and "
            "duplicate names are ignored.",
            "The 'Add Item' form appends a dictionary with an id, name, price and the "
            "chosen category.",
            "For display, the items are grouped category by category, and every group "
            "is shown as a table with the item and its category.",
        ],
        [("store/data.py", "store/data.py - the category and item lists", (1, 30)),
         ("labs/lab1_categories.py", "labs/lab1_categories.py - add category, add item, display grouped items", None)],
        [("02-lab1-categories.png",
          "Lab 1 output. A new category 'Stationery' was created and the item "
          "'A4 Notebook' was added to it. Items are listed under their categories.")],
        "A new category was created and an item was added into it, then all items were "
        "listed under their own category with the category name shown in each row.",
    )

    # ----- Lab 2
    lab_block(
        doc, 2, "Product List and Add to Cart",
        "Create a product list, provide an add-to-cart feature for the products, and "
        "display the items present in the cart.",
        [
            "The product list from Lab 1 is displayed as cards, each with its own "
            "'Add to Cart' button.",
            "The cart is a separate list of dictionaries holding the id, name, price "
            "and quantity of each line.",
            "If the product is already in the cart, only its quantity is increased; "
            "otherwise a new line is appended.",
            "The cart table shows every line with its subtotal, and the total is the "
            "sum of price multiplied by quantity for all lines.",
        ],
        [("labs/lab2_cart.py", "labs/lab2_cart.py - add to cart, remove from cart, display cart", None)],
        [("03-lab2-products.png", "Lab 2. The product list with an Add to Cart button on every product."),
         ("04-lab2-cart.png",
          "Lab 2 output. Bluetooth Headphone and two units of Running Shoes are in the "
          "cart, with subtotals and a total of NPR 9500.")],
        "Products were added to the cart, the quantity of a repeated product increased "
        "instead of creating a duplicate line, and the cart was displayed with the total "
        "amount.",
    )

    # ----- Lab 3
    lab_block(
        doc, 3, "Add to Cart and Checkout",
        "Implement the add-to-cart and checkout features of the shopping store and "
        "display the ordered list of items.",
        [
            "Products are added to the same cart list used in Lab 2.",
            "The checkout form collects the customer name and the delivery address.",
            "On checkout, a new order dictionary is created with an order number, the "
            "customer details, a copy of the cart lines and the total amount.",
            "The order is appended to the orders list and the cart is emptied, which is "
            "how a real store behaves after an order is placed.",
            "Every placed order is then displayed as an ordered list of items.",
        ],
        [("labs/lab3_checkout.py", "labs/lab3_checkout.py - checkout turns the cart into an order", None)],
        [("05-lab3-checkout.png", "Lab 3. The cart on the left and the checkout form on the right."),
         ("06-lab3-order.png",
          "Lab 3 output. Order #1001 was placed, the cart became empty, and the ordered "
          "list of items is displayed with quantities and subtotals.")],
        "The cart was checked out into order number 1001, the cart was emptied, and the "
        "ordered list of items was displayed with the customer name, address and total.",
    )

    # ----- Lab 4
    lab_block(
        doc, 4, "Product List and Wish List",
        "Create a product list with an add-to-wish-list feature and display the wish "
        "list items.",
        [
            "The wish list is a separate list, so a product can be saved for later "
            "without being bought.",
            "A product is appended only once; if it is already saved, the button shows "
            "'In Wish List' and the program reports that the item is already there.",
            "A saved item can be removed from the wish list, or moved into the cart, "
            "in which case it is added to the cart and dropped from the wish list.",
            "The wish list is displayed as a table with the item, its category and price.",
        ],
        [("labs/lab4_wishlist.py", "labs/lab4_wishlist.py - wish list add, remove and move to cart", None)],
        [("07-lab4-wishlist.png",
          "Lab 4 output. Smart Watch and Sunflower Oil 2L are saved in the wish list, "
          "and their buttons now read 'In Wish List'.")],
        "Two products were saved to the wish list and displayed with their category and "
        "price, and each saved item offers a move-to-cart and a remove action.",
    )

    # ----- Lab 5
    lab_block(
        doc, 5, "Payment Gateway Integration (Sandbox)",
        "Integrate a payment gateway of choice into an e-commerce page. eSewa was "
        "chosen, and it is used in test (sandbox) mode.",
        [
            "The payment page shows the order summary: cart subtotal, delivery charge "
            "and the amount payable.",
            "Pressing 'Pay with eSewa' posts the amount and the merchant product code "
            "EPAYTEST to the gateway screen, which is how the live integration also "
            "starts.",
            "The gateway screen asks for the eSewa ID, password and token. The values "
            "used are the published sandbox test credentials, so no real account and no "
            "real money is involved.",
            "The program verifies the credentials, generates a transaction reference, "
            "and records the payment with a status of COMPLETE or FAILED.",
            "The result page shows the gateway response, and every attempt is kept in a "
            "payment log.",
        ],
        [("labs/lab5_payment.py", "labs/lab5_payment.py - sandbox payment flow and verification", None)],
        [("08-lab5-payment.png", "Lab 5. The e-commerce payment page with the order summary and the test mode details."),
         ("09-lab5-gateway.png", "Lab 5. The sandbox gateway screen showing the amount of NPR 4300 to be paid."),
         ("10-lab5-result.png",
          "Lab 5 output. The gateway returned status COMPLETE with a transaction "
          "reference, and the payment is stored in the payment log.")],
        "The order amount was sent to the gateway, the sandbox credentials were "
        "verified, and the gateway returned a transaction reference with the status "
        "COMPLETE. Since this runs in test mode, no live merchant key is used and no "
        "real money is transferred.",
    )

    # ----- Lab 6
    lab_block(
        doc, 6, "Google Analytics Setup and Analytics Parameters",
        "Set up Google Analytics on the store and determine the analytics parameters "
        "that should be measured.",
        [
            "A Google Analytics 4 property with a Web data stream gives a Measurement "
            "ID of the form G-XXXXXXXXXX.",
            "The gtag.js tracking snippet is pasted inside the <head> of the shared "
            "layout templates/base.html, so all six lab pages report a page view with "
            "one copy of the code.",
            "Enhanced measurement covers page views, scrolls and outbound clicks "
            "automatically, so no extra code is needed for those.",
            "The store also fires the standard e-commerce events view_item, "
            "add_to_cart, begin_checkout and purchase, each with parameters such as "
            "item_name, value and currency.",
            "Every fired event is also stored locally and displayed in a table, so the "
            "parameters being collected can be seen directly on the page.",
            "The parameters read from the GA4 reports are listed in the table below.",
        ],
        [("labs/lab6_analytics.py", "labs/lab6_analytics.py - events fired and parameters measured", None),
         ("templates/base.html", "templates/base.html - the GA4 tracking snippet in the page head", (9, 19))],
        [("11-lab6-setup.png", "Lab 6. Setup steps and the tracking snippet installed on every page."),
         ("12-lab6-events.png",
          "Lab 6 output. Five e-commerce events were fired and each one is listed with "
          "the parameters sent, followed by the analytics parameters determined for the store.")],
        "The tracking snippet was installed site wide, the e-commerce events were fired "
        "and captured with their parameters, and the parameters to be monitored were "
        "written down.",
    )

    heading(doc, "Analytics parameters determined", level=2)
    info_table(doc, [
        ("Users / Active users", "How many different people opened the store", "Realtime"),
        ("Sessions", "Number of visits; a session ends after 30 minutes idle", "Acquisition"),
        ("Views (page_view)", "Pages opened, collected automatically by gtag.js", "Engagement > Pages"),
        ("Engagement rate", "Sessions lasting 10s or more, with 2+ views or an event", "Engagement"),
        ("Average engagement time", "Time the page was actually in the foreground", "Engagement"),
        ("Event count", "How many times each event such as add_to_cart was fired", "Engagement > Events"),
        ("Conversions", "Events marked as key events; purchase in this store", "Admin > Events"),
        ("Item revenue / value", "Money value sent with the e-commerce events", "Monetisation"),
        ("Traffic source / medium", "Where the visitor came from, e.g. google / organic", "Acquisition"),
        ("Device, browser, country", "Dimensions collected automatically for each visitor", "Tech, Demographics"),
    ], widths=(1.8, 3.0, 1.3), header=("Parameter", "What it tells us", "GA4 report"))

    para(doc, "Note: the Measurement ID in the code is a placeholder. Replacing it with "
              "the ID of a real GA4 property is the only change needed for live data to "
              "start flowing into the reports.")

    # ----- conclusion
    heading(doc, "Conclusion", level=1)
    para(doc, "All six programs of the E-Commerce Laboratory were completed as one "
              "small working store. Labs 1 to 4 covered the catalogue side of an online "
              "shop: categories and items, the cart, checkout into an order, and the "
              "wish list, all of them using plain lists and dictionaries instead of a "
              "database. Lab 5 connected the order amount to a payment gateway running "
              "in sandbox mode, and Lab 6 added Google Analytics tracking along with "
              "the list of parameters worth measuring for such a store.")
    para(doc, "Building the labs on shared data made the relationship between them "
              "clear: the same product list feeds the cart, the cart feeds the order, "
              "the order feeds the payment, and the actions along the way are exactly "
              "the events that analytics measures.")

    doc.save(OUTFILE)
    print("wrote", OUTFILE)


if __name__ == "__main__":
    build()
