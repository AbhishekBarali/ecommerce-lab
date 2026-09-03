/*
 * Build the E-Commerce Laboratory report as a .docx file using docx-js.
 *
 *   node tools/build_report.js
 *
 * Body text is Times New Roman 12pt and every run is black. Page size is US
 * Letter. Code listings are read straight from the lab programs, so the report
 * can never drift from the code.
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, PageBreak,
  Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  HeadingLevel, LevelFormat, BorderStyle,
} = require("docx");

const ROOT = path.dirname(__dirname);
const SHOTS = path.join(ROOT, "screenshots");
const OUT = path.join(ROOT, "docs", "ECommerce_Lab_Report_Abhishek_Barali_023bscit003.docx");

const BODY = "Times New Roman";
const MONO = "Consolas";
const BLACK = "000000";
const CONTENT_DXA = 9360;          // 6.5in of text between 1in margins
const MAX_W_PX = 586;              // docx-js sizes images in pixels at 96 dpi: 6.1in
const MAX_H_PX = 730;              // 7.6in

let figureNo = 0;

/* ------------------------------------------------------------ small helpers */
const text = (t, o = {}) => new TextRun({
  text: t, font: o.font || BODY, size: o.size || 24,
  bold: !!o.bold, italics: !!o.italics, color: BLACK,
});

const para = (t, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { after: o.after === undefined ? 160 : o.after, before: o.before || 0, line: o.line || 276 },
  children: t === "" ? [] : [text(t, o)],
});

const heading = (t, level) => new Paragraph({
  heading: level,
  spacing: { before: level === HeadingLevel.HEADING_1 ? 360 : 260, after: 140 },
  keepNext: true,
  border: level === HeadingLevel.HEADING_1
    ? { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLACK, space: 2 } }
    : undefined,
  children: [text(t, { bold: true, size: level === HeadingLevel.HEADING_1 ? 32 : 26 })],
});

let listInstance = 0;

/* Each call starts a fresh numbering instance, so every list restarts at 1
 * instead of continuing the count from the previous list in the document. */
const numberedList = (items) => {
  listInstance += 1;
  const instance = listInstance;
  return items.map((t) => new Paragraph({
    numbering: { reference: "steps", level: 0, instance },
    spacing: { after: 90, line: 276 },
    children: [text(t)],
  }));
};

/* ---------------------------------------------------------------- table cell */
function cell(value, { width, head = false, bold = false }) {
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: "EDEDED", color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 110, right: 110 },
    children: [new Paragraph({
      spacing: { after: 0, line: 260 },
      children: [text(String(value), { size: 23, bold: head || bold })],
    })],
  });
}

function table(rows, widths, header) {
  const body = [];
  if (header) {
    body.push(new TableRow({
      tableHeader: true,
      children: header.map((h, i) => cell(h, { width: widths[i], head: true })),
    }));
  }
  rows.forEach((r) => {
    body.push(new TableRow({
      children: r.map((v, i) => cell(v, { width: widths[i], bold: !header && i === 0 })),
    }));
  });
  return new Table({ columnWidths: widths, width: { size: CONTENT_DXA, type: WidthType.DXA }, rows: body });
}

/* --------------------------------------------------------------- code listing */
function wrap(line, limit = 88) {
  if (line.length <= limit) return [line];
  const indent = " ".repeat(line.length - line.trimStart().length + 4);
  const out = [];
  let rest = line;
  while (rest.length > limit) {
    let cut = rest.lastIndexOf(" ", limit);
    if (cut <= indent.length) cut = limit;
    out.push(rest.slice(0, cut));
    rest = indent + rest.slice(cut).trimStart();
  }
  out.push(rest);
  return out;
}

