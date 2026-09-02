#!/usr/bin/env python3
"""Build SomiFinance's end-user and personal files from SomiFinanceDemo.html.

    python3 build.py            build every variant
    python3 build.py --check    rebuild in memory, fail if the files on disk are stale

SomiFinanceDemo.html is the ONLY file anyone edits. It is a working build in its own right
(full fake portfolio, opens straight into the dashboard) and doubles as the source the other
two are projected from:

    SomiFinance.html            what a first-time visitor downloads — empty ledger, onboarding runs
    SomiFinancePersonal.html    the maintainer's own copy — real data, gitignored

Everything the three builds disagree about is either inside a /* @variant:begin NAME */ ...
/* @variant:end NAME */ block or listed in a variant's `strings` table. Everything else is
shared by construction, which is the point: the personal copy previously drifted a full
release behind because it was hand-merged.

Two rules keep this honest, and both abort the build rather than writing something wrong:

  * every replacement must match EXACTLY ONCE. A search string that stops matching (because
    the source was reworded) would otherwise silently no-op and ship a build with the wrong
    storage key or the wrong seed.
  * no output that git tracks may contain any string in FORBIDDEN. Real holdings have leaked
    into this public repo once already; this makes that structural instead of a thing to
    remember.

The last step of every build is recomputing the app script's sha256 and writing it into the
CSP <meta>. The page's script-src lists hashes and deliberately omits 'unsafe-inline', so a
stale hash means the browser refuses the script and the page comes up blank. This replaces
the one-liner that used to live in PROJECT_STATUS.md.
"""

import base64
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = "SomiFinanceDemo.html"
PERSONAL_VARIANT = "personal.variant.json"

BANNER = (
    "<!-- GENERATED FILE — DO NOT EDIT.\n"
    "     Built from {src} by build.py. Any change made here is lost on the next build;\n"
    "     edit {src} and re-run `python3 build.py` instead. -->\n"
)

# Real holdings must never appear in a build git tracks — they were committed publicly once
# before (see PROJECT_STATUS.md, "seed() ships in a public repo").
#
# The terms are read from the gitignored personal.variant.json rather than listed here: writing
# them into this file would publish the very holdings list the guard exists to keep private.
# So the guard covers whatever is actually in the personal data, and updates itself when that does.
#
# Matched on word boundaries, never as substrings — a short ticker is also a substring of ordinary
# English words, and a naive `in` check cries wolf on the source's own prose. Any regex metachar in
# a name is escaped, so a dotted symbol cannot match the same letters with something else between.
#
# STRUCTURAL_LEAKS needs no secret list: it recognises the *shape* of real position data, so it
# still fires on a fresh clone with no personal.variant.json present. Labels are worded so they do
# not match their own patterns, or scanning this file would report itself.
STRUCTURAL_LEAKS = [
    (re.compile(r"\d+\s*sh\s*[×x]\s*\$"), "a share-count note (count, 'sh', then a price)"),
    (re.compile(r"\bLong\s+\d+\s+contracts?\b"), "an options position note"),
]

_secret_re = None


# Row names common enough to carry no information — every build seeds some of these, so treating
# them as secrets would make the guard fire on its own demo data and train everyone to ignore it.
#
# This is a FIXED list on purpose. The obvious-looking alternative — "generic means it already
# appears in the source we're checking" — is circular: pasting a real ticker into the source would
# make that ticker count as generic and let itself through. The reference for what is safe must
# never be the file under test.
GENERIC_NAMES = {
    "401(k)", "403(b)", "457", "IRA", "HSA", "FSA", "Car", "Cash", "Crypto",
    "Mortgage", "Savings", "Checking", "Pension", "Bonds", "Home", "House",
}


