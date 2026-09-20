# SomiFinance — Project Status

> **Maintenance rule:** this doc is scanned by agents working on this project. Track it with `Scan count` below — increment it by 1 every time this doc is read for context. **On every 4th scan** (count reaches a multiple of 4), lint the whole doc against the current state of `SomiFinanceDemo.html` before doing anything else: move shipped items out of "Could be done," delete resolved "Needs polish" / "Rebrand to-do" items, add anything newly true. Don't let this drift from the actual code.
>
> **Scan count:** 8 (pre-launch polish pass — 46 items in six commits, linted against the code on this scan per the rule above; see **Pre-launch polish** under Done; previously: GTM hardening pass — three-reviewer audit, 25 fixes, full-app QA suite; see **GTM hardening** under Done; previously: quarterly archive — encrypted append-only audit record, see **Security posture** and **Done**; previously: full doc lint against the code — goal-aware categories, reset, name colour, fluid sizing, TradingView re-theme fix; previously: three-build split — `build.py`, per-build storage keys, empty-ledger end-user build; previously: security pass — CSP, sandboxed TradingView frame, `sanitizeState()`, genericized seed, history purge; see **Security posture** below)
>
> **Anchor style:** reference code by **symbol name** (`renderBudget()`, `#tvBox`, `THEMES`) — never by line number. A previous version used `file#L123` links and all 26 went stale the moment Chart.js was inlined. Symbol names stay greppable across edits.

## Snapshot

- **What it is:** a single-file, offline-first personal net-worth & macro dashboard. Vanilla HTML/CSS/JS, no bundler, no backend. Persists to `localStorage`. There is one build step, and it is not a compiler: `build.py` projects the source into the other two builds (see **Three builds** below). Every output is still a standalone single file that runs by double-clicking it.
- **Genuinely offline on load.** Chart.js v4.4.1 is **inlined** into the file (~205 KB minified, 13 lines, MIT banner preserved and `@kurkle/color`'s alongside it, `sourceMappingURL` stripped). **Never dump those lines** — they will swamp a context window. Find them by LENGTH rather than by line number, which moves with every edit: `awk 'length($0)>2000 {print NR}'` prints exactly the two that matter, and `awk 'length($0)<2000'` filters them out of any grep — no CDN tag, and the page's own two script blocks are both inline. Opening the page fires **zero** network requests **by default** (auto-refresh ships `off` — see Macro Signals). Only three things ever reach out, all user-triggered: the TradingView widget on first Economic Calendar view, the Treasury/BLS fetches on Refresh from Macro Signals, and the FX-rate fetch when a non-USD currency is selected. The single remaining third-party `script src` is TradingView's, and it lives inside the sandboxed frame's `srcdoc`, never in this document — see **Security posture**. Don't "optimize" Chart.js back to a CDN — inlining is deliberate (it also removes an unpinned-CDN supply-chain path, since the old tag had no SRI hash).
- **File:** `SomiFinanceDemo.html` (~5627 lines / ~528 KB, one file — markup, styles, and script all inline; ~200 KB of that is the inlined Chart.js, so hand-written code is ~255 KB). The quarterly archive added ~550 lines.
- **Three builds, one source.** `SomiFinanceDemo.html` is the **only file anyone edits**. `build.py` projects it into the other two. Never hand-edit a generated file — it carries a DO-NOT-EDIT banner and the next build silently overwrites it.

  | File | What it is | Git |
  | --- | --- | --- |
  | `SomiFinanceDemo.html` | The source, and a working demo build: full fake portfolio, 24 months of history, filled budget, opens straight into the dashboard (`onboarded:true`). | tracked |
  | `SomiFinance.html` | What a first-time visitor downloads. Empty ledger, welcome screen + hint tour run. | tracked, generated |
  | `SomiFinancePersonal.html` | The maintainer's real data. | **gitignored**, generated |

  Real seed data lives in `personal.variant.json` (gitignored, its own `.gitignore` line — the `*[Pp]ersonal*.html` rules are `.html`-only and would not catch a `.json`). If it is absent, `build.py` skips that build so a fresh clone still works.

  **Everything the builds disagree about is either inside a `/* @variant:begin NAME */ … /* @variant:end NAME */` block (`storage`, `seed`, `seedBudget`) or in a variant's `strings` table in `build.py`.** Everything else is shared by construction. Two guards abort the build rather than shipping something wrong: every replacement must match **exactly once** (a reworded source otherwise no-ops silently), and no *tracked* output may contain a real ticker (`FORBIDDEN` / `leaks()` — matched on word boundaries, because a short ticker is also a substring of ordinary English words and a naive `in` check cries wolf on the source's own prose).

  This replaces a hand-merge process under which the personal copy drifted a full release behind — no budget tab, no i18n, no FX, and an *unsandboxed* TradingView script that could read the real holdings out of `localStorage`. Don't go back to it.

- **Each build has its own `localStorage` key**, because on `file://` most browsers treat every local file as one origin — without this, opening the demo would read and overwrite real data. `somifinance.demo.v1` / `somifinance.v1` / `somifinance.personal.v1`. The personal build sets `LEGACY_KEY` to `somifinance.v1`, so `load()`'s existing migration path carries the old data across on first open with no new code. `LEGACY_KEY` is `""` in the demo build and `load()` guards for that rather than calling `getItem("")`.
- **Naming:** rebranded from the old internal "Wealth Desk" name to **SomiFinance** throughout (title, topbar, storage key, export filenames, toast copy). The old `localStorage` key (`wealthdesk.v1`) is migrated automatically on first load under the new key (`somifinance.v1`) so existing users don't lose data — see `load()` in the "Key facts" section below.

## Security posture

Four things here are load-bearing. Breaking any of them silently re-opens a hole, so read this
before touching the `<head>`, `ensureTradingViewWidget()`, `sanitizeState()`, or `seed()`.

### CSP script hashes — **regenerate after every edit to the app script**

The `<head>` carries a `<meta http-equiv="Content-Security-Policy">` whose `script-src` lists two
**sha256 hashes** and deliberately does *not* include `'unsafe-inline'`. That omission is the point:
without it the browser refuses injected event-handler attributes (`onmouseover=`, `onerror=`), so an
XSS is dead even if an escaping site is ever missed.

The cost: **edit the app script and the page goes blank until the hash is regenerated** (with a CSP
error in the console). Hash 1 is the inlined Chart.js and never changes. Hash 2 is the app script,
and it differs per build because each build's seed data differs.

**This is now automatic — just run the build:**

```
python3 build.py
```

Recomputing the hash and writing it into the `<meta>` is the last step of every build, including a
hash refresh of `SomiFinanceDemo.html` itself (it is hand-edited, so its own hash goes stale too).
`python3 build.py --check` rebuilds in memory and exits non-zero if anything on disk is stale.

The build aborts if a file does not contain exactly two attribute-less `<script>` blocks. Three means
something in the file now spells out a script tag literally — which is why `ensureTradingViewWidget()`
assembles its tag as `'<'+'script'`.

`connect-src` names every host the page may contact: three remote hosts (Treasury, BLS,
`open.er-api.com`) plus `http://127.0.0.1:*` and `http://localhost:*` for the optional local
assistant. Adding a data source means adding it there too, or the fetch fails with no visible error.

