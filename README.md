
# SomiFinance

A personal net-worth and macro-signals dashboard that runs entirely in your browser — no install, no account, no server. Open the HTML file and your data stays on your machine.

<img width="665" height="598" alt="Screenshot 2026-09-07 at 11 36 21" src="https://github.com/user-attachments/assets/39cb60d7-c2e1-4ef4-895b-07cd305d4bb1" />

## What it does

SomiFinance is a single-page dashboard for tracking your net worth alongside the macro indicators that give it context — treasury yields, inflation, and an economic calendar — all in one place, updated by hand on your schedule. It speaks three languages and six currencies, and the whole thing is one HTML file you can email to yourself.

### Overview
- Live net worth figure with the change since your last logged snapshot
- Totals for assets, liabilities, invested (brokerage/retirement/crypto), and cash
- Allocation breakdown by category
- Net worth history chart, built from the snapshots you log over time

<img width="1696" height="766" alt="screenshot" src="https://github.com/user-attachments/assets/f48da16b-36d6-4868-988d-7459fc95c94c" />

### Assets & Liabilities ledger
- Fully editable tables — click any cell to update it
- Categorize each item — and the category lists follow what you're tracking. Personal finance gets Brokerage, Cash, Retirement, Vehicle, Real estate, Crypto and more; a business gets Operating cash, Accounts receivable, Inventory, Equipment, and so on. Switching between them never changes a row you've already entered — your existing category is kept and stays selectable
- Add or remove rows freely; totals and net worth update live

<img width="1994" height="1219" alt="Screenshot 2026-09-07 at 12 25 00" src="https://github.com/user-attachments/assets/33ce1ee4-9cba-4cd6-bab7-bac039383b93" />

### Budgeting
- Monthly cash-in / cash-out ledger with drag-to-reorder rows, split into income and expense sections
- Live totals for cash in, cash out, net cash flow, savings rate, and discretionary spend
- Per-category spending limits with a spend-vs-limit chart
- Future spend projection — models what your discretionary spending would be worth if invested instead, at a return rate and time horizon you set
- **Savings goals** — set a target, a date and how much you'll put in each month, then pick which account category funds it. Progress is read straight from your ledger rather than tracked separately, so it updates itself as you update your accounts. Shows what you'd need per month to land on time, and warns when your goals together commit more than your net cash flow

<img width="1999" height="1287" alt="Screenshot 2026-09-07 at 12 25 21" src="https://github.com/user-attachments/assets/5bc61c0c-7286-49c3-a933-2e4c61ed1583" />
<img width="1999" height="1287" alt="Screenshot 2026-09-07 at 12 25 27" src="https://github.com/user-attachments/assets/22016437-5c56-4ff7-98e2-0db67f6e95f7" />

### Macro Signals
- Track 10/20/30-year Treasury yields over time with a running chart
- Track CPI year-over-year inflation readings
- Automatically computed real yield (10-year nominal minus latest CPI)

<img width="1999" height="1287" alt="Screenshot 2026-09-07 at 12 25 38" src="https://github.com/user-attachments/assets/ad916e62-4fec-4663-a34f-6e3cf06518d9" />

### Economic Calendar
- **Personal calendar** — log your own dated events (earnings, options expiries, release dates) with importance tags (High / Medium / Low / Personal); auto-sorts by date and greys out past events
- **Live calendar** — TradingView's US economic calendar embedded alongside it as a read-only reference feed
- Drag either panel to reorder them, and drag the corner grip to resize the live feed to whatever height suits you — the size is remembered

<img width="1999" height="1287" alt="Screenshot 2026-09-07 at 12 25 46" src="https://github.com/user-attachments/assets/c6307acf-e84d-44db-b778-f4c55337f389" />

