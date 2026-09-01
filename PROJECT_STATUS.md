# SomiFinance — Project Status

> **Maintenance rule:** this doc is scanned by agents working on this project. Track it with `Scan count` below — increment it by 1 every time this doc is read for context. **On every 4th scan** (count reaches a multiple of 4), lint the whole doc against the current state of `somiFinance.html` before doing anything else: move shipped items out of "Could be done," delete resolved "Needs polish" / "Rebrand to-do" items, add anything newly true. Don't let this drift from the actual code.
>
> **Scan count:** 2 (security pass — CSP, sandboxed TradingView frame, `sanitizeState()`, genericized seed, history purge; see **Security posture** below)
>
> **Anchor style:** reference code by **symbol name** (`renderBudget()`, `#tvBox`, `THEMES`) — never by line number. A previous version used `file#L123` links and all 26 went stale the moment Chart.js was inlined. Symbol names stay greppable across edits.

## Snapshot

- **What it is:** a single-file, offline-first personal net-worth & macro dashboard. Vanilla HTML/CSS/JS, no build step, no backend. Persists to `localStorage`.
- **Genuinely offline on load.** Chart.js v4.4.1 is **inlined** into the file (~205 KB minified, 13 lines, MIT banner preserved, `sourceMappingURL` stripped) — no CDN tag, and the page's own two script blocks are both inline. Opening the page fires **zero** network requests **by default** (auto-refresh ships `off` — see Macro Signals). Only three things ever reach out, all user-triggered: the TradingView widget on first Economic Calendar view, the Treasury/BLS fetches on Refresh from Macro Signals, and the FX-rate fetch when a non-USD currency is selected. The single remaining third-party `script src` is TradingView's, and it lives inside the sandboxed frame's `srcdoc`, never in this document — see **Security posture**. Don't "optimize" Chart.js back to a CDN — inlining is deliberate (it also removes an unpinned-CDN supply-chain path, since the old tag had no SRI hash).
- **File:** `somiFinance.html` (~2354 lines / ~330 KB, one file — markup, styles, and script all inline; ~205 KB of that is the inlined Chart.js).
- **Two-file setup:** `somiFinance.html` is the repo/shareable copy and the ONLY file to edit by default. `SomiFinancePersonal.html` holds the user's real financial data and is `.gitignore`d — never touch it unless the user explicitly asks to port changes over.
- **Naming:** rebranded from the old internal "Wealth Desk" name to **SomiFinance** throughout (title, topbar, storage key, export filenames, toast copy). The old `localStorage` key (`wealthdesk.v1`) is migrated automatically on first load under the new key (`somifinance.v1`) so existing users don't lose data — see `load()` in the "Key facts" section below.

## Security posture

Four things here are load-bearing. Breaking any of them silently re-opens a hole, so read this
before touching the `<head>`, `ensureTradingViewWidget()`, `sanitizeState()`, or `seed()`.

### CSP script hashes — **regenerate after every edit to the app script**

The `<head>` carries a `<meta http-equiv="Content-Security-Policy">` whose `script-src` lists two
**sha256 hashes** and deliberately does *not* include `'unsafe-inline'`. That omission is the point:
without it the browser refuses injected event-handler attributes (`onmouseover=`, `onerror=`), so an
XSS is dead even if an escaping site is ever missed.

The cost: **edit the app script and the page goes blank until you paste in the new hash** (with a CSP
error in the console). Hash 1 is the inlined Chart.js and never changes. Hash 2 is the app script.
Regenerate with:

```
python3 -c 'import re,hashlib,base64;s=open("somiFinance.html",encoding="utf-8").read();print(chr(10).join("sha256-"+base64.b64encode(hashlib.sha256(m.encode()).digest()).decode() for m in re.findall(r"<script>(.*?)</script>",s,re.S)))'
```

It must print exactly two hashes. If it prints three, something in the file now spells out a script
tag literally — that is why the command lives here and not in an HTML comment.

`connect-src` names the only three hosts the page may contact (Treasury, BLS, `open.er-api.com`).
Adding a data source means adding it there too, or the fetch fails with no visible error.

### The TradingView widget is sandboxed — never add `allow-same-origin`