function code(file, caption) {
  const src = fs.readFileSync(path.join(ROOT, file), "utf8").replace(/\s+$/, "");
  const lines = [];
  src.split("\n").forEach((l) => wrap(l.replace(/\t/g, "    ")).forEach((p) => lines.push(p)));

  const inner = lines.map((l, i) => new Paragraph({
    spacing: { after: 0, line: 216, before: i === 0 ? 40 : 0 },
    children: [text(l === "" ? " " : l, { font: MONO, size: 17 })],
  }));

  const box = new Table({
    columnWidths: [CONTENT_DXA],
    width: { size: CONTENT_DXA, type: WidthType.DXA },
    rows: [new TableRow({
      children: [new TableCell({
        width: { size: CONTENT_DXA, type: WidthType.DXA },
        shading: { type: ShadingType.CLEAR, fill: "F6F6F4", color: "auto" },
        margins: { top: 90, bottom: 90, left: 150, right: 120 },
        children: inner,
      })],
    })],
  });
  return [box, para(caption, { italics: true, size: 21, align: AlignmentType.CENTER, after: 240 })];
}

/* ---------------------------------------------------------------- screenshots */
function pngSize(file) {
  const b = fs.readFileSync(file);
  return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
}

function figure(name, caption) {
  const file = path.join(SHOTS, name);
  const { w, h } = pngSize(file);
  let width = MAX_W_PX;
  let height = (h / w) * width;
  if (height > MAX_H_PX) { height = MAX_H_PX; width = (w / h) * height; }
  figureNo += 1;
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { after: 80, before: 60 },
      children: [new ImageRun({
        data: fs.readFileSync(file), type: "png",
        transformation: { width: Math.round(width), height: Math.round(height) },
      })],
    }),
    para(`Figure ${figureNo}: ${caption}`, {
      italics: true, size: 21, align: AlignmentType.CENTER, after: 280,
    }),
  ];
}

/* ---------------------------------------------------------------- lab section */
function lab({ number, title, app, port, objective, logic, codeFile, codeCaption, figures, outcome }) {
  return [
    heading(`Lab ${number}: ${title}`, HeadingLevel.HEADING_1),
    para(`Program folder: ${app}   |   run with "python app.py" and open http://127.0.0.1:${port}`,
      { size: 22, italics: true, after: 200 }),

    heading("Objective", HeadingLevel.HEADING_2),
    para(objective),

    heading("Logic used", HeadingLevel.HEADING_2),
    ...numberedList(logic),

    heading("Source code", HeadingLevel.HEADING_2),
    ...code(codeFile, codeCaption),

    heading("Output", HeadingLevel.HEADING_2),
    para(outcome),
    ...figures.flatMap(([file, caption]) => figure(file, caption)),
  ];
}