def load_leak_terms(public=None):
    """Build the word-boundary matcher from the gitignored personal data, if it is present.

    `public` is accepted and ignored — see GENERIC_NAMES for why it must not be consulted.
    """
    global _secret_re
    path = os.path.join(HERE, PERSONAL_VARIANT)
    terms = set()
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            d = json.load(fh)
        for row in d.get("assets", []) + d.get("liabilities", []):
            name = (row.get("name") or "").strip()
            # single tokens only — a multi-word name is prose, matched by structure instead
            if not name or " " in name or len(name) < 2:
                continue
            if name not in GENERIC_NAMES:
                terms.add(name)
    _secret_re = (
        re.compile(r"(?<![A-Za-z0-9])(?:%s)(?![A-Za-z0-9])"
                   % "|".join(re.escape(t) for t in sorted(terms)))
        if terms else None
    )
    return sorted(terms)


def leaks(text):
    """Real-data giveaways found in text, deduped, in order of appearance."""
    seen = []
    if _secret_re is None:
        load_leak_terms()
    if _secret_re is not None:
        for m in _secret_re.finditer(text):
            if m.group(0) not in seen:
                seen.append(m.group(0))
    for pat, label in STRUCTURAL_LEAKS:
        if pat.search(text) and label not in seen:
            seen.append(label)
    return seen


def die(msg):
    sys.exit("build.py: " + msg)


# ---------------------------------------------------------------- source surgery

def replace_block(src, name, body, where):
    """Swap the contents of a /* @variant:begin name */ ... /* @variant:end name */ block."""
    pat = re.compile(
        r"(/\* @variant:begin %s \*/\n).*?(/\* @variant:end %s \*/)" % (name, name),
        re.S,
    )
    found = len(pat.findall(src))
    if found != 1:
        die("variant block %r matched %d times in %s (expected 1)" % (name, found, where))
    return pat.sub(lambda m: m.group(1) + body.rstrip("\n") + "\n" + m.group(2), src, count=1)


def replace_string(src, old, new, where):
    n = src.count(old)
    if n != 1:
        die("string matched %d times (expected 1) in %s:\n  %r" % (n, where, old[:110]))
    return src.replace(old, new, 1)


SCRIPT_RE = re.compile(r"<script>(.*?)</script>", re.S)


def script_hashes(html):
    return [
        "sha256-" + base64.b64encode(hashlib.sha256(m.encode("utf-8")).digest()).decode()
        for m in SCRIPT_RE.findall(html)
    ]


def rewrite_csp(html, where):
    """Recompute both inline-script hashes and write them into the CSP meta tag."""
    hashes = script_hashes(html)
    if len(hashes) != 2:
        die(
            "%s has %d attribute-less <script> blocks, expected 2. If it is 3, something in "
            "the file now spells out a script tag literally." % (where, len(hashes))
        )

    meta = re.search(r'<meta http-equiv="Content-Security-Policy" content="(.*?)">', html, re.S)
    if not meta:
        die("no CSP meta tag found in " + where)

    listed = re.findall(r"'sha256-[^']+'", meta.group(1))
    if len(listed) != 2:
        die("CSP in %s lists %d hashes, expected 2" % (where, len(listed)))

    body = meta.group(1)
    for old, new in zip(listed, hashes):
        body = body.replace(old, "'" + new + "'", 1)
    return html[: meta.start(1)] + body + html[meta.end(1):]


def build(src, variant, name):
    out = src
    for block, code in variant.get("blocks", {}).items():
        out = replace_block(out, block, code, name)
    for old, new in variant.get("strings", []):
        out = replace_string(out, old, new, name)
    out = BANNER.format(src=SOURCE) + out
    return rewrite_csp(out, name)


# ---------------------------------------------------------------- variant data

def storage_block(key, legacy):
    return (
        "// Each build gets its own key so opening one can never read or overwrite another's data —\n"
        "// on file:// most browsers treat every local file as a single origin. LEGACY_KEY is the\n"
        "// one-time migration path load() already walks; the personal build points it at the old key.\n"
        'const KEY="%s";\n'
        'const LEGACY_KEY="%s";' % (key, legacy)
    )


