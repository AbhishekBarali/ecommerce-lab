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
const OUT = path.join(ROOT, "docs", "ECommerce_Lab_Report_COMPLETE_Abhishek_Barali_023bscit003.docx");

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

const heading = (t, level, opts) => new Paragraph({
  heading: level,
  spacing: { before: level === HeadingLevel.HEADING_1 ? 360 : 260, after: 140 },
  keepNext: true,
  pageBreakBefore: !!(opts && opts.pageBefore),
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

  // Plain monospace lines, no shaded box and no border around the code.
  const out = lines.map((l, i) => new Paragraph({
    spacing: { after: 0, line: 216, before: i === 0 ? 60 : 0 },
    children: [text(l === "" ? " " : l, { font: MONO, size: 17 })],
  }));
  out.push(para(caption, { italics: true, size: 21, align: AlignmentType.CENTER, after: 240, before: 80 }));
  return out;
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
    heading(`Lab ${number}: ${title}`, HeadingLevel.HEADING_1, { pageBefore: true }),
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
  para("Complete Lab Report: Programs 1 to 6", { size: 28, align: AlignmentType.CENTER, after: 80 }),
  para("Labs 1 to 5 are Python programs. Lab 6 studies Google Analytics 4 on Google's live Merchandise Store demo.", { size: 22, italics: true, align: AlignmentType.CENTER, after: 640 }),
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
  para("This report covers all six labs of the E-Commerce Laboratory. Labs 1 to 5 are "
    + "separate programs, each with its own folder, product data and interface, written in "
    + "Python with the Flask micro framework and keeping their records in ordinary Python "
    + "lists and dictionaries (no database, as the assignment allows). Lab 6 is different: it "
    + "studies Google Analytics 4 directly on Google's public Merchandise Store demo, with no "
    + "program to write."),
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
    ["Lab 6", "Google Analytics 4, studied on Google's live demo (no program)", "-"],
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

// ---- Lab 6: the real Google Analytics demo (not a program; a study of GA4) ----
const bulletList = (items) => items.map((t) => new Paragraph({
  numbering: { reference: "dots", level: 0 },
  spacing: { after: 80, line: 276 },
  children: [text(t)],
}));

children.push(
  heading("Lab 6: Google Analytics Setup and Analytics Parameters", HeadingLevel.HEADING_1, { pageBefore: true }),
  para("Studied on Google's official public GA4 demo, the Google Merchandise Store. "
    + "No website was built and no tracking code was written for this lab; the demo is a fully "
    + "working GA4 property that any Google user can add to their own Analytics, and it already "
    + "carries real traffic and real e-commerce data from Google's own online store.", { italics: true, after: 200 }),

  heading("Objective", HeadingLevel.HEADING_2),
  para("Sign in to Google Analytics, open the Merchandise Store demo, and study the main GA4 "
    + "analytics parameters: users and sessions, engagement, events, conversions, and the "
    + "e-commerce figures. Every screenshot below was taken from the live demo."),

  heading("Property setup and Measurement ID", HeadingLevel.HEADING_2),
  para("The demo property was added through Google's demo-account help page, which links the "
    + "Google Merchandise Store GA4 property into the signed-in account with one click. Because "
    + "it is a shared demo, the property already exists and is read-only, so nothing had to be "
    + "created. Its Measurement ID, the G-XXXXXXXXXX handle a real site would put in its "
    + "gtag.js snippet, is:"),
  para("G-P2XN2NGD35", { font: MONO, size: 24, align: AlignmentType.CENTER, after: 160 }),
  para("The Home screen confirms the property is live. Over the last 7 days it shows about 21K "
    + "active users, 26K sessions and 20K key events, with a world map of where the users are "
    + "(United States 5.6K, India 1.3K, Japan 599, Taiwan 327, Pakistan 185) and the top selling "
    + "items with their revenue."),
  ...figure("ga-home.png", "GA4 Home for the Google Merchandise Store demo: about 21K active users, 26K sessions and 20K key events over 7 days, with the live world map."),

  heading("The demo data (Reports snapshot)", HeadingLevel.HEADING_2),
  para("The Reports snapshot gathers the headline numbers for the last 28 days: about 88K active "
    + "users, 80K new users, an average engagement time of 49 seconds, and 1.3M events. It also "
    + "lists the top pages (Home at 101K views), the busiest cities (New York, Mountain View, "
    + "Singapore, Lahore), the traffic sources, and audiences such as non-purchasers and likely "
    + "7-day purchasers. Home and the snapshot differ (21K versus 88K users) only because Home "
    + "is showing 7 days and the snapshot 28 days; every GA4 report has its own date range."),
  ...figure("ga-reports-snapshot.png", "Reports snapshot: 88K active users, 80K new users, 49s average engagement time and 1.3M events, plus top pages, cities, sources and audiences (last 28 days)."),

  heading("Realtime report", HeadingLevel.HEADING_2),
  para("The Realtime report shows the last 30 minutes as it happens. During the lab it showed "
    + "about 67 active users, a world map of where they were, their source (mostly direct, some "
    + "google), and the events firing live. The Realtime pages view broke the same traffic down "
    + "by page: 69 active users and 243 views, with the home path busiest."),
  ...figure("ga-realtime-overview.png", "Realtime overview: about 67 active users in the last 30 minutes, their live locations, sources, and the events firing in real time."),
  ...figure("ga-realtime-pages.png", "Realtime pages: 69 active users and 243 views in the last 30 minutes, broken down by page path."),

  heading("Events report", HeadingLevel.HEADING_2),
  para("GA4 is event-based: every interaction is an event. Over the 28 days there were about "
    + "1.26M events from 91K users, an average of 14.36 per user. The most common were page_view "
    + "(344,109, about 27%), view_item_list (311,044, about 25%), session_start (108,642), "
    + "first_visit (80,261) and view_item (74,245). Automatic events like session_start, "
    + "first_visit, user_engagement and scroll appear without any extra setup."),
  ...figure("ga-events.png", "Events report: about 1.26M events over 28 days, led by page_view, view_item_list, session_start, first_visit and view_item."),

  heading("Conversions (key events)", HeadingLevel.HEADING_2),
  para("Conversions in GA4 are ordinary events marked as key events because they matter to the "
    + "business, such as purchase, add_to_cart and view_item. The report showed about 85,871 key "
    + "events and $212,242.69 of event revenue. view_item from google/organic was the largest "
    + "(31,574), and the purchase key event from direct traffic carried $98,494.71 of revenue on "
    + "its own."),
  ...figure("ga-conversions.png", "Conversions report: key events such as view_item, add_to_cart and purchase, with the purchase event carrying the revenue."),

  heading("Monetization (e-commerce purchases)", HeadingLevel.HEADING_2),
  para("The Ecommerce purchases report reads product performance. Across 28 days the store had "
    + "73,602 items viewed, 39,328 added to cart, 12,604 purchased, and $185,866.84 in item "
    + "revenue. Each row carries the product name, views, adds to cart, purchases and revenue. "
    + "The best earner was the Google Marine Layer 1998 Pullover (3,049 views, 149 purchased, "
    + "$15,225.00), ahead of the Super G Gradient Tee and the Google 1998 Pickleball Set."),
  ...figure("ga-ecommerce.png", "Ecommerce purchases: items viewed, added to cart, purchased and item revenue per product, led by the Google Marine Layer 1998 Pullover at $15,225."),

  heading("Analytics parameters explained", HeadingLevel.HEADING_2),
  para("Users and Sessions: users are unique visitors (people); sessions are visits, and a "
    + "session ends after 30 minutes of no activity. The demo showed about 88K active users and "
    + "80K new users over 28 days, so most traffic here was first-time visitors."),
  para("Engagement: engagement rate is the share of sessions that were meaningful (10 seconds "
    + "or more, a key event, or 2+ views); average engagement time is how long the page was in "
    + "the foreground. The demo's average was 49 seconds, with a large 'Users scrolled 75%+' "
    + "audience, both signs of real engagement."),
  para("Events: everything is an event, from page_view, session_start, first_visit and "
    + "user_engagement to e-commerce events like view_item, add_to_cart and purchase. Some fire "
    + "automatically, some are set up by the site. The demo recorded about 1.26M events."),
  para("Conversions: a conversion is an event flagged as a key event because it matters, here "
    + "purchase, add_to_cart and view_item. Marking a key event is what lets GA4 count "
    + "conversions and attribute revenue; the purchase key event carried the store's revenue."),
  para("E-commerce parameters: these describe the products, item name, category, quantity, "
    + "price and revenue. GA4 ties them to the item events, so one report shows how often a "
    + "product was viewed, added to cart, bought, and how much it earned."),

  heading("Observations from filtering", HeadingLevel.HEADING_2),
  para("The reports were read across device, location and traffic source:"),
  ...bulletList([
    "By device: the 'Key events by Platform' card reads 100% Web, because the demo only has a web data stream (no app), so all activity is desktop and mobile browsers.",
    "By location: worldwide, but the United States dominates (5.6K active users), then India (1.3K), Japan (599), Canada (363), Taiwan (327) and Pakistan (185). Top cities were New York, Mountain View, Singapore and Lahore.",
    "By traffic source: direct traffic is largest (about 59K users, 61K sessions), then google organic search (16K users, 27K sessions), then google paid search (google/cpc, 8.3K).",
  ]),

  heading("Conclusion", HeadingLevel.HEADING_1),
  para("The first five labs were built as separate working programs: Labs 1 to 4 cover the "
    + "catalogue side of an online shop (categories and items, the cart, checkout into an order, "
    + "and the wish list), each keeping its records in plain Python lists and dictionaries, and "
    + "Lab 5 sends an invoice amount to a payment gateway running in sandbox mode and reads back "
    + "the transaction reference and status. Lab 6 stepped outside coding to study Google "
    + "Analytics 4 on Google's own Merchandise Store demo."),
  para("GA4 works on an event-based model: instead of counting only page views, it records every "
    + "interaction as an event with its own parameters, and conversions are simply events marked "
    + "as key events. Together the parameters describe behaviour and sales from both ends. Users, "
    + "sessions and engagement show how many people come and how involved they are; events show "
    + "what they do; conversions and the e-commerce figures show what it is worth. On the demo it "
    + "was possible to see 88K users produce 1.26M events and $185,866.84 in item revenue, and to "
    + "trace which products, channels and places drove that result, all without owning a website "
    + "or writing any tracking code."),
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