/* ---------------------------------------------------------------- the content */
const children = [
  para("", { after: 900 }),
  para("E-COMMERCE LABORATORY", { bold: true, size: 44, align: AlignmentType.CENTER, after: 120 }),
  para("Lab Assignment Report: Programs 1 to 6", { size: 28, align: AlignmentType.CENTER, after: 80 }),
  para("Six separate e-commerce programs written in Python", { size: 24, italics: true, align: AlignmentType.CENTER, after: 700 }),
  table([
    ["Name", "Abhishek Barali"],
    ["Roll No.", "023bscit003"],
    ["Section", "A"],
    ["Semester / Batch", "2023"],
    ["Subject", "E-Commerce Laboratory"],
    ["Language used", "Python 3 with the Flask micro framework"],
    ["Data storage", "Lists and dictionaries inside each program, no database"],
  ], [3100, 6260]),
  para("", { after: 600 }),
  para("Source code: https://github.com/AbhishekBarali/ecommerce-lab", { size: 22, align: AlignmentType.CENTER, after: 0 }),
  new Paragraph({ children: [new PageBreak()] }),

  heading("Contents", HeadingLevel.HEADING_1),
  ...numberedList([
    "Introduction",
    "How the programs are organised and run",
    "Lab 1: Product category list and items",
    "Lab 2: Product list and add to cart",
    "Lab 3: Add to cart and checkout",
    "Lab 4: Product list and wish list",
    "Lab 5: Payment gateway integration in sandbox mode",
    "Lab 6: Google Analytics setup and analytics parameters",
    "Conclusion",
  ]),

  heading("Introduction", HeadingLevel.HEADING_1),
  para("This report covers the six programs of the E-Commerce Laboratory. Each lab is a "
    + "separate program with its own folder, its own product data and its own interface, so "
    + "one lab can be run and shown without touching the others. Every program is written in "
    + "Python using the Flask micro framework, and the records are kept in ordinary Python "
    + "lists and dictionaries, which the assignment allows in place of a database."),
  para("Each lab is presented with its objective, the logic that was used, the full source "
    + "code of the program, and screenshots taken while the program was running. The store "
    + "data carries the name Abhishek Barali and the roll number 023bscit003 so the output "
    + "belongs to this submission."),

  heading("How the programs are organised and run", HeadingLevel.HEADING_2),
  para("Each folder holds one program: app.py with the logic, and a templates folder with the "
    + "page it renders. Every lab listens on its own port, so several labs can run side by side."),
  table([
    ["lab1_categories", "Categories and items", "5001"],
    ["lab2_cart", "Product list and cart", "5002"],
    ["lab3_checkout", "Cart and checkout", "5003"],
    ["lab4_wishlist", "Wish list", "5004"],
    ["lab5_payment", "Payment gateway, sandbox", "5005"],
    ["lab6_analytics", "Google Analytics", "5006"],
  ], [2900, 4460, 2000], ["Folder", "Program", "Port"]),
  para("", { after: 120 }),
  ...code("docs/run_commands.txt", "Commands used to install Flask and run one lab"),
];

children.push(...lab({
  number: 1,
  title: "Product Category List and Items",
  app: "lab1_categories",
  port: 5001,
  objective: "Create a product category list, add items into the created categories, and "
    + "display all items together with their categories. The program is presented as the "
    + "catalogue desk of a shop called Barali Traders.",
  logic: [
    "Categories are held in a plain list of names, and items in a list of dictionaries where every item stores the category it belongs to.",
    "The category form appends a new name to the category list, and a name that already exists is reported instead of being added twice.",
    "The item form appends a dictionary with a code, name, price, stock and the category chosen from the dropdown.",
    "The item code is generated from the first two letters of the category and the item count, for example ST-08 for the eighth item filed under Stationery.",
    "For display, the items are grouped category by category and each group is shown as its own table, so every item appears next to its category.",
  ],
  codeFile: "lab1_categories/app.py",
  codeCaption: "lab1_categories/app.py",
  outcome: "The category 'Stationery' was created, the item 'A4 Notebook' was filed under it, "
    + "and the catalogue then listed every item under its own category with the item count per "
    + "category.",
  figures: [
    ["lab1-a-start.png", "Lab 1 before any change: three categories and seven items."],
    ["lab1-b-added.png", "Lab 1 output. 'Stationery' was created and 'A4 Notebook' was added to it, so the catalogue now shows four categories and eight items."],
  ],
}));

children.push(...lab({
  number: 2,
  title: "Product List and Add to Cart",
  app: "lab2_cart",
  port: 5002,
  objective: "Create a product list, provide an add-to-cart feature for the products, and "
    + "display the cart items. The program is presented as an online grocery called Hariyo "
    + "Bazaar, with the cart kept beside the shelves.",
  logic: [
    "Products are a list of dictionaries and are drawn shelf by shelf, so the same list produces the Grains, Beverages and Dairy sections.",
    "The cart is a separate list; each cart line stores the product id, name, unit, price and quantity.",
    "Adding a product that is already in the cart raises its quantity instead of creating a second line.",
    "The minus button lowers the quantity, and a line that reaches zero is dropped from the cart.",
    "The cart panel shows every line with its own amount, and the total is the sum of price multiplied by quantity across all lines.",
  ],
  codeFile: "lab2_cart/app.py",
  codeCaption: "lab2_cart/app.py",
  outcome: "Basmati Rice, Green Tea and Cheddar Cheese were added, and Green Tea was added "
    + "twice so its line shows a quantity of two. The cart reported four items and a total of "
    + "NPR 2800.",
  figures: [
    ["lab2-a-products.png", "Lab 2 with an empty cart, showing the product shelves."],
    ["lab2-b-cart.png", "Lab 2 output. Three products in the cart, one of them with quantity two, and the total for the customer 023bscit003."],
  ],
}));

