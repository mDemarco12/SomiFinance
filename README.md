
# SomiFinance

A personal net-worth and macro-signals dashboard that runs entirely in your browser — no install, no account, no server. Open the HTML file and your data stays on your machine.

<img width="1696" height="766" alt="screenshot" src="https://github.com/user-attachments/assets/f48da16b-36d6-4868-988d-7459fc95c94c" />

## What it does

SomiFinance is a single-page dashboard for tracking your net worth alongside the macro indicators that give it context — treasury yields, inflation, and an economic calendar — all in one place, updated by hand on your schedule. It speaks three languages and six currencies, and the whole thing is one HTML file you can email to yourself.

### Overview
- Live net worth figure with the change since your last logged snapshot
- Totals for assets, liabilities, invested (brokerage/retirement/crypto), and cash
- Allocation breakdown by category
- Net worth history chart, built from the snapshots you log over time

### Assets & Liabilities ledger
- Fully editable tables — click any cell to update it
- Categorize each item (Brokerage, Cash, Retirement, Vehicle, Real estate, Crypto, and more for assets; Credit card, Auto loan, Mortgage, and more for liabilities)
- Add or remove rows freely; totals and net worth update live

### Budgeting
- Monthly cash-in / cash-out ledger with drag-to-reorder rows, split into income and expense sections
- Live totals for cash in, cash out, net cash flow, savings rate, and discretionary spend
- Per-category spending limits with a spend-vs-limit chart
- Future spend projection — models what your discretionary spending would be worth if invested instead, at a return rate and time horizon you set

### Macro Signals
- Track 10/20/30-year Treasury yields over time with a running chart
- Track CPI year-over-year inflation readings
- Automatically computed real yield (10-year nominal minus latest CPI)

### Economic Calendar
- **Personal calendar** — log your own dated events (earnings, options expiries, release dates) with importance tags (High / Medium / Low / Personal); auto-sorts by date and greys out past events
- **Live calendar** — TradingView's US economic calendar embedded alongside it as a read-only reference feed
- Drag either panel to reorder them, and drag the corner grip to resize the live feed to whatever height suits you — the size is remembered

### Languages & currency
- **Three languages** — English, 繁體中文 (Traditional Chinese), 简体中文 (Simplified Chinese), covering the app's headings, tabs, table columns, and buttons
- **Six currencies** — USD, JPY, TWD, CNY, EUR, GBP. Every figure, chart axis, and editable cell converts, with live exchange rates fetched on demand from a free, keyless API. Your data is always stored in USD, so switching back and forth never drifts your numbers
- Both are picked from the ⚙ settings menu and persist between visits

### Everything else
- **First-run welcome** — a one-time setup screen asks your name and what you're tracking (personal finance, start-up, business), then drops you into the ledger with short hints pointing at the fields you need. Dismiss any hint with ✕; it never returns
- **5 built-in themes** (a default terminal-style theme plus four Catppuccin variants), with charts that re-theme live when you switch
- **Scrolling ticker tape** summarizing your key numbers at a glance
- **Export / Import** your full dataset as JSON for backup or transfer
- **Snapshot history** — hit Refresh to log a dated point to your net worth chart whenever you update your figures
- **Optional auto-refresh** of Treasury and CPI data on load (ships off — see below)
- A gentle reminder banner if your numbers haven't been touched in a while
- Keyboard shortcuts (`1`–`6` to switch tabs, `Esc` to close menus)
- Responsive layout for smaller screens

## Getting started

There's nothing to install. Download `somiFinance.html` and open it in any modern browser.

Your data is saved automatically to that browser's local storage. Use **Export** regularly to back it up as a JSON file — that backup is also how you'd move your data to a new browser or machine (**Import** it there).

## Data & privacy

Everything runs client-side. Your figures never leave your browser — there's no account, no server, and no analytics.

Chart.js is bundled directly into the file rather than loaded from a CDN, so **opening the page makes zero network requests by default**. The app only ever reaches out when you ask it to, and never sends your financial data anywhere:

| Request | When | What it's for |
|---|---|---|
| TradingView | First time you open the Economic Calendar tab | The live calendar widget |
| U.S. Treasury + BLS | Refresh on Macro Signals (or on load, if you turn auto-refresh on) | Latest yields and CPI |
| open.er-api.com | Only when a non-USD currency is selected | Exchange rates |

Each fails gracefully — if a request doesn't go through, the app keeps working and falls back to manual entry or the last cached values.

Two things enforce that rather than just promising it:

- **A Content-Security-Policy** in the page head names the only three hosts the app may contact, so even a bug or an injection has nowhere to send your figures. Its `script-src` lists SHA-256 hashes instead of allowing inline script, which means injected event handlers won't run at all.
- **The TradingView widget is sandboxed.** It's third-party code, so it loads in an iframe with no same-origin access — it can't read your saved data or touch the page. Opening the Calendar tab does contact TradingView's servers, but they receive nothing about you beyond the request itself.

Imported backups are treated as untrusted input: every field is validated against a whitelist and all row ids are regenerated, and nothing is written to storage until the imported file has rendered cleanly.

## Tech stack

- Vanilla HTML, CSS, and JavaScript — no framework, no build step, one file
- [Chart.js](https://www.chartjs.org/) for charts (inlined, not CDN-loaded)
- Browser `localStorage` for persistence

## Roadmap

This is an actively evolving personal project. For the full breakdown of what's built, what's planned, and known rough edges, see [PROJECT_STATUS.md](PROJECT_STATUS.md).

## Disclaimer

Not financial advice. SomiFinance is a personal tracking tool, not investment guidance.
