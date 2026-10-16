# Security policy

SomiFinance handles personal financial figures, so security reports are welcome and taken
seriously.

## Reporting a vulnerability

**Please do not open a public issue for a security problem.** Use GitHub's private reporting
instead: go to the **Security** tab of this repository and choose **Report a vulnerability**.

Expect an acknowledgement within a few days. This is a personal project maintained by one person,
so a fix may take longer than that, but you will be told where things stand.

Please include what you would need to reproduce it: the build you used
(`SomiFinance.html` or `SomiFinanceDemo.html`), the browser and version, and the steps. A crafted
backup or archive file that demonstrates the issue is ideal. If it involves stock quotes, say
whether `quotes.py` was running and on which port.

## What the app already assumes

These are deliberate design decisions, not oversights. A report that rests on one of them is still
worth sending if you can show the mitigation fails, but the reasoning is documented in
`PROJECT_STATUS.md` under **Security posture**.

- **All data is local.** Figures live in `localStorage` and never reach a server. There is no
  account, no backend and no telemetry. Anyone with access to the browser profile has the data;
  full-disk encryption is the answer to a stolen laptop, not anything the app can do. The one
  thing about your holdings that can leave the machine is a list of ticker symbols, and only if
  you turn stock quotes on — see the next two points.
- **A hash-only Content-Security-Policy.** `script-src` lists SHA-256 hashes and deliberately omits
  `'unsafe-inline'`, so injected event-handler attributes do not run. `connect-src` names every host
  the page may contact.
- **Loopback is allowed on any port** so the optional local assistant can reach Ollama and the
  optional quote helper. This is unroutable off the machine but does widen what injected script
  could reach on it. The tradeoff is written up in `PROJECT_STATUS.md`. One consequence is new:
  while `quotes.py` is running, a loopback request to it does cause a request off the machine —
  to Yahoo Finance only, carrying only symbol-shaped strings. The in-app switch does not protect
  the helper from script that has already managed to run in the page, so stop the helper when you
  are not using it.
- **Stock quotes are off by default and send ticker symbols only.** The page cannot call Yahoo
  Finance itself (Yahoo's endpoints are not CORS-open), so prices come through `quotes.py`, a
  standard-library script you run on your own machine. With the feature on, pressing Refresh on
  Assets & Liabilities sends every ticker symbol on your asset rows (up to 50, whether you typed
  them or they came in with an imported backup) to that helper, which sends them to Yahoo. That
  button is the only trigger: auto-refresh does not fetch quotes, so nothing is sent on page load.
  No share count, value, name or note is put in the request; each position's value is computed in
  the browser. Three things back that up:
  - *Consent is given in the app, by the person using it.* The switch is off in every build. The
    only way to turn it from off to on is the dialog under ⚙ → Stock quotes. The dialog is shown
    on every such switch; there is no stored "already agreed" flag that skips it. Once on, the
    setting is saved in this browser and stays on across reloads until you turn it off.
    Importing a backup forces the switch off, so a file cannot opt anyone in — though the
    tickers in that file are kept, and are what gets sent if you then turn quotes on.
  - *The switch is checked where the request is made*, not only where the columns are drawn, and
    again after each wait, so turning it off mid-request stops any further request and stops the
    result being applied.
  - *The helper address must be loopback*: `127.0.0.1` or the name `localhost`, on any port. It is
    user- and import-editable, so it is checked against the same loopback-only pattern as the
    assistant's endpoint on every load and before every request. An imported backup can change
    the port, but not point it off the machine.

  Yahoo therefore learns which symbols you asked about and your IP address, as it would if you
  looked them up on its website. If a quote comes back priced in one of the other currencies the
  app converts (JPY, TWD, CNY, EUR, GBP) and no rate has been fetched yet that day, an
  exchange-rate lookup to `open.er-api.com` also runs, even when your display currency is USD.
  That request is a fixed URL with nothing about you in it; that host sees your IP address.
- **`quotes.py` is deliberately not a proxy.** It listens on `127.0.0.1` only, answers one path,
  builds the Yahoo URL itself from symbols it has validated (at most 50 per request), follows no
  redirects, and refuses a request whose `Host` header is not loopback. It sends a CORS header
  only to a `null` origin (a page opened from a file) or a loopback origin, so an ordinary website
  cannot read its answers. It answers at most 20 requests a minute. It keeps no record of what was
  asked, and logs that a request happened, not which symbols. It does use your system's proxy
  settings, if you have any. Three limits are known and accepted:
  - A website can still cause it to *make* a lookup for symbols that site chose, without seeing
    the result. The per-minute cap bounds how many Yahoo requests that can spend from your IP.
  - A sandboxed frame on any site has a `null` origin, so it can read public quotes for symbols
    it supplies. Neither of these reveals your holdings: the helper is told only the symbols in
    each request, and these requests are not yours.
  - **The helper is unauthenticated, and the page trusts whatever answers on the helper port.**
    This is the one limit that can expose your symbol list. If `quotes.py` is not running and
    another program on the same machine — another user's, on a shared computer — is listening
    on that port, pressing Refresh hands it your ticker symbols. A careless one makes the Refresh fail; a
    deliberate one could answer with real prices and give no sign. Don't turn stock quotes on on a machine you share with
    people you would not show that list to.
- **The TradingView calendar runs no third-party script.** It's a sandboxed iframe pointed
  directly at TradingView's own embed URL, without `allow-same-origin`, giving it an opaque origin
  so it cannot read stored data or touch the page — there's no loader script to sandbox in the
  first place.
- **Imported backups are untrusted input.** Every field is whitelisted and coerced by
  `sanitizeState()`, row ids are regenerated, and nothing is persisted until it renders cleanly.
- **`connect-src` is not the only channel, and never was.** `img-src` allows `data:` and `https:`,
  so script that did manage to run could build a tracking pixel and put figures in its URL. This is
  known and accepted: the defence against it is `script-src`'s hashes-with-no-`'unsafe-inline'`,
  which kills an injection before it can construct the tag. A report that assumes script execution
  as its starting point needs to show how the script got to run.
- **An archive is bound to the build that wrote it.** The cipher key is derived from the passphrase
  plus a per-file random salt plus the build's `KEY` constant, so a file written by one build will
  not open in another even with the correct passphrase. That is intended, not a bug.
- **The quarterly archive is not a backup.** Entries are AES-256-GCM with PBKDF2-SHA256, chained by
  hash, with authenticated metadata. The passphrase is never stored anywhere and cannot be
  recovered. The `KEY` constant in the HTML is not a secret; it contributes build binding only.

## In scope

Anything that lets one of the above fail: a cross-site scripting path, a way to exfiltrate figures
past the CSP, a crafted backup or `.somiq` file that escapes sanitising or forges verification, or a
way to make the app persist something it should not.

For stock quotes specifically: any way to turn them on without the consent dialog, any request
made while they are off, anything other than ticker symbols reaching the helper or Yahoo, a helper
address that is not loopback being contacted, or a way to make `quotes.py` fetch a URL it did not
build itself, answer on a non-loopback interface, or disclose the symbols a user asked for.

## Out of scope

Issues that require an attacker who already controls the machine or the browser profile, the
third-party TradingView widget's own code, the security of an Ollama instance you chose to run, and
what Yahoo Finance does with the symbol lookups it receives. Yahoo's endpoint is unofficial and may
change or stop working; prices failing to arrive is a bug report, not a security one.