children.push(...lab({
  number: 3,
  title: "Add to Cart and Checkout",
  app: "lab3_checkout",
  port: 5003,
  objective: "Implement the add-to-cart and checkout features of a shopping store and display "
    + "the ordered list of items. The program is presented as the desk accessory store "
    + "DeskWorks, and every completed order prints as a receipt.",
  logic: [
    "Products are added to a cart list in the same way as Lab 2, with repeat additions raising the quantity.",
    "The payable amount is the goods total plus a fixed delivery charge of NPR 100.",
    "The checkout form collects the customer name, delivery address and phone number, pre-filled with the details of Abhishek Barali.",
    "On checkout an order dictionary is built with an order number, the customer details, the time, a copy of the cart lines and the totals.",
    "The order number is generated from the roll number, so the first order is ORD-023BSCIT003-01.",
    "The order is appended to the orders list and the cart is cleared, which is how a store behaves once an order is placed.",
    "Every placed order is then printed below as an ordered list of items with rate, quantity and amount.",
  ],
  codeFile: "lab3_checkout/app.py",
  codeCaption: "lab3_checkout/app.py",
  outcome: "One mechanical keyboard and two USB-C hubs were checked out as order "
    + "ORD-023BSCIT003-01 for NPR 11,400 including delivery. The cart is empty afterwards and "
    + "the order appears as a receipt.",
  figures: [
    ["lab3-a-cart.png", "Lab 3 before checkout: the cart holds three units and shows the payable amount."],
    ["lab3-b-order.png", "Lab 3 output. Order ORD-023BSCIT003-01 was placed, the cart is empty, and the ordered list of items is printed as a receipt."],
  ],
}));

children.push(...lab({
  number: 4,
  title: "Product List and Wish List",
  app: "lab4_wishlist",
  port: 5004,
  objective: "Create a product list with an add-to-wish-list feature and display the wish "
    + "list items. The program is presented as WishBox, a saved-items page belonging to "
    + "Abhishek Barali.",
  logic: [
    "The wish list is a list separate from the cart, so a product can be kept for later without being bought.",
    "Saving a product copies its dictionary and stamps the time it was saved, which is shown next to the item.",
    "A product already on the wish list cannot be saved twice; its button changes to 'Already on wish list'.",
    "A saved item can be removed, or moved to the cart, in which case it is appended to the cart list and dropped from the wish list.",
    "The wish list shows the saved items in order with their brand, saved time and price, and adds up the value being held.",
  ],
  codeFile: "lab4_wishlist/app.py",
  codeCaption: "lab4_wishlist/app.py",
  outcome: "Three products were saved, holding a value of NPR 51,900, and their buttons "
    + "changed to 'Already on wish list'. The espresso maker was then moved to the cart, which "
    + "left two items on the wish list.",
  figures: [
    ["lab4-a-products.png", "Lab 4 with an empty wish list."],
    ["lab4-b-wishlist.png", "Lab 4 output. Three items saved to the wish list of Abhishek Barali with the total value held."],
    ["lab4-c-moved.png", "Lab 4 after 'Move to cart' on the espresso maker: the wish list drops to two items and the cart strip names the moved product."],
  ],
}));

