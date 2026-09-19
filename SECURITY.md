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
backup or archive file that demonstrates the issue is ideal.

## What the app already assumes

These are deliberate design decisions, not oversights. A report that rests on one of them is still
worth sending if you can show the mitigation fails, but the reasoning is documented in
`PROJECT_STATUS.md` under **Security posture**.

- **All data is local.** Figures live in `localStorage` and never reach a server. There is no
  account, no backend and no telemetry. Anyone with access to the browser profile has the data;
  full-disk encryption is the answer to a stolen laptop, not anything the app can do.
- **A hash-only Content-Security-Policy.** `script-src` lists SHA-256 hashes and deliberately omits
  `'unsafe-inline'`, so injected event-handler attributes do not run. `connect-src` names every host
  the page may contact.
- **Loopback is allowed on any port** so the optional local assistant can reach Ollama. This is
  unroutable off the machine but does widen what injected script could reach on it. The tradeoff is
  written up in `PROJECT_STATUS.md`.
- **The TradingView widget is sandboxed** without `allow-same-origin`, giving it an opaque origin so
  it cannot read stored data or touch the page.
- **Imported backups are untrusted input.** Every field is whitelisted and coerced by
  `sanitizeState()`, row ids are regenerated, and nothing is persisted until it renders cleanly.
- **The quarterly archive is not a backup.** Entries are AES-256-GCM with PBKDF2-SHA256, chained by
  hash, with authenticated metadata. The passphrase is never stored anywhere and cannot be
  recovered. The `KEY` constant in the HTML is not a secret; it contributes build binding only.

## In scope

Anything that lets one of the above fail: a cross-site scripting path, a way to exfiltrate figures
past the CSP, a crafted backup or `.somiq` file that escapes sanitising or forges verification, or a
way to make the app persist something it should not.

## Out of scope

Issues that require an attacker who already controls the machine or the browser profile, the
third-party TradingView widget's own code, and the security of an Ollama instance you chose to run.