def seed_block(assets, liabilities, calendar, profile, onboarded, note):
    """Render a seed() whose shared fields track the demo's — only data differs."""
    def rows(items):
        if not items:
            return "[]"
        out = []
        for r in items:
            fields = ",".join(
                "%s:%s" % (k, json.dumps(v, ensure_ascii=False)) for k, v in r.items()
            )
            out.append("      {id:uid()," + fields + "}")
        return "[\n" + ",\n".join(out) + "\n    ]"

    return """// %s
function seed(){
  return {
    updated:today(),
    onboarded:%s,
    hintsDone:%s,
    profile:{name:%s,goal:"personal"},   // goal keys: see GOALS
    theme:"terminal",
    lang:"en",
    currency:"USD",
    fx:{rates:{USD:1},lastFetch:""},
    calendarOrder:["personal","live"],
    liveCalHeight:500,   // px height of the TradingView box — user-set via the corner grip
    autoRefresh:"off",   // off | stale | always — default off keeps page load request-free
    lastFetch:"",        // YYYY-MM-DD of the last fully successful macro fetch
    assets:%s,
    liabilities:%s,
    history:[],
    yields:[{date:"2026-08-20",y10:4.69,y20:5.05,y30:5.23}],
    inflation:[{date:"2026-07-31",cpi:3.2,note:"EXAMPLE — replace with latest print"}],
    calendar:%s,
    budget:seedBudget()
  };
}""" % (
        note,
        "true" if onboarded else "false",
        "true" if onboarded else "false",
        json.dumps(profile, ensure_ascii=False),
        rows(assets),
        rows(liabilities),
        rows(calendar),
    )


# The zeroed row template both non-demo builds ship. The row LIST lives only in the demo's
# seedBudget(); this mirrors its shape with every amount at 0.
BUDGET_TEMPLATE = """function seedBudget(){
  const inc=(name,cat,optional)=>({id:uid(),name,cat,amount:0,optional:!!optional,notes:""});
  const exp=(name,cat,kind,optional)=>({id:uid(),name,cat,amount:0,limit:0,kind,optional:!!optional,notes:""});
  return {
    income:[
      inc("Net monthly income","Salary (net)",false),
      inc("401(k) contribution","401(k) contribution",true),
      inc("Employer 401(k) match","Employer match",true),
      inc("Other income stream","Other income",true)
    ],
    expenses:[
      exp("Rent / mortgage","Housing","essential"),
      exp("Utilities","Utilities","essential"),
      exp("Groceries","Groceries","essential"),
      exp("Insurance","Insurance","essential"),
      exp("Transportation / fuel","Transportation","essential"),
      exp("Phone / internet","Phone / internet","essential"),
      exp("Debt payments","Debt payments","essential",true),
      exp("Eating out","Eating out","discretionary"),
      exp("Food delivery","Food delivery","discretionary"),
      exp("Subscriptions","Subscriptions","discretionary"),
      exp("Shopping","Shopping","discretionary"),
      exp("Entertainment","Entertainment","discretionary"),
      exp("Travel","Travel","discretionary",true)
    ],
    assumptions:{rate:7,years:30}
  };
}"""

# Calendar releases are reference data, not user data — every build keeps them.
RELEASES = [
    {"date": "2026-09-04", "event": "Nonfarm payrolls (Aug)", "imp": "High", "notes": "verify date"},
    {"date": "2026-09-10", "event": "CPI (Aug)", "imp": "High", "notes": "verify date"},
    {"date": "2026-09-16", "event": "FOMC rate decision", "imp": "High", "notes": "verify date"},
]


def demo_strings(title, watermark, key, calendar_note):
    """The demo's own wording on the left, this variant's on the right."""
    return [
        ("<title>SomiFinance — Demo</title>", "<title>%s</title>" % title),
        (
            '<div class="watermark">SomiFinance — Demo ©2026 mDemarco12</div>',
            '<div class="watermark">%s</div>' % watermark,
        ),
        (
            "under the key <code>somifinance.demo.v1</code>",
            "under the key <code>%s</code>" % key,
        ),
        (
            'localStorage["somifinance.demo.v1"] — every holding',
            'localStorage["%s"] — every holding' % key,
        ),
        (
            "Seeded with recurring US releases plus two example personal dates.",
            calendar_note,
        ),
    ]


