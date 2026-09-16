/*
 * Build the GA4 lab report as a .docx using docx-js.
 *   cd ecommerce-lab && node ga4-report/build.js
 *
 * Body text Times New Roman 12pt, all black, US Letter. Screenshots are the
 * real Google Merchandise Store GA4 demo captured by the student. All prose is
 * plain ASCII (no arrows, section signs, en-dashes, or middle dots).
 */
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, ImageRun, PageBreak,
  Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  HeadingLevel, LevelFormat, BorderStyle,
} = require("docx");

const DIR = __dirname;
const SHOTS = path.join(DIR, "shots");
const OUT = path.join(DIR, "GA4_Lab_Report_Abhishek_Barali_023bscit003.docx");

const BODY = "Times New Roman";
const MONO = "Consolas";
const BLACK = "000000";
const CONTENT = 9360;
const MAX_W_PX = 600;
const MAX_H_PX = 470;   // keep a figure to about 2/3 page so caption + text share the page
let figureNo = 0;
let listInstance = 0;

const text = (t, o = {}) => new TextRun({
  text: t, font: o.font || BODY, size: o.size || 24,
  bold: !!o.bold, italics: !!o.italics, color: BLACK,
});
const para = (t, o = {}) => new Paragraph({
  alignment: o.align,
  spacing: { after: o.after === undefined ? 160 : o.after, before: o.before || 0, line: 276 },
  children: t === "" ? [] : [text(t, o)],
});
const h1 = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_1,
  spacing: { before: 360, after: 140 }, keepNext: true,
  border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: BLACK, space: 2 } },
  children: [text(t, { bold: true, size: 32 })],
});
const h2 = (t) => new Paragraph({
  heading: HeadingLevel.HEADING_2,
  spacing: { before: 240, after: 120 }, keepNext: true,
  children: [text(t, { bold: true, size: 26 })],
});
const numbered = (items) => {
  listInstance += 1;
  const instance = listInstance;
  return items.map((t) => new Paragraph({
    numbering: { reference: "n", level: 0, instance },
    spacing: { after: 90, line: 276 },
    children: Array.isArray(t) ? t : [text(t)],
  }));
};
const bullets = (items) => items.map((t) => new Paragraph({
  numbering: { reference: "b", level: 0 },
  spacing: { after: 80, line: 276 },
  children: Array.isArray(t) ? t : [text(t)],
}));

function cell(runs, { width, head }) {
  const children = Array.isArray(runs) ? runs : [text(String(runs), { size: 22, bold: head })];
  return new TableCell({
    width: { size: width, type: WidthType.DXA },
    shading: head ? { type: ShadingType.CLEAR, fill: "E9E9E9", color: "auto" } : undefined,
    margins: { top: 60, bottom: 60, left: 110, right: 110 },
    children: [new Paragraph({ spacing: { after: 0, line: 252 }, children })],
  });
}
function table(rows, widths, header) {
  const body = [];
  if (header) body.push(new TableRow({ tableHeader: true, children: header.map((h, i) => cell(h, { width: widths[i], head: true })) }));
  rows.forEach((r) => body.push(new TableRow({
    children: r.map((v, i) => cell([text(String(v), { size: 22, bold: !header && i === 0 })], { width: widths[i] })),
  })));
  return new Table({ columnWidths: widths, width: { size: CONTENT, type: WidthType.DXA }, rows: body });
}