children.push(...lab({
  number: 5,
  title: "Payment Gateway Integration (Sandbox)",
  app: "lab5_payment",
  port: 5005,
  objective: "Integrate a payment gateway of choice into an e-commerce page. eSewa was "
    + "chosen and is used in sandbox (test) mode, so the whole payment flow can be shown "
    + "without a live merchant key and without any real money.",
  logic: [
    "The invoice page adds up the invoice lines and shows the payable amount for the customer 023bscit003.",
    "Pressing the pay button posts the amount and the merchant product code EPAYTEST to the gateway, which is how the live integration also begins.",
    "The gateway screen asks for the eSewa ID, password and token. The published sandbox test values are pre-filled.",
    "The program verifies the three values and builds a payment record with a transaction reference, the amount, the channel, the time and a status.",
    "The status is COMPLETE when the credentials match and FAILED when they do not, so both paths of a real gateway can be demonstrated.",
    "The result page shows the response from the gateway, and every attempt is kept in a payment log.",
  ],
  codeFile: "lab5_payment/app.py",
  codeCaption: "lab5_payment/app.py",
  outcome: "The invoice for NPR 5,000 was paid through the sandbox gateway. It returned the "
    + "reference ESW-003 with status COMPLETE, and the payment was written to the log. Being "
    + "test mode, no live key is used and no money is transferred.",
  figures: [
    ["lab5-a-invoice.png", "Lab 5. The invoice page with the payable amount and the sandbox configuration sent to the gateway."],
    ["lab5-b-gateway.png", "Lab 5. The gateway screen, which in production is hosted by eSewa, showing the amount and the pre-filled test credentials."],
    ["lab5-c-result.png", "Lab 5 output. The gateway returned status COMPLETE with a transaction reference, and the payment log records the attempt."],
  ],
}));

children.push(...lab({
  number: 6,
  title: "Google Analytics Setup and Analytics Parameters",
  app: "lab6_analytics",
  port: 5006,
  objective: "Set up Google Analytics on the store and determine the analytics parameters "
    + "that should be measured. The program is presented as an analytics console, so the "
    + "events being sent and the parameters being read are visible on one page.",
  logic: [
    "A GA4 property with a web data stream issues a Measurement ID of the form G-XXXXXXXXXX.",
    "The gtag.js snippet is pasted into the head of the page, and the config call also passes user_id 023bscit003, so activity is tied to this account.",
    "The Measurement ID is read from the GA_MEASUREMENT_ID environment variable, so a real property can be used without editing the code.",
    "Enhanced measurement is left on, so page views, scrolls and outbound clicks are collected without any extra code.",
    "Clicking an event button hands that event to gtag on the next page load, so page_view, view_item, add_to_cart, add_to_wishlist, begin_checkout and purchase are really sent to Google Analytics with their parameters.",
    "The page also records every request the browser makes to google-analytics.com and lists them, so the integration can be checked without opening the Google Analytics dashboard.",
    "Every fired event is stored locally with its parameters and time as well, and the report parameters chosen for this store are listed in a table on the page.",
  ],
  codeFile: "lab6_analytics/app.py",
  codeCaption: "lab6_analytics/app.py",
  outcome: "All six events were fired and each one was captured with the parameters sent, for "
    + "example purchase with transaction_id ORD-023BSCIT003-01 and a value of 6800. The hit "
    + "panel shows the same events leaving the browser for the Google Analytics collect "
    + "endpoint. The ten parameters chosen for the store are listed after the figures.",
  figures: [
    ["lab6-a-setup.png", "Lab 6. The setup steps and the tracking snippet installed in the page head."],
    ["lab6-b-events.png", "Lab 6 output. Six events collected with their parameters, followed by the analytics parameters determined for the store."],
    ["lab6-c-hits.png", "Lab 6 verification. The panel lists each hit the browser sent to google-analytics.com, naming the event and the Measurement ID it was sent to."],
  ],
}));