### ✦ AI assistant (optional, runs locally)
- A chat panel that reads a summary of your figures and answers questions about them in plain English — "how am I doing against my goals?", "where is most of my spending going?"
- **Runs entirely on your own machine** via [Ollama](https://ollama.com), a free app you install separately. **No API key, no account, no sign-up** — and nothing you type is sent anywhere off your computer
- Setup happens in the panel itself: open ✦, press **Connect**, then pick from whichever models you have installed. If it can't reach Ollama, it tells you exactly why and shows the fix inline
- **New to this?** Step-by-step guides written for non-technical users, from installing Ollama to your first question: **[macOS & Ubuntu](ASSISTANT-SETUP.md)** · **[Windows](ASSISTANT-SETUP-WINDOWS.md)**
- **Read-only.** It can't change a single figure in your ledger. It receives category-level totals only — individual holding names and your free-text notes are never sent
- It's a small local model: it can be confidently wrong, and nothing it says is financial advice. The panel says so, permanently

### Languages & currency
- **Three languages** — English, 繁體中文 (Traditional Chinese), 简体中文 (Simplified Chinese), covering the app's headings, tabs, table columns, and buttons
- **Six currencies** — USD, JPY, TWD, CNY, EUR, GBP. Every figure, chart axis, and editable cell converts, with live exchange rates fetched on demand from a free, keyless API. Your data is always stored in USD, so switching back and forth never drifts your numbers
- Both are picked from the ⚙ settings menu and persist between visits

### Everything else
- **First-run welcome** — a one-time setup screen asks your name and what you're tracking (personal finance, start-up, personal business, or something else), then drops you into the ledger with short hints pointing at the fields you need. Your answer tailors both the hints and the category lists you'll work with. Dismiss any hint with ✕; it never returns
- **5 built-in themes** (a default terminal-style theme plus four Catppuccin variants), with charts that re-theme live when you switch
- **Make it yours** — change your display name at any time from ⚙, and pick the colour it shows in beside the SomiFinance logo (cyan, your theme's accent, green or blue — each one adapts to whichever theme you're on)
- **Scrolling ticker tape** summarizing your key numbers at a glance
- **Export / Import** your full dataset as JSON for backup or transfer
- **Snapshot history** — hit Refresh to log a dated point to your net worth chart whenever you update your figures
- **Optional auto-refresh** of Treasury and CPI data on load (ships off — see below)
- A gentle reminder banner if your numbers haven't been touched in a while
- **Start over** — ⚙ → Reset all data clears everything and returns you to the first-run screen. It warns you what will go, offers to export a backup first, and won't proceed until you type `Yes`
- Keyboard shortcuts (`1`–`6` to switch tabs, `Esc` to close menus)
- Layout that follows your window — the shell, tiles and type scale up on a large monitor and collapse to a single column on a small one
- Reset your instance to Factory Specs with an integrated Reset button within the settings (and you have the option to back-up your data, and you must type 'Yes' before the reset)
- 
<img width="665" height="598" alt="Screenshot 2026-09-07 at 11 34 42" src="https://github.com/user-attachments/assets/c783c2af-1bd0-4c39-b9b5-d5f0d374a98d" />


## Getting started

There's nothing to install. Download `SomiFinance.html` and open it in any modern browser.

Want to see it with data in it first? `SomiFinanceDemo.html` is the same app carrying a full example portfolio — 24 months of history, a filled budget, populated charts. It keeps its own browser storage, so opening it never touches the data in your own copy.

Your data is saved automatically to that browser's local storage. Use **Export** regularly to back it up as a JSON file — that backup is also how you'd move your data to a new browser or machine (**Import** it there).

**Want the ✦ AI assistant too?** That's the one part with a setup step, because it needs Ollama installed on your machine. Full walkthroughs, written for people who don't consider themselves technical: **[macOS & Ubuntu](ASSISTANT-SETUP.md)** · **[Windows](ASSISTANT-SETUP-WINDOWS.md)**. Everything else in SomiFinance works without it.

## Data & privacy

Everything runs client-side. Your figures never leave your browser — there's no account, no server, and no analytics.

Chart.js is bundled directly into the file rather than loaded from a CDN, so **opening the page makes zero network requests by default**. The app only ever reaches out when you ask it to, and never sends your financial data anywhere:

| Request | When | What it's for |
|---|---|---|
| TradingView | First time you open the Economic Calendar tab | The live calendar widget |
| U.S. Treasury + BLS | Refresh on Macro Signals (or on load, if you turn auto-refresh on) | Latest yields and CPI |
| open.er-api.com | Only when a non-USD currency is selected | Exchange rates |
| Your own machine (`127.0.0.1`/`localhost`) | When you open the ✦ assistant panel (one quick check that Ollama is reachable) and when you send it a message | Local Ollama chat — never leaves your computer |

Each fails gracefully — if a request doesn't go through, the app keeps working and falls back to manual entry or the last cached values.

Two things enforce that rather than just promising it:

- **A Content-Security-Policy** in the page head names every host the app may contact — three remote hosts, plus loopback ports for the optional local assistant — so even a bug or an injection has nowhere to send your figures off this machine. Its `script-src` lists SHA-256 hashes instead of allowing inline script, which means injected event handlers won't run at all. The loopback allowance is unroutable off-machine, but it does widen what injected script could reach on your own machine — see `PROJECT_STATUS.md` for the honest tradeoff.
- **The TradingView widget is sandboxed.** It's third-party code, so it loads in an iframe with no same-origin access — it can't read your saved data or touch the page. Opening the Calendar tab does contact TradingView's servers, but they receive nothing about you beyond the request itself.

Imported backups are treated as untrusted input: every field is validated against a whitelist and all row ids are regenerated, and nothing is written to storage until the imported file has rendered cleanly.

## Tech stack

- Vanilla HTML, CSS, and JavaScript — no framework, no bundler, one self-contained file
- [Chart.js](https://www.chartjs.org/) for charts (inlined, not CDN-loaded)
- Browser `localStorage` for persistence

There's nothing to build to *use* SomiFinance — you download one HTML file and open it. Contributors should know that the distributed files are generated: `SomiFinanceDemo.html` is the source everyone edits, and `python3 build.py` projects it into `SomiFinance.html`. Don't hand-edit a generated file; it carries a DO-NOT-EDIT banner and the next build overwrites it.

## Roadmap

This is an actively evolving personal project. For the full breakdown of what's built, what's planned, and known rough edges, see [PROJECT_STATUS.md](PROJECT_STATUS.md).

## Disclaimer

Not financial advice. SomiFinance is a personal tracking tool, not investment guidance.