USER = {
    "out": "SomiFinance.html",
    "blocks": {
        "storage": storage_block("somifinance.v1", "wealthdesk.v1"),
        "seedBudget": BUDGET_TEMPLATE,
        "seed": seed_block(
            assets=[],
            liabilities=[],
            calendar=RELEASES,
            profile="",
            onboarded=False,
            note=(
                "A first install starts with an empty ledger — the welcome screen and hint tour\n"
                "// walk the user through adding their first account. The calendar releases below are\n"
                "// reference data, not user data, so they stay."
            ),
        ),
    },
    "strings": demo_strings(
        title="SomiFinance",
        watermark="SomiFinance ©2026 mDemarco12",
        key="somifinance.v1",
        calendar_note="Seeded with recurring US releases. Add your own dates alongside them.",
    ),
}


def personal_variant():
    """Read the gitignored real-data variant, if it is present."""
    path = os.path.join(HERE, PERSONAL_VARIANT)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as fh:
        d = json.load(fh)
    return {
        "out": "SomiFinancePersonal.html",
        "blocks": {
            "storage": storage_block("somifinance.personal.v1", "somifinance.v1"),
            "seedBudget": BUDGET_TEMPLATE,
            "seed": seed_block(
                assets=d.get("assets", []),
                liabilities=d.get("liabilities", []),
                calendar=d.get("calendar", RELEASES),
                profile=d.get("name", ""),
                onboarded=True,
                note=(
                    "REAL DATA — generated from personal.variant.json, which is gitignored.\n"
                    "// Never copy this block back into SomiFinanceDemo.html."
                ),
            ),
        },
        "strings": demo_strings(
            title="SomiFinance — Personal",
            watermark="SomiFinance ©2026 mDemarco12",
            key="somifinance.personal.v1",
            calendar_note=d.get(
                "calendarNote",
                "Seeded with recurring US releases plus your own dates.",
            ),
        ),
        "tracked": False,
    }


# ---------------------------------------------------------------- entry point

def main():
    check = "--check" in sys.argv[1:]

    src_path = os.path.join(HERE, SOURCE)
    if not os.path.exists(src_path):
        die("%s not found — it is the source every build is projected from" % SOURCE)
    with open(src_path, encoding="utf-8") as fh:
        src = fh.read()

    # The source is hand-edited, so its own hash goes stale too. Fix it in place first.
    fixed = rewrite_csp(src, SOURCE)
    if fixed != src:
        if check:
            die("%s has a stale CSP hash — run `python3 build.py`" % SOURCE)
        with open(src_path, "w", encoding="utf-8") as fh:
            fh.write(fixed)
        print("  %-28s CSP hash refreshed" % SOURCE)
        src = fixed
    terms = load_leak_terms()
    print("  %-28s leak guard: %d private term%s + %d structural"
          % ("", len(terms), "" if len(terms) == 1 else "s", len(STRUCTURAL_LEAKS)))
    found = leaks(src)
    if found:
        die("%s contains real data (%s) — it must never enter a tracked build"
            % (SOURCE, ", ".join(found)))

    variants = [USER]
    personal = personal_variant()
    if personal:
        variants.append(personal)
    else:
        print("  %-28s skipped (%s not present)" % ("SomiFinancePersonal.html", PERSONAL_VARIANT))

    stale = []
    for v in variants:
        out = build(src, v, v["out"])

        if v.get("tracked", True):
            found = leaks(out)
            if found:
                die("%s contains real data (%s) — refusing to write a tracked build"
                    % (v["out"], ", ".join(found)))

        # a generated file must agree with its own CSP, or it renders blank
        listed = re.findall(r"'(sha256-[^']+)'", out)
        if script_hashes(out) != listed:
            die("internal error: %s CSP does not match its own scripts" % v["out"])

        path = os.path.join(HERE, v["out"])
        current = None
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                current = fh.read()
        if current == out:
            print("  %-28s up to date" % v["out"])
            continue
        if check:
            stale.append(v["out"])
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(out)
        print("  %-28s written (%d KB)" % (v["out"], len(out.encode("utf-8")) // 1024))

    if check and stale:
        die("stale: %s — run `python3 build.py`" % ", ".join(stale))
    if check:
        print("  all builds up to date")


if __name__ == "__main__":
    main()