children.push(
  heading("Verification that the events reach Google Analytics", HeadingLevel.HEADING_2),
  para("The events are not only logged inside the program; they are handed to gtag, which "
    + "sends them to Google. A script drives the page in a browser, clicks every event button "
    + "and records each request made to the Google Analytics collect endpoint. Its output is "
    + "below."),
  ...code("docs/analytics_verification.txt", "Output of tools/verify_analytics.py"),
  para("The Measurement ID in the code is a placeholder, so Google accepts these hits and "
    + "drops them: no property owns that ID. Creating a GA4 property needs the account owner "
    + "to sign in to Google, which is the one step that cannot be automated. Once the property "
    + "exists, running the program with its ID sends the same events to it, and they appear in "
    + "Reports > Realtime. No code changes:"),
  ...code("docs/ga4_command.txt", "Running Lab 6 against a real GA4 property"),
  para("The full click-by-click setup is written up in docs/GA4-SETUP.md in the repository."),
);

children.push(
  heading("Analytics parameters determined", HeadingLevel.HEADING_2),
  table([
    ["Active users", "Different people who opened the store", "Realtime"],
    ["Sessions", "Visits; a session closes after 30 minutes idle", "Acquisition"],
    ["Views", "Pages opened, collected automatically by gtag.js", "Pages and screens"],
    ["Engagement rate", "Visits of 10s or more, 2 views, or an event", "Engagement"],
    ["Average engagement time", "Time the page stayed in the foreground", "Engagement"],
    ["Event count", "How often each event such as add_to_cart fired", "Events"],
    ["Key events", "Events marked as conversions, purchase here", "Admin, Events"],
    ["Total revenue", "Value carried by the purchase event", "Monetisation"],
    ["Session source", "Where the visit came from, e.g. google / organic", "Acquisition"],
    ["Device and country", "Dimensions collected for every visitor", "Tech, Demographics"],
  ], [2500, 4360, 2500], ["Parameter", "What it tells us", "GA4 report"]),
  para("", { after: 120 }),
  para("The Measurement ID in the code is a placeholder. Replacing it with the ID of a real "
    + "GA4 property is the only change needed for live data to reach these reports."),

  heading("Conclusion", HeadingLevel.HEADING_1),
  para("All six programs of the E-Commerce Laboratory were completed as six separate working "
    + "stores. Labs 1 to 4 cover the catalogue side of an online shop: categories and items, "
    + "the cart, checkout into an order, and the wish list, each keeping its records in plain "
    + "Python lists and dictionaries. Lab 5 sends an invoice amount to a payment gateway "
    + "running in sandbox mode and reads back the transaction reference and status. Lab 6 "
    + "installs Google Analytics tracking and settles on the parameters worth watching for "
    + "such a store."),
  para("Writing each lab as its own program made the differences between them clear, since "
    + "each one owns its data and its interface. The order the labs follow is also the order a "
    + "real purchase takes: a catalogue is browsed, a cart is filled, an order is placed, the "
    + "payment is settled, and the actions along the way are exactly what analytics measures."),
);

/* ------------------------------------------------------------------- document */
const doc = new Document({
  creator: "Abhishek Barali",
  title: "E-Commerce Laboratory Report",
  styles: {
    default: {
      document: { run: { font: BODY, size: 24, color: BLACK } },
      heading1: { run: { font: BODY, size: 32, bold: true, color: BLACK } },
      heading2: { run: { font: BODY, size: 26, bold: true, color: BLACK } },
    },
  },
  numbering: {
    config: [
      {
        reference: "steps",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.START,
          style: { paragraph: { indent: { left: 460, hanging: 300 } }, run: { font: BODY, size: 24, color: BLACK } },
        }],
      },
      {
        reference: "dots",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.START,
          style: { paragraph: { indent: { left: 460, hanging: 300 } }, run: { font: BODY, size: 24, color: BLACK } },
        }],
      },
    ],
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },              // US Letter
        margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 },
      },
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buffer) => {
  fs.mkdirSync(path.dirname(OUT), { recursive: true });
  fs.writeFileSync(OUT, buffer);
  console.log("wrote", OUT, `(${figureNo} figures)`);
});
