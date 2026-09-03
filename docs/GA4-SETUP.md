# Connecting Lab 6 to a real Google Analytics property

The program works without an account: it installs the GA4 snippet, sends real
events and shows the hits leaving the browser. The one part that needs a Google
login is creating the property, because only the account owner can do that.

It takes about two minutes.

## 1. Create the property

1. Sign in at <https://analytics.google.com> with your Google account.
2. **Admin** (bottom left gear) → **Create** → **Property**.
3. Property name: `Barali Store Web`. Set the time zone to Nepal and the
   currency to Nepalese Rupee. Click **Next**, answer the business questions
   however you like, then **Create** and accept the terms.

## 2. Add a web data stream

1. In the new property: **Admin** → **Data streams** → **Add stream** → **Web**.
2. Website URL: anything you will open the page from. `http://127.0.0.1:5006`
   is fine for the lab; GA does not verify the URL.
3. Stream name: `Barali Store - Web stream` → **Create stream**.
4. The stream page shows the **Measurement ID**, in the form `G-ABCD123456`.
   Copy it. It is not a secret; every website using GA has it in plain HTML.

## 3. Run Lab 6 against it

```bash
cd lab6_analytics
GA_MEASUREMENT_ID=G-ABCD123456 ../.venv/bin/python app.py
```

Open <http://127.0.0.1:5006>. The Measurement ID tile shows your ID and the
placeholder warning is replaced by a green confirmation.

## 4. Watch the data arrive

1. Click each event button once: `page_view`, `view_item`, `add_to_cart`,
   `add_to_wishlist`, `begin_checkout`, `purchase`.
2. In Google Analytics open **Reports → Realtime**. Within a few seconds you
   will see 1 active user, and the *Event count by Event name* card lists the
   events you just fired.
3. Screenshot that Realtime report. It is the one screenshot that has to come
   from your logged-in account.

## 5. Mark the conversion

**Admin** → **Events** → find `purchase` → turn on **Mark as key event**. That
is what makes it count as a conversion in the reports.

## Checking it without the dashboard

```bash
GA_MEASUREMENT_ID=G-ABCD123456 .venv/bin/python tools/verify_analytics.py
```

This drives the page in a browser, clicks every event, and writes
`docs/analytics_verification.txt` listing each hit that left the browser for
`https://www.google-analytics.com/g/collect`, plus a screenshot of the page's
own hit panel.