`ensureTradingViewWidget()` puts the third-party loader inside a `srcdoc` iframe with
`sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox"`. Omitting `allow-same-origin`
is the entire mitigation: it gives the frame an **opaque origin**, so TradingView's unpinned,
unhashable script cannot read `localStorage["somifinance.v1"]` (every holding, value and note) or
touch this document. Appended directly to `#tvBox` — as it was originally — it had all of that.

**Adding `allow-same-origin` to a srcdoc frame makes it inherit *this* document's origin**, handing
back exactly the access the sandbox removes. Don't, even if the widget misbehaves. If it degrades
under the opaque origin, the fallback is to drop the loader entirely and point the iframe at
TradingView's embed URL directly (`https://www.tradingview.com/embed-widget/events/?locale=en#<config>`),
which removes third-party script execution altogether and needs only a `frame-src` entry.

A srcdoc frame **inherits the parent CSP**, which is why `script-src` lists `s3.tradingview.com` and
`frame-src` lists TradingView's frame origins. Consequence: if their loader ever starts writing
inline script, our hash-only `script-src` will block it — that is the expected failure mode, not a
bug to fix by loosening the policy.

Because the widget now lives in a frame, TradingView's `height:100%` clobber lands on a div inside
*its* document, not on `#tvBox`. The `#tvBox{…!important}` rule is therefore belt-and-braces now
rather than load-bearing — but keep it, and keep `setLiveCalPx()` as the sole writer of
`--live-cal-h`. Never set `tvBox.style.height` directly.

### `sanitizeState()` is the only door into `state`

Called by **both** `load()` and `importJSON()`. It builds a fresh state by **explicit field copy from
a whitelist** — it is not `Object.assign(seed(), d)`, and must never go back to being that:
`Object.assign` writes through `[[Set]]`, so a parsed-JSON `__proto__` key hits the
`Object.prototype` setter and re-parents the state object.

- **Every new state field needs a line in `sanitizeState()`** or it will be silently dropped on the
  next load. This replaces the old "every new scalar needs a `load()` backfill" rule — the backfills
  are gone, `sanitizeState()` supplies every default now (including the `onboarded:false` one that
  makes the welcome screen appear once for pre-existing saves).
- **Row ids are always regenerated**, never taken from a file — ids are interpolated into markup.
  Safe because `calendarOrder` holds panel names, not ids, and budget order is array order, so no id
  crosses a save boundary.
