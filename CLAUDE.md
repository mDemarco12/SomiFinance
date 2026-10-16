## Local worker
Ollama models are worker agents only. Claude is the manager: it plans, hands off with
/local-worker-agent, and verifies. Worker output is not done until the manager has re-run
every check itself and reviewed every changed and new file. Only the user commits.

When asked to plan for the local worker, write PLAN.md with:
- numbered steps small enough for a few edits each
- exact file paths and function names
- one check command per step that the manager can re-run and that gives the same answer every time
- no open design decisions

For more than one worker, write one plan per worker (PLAN.w1.md, PLAN.w2.md) with disjoint
files, run them one after another, and give each its own log with LOCAL_LOG.

Project rules (the manager rejects any run that breaks them):
- Edit only SomiFinanceDemo.html, never SomiFinance.html or SomiFinancePersonal.html.
  Any plan that changes it ends with `python3 build.py`, checked by `python3 build.py --check`.
- Never edit personal.variant.json; it holds real financial data.
- The worker script's DENY list enforces both rules. The manager never reads these files
  either, because it is not local.
- The native app lives in app/ (Rust workspace: Tauri 2 shell + Leptos UI). Run cargo with
  `--manifest-path app/Cargo.toml` from the repo root. Never name an app file `somifinance-*.json`:
  that pattern is reserved for real-data exports and is git-ignored and worker-denied.