function pngSize(file) { const b = fs.readFileSync(file); return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) }; }
function figure(name, caption) {
  const file = path.join(SHOTS, name);
  const { w, h } = pngSize(file);
  let width = MAX_W_PX, height = (h / w) * width;
  if (height > MAX_H_PX) { height = MAX_H_PX; width = (w / h) * height; }
  figureNo += 1;
  return [
    new Paragraph({
      alignment: AlignmentType.CENTER, spacing: { after: 80, before: 80 },
      border: {
        top: { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB", space: 4 },
        bottom: { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB", space: 4 },
        left: { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB", space: 4 },
        right: { style: BorderStyle.SINGLE, size: 4, color: "BBBBBB", space: 4 },
      },
      children: [new ImageRun({ data: fs.readFileSync(file), type: "png",
        transformation: { width: Math.round(width), height: Math.round(height) } })],
    }),
    para(`Figure ${figureNo}: ${caption}`, { italics: true, size: 21, align: AlignmentType.CENTER, after: 240 }),
  ];
}

const children = [
  para("", { after: 900 }),
  para("GOOGLE ANALYTICS 4 (GA4)", { bold: true, size: 40, align: AlignmentType.CENTER, after: 100 }),
  para("Lab Report: Setup and Analysis using the Google Merchandise Store demo", { size: 26, align: AlignmentType.CENTER, after: 80 }),
  para("Studied on Google's official public GA4 demo account. No website was built and no code was written.", { size: 22, italics: true, align: AlignmentType.CENTER, after: 640 }),
  table([
    ["Name", "Abhishek Barali"],
    ["Roll No.", "023bscit003"],
    ["Section", "A"],
    ["Semester / Batch", "2023"],
    ["Subject", "E-Commerce Laboratory"],
    ["Property studied", "Google Merchandise Store (GA4 demo)"],
    ["Measurement ID", "G-P2XN2NGD35"],
    ["Date range in reports", "Aug 19 to Sep 15, 2026 (last 28 days), Realtime is last 30 minutes"],
  ], [3000, 6360]),
  new Paragraph({ children: [new PageBreak()] }),

  h1("1. Introduction"),
  para("This lab studies Google Analytics 4 (GA4) using the Google Merchandise Store, "
    + "Google's official public demo property. The demo is a fully working GA4 account that any "
    + "Google user can add to their own Analytics, so it needs no website of one's own and no "
    + "tracking code. It already carries real traffic and real e-commerce data from Google's own "
    + "online store, which is what makes it useful for learning the reports."),
  para("The aim was to sign in to Google Analytics, open the demo, and study the main analytics "
    + "parameters: users and sessions, engagement, events, conversions, and the e-commerce "
    + "figures. Every screenshot in this report was taken from the live demo during the lab."),

  h1("2. Step 1 - GA4 property setup and Measurement ID"),
  para("The demo property was added through the Google Analytics demo-account help page, which "
    + "links the Google Merchandise Store GA4 property into the signed-in account with one click. "
    + "Because it is a shared demo, the property already exists and is read-only, so nothing had "
    + "to be created or configured. Its Measurement ID, the G-XXXXXXXXXX handle that a real site "
    + "would place in its gtag.js snippet, is:"),
  para("G-P2XN2NGD35", { font: MONO, size: 24, align: AlignmentType.CENTER, after: 160 }),
  para("The Home screen below confirms the property is live and receiving data. For the last 7 "
    + "days it shows about 21K active users, 26K sessions and 20K key events, with a world map of "
    + "where the users are (United States 5.6K, India 1.3K, Japan 599, Taiwan 327, Pakistan 185) "
    + "and the top selling items with their revenue."),
  ...figure("home.png", "GA4 Home for the Google Merchandise Store demo, confirming the property is live (about 21K active users, 26K sessions, 20K key events over 7 days)."),

  h1("3. Steps 2 and 3 - the demo store and its pre-tracked data"),
  para("No coding was required to reach the data. The Reports snapshot gathers the headline "
    + "numbers for the last 28 days on one screen: about 88K active users, 80K new users, an "
    + "average engagement time of 49 seconds, and 1.3M events. It also lists the top pages (Home "
    + "with 101K views, then the Google Merch Shop category pages), the busiest cities (New York, "
    + "Mountain View, Singapore, Lahore), the traffic sources, and audiences such as "
    + "non-purchasers and likely 7-day purchasers."),
  ...figure("reports-snapshot.png", "Reports snapshot: 88K active users, 80K new users, 49s average engagement time, 1.3M events, plus top pages, cities, sources and audiences for the last 28 days."),
  para("The Home and snapshot numbers differ (21K versus 88K active users) only because they use "
    + "different date ranges: Home is showing the last 7 days while the snapshot is showing the "
    + "last 28 days. This is normal in GA4, where every report carries its own date selector."),

  h1("4. Step 5 - Realtime report"),
  para("The Realtime report shows activity from the last 30 minutes, updating as it happens. "
    + "During the lab it showed about 67 active users, a world map of where they were at that "
    + "moment, their traffic source (mostly direct, some google), and the events firing live "
    + "(view_item_list, page_view, session_start, view_item, add_to_cart)."),
  ...figure("realtime-overview.png", "Realtime overview: about 67 active users in the last 30 minutes, their live locations on the map, sources, and the events firing in real time."),
  para("The Realtime pages view breaks the same live traffic down by page. It showed 69 active "
    + "users and 243 views in the last 30 minutes, with the home path busiest, followed by the "
    + "1998 retro collection, bags, and new-arrivals pages."),
  ...figure("realtime-pages.png", "Realtime pages: 69 active users and 243 views in the last 30 minutes, broken down by page path."),

  h1("5. Step 5 - Events report"),
  para("GA4 is event-based: every interaction is an event. The Events report lists each event "
    + "with how many times it fired. Over the 28 days there were about 1.26M events from 91K "
    + "users, an average of 14.36 events per user. The most common events were page_view "
    + "(344,109, about 27%), view_item_list (311,044, about 25%), session_start (108,642), "
    + "first_visit (80,261) and view_item (74,245). Automatic events like session_start, "
    + "first_visit, user_engagement and scroll appear without any extra setup."),
  ...figure("events.png", "Events report: about 1.26M events over 28 days, led by page_view, view_item_list, session_start, first_visit and view_item."),

  h1("6. Step 5 - Conversions (key events)"),
  para("Conversions in GA4 are ordinary events that have been marked as key events because they "
    + "matter to the business, such as purchase, add_to_cart and view_item. The Conversions "
    + "report showed about 85,871 key events and total event revenue of $212,242.69. Broken down "
    + "by source, view_item from google/organic was the largest (31,574), followed by view_item "
    + "from direct traffic (29,117); the purchase key event from direct traffic carried "
    + "$98,494.71 of revenue on its own."),
  ...figure("conversions.png", "Conversions report: key events such as view_item, add_to_cart and purchase, with the purchase event carrying the revenue."),

  h1("7. Step 5 - Monetization (e-commerce purchases)"),
  para("The Ecommerce purchases report is where product performance is read. Across the 28 days "
    + "the store had 73,602 items viewed, 39,328 items added to cart, 12,604 items purchased, and "
    + "$185,866.84 in item revenue. Each product row carries its name, how many times it was "
    + "viewed, added to cart and purchased, and the revenue it earned. The best earner was the "
    + "Google Marine Layer 1998 Pullover (3,049 views, 149 purchased, $15,225.00), ahead of the "
    + "Super G Gradient Tee (188 purchased, $4,584) and the Google 1998 Pickleball Set."),
  ...figure("ecommerce.png", "Ecommerce purchases: items viewed, added to cart, purchased and item revenue per product, led by the Google Marine Layer 1998 Pullover at $15,225."),

  h1("8. Step 4 - Analytics parameters explained"),
  para("Below is a short write-up of each parameter category the lab asked for, with what it "
    + "means and what the demo showed."),

  h2("Users and Sessions"),
  para("Users are the unique visitors (people). Sessions are visits: a single user can start "
    + "several sessions, and a session ends after 30 minutes of no activity. New users are "
    + "people seen for the first time. The demo showed about 88K active users and 80K new users "
    + "over 28 days, which means most traffic in this window was first-time visitors."),

  h2("Engagement"),
  para("Engagement rate is the share of sessions that were meaningful (lasted 10 seconds or "
    + "more, produced a key event, or had at least two page views); its opposite is the bounce "
    + "rate. Average engagement time is how long the page was actually in the foreground. The "
    + "demo's average engagement time was 49 seconds, and the audience list showed a large "
    + "'Users scrolled 75%+' group (about 29K), both signs of real engagement rather than quick "
    + "bounces."),

  h2("Events"),
  para("Because GA4 is event-based, everything is an event: page_view (a page opened), "
    + "session_start (a visit began), first_visit (a brand-new user), user_engagement (time spent "
    + "in the foreground), and e-commerce events like view_item, add_to_cart and purchase. Some "
    + "fire automatically and some are set up by the site. The demo recorded about 1.26M events, "
    + "led by page_view and view_item_list."),

  h2("Conversions"),
  para("A conversion is an event the business has flagged as important, called a key event in "
    + "GA4. Here the key events include purchase, add_to_cart and view_item. Marking an event as "
    + "a key event is what lets GA4 count conversions and attribute revenue to them; in the demo "
    + "the purchase key event is what carried the store's revenue."),

  h2("E-commerce parameters"),
  para("These describe the products themselves: item name, category, quantity, price and the "
    + "revenue each product earns. GA4 ties them to the item events, so a single report can show "
    + "how many times a product was viewed, how often it was added to cart, how many were bought, "
    + "and how much money it made, as seen in the Ecommerce purchases table."),

  h1("9. Observations from filtering"),
  para("The reports were read across device, location and traffic source:"),
  ...bullets([
    "By device: the demo's 'Key events by Platform' card reads 100% Web, because the Merchandise Store demo only has a web data stream (no app), so all activity here is desktop and mobile browsers rather than an app.",
    "By location: traffic is worldwide but United States dominates (5.6K active users), followed by India (1.3K), Japan (599), Canada (363), Taiwan (327) and Pakistan (185). By city the leaders were New York, Mountain View, Singapore and, notably, Lahore.",
    "By traffic source: direct traffic is the largest by far (about 59K users and 61K sessions), then google organic search (16K users, 27K sessions), then google paid search (google/cpc, 8.3K). So most visitors arrive by typing the address or from unattributed links, with organic search the biggest earned channel.",
  ]),

  h1("10. Conclusion"),
  para("GA4 works on an event-based model: instead of counting only page views, it records every "
    + "interaction as an event with its own parameters, from page_view and session_start to "
    + "view_item, add_to_cart and purchase. Conversions are not a separate kind of data; they are "
    + "ordinary events that have been marked as key events because they matter to the business, "
    + "which is how GA4 counts them and attaches revenue."),
  para("Together these parameters describe user behaviour and sales from both ends. Users, "
    + "sessions and engagement show how many people come and how involved they are; events show "
    + "what they do; conversions and the e-commerce figures show what that activity is worth. "
    + "Reading the Google Merchandise Store demo, it was possible to see 88K users produce 1.26M "
    + "events and $185,866.84 in item revenue, and to trace which products, channels and places "
    + "drove that result, all without owning a website or writing any tracking code."),
];

const doc = new Document({
  creator: "Abhishek Barali",
  title: "GA4 Lab Report",
  styles: { default: {
    document: { run: { font: BODY, size: 24, color: BLACK } },
    heading1: { run: { font: BODY, size: 32, bold: true, color: BLACK } },
    heading2: { run: { font: BODY, size: 26, bold: true, color: BLACK } },
  } },
  numbering: { config: [
    { reference: "n", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.START,
      style: { paragraph: { indent: { left: 460, hanging: 300 } }, run: { font: BODY, size: 24, color: BLACK } } }] },
    { reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022", alignment: AlignmentType.START,
      style: { paragraph: { indent: { left: 460, hanging: 300 } }, run: { font: BODY, size: 24, color: BLACK } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => { fs.writeFileSync(OUT, buf); console.log("wrote", OUT, `(${figureNo} figures)`); });