- Helpers: `sStr` (length-capped), `sNum` / `sNumN` (`Number.isFinite`, so `NaN`/`Infinity`/`"1e999"`
  can't through), `sArr` (`MAX_ROWS`), `sPick` (allowlist), `sDate` (`YYYY-MM-DD` shape).
  `MAX_STR`=200, `MAX_ROWS`=1000.
- `cat` is deliberately a free string, not an `ASSET_CATS` allowlist — the Overview allocation panel
  is documented to render whatever category an asset carries, and `colorForCat()` handles unknown
  ones. It is escaped at render time instead.
- `importJSON()` renders **before** it persists. A malformed file used to be `save()`d first, which
  left the app crashing on every subsequent load with no in-app way out; it now rolls back to the
  previous state on any throw.

### `seed()` ships in a public repo

Keep every figure fake. It previously carried the author's real holdings, cost basis, an options
position and a tax-timing note — all of which went public, and the first-run hint tour points users
straight at those rows. Real data belongs in `SomiFinancePersonal.html`, which is gitignored by
**pattern** now (`*[Pp]ersonal*.html` etc.), not by exact filename, so a rename or a "Save as" copy
can't slip past.

Also: `esc()` is the only escaping helper — use it for anything interpolated into markup, including
`data-` attributes. `cellInput()` used to escape `"` alone; it routes through `esc()` now.

## Done

**Overview tab**
- Net worth hero figure + delta vs. last snapshot (`renderOverview()`)
- Summary stats: total assets, total liabilities, invested (Brokerage/Retirement/Crypto), cash
- Allocation-by-category bars, colored per category, sized by % of net worth — one unified list, no separate "custom category" UI (that was tried and rolled back; see below)
- Net worth over time chart, built from logged snapshots + live point

**Ledger tab (Assets & Liabilities)**
- Inline-editable tables — click any cell, category dropdown, notes field (`renderLedger()` / `rowHTML()` / `wireCells()`)
- 13 fixed asset categories including a catch-all **"Alternative Asset"** entry — there's no in-app category management (add/rename) anymore; to track something odd (a wine cellar, a pet, a jean collection), add an asset in the Ledger, name the asset itself whatever you want, and assign it the "Alternative Asset" category. It then appears in the Overview allocation automatically since that panel groups by whatever category real assets carry, not by a separate managed list.
- Add/delete rows, live-updating totals and net worth strip

**Budgeting tab** (shortcut `3`, between Ledger and Macro)
- **Cash in / cash out table** (`<section id="tab-budget">` markup, `renderBudget()`) — one `<table>` with multiple `<tbody>`s: a static section-header tbody + a sortable tbody per section, so drag-reordering can't disturb the headers. Shared 8-column grid; Limit/Type render as a muted `—` on income rows. Each section ends with its own inline "+ Add Row" button-row.
- **Optional-row dimming**: rows flagged `optional` render at 60% opacity while their amount is 0, snapping to full opacity the moment a value is entered (live on `input`, not just re-render). Seeded optional rows: 401(k) contribution, employer match, other income, debt payments, travel.
- **Drag-to-reorder within a section only** (`wireBudgetDrag()` / `moveBudgetRow()`) — a `⠿` handle per row; drops from a different section are rejected outright (no insertion indicator shown). Reorder algorithm unit-tested against 7 cases incl. self-drop and unknown-id.
- **Spend vs limit chart** (`renderSpendChart()`) — horizontal paired bars aggregated **by category** (not per row), Spent vs Limit. Over-limit categories render red in the chart AND tint the Amount cell in the table.
- **Future spend** (`renderFutureChart()`) — treats discretionary rows as a forgone monthly investment; two curves over 0→N years (*Total diverted* linear vs *If invested instead* compounded). Configurable rate/horizon persisted in `state.budget.assumptions` (default 7% / 30yr). Math is the ordinary-annuity FV: `PMT × ((1+i)^n − 1)/i`, `futureValue()`, with a rate-0 linear guard.
- Stat row (cash in/out, net flow, savings rate, discretionary share) + net-flow strip, reusing existing `.stat-row`/`.net-strip` classes. `NET FLOW` also added to the ticker tape.
- **The `kind` field (essential/discretionary) is load-bearing** — Future Spend sums discretionary rows only. It's a per-row dropdown, so seeded defaults are just defaults.

**Macro Signals tab** (shortcut `4`)
- Manual 10/20/30yr Treasury yield entry + line chart, CPI YoY inflation entry + chart, computed real yield (10yr nominal − nearest CPI) (`renderMacro()`) — all three panels now have a matching `.read-row` stat above their chart (Real Yield's was added specifically to fix a vertical-alignment bug where it and the Inflation panel's charts didn't line up in the 2-col grid)
- **Auto-refresh on load** (`state.autoRefresh` = `off` | `stale` | `always`, picked in ⚙ Settings; `renderAutoRefreshList()` / `maybeAutoRefresh()`). **Ships `off` on purpose** — the About page claims opening the page makes no network requests, and defaulting this on would make that copy false. Staleness is `state.lastFetch !== today()` ("have we fetched today?"), deliberately *not* "is the newest yield row dated today" — Treasury doesn't publish on weekends/holidays, so the latter would refetch on every load all weekend. `lastFetch` is stamped only on **full** success so a partial failure retries next load. Fired from `boot()` guarded on `!rerender` (never on the `importJSON` path) and never awaited, since the Treasury endpoint can take ~9-15s.
- **Live data pull**: hitting the top-right Refresh button while on this tab calls `refreshMacroData()`, which pulls the latest 10/20/30yr yields from the U.S. Treasury's own daily par-yield-curve feed and the latest CPI YoY from the BLS public API — both confirmed CORS-open, no API key, no backend needed. Merges into `state.yields`/`state.inflation` via the same de-dupe-by-date logic the manual entry forms use. Manual entry remains the fallback if a fetch fails.

**Economic Calendar tab**
- Two panels, `data-panel="personal"` and `data-panel="live"`: the editable **Personal economic calendar** and the read-only **Live economic calendar**.
- Editable dated events, importance tags (High/Med/Low/Personal), auto-sorts by date, past events greyed out (`renderCalendar()`)
- **Live reference widget**: a second panel embeds TradingView's official Economic Calendar widget (`embed-widget-events.js`, US-filtered) (`#tvBox`) — read-only, not saved to `state`, sits alongside the editable table rather than replacing it.
- **The live panel is user-resizable** via a hollow-triangle corner grip (`#tvResize`, `initLiveCalResize()`), persisted in `state.liveCalHeight` (clamped 260–1600 by `clampLiveCal()`). Uses **pointer events with `setPointerCapture`**, not mouse events — the cross-origin TradingView iframe swallows `mousemove` the instant the cursor crosses into it mid-drag. Arrow keys on the focused grip nudge ±20 (±60 with Shift).
- **`#tvBox` height is pinned by an `!important` rule reading `--live-cal-h`, and `setLiveCalPx()` is the only writer.** This is load-bearing and non-obvious: the TradingView embed script writes a plain `height:100%` onto its own container (which *is* `#tvBox`) a few ms after the async script lands, silently clobbering the saved height and collapsing the box to ~150px. A normal author `!important` beats TradingView's non-important inline style. Consequence: **never set `tvBox.style.height` directly** — the `!important` rule would ignore it and the drag would appear frozen. Confirmed via MutationObserver; TradingView does not use `!important` itself.
- **The live panel no longer auto-sizes to the personal panel.** A previous `syncCalendarWidgetHeight()` measured the personal panel and forced `#tvBox` to match, so deleting a row there shrank the live feed. Deleted deliberately — `applyLiveCalHeight()` reads saved state only and never touches the personal panel. Don't reintroduce a coupling here.
- **The widget is lazy-loaded** by `ensureTradingViewWidget()` (guarded by a `tvLoaded` flag) on first Calendar render — it is deliberately NOT a `<script>` in the markup, because that fired on every page load even for users who never opened the tab. Its `colorTheme` is derived from `state.theme` at injection time (Latte → light). Known limitation: switching themes after it loads won't re-theme it until reload, since re-injecting would mean a fresh TradingView request.
- **`applyCalendarOrder()` early-returns when the DOM order already matches.** This is load-bearing, not a micro-optimization: `appendChild` on an existing child re-inserts it, and re-parenting an `<iframe>` makes the browser reload it. Without the guard the widget reloaded (and re-pinged TradingView) on *every* calendar render. An actual drag/click reorder still reloads it — unavoidable when moving a node in the DOM. Chosen after Bloomberg's and investing.com's calendar pages both returned HTTP 403 (confirmed active anti-bot blocking, and both prohibit scraping in their ToS) — TradingView's widget is an official no-key embed built for exactly this. Finnhub and Financial Modeling Prep were also confirmed CORS-open alternatives if structured (not embedded) calendar data is wanted later, but both need a free API key/signup; not pursued since the no-key widget covered the ask.

**About tab** (shortcut `6`, last in the nav)
- Static page, no render function — `show()` just toggles `.active` and `renderTab()` deliberately has no `about` branch (`<section id="tab-about">` markup, `/* about page */` CSS).
- Three panels: author card (CSS-only initials monogram + `mDemarco12` + GitHub link), credits, and an app description.
- **Monogram, not a photo** — deliberate. The user's GitHub avatar is a 62 KB GIF; hotlinking it would break the "PERSONAL · LOCAL · OFFLINE" topbar claim and embedding it would roughly double the file. The monogram is pure CSS built from theme vars, so it re-themes for free and adds zero bytes and zero network requests. Don't "improve" this by adding the real avatar without re-checking that decision.
- Display name is the handle `mDemarco12` only — the user explicitly chose not to show a real name anywhere.
- Credits: Catppuccin (the ask), plus Chart.js, TradingView, U.S. Treasury and BLS. All links verified HTTP 200 except `bls.gov`, which blanket-403s every non-browser client including its own root domain — that's edge bot-blocking, not a dead link.
- Careful: the app ships **5** themes but only **4** are Catppuccin (Terminal is SomiFinance's own). The credit copy says so explicitly; keep it accurate if themes change.

**First-run onboarding**
- **Welcome screen** (`showWelcome()`) reuses the intro wipe: `.intro-wipe.hold` sweeps the accent panel to full coverage and *stays* (`introSweepIn` keyframes) instead of sweeping back out, with the form on top. Collects name + goal (`GOALS`: personal | startup | business | other), then routes to the Ledger. "Skip for now" completes with an empty name and no tour.
- **Guided hints** (`HINTS` / `startHints()` / `showHint()`) replace what was originally speced as a Clippy character — dropped because Clippy is Microsoft IP. Four steps on the Ledger, each outlining a real field (`.hint-target`) with a card beside it; ✕ or Escape ends the tour permanently (`endHints()`).
- **Selectors are re-resolved on every step, never cached** — `renderLedger()` rebuilds `#assetBody` via `innerHTML`, so a held node reference dies. Highlights are cleared by `querySelectorAll('.hint-target')` for the same reason. Steps whose selector resolves to nothing are skipped.
- **Goal tailors the hint copy only** — each step's `body` is keyed by goal (`body[state.profile.goal] || body.personal`). It deliberately does **not** reseed the ledger/budget; that was considered and rejected as too destructive to existing data.
- **"Runs once" is a flag, not self-deleting code** — a single HTML file can't remove its own source. `state.onboarded` gates everything. Note `load()` backfills `onboarded:false` on *existing* saves too, so the welcome shows once for everyone after the feature landed rather than only brand-new browsers. There is intentionally **no "replay intro"** menu item (user declined) — clearing site data is the only way back.
- `maybeBanner()` is held back until the tour ends (`endHints()` calls it) — the banner says "open the ledger" while the tour is already doing exactly that on the ledger.
- Name shows in the topbar via `applyGreeting()` / `#brandWho` (hidden when blank via `:empty`).

**Languages (i18n)**
- Three languages: `en`, `zh-Hant`, `zh-Hans` (`LANGS`, picked in ⚙, `state.lang`). `t(key)` falls back to English then to the raw key, so a missing translation never renders blank.
- **Scope is core chrome only** — tabs, panel headings, table columns, buttons. Long-form notes and toasts stay English by design.
- **Mixed application strategy, deliberately.** Most target strings are static HTML written once and never re-rendered, so `applyChromeI18n()` relabels them by id from `CHROME_MAP`. The few JS-templated pieces (`t("tab."+tab)` in `show()`, the budget "+ Add Row" button) call `t()` inline. Expect both patterns to coexist.
- **Category values are NOT translated** (`ASSET_CATS`, `EXPENSE_CATS`, `SPEND_KINDS`, …) — they're persisted as literal strings and matched by value, so translating them would corrupt saved data across a language switch.

**Currency**
- Six currencies (`CURRENCIES`: USD/JPY/TWD/CNY/EUR/GBP, each with `symbol` + `decimals`; JPY and TWD are 0-decimal). `state.currency`, picked in ⚙.
- **`fmt`/`fmt2` read currency as a closure, not a parameter** — same trick `css()` uses for live theme colors. That's why adding currency needed *zero* edits at the ~20 existing call sites. Keep it that way.
- Chart **datasets stay in USD**; only the tick formatters (`tickMoney()` / `tickMoneyK()`) convert at render time. Converting the data would corrupt axis scaling.
- **Editable cells round-trip through `toDisplay()` / `fromDisplay()`; `state` is always USD.** Every display is re-derived from that single source of truth, so flipping currencies repeatedly causes no drift (nothing is written unless the user actually edits).
- **FX source is `open.er-api.com`, not Frankfurter.** Frankfurter was the first choice (open-source, ECB-backed) but **ECB publishes no TWD rate at all**, and TWD is required. Don't "improve" this back to Frankfurter without re-checking that. `fetchFxRates()` / `refreshFx()` / `maybeRefreshFx()`; keyless, CORS-open, cached in `state.fx.rates` with `state.fx.lastFetch`.
- FX fetch is **deliberately not gated by `state.autoRefresh`** — unlike opt-in Treasury/CPI data, currency is an explicit user selection, and a missing rate would silently mislabel USD figures as ¥/€. It fetches once a day whenever a non-USD currency is active, falls back to the last cached rate, and marks the picker `(est.)` when no rate was ever fetched.

**Settings menu (⚙)**
- Four collapsible sections (`.set-sec` / `.set-head` / `.set-body`): Theme, Auto-refresh, 語 Language, € Currency. **Accordion — one open at a time** (`openSetSection()`), all collapsed on every open, with the active value shown in each collapsed header (`setSectionCurrent()`). Wired once by `initSettingsSections()`.
- `.theme-list` has `max-height` + `overflow-y:auto` + **`overscroll-behavior:contain`** — that last property is what stops scrolling the menu from chaining to the page behind it.
- **Scope picker selectors to their `data-` attribute, never `.theme-opt`.** That class is shared by all four pickers (17 elements). `renderThemeList()` used the broad selector and cleared `aria-current` on Language/Currency/Auto-refresh every time a theme was picked — fixed by scoping to `[data-theme]` (5 elements). The other three already scoped correctly.

**Cross-cutting**
- 5 themes via CSS custom properties (Terminal default + 4 Catppuccin variants), live chart re-theming on switch (`THEMES` / `applyTheme()`)
- Scrolling ticker tape summarizing net worth, invested, cash, yields, CPI, real yield (`renderTape()`)
- JSON export/import for backup and restore (`exportJSON()` / `importJSON()`)
- **Tab-scoped Refresh button**: behavior now branches on the active tab (refreshBtn handler inside `init()`) — Overview still snapshots net worth into history (unchanged); Macro Signals pulls live data (see above); Ledger/Calendar just re-render with a light toast. Previously Refresh always snapshotted + jumped to Overview regardless of tab; changed because a full page reload (F5) covers the "everything" case and the button reads clearer scoped to what's on screen. The stale-data banner copy was updated to match (now explicitly says update in Ledger, then hit Refresh on **Overview**).
- Stale-data nudge banner (fires after 7 days since last update, or if no snapshots exist) (`maybeBanner()`)
- Keyboard shortcuts (1-6 switch tabs, Esc closes menus). Order: Overview, Ledger, Budgeting, Macro, Calendar, About. Budgeting was inserted at 3 (shifting Macro 3→4, Calendar 4→5); About was appended at 6 specifically to avoid shifting anything again. **Adding a tab means editing four places in lockstep** — the menu `<button>`, the `<section id="tab-…">`, `TAB_NAMES`/`REFRESH_TITLE`, and the keydown array.
- Chart helpers: `mountChart(id,type,...)` is the shared guard/destroy core; `line()` and `bars()` are thin wrappers over it (`mountChart()`). Use `bars()` for any new bar chart rather than hand-rolling a `new Chart(...)`.
- Watermark footer: "SomiFinance ©2026 mDemarco12" (`.watermark`)
- Responsive layout — grid collapses to 1 column under 840px
- aria attributes on menus and chart canvases; graceful fallback text if Chart.js somehow isn't available (`mountChart()` guards on `window.Chart`) — kept from the CDN era, harmless now that it's inlined

## Could be done

- Live market price feeds for **assets** (brokerage holdings, etc.) — still manual entry. (Treasury yields, CPI, and a reference economic calendar are now live-pulled — see Macro Signals / Economic Calendar above.)
- Per-asset value history — only net-worth *totals* are snapshotted, not individual holdings over time
- Budget **history** — the Budgeting tab models a single current month; there's no month-over-month tracking or actual-vs-budget over time (net worth has `history[]`, budget has no equivalent). Natural next step if budgeting gets used seriously.
- Transaction-level tracking / bank import — budgeting is category-level and hand-entered by design
- CSV export (JSON only today)
- Column sort/search/filter in ledger tables (calendar auto-sorts by date; ledger does not)
- Recurring/scheduled automatic snapshots (currently manual "Refresh" click only)
- PWA install support (manifest + service worker) — would also make the "offline" claim fully true on first load
- State-schema *versioning* (the storage key is suffixed `.v1` and `sanitizeState()` now coerces any shape to the current one, but there's no explicit version field or migration ladder)
- Cloud sync / accounts — explicitly out of scope today; footer says "your pipeline can write the same JSON shape... and you re-Import it"
- Delete confirmation on ledger/calendar row deletes (currently instant, no undo)
- In-app category management (add a custom category from the Overview tab, rename one in place) — **tried and deliberately reverted.** It added a "+" button + ✎ rename chips to the Allocation panel, but the user decided category management should happen implicitly: pick "Alternative Asset" (or any category) in the Ledger when adding an asset, name the asset itself, and it flows into the allocation automatically. Don't re-add a category CRUD UI without checking this decision first.

## Needs polish

- No favicon, no OG tags (a `<meta name="description">` was added with the CSP)
- Onboarding copy (welcome screen + all 4 hint bodies) is English-only, so a zh-Hant/zh-Hans user still gets an English first run. Consistent with the "chrome only" i18n scope, but it's the one place that inconsistency is most likely to be noticed.
- Monolithic single file (~316 KB, ~2115 lines) — ~205 KB of that is inlined Chart.js, so hand-written code is ~110 KB. Fine for personal use; worth a deliberate decision (keep as a distribution feature vs. split into modules) once this becomes a shipped product
- The TradingView widget still won't re-theme after a theme switch until reload (pre-existing; re-injecting means a fresh TradingView request)

## Key facts for future me

- Everything lives in one `<script>` block at the bottom of the file.
- State object shape: `{ updated, onboarded, hintsDone, profile{name,goal}, theme, lang, currency, fx{rates{},lastFetch}, calendarOrder[], liveCalHeight, autoRefresh, lastFetch, assets[], liabilities[], history[], yields[], inflation[], calendar[], budget{} }`. No category-management fields — categories are just strings on each asset/liability. **All monetary values are stored in USD regardless of the selected display currency.**
- **Every new state field needs a line in `sanitizeState()`** — it is the single door into `state` (called by both `load()` and `importJSON()`) and supplies every default, so a field missing from it is silently dropped on the next load. This replaces the old per-scalar `load()` backfills, which are gone. `normalizeBudget()` still plays the same role for the budget block. See **Security posture**.
- `budget` = `{ income:[{id,name,cat,amount,optional,notes}], expenses:[{id,name,cat,amount,limit,kind,optional,notes}], assumptions:{rate,years} }`, where `kind` ∈ `essential|discretionary`. Categories come from `INCOME_CATS` (11) / `EXPENSE_CATS` (21). **`normalizeBudget()` is the compatibility shim** — called from BOTH `load()` and `importJSON()`; it backfills missing arrays/assumptions/ids and coerces a bad `kind`, so older saves and partial imports don't crash the tab. Any new budget field should get a default there too.
- `assets`/`liabilities` items: `{ id, name, cat, value, notes }`. Categories come straight from the fixed `ASSET_CATS` (13 entries, incl. "Alternative Asset" and "Other") / `LIAB_CATS` arrays — no user-editable category list. `colorForCat(c)` returns the curated color from `CAT_COLOR` when one exists, otherwise a deterministic hash-based color from `CAT_PALETTE`, so any category string (even a stray/legacy one) still renders with a stable color.
- The Overview allocation panel (`renderOverview()`) groups `state.assets` by whatever string is in `a.cat` — it has no awareness of `ASSET_CATS` beyond coloring, so it will happily show a category that isn't in the dropdown if old/imported data has one.
- `history` items: `{ date, net, assets, liab }` — one point per `snapshot()` call.
- `yields` items: `{ date, y10, y20, y30 }`; `inflation` items: `{ date, cpi, note? }`.
- `calendar` items: `{ id, date, event, imp, notes }`, `imp` ∈ High/Med/Low/Personal.
- `THEMES` object defines all theme tokens; `applyTheme()` writes them as CSS custom properties at runtime.
- `seed()` produces first-run data; `load()`/`save()` wrap `localStorage` under key `somifinance.v1`. `load()` also checks the legacy key `wealthdesk.v1` and migrates it forward automatically if the new key is empty. Note: browsers that went through the earlier (reverted) custom-category feature may still have stray `customCats`/`altAssetSeeded` keys sitting unused in their saved JSON — harmless, nothing reads them anymore.
- Live-data functions: `fetchTreasuryYields()` / `fetchLatestCPI()` / `refreshMacroData()` (`refreshMacroData()`) — no API keys, both sources are open government data. **Do not swap these for Yahoo Finance** if asked again: confirmed via direct testing that Yahoo's endpoints aren't CORS-open (would silently fail in-browser with no backend to proxy through) and Yahoo has no CPI data at all (that's a BLS/government stat, not market data).
- Same rejection logic applies to the calendar widget: Bloomberg and investing.com both returned HTTP 403 on direct request (active bot-blocking) and both prohibit scraping in ToS — don't attempt to pull structured data from either. TradingView's `embed-widget-events.js` (`#tvBox`) is the current no-key solution; Finnhub and Financial Modeling Prep are confirmed CORS-open fallbacks if structured (editable-table-feeding) calendar data is wanted later, but both require the user to sign up for a free API key first.