### The assistant's loopback CSP entry — a real widening, honestly bounded

`connect-src` also allows `http://127.0.0.1:*` and `http://localhost:*`, added so the ✦ assistant
panel can talk to a local Ollama server. This is worth being precise about:

- **It creates no path off the machine.** Both hosts are unroutable, and with `default-src 'none'`
  this `connect-src` is the entire allowlist — injected script still cannot POST your figures
  anywhere remote.
- **It does let injected script reach any other loopback service** on any port, and read the
  response if that service is CORS-permissive. Pinning to `:11434` would shrink that, but it
  silently breaks anyone running Ollama on a non-default `OLLAMA_HOST` port, with a blocked fetch
  and no visible error — the wildcard port is the deliberate tradeoff.
- The endpoint is also user- and import-editable, so it carries its own second lock:
  `CHAT_LOOPBACK` in `SomiFinanceDemo.html` regexes it back to `127.0.0.1`/`localhost`/`[::1]` on
  every load — a crafted backup pointing it at a remote host is rejected before any request is made.
- Model output is written with `bubble.textContent`, never `innerHTML` — the same XSS-dead-on-
  arrival property the CSP gives the rest of the app extends to whatever a local model streams back.
- The chat transcript persists in `state.chat.messages` (capped at 40 messages / 2000 chars each)
  and rides along in every Export, exactly like every other field — see **Key facts** below. It is
  **never** sealed into a quarterly archive: `archivePayload()` whitelists the financial record only.
- `connect-src` was never the only exfil channel — `img-src data: https:` has always permitted an
  injected tracking pixel. `script-src`'s hashes-with-no-`'unsafe-inline'` is what actually kills an
  injection before it can build that tag.

### Two assistant invariants that keep the panel honest

Both exist because the connection UI was originally split across two surfaces and drifted:

- **`renderChatLog()` is the only function permitted to write to `#chatLog`.** The old
  ⚙ Test-connection handler wrote the setup guide straight into the log, which could erase an
  un-acknowledged disclaimer card and leave no way back except closing the panel. Everything now
  routes through the renderer; a step's markup lives in a `chat*CardHTML()` builder, never in a
  handler.
- **`chatConn` is deliberately ephemeral** — never persisted, never sanitized. It describes the
  world outside the browser (is Ollama up, which models exist), not the user's data. A stale
  "connected" restored from `localStorage` would be worse than no memory at all: the panel would
  look ready and fail on the first send. `chatStep()` derives the panel's state from it fresh each
  render, and `chatConnect()` / `chatSetModel()` / `chatSetEndpoint()` are the only three functions
  that mutate connection state — both the panel and the ⚙ section call them rather than carrying
  their own copies.

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

### The quarterly archive — an audit record, not a backup; the passphrase is the only secret

⚙ → **⧉ Quarterly archive** writes a `.somiq` file: a cleartext JSON envelope around AES-256-GCM
entries, one per archived quarter. Everything lives in the `/* ---------- quarterly archive */`
block beside `exportJSON()`. Five things here are load-bearing:

- **It is not a backup, structurally.** `archivePayload()` is an explicit *whitelist* of the
  financial record (ledger, budget, goals, history, yields, inflation, calendar, profile name/goal,
  plus a fixed `currency:"USD"` unit marker). Theme, language, currency preference, FX, onboarding
  flags and `chat` are omitted, so a file cannot restore an install even by hand, and there is no
  Restore or per-quarter re-export anywhere. **Don't add one** — an archive that can be restored is
  a backup, and one that can be edited then restored is worse than no archive. `⭳ Export` /
  `⭱ Import` stay the only backup path, and every archive surface says so.
- **`KEY` is not a secret.** The cipher key is `PBKDF2-SHA256(passphrase, randomSalt || KEY)`.
  `KEY` is plaintext in this HTML, so it contributes *build binding* (a demo archive won't open in
  the personal build) and nothing else. The passphrase is never persisted anywhere; lose it and the
  archive is unreadable, and the dialog says so before the first write. `iterations` lives in each
  file and loaders read the file's value, clamped to `ARCHIVE_ITER_MIN`/`MAX` so a crafted header can
  neither demand a weak key nor hang the tab.
- **Metadata is authenticated, not just stored.** `id|quarter|takenAt|prev` is GCM
  `additionalData`, so re-dating or relabelling an entry fails the tag exactly like editing the
  payload. `prev` is `sha256(previous ct)` — a hash chain, so a deleted, inserted or reordered
  entry shows as a break at that row. Dropping the *newest* entries can't break a chain; the local
  anchor `state.archive.head` catches that, but only in the browser that wrote them.
- **`archiveSession` is ephemeral, exactly like `chatConn`.** Decrypted entries and the
  (non-extractable) `CryptoKey` live only there — never in `state`, never in `localStorage`, gone on
  reload or *Close archive*. `state.archive` holds bookkeeping only: `{lastQuarter,lastAt,salt,head,count}`,
  all public values, sanitized field by field.
- **No plaintext fallback.** `cryptoOK()` gates everything; if `crypto.subtle` is missing (it is
  secure-context-only) the ⚙ section explains and offers no buttons. Verified present on `file://`
  in Chrome, Firefox and WebKit, and files written in each open in the other two.

Decrypted records still go through `sanitizeState()` for caps and coercion, after a shape check —
`sanitizeState()` fills missing fields from `seed()`, and an archive must never display a figure
it didn't carry. Every archived string renders outside `cellInput()`, so every one is `esc()`'d.
`showArchiveDialog()`'s Escape handler is named `onEsc`, not `esc`: `showResetConfirm()`'s is
called `esc`, which shadows the global escaper for that whole function body.

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
  can't through), `sArr` (`MAX_ROWS`, keeps the FIRST rows — for row lists), `sTail` (sorts by
  date and keeps the NEWEST `MAX_ROWS` — for `history`/`yields`/`inflation`; `capTail()` does the
  same at push time), `sPick` (allowlist), `sDate` (`YYYY-MM-DD` shape), `own()` (own-property
  test for every allowlist lookup — a bare `TABLE[key]` is truthy for `"constructor"`).
  `MAX_STR`=200, `MAX_ROWS`=1000.
- `cat` is deliberately a free string, not a `CAT_SETS` allowlist — the Overview allocation panel
  is documented to render whatever category an asset carries, and `colorForCat()` handles unknown
  ones. It is escaped at render time instead. **This is now load-bearing for goal switching:**
  because `cat` survives sanitize/import untouched, changing goal can never destroy a row's
  category, and `catOptions()` surfaces an out-of-list value at the top of the dropdown so a stray
  click can't overwrite it either.
- `importJSON()` renders **before** it persists. A malformed file used to be `save()`d first, which
  left the app crashing on every subsequent load with no in-app way out; it now rolls back to the
  previous state on any throw.

### Reset removes BOTH storage keys

`clearStoredData()` removes `KEY` **and** `LEGACY_KEY`. Removing only `KEY` does not reset
anything: `load()` falls back to `LEGACY_KEY` and copies it forward into `KEY` on the next boot, so
the data comes straight back. That is live in two builds — the personal build's `LEGACY_KEY` is
`somifinance.v1`, and the end-user build's is `wealthdesk.v1` for anyone migrated from the old app.
It is wrapped in `try/catch` because a private window can throw on `localStorage` access, and it
sets `canPersist=false` before `location.reload()` so no in-flight `save()` can rewrite the key
between the removal and the navigation.

### `seed()` ships in a public repo

Keep every figure fake. It previously carried the author's real holdings, cost basis, an options
position and a tax-timing note — all of which went public, and the first-run hint tour points users
straight at those rows. This now matters **more**, not less: `SomiFinanceDemo.html`'s seed is a
full portfolio built to be shown to people, so use placeholder fund names ("Global Index Fund"),
never real tickers.

Real data belongs in `personal.variant.json`, which is gitignored, and reaches
`SomiFinancePersonal.html` only through `build.py`. That file is gitignored by **pattern**
(`*[Pp]ersonal*.html` etc.), not by exact filename, so a rename or a "Save as" copy can't slip
past — and `build.py` refuses to write a *tracked* build containing any real ticker, so the guard
no longer depends on anyone remembering.

Also: `esc()` is the only escaping helper — use it for anything interpolated into markup, including
`data-` attributes. `cellInput()` used to escape `"` alone; it routes through `esc()` now.

**`sanitizeState()` caps and coerces; it does NOT escape.** Escaping happens at render. The two jobs
are separate on purpose, but the gap is easy to miss: `inflation[].note` is the one free-text field
that reaches `innerHTML` *outside* `cellInput()` (in `renderMacro()`'s `infReads` row), and it was
shipped unescaped in the first security pass — caught only when relabelling those dates. It is
`esc()`'d now. **If you add another field that renders outside `cellInput()`, escape it explicitly**;
the tables are safe by construction because everything there goes through `cellInput()`.

The read-row dates all read `as of <date>` rather than a bare date — that date is the *source's*
publication date, not a fetch timestamp. Treasury posts the daily curve ~3:30pm ET on business days,
so a same-morning refresh legitimately returns the prior business day.

## Done

**Overview tab**
- Net worth hero figure + delta vs. last snapshot (`renderOverview()`)
- Summary stats: total assets, total liabilities, invested, cash — the last two are **`CAT_META`-driven, not name-matched**: `invested()` / `cash()` / `accessibleAssets()` filter on a category's `group` and `liquid` flags rather than hardcoded `"Brokerage"`/`"Cash"` strings, so a goal that renames its categories keeps the tiles meaningful
- Allocation-by-category bars, colored per category, sized by % of net worth — one unified list, no separate "custom category" UI (that was tried and rolled back; see below)
- Net worth over time chart, built from logged snapshots + live point

**Ledger tab (Assets & Liabilities)**
- Inline-editable tables — click any cell, category dropdown, notes field (`renderLedger()` / `rowHTML()` / `wireCells()`)
- Asset categories come from the active goal's `CAT_SETS` entry (personal: 13, including a catch-all **"Alternative Asset"**; business: 10) — there's no in-app category management (add/rename) anymore; to track something odd (a wine cellar, a pet, a jean collection), add an asset in the Ledger, name the asset itself whatever you want, and assign it the "Alternative Asset" category. It then appears in the Overview allocation automatically since that panel groups by whatever category real assets carry, not by a separate managed list.
- Add/delete rows, live-updating totals and net worth strip
- **Empty state on the assets table** mirroring the liabilities one — `renderLedger()` used to map an empty array into bare table headers. Also covers a user who deletes their last row.

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
- **The widget is lazy-loaded** by `ensureTradingViewWidget()` on first Calendar render — it is deliberately NOT a `<script>` in the markup, because that fired on every page load even for users who never opened the tab.
- **It re-themes on a light/dark flip.** The guard is `tvTheme`, a sentinel holding the polarity currently on screen, not a plain loaded-once boolean (`tvColorTheme()` maps Latte → light, everything else → dark). `colorTheme` is baked into the widget config at injection and the opaque-origin frame is unreachable from our CSS, so rebuilding the frame is the only lever. Without it a widget first shown under a dark theme kept TradingView's pale-grey text after a switch to Latte and washed out completely against the light panel. **Dark→dark switches and ordinary re-renders still bail out** and never re-ping TradingView — only a polarity flip rebuilds. Clearing `#tvBox` leaves its inline `--live-cal-h` alone, so the user's saved height survives.
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
- **`HINTS_EMPTY` is the two-step variant for an empty ledger** — the end-user build seeds no rows, so the first two steps of `HINTS` have nothing to point at. Its final step is `HINTS[3]` **by reference, never copied**, so that copy exists in exactly one place; editing it in place would fork the two lists.
- **Selectors are re-resolved on every step, never cached** — `renderLedger()` rebuilds `#assetBody` via `innerHTML`, so a held node reference dies. Highlights are cleared by `querySelectorAll('.hint-target')` for the same reason. `startHints()` filters out steps whose target is absent *before* the tour starts (after switching to the Ledger, so targets exist), which is what keeps the counter reading `1 / n … n / n`; `showHint()`'s skip loop remains as a safety net for a target that vanishes mid-tour, and it skips without renumbering.
- **Goal drives hint copy AND the category lists.** Each step's `body` is keyed by goal (`body[state.profile.goal] || body.personal`, all four keys present), and `GOAL_SET` maps the goal onto a `CAT_SETS` entry — see *Goal-aware categories* below.
- **Onboarding re-seeds the budget; a later goal change never does.** `load()` seeds before the goal is known, so a business user would otherwise land on Rent / Groceries / Eating out; `finish()` swaps in `businessBudget()` while the rows are still untouched seed data. Changing goal later from ⚙ deliberately re-seeds nothing and rewrites no row — by then the rows may be real. That is the original "too destructive to existing data" reasoning, still holding, now scoped to the path where it actually applies.
- **"Runs once" is a flag, not self-deleting code** — a single HTML file can't remove its own source. `state.onboarded` gates everything. Note `load()` backfills `onboarded:false` on *existing* saves too, so the welcome shows once for everyone after the feature landed rather than only brand-new browsers. There is intentionally **no "replay intro"** menu item (user declined) — clearing site data is the only way back.
- `maybeBanner()` is held back until the tour ends (`endHints()` calls it) — the banner says "open the ledger" while the tour is already doing exactly that on the ledger.
- Name shows in the topbar via `applyGreeting()` / `#brandWho` (hidden when blank via `:empty`).

**Goal-aware categories**
- `CAT_SETS` holds **two** category sets — `personal` (13 assets / 6 liabilities / 11 income / 21 expense) and `business` (10 / 6 / 7 / 16). `GOAL_SET` maps the four goals onto them: personal and "Something else" → personal; "Start-up" and "Personal business" → business. `catsFor()` is the single read point; `renderLedger()`, `budgetRowHTML()` and all four add-row defaults (`catsFor().defaults`) go through it.
- **`catOptions()` preserves an out-of-list category and lists it first.** Without it a row whose category isn't in the active set renders as the *first* option while `state` still holds the true value — the ledger and the allocation chart then disagree, and the user's next click on that select destroys the real value with no undo. Rendering alone is safe (both writers bind to `change`, which `innerHTML` doesn't fire), so it was a display-then-lose bug. This also fixes orphaned categories arriving from an import, which was a live bug independent of goals.
- **`CAT_META` carries the meaning, so no function name-matches a category.** `group` (`cash` / `invested`) drives the Overview tiles and the tape; `liquid` drives the allocation panel's cash+brokerage readout. **Invariant: every goal's asset list needs at least one `cash` and one `invested` category**, or those tiles read $0 on a full ledger — that is why the business set carries "Reserves / investments". Verified at the time of the change that the refactor reproduced the old figures exactly.
- `businessBudget()` is the business row template. It lives **outside** the `@variant:begin seedBudget` block on purpose: `build.py` rewrites that block per build, and this must survive all three. Amounts are 0 because its only caller is onboarding.

**Quarterly archive**
- ⚙ → **⧉ Quarterly archive** (`renderArchiveList()`): *Start a new archive* / *Open an archive…*, and once one is open, *Archive a quarter* / *Close archive*. The collapsed header is the nudge (`renderArchiveCurrent()`, called from `setSectionCurrent()`): `Not started`, `Q2 26 archived`, or `Q2 26 not archived` — the quarter that's *due* is the one that just closed.
- **Rolling, append-only file.** Browsers can't overwrite a file, so each archive action downloads the whole file with the new entry appended (`somifinance-archive-<quarter>.somiq`) and the user keeps it in place of the old copy. Re-archiving a quarter appends a newer entry and marks the older one *superseded*; nothing is ever removed. Appending onto a file that failed verification is refused — it would seal the damage into the history.
- **Read-only viewer on Overview** (`#archPanel`, `renderArchive()`, called at the tail of `renderOverview()`): hidden until an archive is open; one row per entry with the quarter in a red `.q-badge`, date archived, net worth / assets / liabilities, and status (`✓ verified`, `⚠ modified — can't be opened`, `⚠ chain broken here`, `superseded`). Click or Enter expands a row into its archived ledger, budget and goals. No control in the panel writes anything.
- **Two quarter forms, kept apart.** Stored: `2026-Q3` (`quarterOf()`, sortable, century-proof). Displayed: `Q3 26` (`quarterLabel()`), standard finance shorthand. Never store the display form.
- **Archived figures render in USD** via `fmtUSD()`, not `fmt()` — `fmt()` would convert at *today's* FX rate and quietly rewrite a historical record. The panel note says so.
- **The badge is red on purpose, and deliberately reuses `--down`** — the one place in the app where `--down` does not mean "loss". Reusing the token keeps it legible in every theme; measured badge-on-panel contrast is 4.50 (Terminal) to 7.08 (Mocha), 4.80 on Latte.
- The table has `min-width:680px` inside an `overflow-x:auto` wrapper; without it a phone-width table wraps dates across two lines and clips the expanded row's figures.
- QA: an end-to-end Playwright suite over `file://` (78 checks — tamper cases, build binding, whitelist, XSS file names, theme contrast, regressions) passed in Chrome, with Firefox and WebKit round-trip smoke tests and cross-engine file compatibility.

**GTM hardening pass (pre-launch review)**
Three reviewers (security/data-integrity, financial correctness, product polish + static lint) audited the app; static lint was clean (no dead functions, no unresolved ids, i18n dicts in sync, README accurate). Every code finding was fixed:
- **Input**: `fromDisplay()` strips grouping/currency characters (`1,250.50`, `$3,000`) and returns `null` for anything non-finite; every cell commit keeps the previous value and toasts instead of writing 0 or `Infinity`. An emptied cell is an explicit 0.
- **Dates**: `today()` is the LOCAL calendar date (it was UTC — evening users west of Greenwich got tomorrow's date, and a morning snapshot overwrote the previous evening's). `maybeBanner()` diffs civil dates.
- **FX**: `fxRateKnown()` — when no rate exists for the selected currency, `curInfo()`/`fxRate()` fall back to USD (symbol and rate) and the tape, the currency picker and the ⚙ header say "rate unavailable — shown in USD". Never 1:1 under a foreign symbol. `importJSON()` calls `maybeRefreshFx()`, and a successful boot fetch re-renders the picker.
- **Snapshots**: `prevSnapshot()` measures the Overview/tape delta against the newest point NOT taken today, so Refresh no longer reads "▲ $0 since today". Dated series keep their newest rows past `MAX_ROWS` (`sTail`/`capTail`).
- **Prototype hygiene**: `allocByCat`, `spendByCat` and `chatContext`'s goal grouping use `Object.create(null)` — a category or `fundedBy` named `__proto__` was writing onto `Object.prototype`. `own()` guards every allowlist lookup. `chatSend()` builds its body inside the `try` so a throw can't wedge the composer on "Stop".
- **Budget**: a category with any unlimited (`limit` 0) row is never "over limit" (`unlimited` flag on the `spendByCat` bucket); one `clampYears()`/`clampRate()` for sanitize, chart and inputs.
- **Macro**: fetched dates/values go through `sDate`/`sNumN` and are `esc()`'d at render; BLS periods outside M01–M12 are rejected; re-entering a CPI reading keeps its note; no CPI back-fill onto older yields; empty yield read-row clears; tape REAL 10Y is neutral with no data.
- **Storage**: a failed `save()` re-renders the footer AND shows a persistent banner (`showSaveBlocked()`), not just a 2.6s toast.
- **Shortcuts**: 1–6 ignored while any `.intro-wipe.hold` dialog or `.hint-card` is on screen.
- **a11y / motion / contrast**: `aria-label` on every `.del`, `role=status aria-live=polite` on `#toast`, charts get `animation:false` under reduced motion; `--faint` raised in all five themes and `--muted` on Latte so `.note`/`.empty`/notes cells clear 4.5:1 on both `--bg` and `--panel` (Latte was 1.97:1).
- **Phone width**: `.topbar` wraps under 520px; no horizontal page overflow at 390/360px. Inline SVG favicon (data URI, zero requests). Real builds ship `inflation:[]`. `build.py`'s leak guard now also harvests whole multi-word row names, identifier-shaped tokens from notes/calendar (tickers, digit-bearing ids — never prose words) and the profile name; `GENERIC_NAMES` gained common multi-word account names. Dead `INTRO_ONCE_PER_SESSION` removed.
- **QA**: three Playwright suites over `file://` — archive (78), settings menu (59) and a full-app regression suite (101 checks: every tab, CRUD on every table, grouped/hostile number entry, local-date in Honolulu and Tokyo, FX offline + mocked rates, `__proto__` imports, 1005-row history cap, shortcuts under modals, over-limit, save-blocked notice, per-theme contrast, 390/360px, favicon, a11y, export/import round-trip, reset) — all green in Chrome, with Firefox/WebKit smoke subsets. Suites live outside the repo (scratchpad); see Key facts for the two Playwright gotchas.

**Savings goals** (Budgeting tab)
- A target, a target date, a monthly contribution and the account category that funds it
  (`renderGoals()` / `goalRowHTML()` / `wireGoalRows()` / `goalFundOptions()`; `renderGoalList()`
  drives the ⚙ picker; `demoGoals()` seeds the example set).
- **Progress is derived, never stored.** A goal reads the live balance of whatever `CAT_SETS`
  category `fundedBy` names, so it moves as the ledger moves and there is no second number to keep
  in sync. `fundedBy:""` means "not tied to an account" and shows contributions only.
- Shows the monthly figure needed to land on the target date, and warns when the goals together
  commit more than net cash flow — the one place the Budgeting tab cross-checks itself.
- `MAX_GOALS` = 50, sanitized like every other row list. `fundedBy` is a free string for the same
  reason `cat` is: a goal must survive a goal-type switch that renames the categories.
- **This section was missing entirely until scan 8**, despite being a headline README feature with
  two screenshots. It is the clearest example of why the lint rule at the top of this file exists.


**Pre-launch polish pass** (scan 8 — six commits, 46 items)
Three audit agents swept animations/empty states, every interactive control, and the first-run
experience; an Opus manager verified each commit and a Sonnet agent ran lint + QA. Highlights,
grouped by what they protect:

- **A real correctness bug.** Three delete handlers ran `findIndex` → `splice(i,1)` with no `-1`
  guard, so a miss removed the **last row of the array** instead. Reachable because the handlers
  closed over `arr` while `importJSON()` replaces `state` wholesale. All four tables now go through
  one `deleteRow(path,id)` that resolves the array from live `state` per call — which is also what
  makes undo safe, since an undo closure capturing `arr` would reintroduce the very bug it fixes.
  `undoBuf` holds `{path,index,row,seq}`, is ephemeral like `chatConn`, and is cleared by
  `importJSON()`. Undo is offered in the toast **and** on Ctrl/⌘-Z, because a few-second toast
  button is not a fair sole recovery affordance for a keyboard user.
- **`toast()` is no longer single-slot.** It queues, in three classes: plain (collapses — only the
  newest waits), error (`toastErr()`, preserved, deduped) and action (always preserved). A plain
  FIFO was tried first and was wrong: action toasts sit for seconds, so a burst left the user
  reading stale notices. The live region is the message **span**, so an action button is its
  sibling — a control inside `aria-live` gets the region re-announced and never takes focus.
- **The app stated a falsehood on the landing tab.** The Overview chart note read "One snapshot
  logged so far" in the branch that only ever runs with **zero** snapshots (`pts` always carries
  the live point). Branch-aware now, as are the Macro, budget and future-spend empty states —
  real yield's copy names the actual cause, since it needs a CPI print dated at or *before* a
  yield reading and can be empty with both series populated.
- **Seeded data no longer rots.** `nextReleases()` and `dayOffset()` build the calendar at first
  open; `build.py` passes it through as `RawJS("nextReleases()")` so the emitted file stays
  byte-stable and `--check` stays meaningful. **Verified: two rebuilds are byte-identical.** The
  author's `"verify date"` note and a hardcoded 2026-08-20 yield are gone from both builds.
- **Keyboard parity.** Focus rings on the tab menu and every picker; Alt+↑/↓ reorders budget rows
  (previously mouse-only, with no `tabindex`, `role` or key handler at all); focus traps and
  immediate autofocus in all four dialogs — the old 480ms timer meant an early typist could put an
  **archive passphrase into a ledger cell**, which then persisted it; `role="slider"` with live
  values on both resize grips, Home to reset, and the keyboard save debounced via `saveSoon()`.
- **Theme correctness.** `color-scheme` comes off a `scheme` field on each `THEMES` entry, written
  by `applyTheme()` — it cannot be a static `:root` rule, because themes are applied as inline
  custom properties with no `data-theme` attribute to select on. Several dark literals that
  `applyTheme()` could never rewrite (table borders, row hover, banner gradient, importance tags,
  a raw hex in the footer) are `color-mix()` off live tokens now.
- **Example data** (`loadExampleData()`), offered in ⚙ **only on a genuinely empty install**
  (`isFreshInstall()`, which measures budget *amounts*, not row counts — every build seeds rows and
  a calendar). That gate is load-bearing: it means the feature can never touch `state.archive`,
  whose `head`/`count` are the truncation anchor, and whose loss the way-back-out (a reset) would
  otherwise cause. `exampleData` is sanitized, or the banner would vanish on reload while the fake
  data stayed. The dataset was hoisted **outside** the `seed` variant block so the end-user build
  has it at all; it takes no variant input, ever.
- Import confirms before replacing everything, and always asks — an emptiness heuristic that is
  wrong destroys work to save one click. Clearing a numeric cell keeps the previous value
  (`commitNum()`); `fromDisplay("")` returning 0 used to zero an account silently while the blur
  re-format left the box *looking* empty. Ticker tape has a pause control (WCAG 2.2.2). The tour
  can be replayed. `APP_VERSION` is surfaced in About and the footer, and the copyright year is
  computed. Repo gained `LICENSE` (MIT), `SECURITY.md` and issue templates.
- **QA:** eight Playwright suites over `file://` — full-app 102, archive 70, settings menu 61,
  keyboard/undo 60, first-run 26, example data 19, stale gate 16, per-theme contrast 10 — plus a
  personal-build check (13) and a narrow-width overflow check that asserts zero horizontal page
  overflow at 360 and 390px. Lint clean: no unresolved ids, no dead functions, no `console.log`,
  i18n dicts in sync at 71 keys each. The archive's rejection paths were re-verified independently
  by **mutation testing** (deleting the KDF bounds check and confirming the suite fails), because
  a toast-helper change had made three archive tests pass again and that needed to be proven not
  to be masking.
- **`build.py` gained a third guard.** `check_budget_parity()` compares the row lists in
  `exampleBudget()` (the HTML, filled amounts) and `BUDGET_TEMPLATE` (build.py, zeroed) and fails
  the build if they differ by name, category or kind. There are deliberately two copies — the demo
  seeds one and the other builds get the other — and nothing else would notice a row added to just
  one of them. A comment used to claim the rows lived in one place; they do not.
- **The one bug this pass introduced, and how it was caught.** The ⚙ example-data offer was gated
  on `isFreshInstall()` at RENDER time only, and `loadExampleData()` never re-checked. Add your
  first account without reloading, open ⚙ for the first time, and the offer was still live —
  clicking it replaced that account and saved. The feature deliberately has no confirm, on the
  argument that the gate makes one unnecessary, so a render-time-only gate took the whole safety
  argument with it. **When a gate is the reason there is no confirm, it has to live where the
  confirm would have.** Fixed by re-checking inside the action; mutation-tested (7 checks fail
  with the guard removed). A sweep of every other render-time gate found no second instance —
  archive append, reset commit, `deleteRow()`, `undoDelete()` and import all re-check at the
  action.

**Reset all data**
**Reset all data**
- ⚙ → **Reset all data** opens `showResetConfirm()`, which reuses the first-run overlay (`.intro-wipe.hold` + `.welcome`) in `--down` rather than the accent, so a destructive dialog never wears the friendly colour. It names what will go, states there is no server copy to recover from, offers an **Export a backup first** button wired straight to `exportJSON()`, and gates the confirm button behind typing `RESET_PHRASE` exactly.
- **The phrase is case-sensitive on purpose** (trimmed, but `yes`/`YES` are rejected). A case-insensitive match makes the gesture reflexive, which is the one thing a destructive confirm must not be.
- Confirm calls `clearStoredData()` then `location.reload()` — see **Security posture** for why both keys go, and why a reload rather than an in-place re-init.
- Reset clears `state.archive` bookkeeping with everything else; archive *files* live outside the browser and are untouched. The dialog's *Export a backup first* button stays pointed at `exportJSON()` and must never offer archiving instead.
- **Per-build behaviour differs, correctly.** Reset restores each build's own `seed()`, and only the end-user build seeds `onboarded:false`. So the end-user build returns to the welcome screen, while the demo and personal builds restore their own baseline dataset — which is what a reset should do in those files. Falls out of the variant seeds; no special-casing.

**Brand name colour**
- The name beside "SomiFinance" (`#brandWho`) is cyan, not grey. `--cyan` is a **theme token** defined in `:root` and all five themes: Terminal is literally `#00FFFF` (the default theme, so the default install), the Catppuccin darks use their own Sky, and Latte uses Teal `#179299` — pure cyan scores **1.11 contrast** on Latte's near-white topbar, i.e. invisible.
- `NAME_COLORS` offers four choices — Cyan, Accent (`--amber`), Green (`--up`), Blue (`--blue`) — stored in `profile.nameColor` as the **token name**, so `applyGreeting()` writes an inline `var(--token)` and `applyTheme()` recolours it for free on every theme switch. `sanitizeState()` `sPick`s it, so a tampered value falls back to cyan rather than emitting `var(--evil)`.
- **Second deliberate colour exception, elsewhere:** the quarterly archive's `.q-badge` uses `--down` as a period marker, not a loss — see *Quarterly archive*.
- **Known, deliberate exception:** Green measures 2.96 contrast on Latte against a 3.0 threshold for large bold text. Kept because 3.0 is a rounded heuristic and this is Catppuccin's own green on its own base; the alternatives are worse (Violet 2.81, Peach 2.64) and the only token clearing 3.0 everywhere is `--down`, which means "loss" throughout the app. Swap to Rose if strict compliance is ever wanted.
- The same ⚙ section carries a **rename field** — before it, the name was write-once at onboarding and a typo was fixable only by a full reset.

**Fluid sizing**
- The shell and the whole type scale respond to window width via tokens in `:root`. `--shell` is `clamp(min(100vw,1180px),92vw,1800px)`: the lower bound floors it at the old fixed 1180px cap so **no viewport loses room**, while a 2000px window gains ~620px of content area.
- Every ramp is `clamp(floor, calc(px + vw), ceiling)`. **The px term is load-bearing** — a bare `vw` value ignores browser zoom and user font settings. Floors equal the previous fixed values, so nothing changes below ~1180px.
- `--tile-min` caps at 260px specifically so Budget's **five** stat tiles stay on one row inside the 1800px shell; raising it wraps that row 3+2.
- Numbers ramp harder than reading text: the hero goes 52→82px (×1.58) while table text goes 13.5→17px (×1.26). Scaling body copy like a headline gives 18px text on very long lines, which is harder to read, not easier.
- Chart boxes are fluid too, and `.chart-box.tall` must stay **above** the base at every width — if only the base is fluid, a fixed 300px `.tall` ends up shorter than the base on a wide screen.

**Languages (i18n)**
- Three languages: `en`, `zh-Hant`, `zh-Hans` (`LANGS`, picked in ⚙, `state.lang`). `t(key)` falls back to English then to the raw key, so a missing translation never renders blank.
- **Scope is core chrome only** — tabs, panel headings, table columns, buttons. Long-form notes and toasts stay English by design.
- **Mixed application strategy, deliberately.** Most target strings are static HTML written once and never re-rendered, so `applyChromeI18n()` relabels them by id from `CHROME_MAP`. The few JS-templated pieces (`t("tab."+tab)` in `show()`, the budget "+ Add Row" button) call `t()` inline. Expect both patterns to coexist.
- **Category values are NOT translated** (`CAT_SETS`, `SPEND_KINDS`, …) — they're persisted as literal strings and matched by value, so translating them would corrupt saved data across a language switch.

**Currency**
- Six currencies (`CURRENCIES`: USD/JPY/TWD/CNY/EUR/GBP, each with `symbol` + `decimals`; JPY and TWD are 0-decimal). `state.currency`, picked in ⚙.
- **`fmt`/`fmt2` read currency as a closure, not a parameter** — same trick `css()` uses for live theme colors. That's why adding currency needed *zero* edits at the ~20 existing call sites. Keep it that way.
- Chart **datasets stay in USD**; only the tick formatters (`tickMoney()` / `tickMoneyK()`) convert at render time. Converting the data would corrupt axis scaling.
- **Editable cells round-trip through `toDisplay()` / `fromDisplay()`; `state` is always USD.** Every display is re-derived from that single source of truth, so flipping currencies repeatedly causes no drift (nothing is written unless the user actually edits).
- **FX source is `open.er-api.com`, not Frankfurter.** Frankfurter was the first choice (open-source, ECB-backed) but **ECB publishes no TWD rate at all**, and TWD is required. Don't "improve" this back to Frankfurter without re-checking that. `fetchFxRates()` / `refreshFx()` / `maybeRefreshFx()`; keyless, CORS-open, cached in `state.fx.rates` with `state.fx.lastFetch`.
- FX fetch is **deliberately not gated by `state.autoRefresh`** — unlike opt-in Treasury/CPI data, currency is an explicit user selection, and a missing rate would silently mislabel USD figures as ¥/€. It fetches once a day whenever a non-USD currency is active, falls back to the last cached rate, and marks the picker `(rate unavailable — shown in USD)` when no rate exists for the selected currency — figures then stay in USD (`fxRateKnown()`) rather than showing USD numbers under a foreign symbol.

**Settings menu (⚙)**
- Eight collapsible sections (`.set-sec` / `.set-head` / `.set-body`): Theme, Auto-refresh, 語 Language, € Currency, ◎ Tracking, ✎ Your name, ✦ Assistant, ⧉ Quarterly archive — plus **◷ Replay the intro hints**, a conditional **◆ Load example data** (shown only while `isFreshInstall()`), and a **Reset all data** button below them. The reset is deliberately *not* a `.set-sec`: `openSetSection()` treats every `.set-head` as an accordion panel, and a one-shot destructive action is not a picker. **Accordion — one open at a time** (`openSetSection()`), all collapsed on every open, with the active value shown in each collapsed header (`setSectionCurrent()`). Wired once by `initSettingsSections()`.
- `.theme-list` has `max-height` + `overflow-y:auto` + **`overscroll-behavior:contain`** — that last property is what stops scrolling the menu from chaining to the page behind it.
- **User-resizable, and the contents scale with it.** A corner grip (`#setMenuResize`, bottom-left, mirroring `#tvResize`'s conventions — pointer events + `setPointerCapture`, arrow-key nudging, drag saves once on release while a keypress saves immediately) drives `state.setMenuScale` (clamped `0.85`–`1.6` by `clampSetScale()`, default `1`). `applySetMenuScale()` is the sole writer of `--set-scale` on `#themeList`. **Every fixed-px size inside the menu is `calc(basePx * var(--set-scale,1))`** — font-sizes, paddings, gaps, the theme swatch icons, even the one existing fluid-token exception (`.set-danger button`'s `var(--l-micro)`) — so scale 1 is pixel-identical to before this feature and every other value moves in lockstep with it. **Deliberately NOT scaled:** border-width, border-radius and box-shadow (decoration, not legibility). `max-height` is `min(70vh,calc(520px * var(--set-scale,1)))` — the 520px term scales so a bigger menu is actually taller, while the `70vh` term is what still keeps it on screen. It was a flat `520px` at first, which meant the box stopped growing at ~15% up while its rows kept inflating: you got a scrollbar and stretched-looking rows instead of a bigger menu.
- **Each drag axis is normalised by its own base dimension** (`initSetMenuResize()`). Both axes originally divided the pointer delta by `250` — the base *width* — but the menu is ~1.8x taller than it is wide, so a downward drag resized it 1.8x faster than the cursor moved (100px of drag jumped the scale to 1.4). `dy` now divides by the base *height*, so the bottom edge tracks the pointer the way the left edge always did; whichever axis asks for more growth drives the scale, so the grip never lags behind a diagonal drag. Bases are measured from the live box once on `pointerdown` (`offsetWidth`/`scrollHeight` ÷ the starting scale) — re-measuring mid-drag would feed a just-resized box back into its own input, and `scrollHeight` is the right height because `max-height` clips the visible box while the content is what the scale drives. The QA suite asserts the 1:1 tracking property rather than a scale number; the old test encoded the buggy divisor as `1.09`. `min-width` is capped to `calc(100vw - 24px)` for the same reason sideways, so a maxed-out scale can't force horizontal scroll on a narrow screen. The grip lives in a `position:sticky` footer row so it never scrolls out of reach, even with Quarterly Archive's long content open. Double-click resets to `1`.
- **Scope picker selectors to their `data-` attribute, never `.theme-opt`.** That class is now shared by all six theme-styled pickers (`[data-theme]`, `[data-auto]`, `[data-lang]`, `[data-cur]`, `[data-goal]`, `[data-namecolor]`); the Assistant section's model `<select>` uses `[data-chatset]` for the same reason. `renderThemeList()` used the broad selector and cleared `aria-current` on Language/Currency/Auto-refresh every time a theme was picked — fixed by scoping to `[data-theme]` (5 elements). The other three already scoped correctly.

**✦ Assistant — in-panel connection onboarding**
- The panel is a four-step machine derived fresh on every render by `chatStep()`: **ack** (one-time
  disclaimer) → **connect** → **model** → **chat**. The composer is enabled only in `chat`. Every
  step except `ack` renders *below* the transcript, so losing the connection mid-conversation doesn't
  read as the conversation being wiped; `ack` takes the log over completely, because an imported
  backup can carry `ack:false` alongside messages.
- **Setup lives in the panel, not in ⚙.** The connect step leads with one **Connect** button and
  states plainly that Ollama needs no API key, no account and no sign-up — the endpoint field is
  collapsed behind a "Change address" disclosure, since the default is right for almost everyone and
  a URL box is the wrong first thing to show someone who has never run Ollama. A failed attempt
  swaps the button to **Try again** and inlines `chatGuideHTML()` right there, so the instructions
  and the button that retries them are in the same place. Previously the guide rendered in the chat
  log while the only control that could produce it sat in a collapsed ⚙ accordion — a dead end.
- The header model badge (`#cpModelBadge`) is a **button** — once connected it is the only route
  back to the picker (`chatWantModelPick`).
- **`chatStep()` treats a saved model that is no longer installed as "pick again"**, with a line
  saying so, rather than silently reassigning to `models[0]` the way the old settings-only path did.
- A send failure routes by shape (`chatFailKind()`): a 404/"not found" means Ollama is reachable and
  the model is gone → back to the **model** step; no HTTP status at all means the connection died →
  back to **connect**; anything else is a real error from a reachable Ollama and stays an inline
  bubble. The failed message stays in the transcript either way.
- **Panel open runs one silent probe per page load** (`chatConn.checked`), at a 1.5s timeout with
  `diagnose:false` — a stored model says nothing about whether Ollama is running *now*, and the
  cheap check is what stops the composer looking ready and then failing on send. It paints first and
  probes second, so the panel never blocks on the network. The full cors-vs-down diagnosis (the
  second `no-cors` leg) is only paid for when the user presses Connect.

**Cross-cutting**
- 5 themes via CSS custom properties (Terminal default + 4 Catppuccin variants), live chart re-theming on switch (`THEMES` / `applyTheme()`). Every theme also defines `--cyan` for the brand-name colour — Terminal is literally `#00FFFF`, Latte uses Catppuccin Teal because pure cyan scores 1.11 contrast on its light topbar
- Scrolling ticker tape summarizing net worth, invested, cash, yields, CPI, real yield (`renderTape()`)
- JSON export/import for backup and restore (`exportJSON()` / `importJSON()`)
- **Tab-scoped Refresh button**: behavior now branches on the active tab (refreshBtn handler inside `init()`) — Overview still snapshots net worth into history (unchanged); Macro Signals pulls live data (see above); Ledger/Calendar just re-render with a light toast. Previously Refresh always snapshotted + jumped to Overview regardless of tab; changed because a full page reload (F5) covers the "everything" case and the button reads clearer scoped to what's on screen. The stale-data banner copy was updated to match (now explicitly says update in Ledger, then hit Refresh on **Overview**).
- Stale-data nudge banner (fires after 7 days since last update, or if no snapshots exist) (`maybeBanner()`), with a third branch for an empty ledger — "confirm today's values" is wrong copy when there are no values yet
- Keyboard shortcuts (1-6 switch tabs, Esc closes menus). Order: Overview, Ledger, Budgeting, Macro, Calendar, About. Budgeting was inserted at 3 (shifting Macro 3→4, Calendar 4→5); About was appended at 6 specifically to avoid shifting anything again. **Adding a tab means editing five places in lockstep** — the menu `<button>`, the `<section id="tab-…">`, `REFRESH_TITLE`, the keydown array, and `CHROME_MAP` plus the three `LANGS` dicts.
- **Numeric table headers are LEFT-aligned while the figures stay right-aligned** (`thead th.num{text-align:right}` was deleted; `.cell.num` / `tfoot td.num` / `.sec-head td.num` keep the numbers right). Recorded as a decision so it isn't "fixed" back: right-aligning a numeric header pins it to its column's right edge, landing it within one `th`'s padding (~20px, whatever the column widths are) of the next left-aligned header — Budget's LIMIT and TYPE read as one jammed pair. **No column-width change can widen that gap**; only the alignment can.
- Chart helpers: `mountChart(id,type,...)` is the shared guard/destroy core; `line()` and `bars()` are thin wrappers over it (`mountChart()`). Use `bars()` for any new bar chart rather than hand-rolling a `new Chart(...)`.
- Watermark footer: "SomiFinance ©2026 mDemarco12" (`.watermark`)
- Responsive layout — fluid shell and type (see *Fluid sizing* under Done); the panel grid still collapses to 1 column under 840px
- aria attributes on menus and chart canvases; graceful fallback text if Chart.js somehow isn't available (`mountChart()` guards on `window.Chart`) — kept from the CDN era, harmless now that it's inlined

## Could be done

- Live market price feeds for **assets** (brokerage holdings, etc.) — still manual entry. (Treasury yields, CPI, and a reference economic calendar are now live-pulled — see Macro Signals / Economic Calendar above.)
- Per-asset value history — only net-worth *totals* are snapshotted continuously. The quarterly archive now records every holding once per quarter; anything finer-grained is still open
- Budget **history** — the Budgeting tab models a single current month. The quarterly archive seals the budget once per quarter, but there's still no month-over-month tracking or actual-vs-budget over time (net worth has `history[]`, budget has no equivalent). Natural next step if budgeting gets used seriously.
- Transaction-level tracking / bank import — budgeting is category-level and hand-entered by design
- CSV export (JSON only today)
- Column sort/search/filter in ledger tables (calendar auto-sorts by date; ledger does not)
- Recurring/scheduled automatic snapshots (currently manual "Refresh" click only). Automatic quarter-end *archiving* is deliberately not planned — the ⚙ header nudge is the prompt; an offline single-file app shouldn't write files in the background
- Chart overlay of archived quarters on the Overview net-worth chart — scoped in the archive plan and not built; archive dates don't align with snapshot labels on the category axis
- PWA install support (manifest + service worker) — would also make the "offline" claim fully true on first load
- State-schema *versioning* (the storage key is suffixed `.v1` and `sanitizeState()` now coerces any shape to the current one, but there's no explicit version field or migration ladder)
- Cloud sync / accounts — explicitly out of scope today; footer says "your pipeline can write the same JSON shape... and you re-Import it"
- In-app category management (add a custom category from the Overview tab, rename one in place) — **tried and deliberately reverted.** It added a "+" button + ✎ rename chips to the Allocation panel, but the user decided category management should happen implicitly: pick "Alternative Asset" (or any category) in the Ledger when adding an asset, name the asset itself, and it flows into the allocation automatically. Don't re-add a category CRUD UI without checking this decision first.

## Needs polish

- No OG/Twitter card tags. The inline SVG favicon and `<meta name="description">` are in.
- Onboarding copy is English-only, so a zh-Hant/zh-Hans user still gets an English first run. Now broader than it was: the welcome screen, all hint bodies (four goals × five steps), the reset confirm dialog, and the two newest ⚙ sections are all untranslated. Consistent with the "chrome only" i18n scope, but it's the one place that inconsistency is most likely to be noticed.
- Monolithic single file (~528 KB, ~5627 lines) — ~200 KB of that is inlined Chart.js, so hand-written code is ~328 KB. Fine for personal use; worth a deliberate decision (keep as a distribution feature vs. split into modules) once this becomes a shipped product

## Key facts for future me

- Everything lives in one `<script>` block at the bottom of the file.
- **There is no test suite in the repo.** The quarterly archive was QA'd with a throwaway Playwright script driving the real builds over `file://` (Chrome, plus Playwright's Firefox and WebKit). Two things will bite anyone automating this page again: **`page.wait_for_function()` fails** — it polls by evaluating a string, which the hash-only `script-src` correctly refuses (`EvalError … 'unsafe-eval'`); poll `page.evaluate()` from the test side instead, which isn't subject to page CSP. And **don't assign to a global named `status` in an evaluate** — it's `window.status` and coerces arrays to strings. Don't "fix" the first one with `bypass_csp`: the CSP is part of what needs testing.
- State object shape: `{ updated, onboarded, hintsDone, profile{name,goal,nameColor}, theme, lang, currency, fx{rates{},lastFetch}, calendarOrder[], liveCalHeight, autoRefresh, lastFetch, assets[], liabilities[], history[], yields[], inflation[], calendar[], goals[], budget{}, chat{ack,endpoint,model,messages[]}, archive{lastQuarter,lastAt,salt,head,count}, tapePaused, exampleData }`. No category-management fields — categories are just strings on each asset/liability. **All monetary values are stored in USD regardless of the selected display currency.**
- **Every new state field needs a line in `sanitizeState()`** — it is the single door into `state` (called by both `load()` and `importJSON()`) and supplies every default, so a field missing from it is silently dropped on the next load. This replaces the old per-scalar `load()` backfills, which are gone. `normalizeBudget()` still plays the same role for the budget block. See **Security posture**.
- `budget` = `{ income:[{id,name,cat,amount,optional,notes}], expenses:[{id,name,cat,amount,limit,kind,optional,notes}], assumptions:{rate,years} }`, where `kind` ∈ `essential|discretionary`. Categories come from the active goal's `CAT_SETS` entry (personal 11 income / 21 expense; business 7 / 16). **`normalizeBudget()` is the compatibility shim** — called from BOTH `load()` and `importJSON()`; it backfills missing arrays/assumptions/ids and coerces a bad `kind`, so older saves and partial imports don't crash the tab. Any new budget field should get a default there too.
- `assets`/`liabilities` items: `{ id, name, cat, value, notes }`. Categories come from the active goal's `CAT_SETS` entry (personal 13 assets incl. "Alternative Asset" and "Other" / 6 liabilities; business 10 / 6) — no user-editable category list. `colorForCat(c)` returns the curated color from `CAT_COLOR` when one exists, otherwise a deterministic hash-based color from `CAT_PALETTE`, so any category string (even a stray/legacy one) still renders with a stable color.
- The Overview allocation panel (`renderOverview()`) groups `state.assets` by whatever string is in `a.cat` — it has no awareness of `CAT_SETS` beyond coloring, so it will happily show a category that isn't in the active goal's dropdown if old, imported, or other-goal data has one. That is by design and is why `catOptions()` exists: the chart and the select agree on the real value rather than the select quietly showing something else.
- `history` items: `{ date, net, assets, liab }` — one point per `snapshot()` call.
- `yields` items: `{ date, y10, y20, y30 }`; `inflation` items: `{ date, cpi, note? }`.
- `calendar` items: `{ id, date, event, imp, notes }`, `imp` ∈ High/Med/Low/Personal.
- `THEMES` object defines all theme tokens; `applyTheme()` writes them as CSS custom properties at runtime.
- `seed()` produces first-run data; `load()`/`save()` wrap `localStorage` under **the key for that build** — `KEY` / `LEGACY_KEY` live in the `@variant:begin storage` block and differ per build (see Snapshot). `load()` migrates `LEGACY_KEY` forward automatically if `KEY` is empty, which is both the `wealthdesk.v1` path and the personal build's `somifinance.v1` path. Note: browsers that went through the earlier (reverted) custom-category feature may still have stray `customCats`/`altAssetSeeded` keys sitting unused in their saved JSON — harmless, nothing reads them anymore.
- Live-data functions: `fetchTreasuryYields()` / `fetchLatestCPI()` / `refreshMacroData()` (`refreshMacroData()`) — no API keys, both sources are open government data. **Do not swap these for Yahoo Finance** if asked again: confirmed via direct testing that Yahoo's endpoints aren't CORS-open (would silently fail in-browser with no backend to proxy through) and Yahoo has no CPI data at all (that's a BLS/government stat, not market data).
- Same rejection logic applies to the calendar widget: Bloomberg and investing.com both returned HTTP 403 on direct request (active bot-blocking) and both prohibit scraping in ToS — don't attempt to pull structured data from either. TradingView's `embed-widget-events.js` (`#tvBox`) is the current no-key solution; Finnhub and Financial Modeling Prep are confirmed CORS-open fallbacks if structured (editable-table-feeding) calendar data is wanted later, but both require the user to sign up for a free API key first.
