#!/usr/bin/env python3
"""SomiFinance quote helper — last prices from Yahoo Finance, served to the page on loopback.

    python3 quotes.py              listen on http://127.0.0.1:8765
    python3 quotes.py --port 9000  use another port (then set the same address in ⚙ → Stock quotes)

Why this exists: Yahoo's endpoints send no CORS headers, so a browser page cannot call them.
This script runs on YOUR machine, asks Yahoo, and hands SomiFinance a small JSON answer. The
page's Content-Security-Policy already allows loopback, so no remote host had to be added to it.

What leaves your machine: the ticker symbols in the request, sent to Yahoo. Nothing else — the
page never tells this script a share count, a value or a note, so it has none to send.

    GET /quote?symbols=AAA,BBB
    -> {"quotes":[{"symbol","name","price","currency","asOf"}],"errors":[{"symbol","reason"}]}

Standard library only. Yahoo has no official API: this endpoint is unofficial and can change or
rate-limit without notice. If prices stop arriving, this file is the one place to fix.

It is deliberately not a proxy. It answers one path, builds the upstream URL itself from symbols
it has validated, and listens on 127.0.0.1 only.
"""

import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
DEFAULT_PORT = 8765
MAX_SYMBOLS = 50                                   # the page enforces the same cap (QUOTE_MAX)
SYMBOL_RE = re.compile(r"^[A-Z0-9.\-^=]{1,12}$")   # the page's TICKER_RE
UPSTREAM = "https://query1.finance.yahoo.com/v8/finance/chart/%s?range=1d&interval=1d"
UA = "Mozilla/5.0 (SomiFinance quote helper)"
TIMEOUT = 8

# A page opened by double-clicking the file has the origin "null". Loopback origins cover anyone
# serving the file locally. Any other origin gets no CORS header, so a website you happen to
# visit cannot read answers from this script.
ORIGIN_OK = re.compile(r"^(null|https?://(127\.0\.0\.1|localhost|\[::1\])(:\d{1,5})?)$")


def fetch_one(symbol):
    """One symbol -> ("ok", quote) or ("err", reason). Never raises."""
    url = UPSTREAM % urllib.parse.quote(symbol, safe="")
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as res:
            data = json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return "err", "not found" if e.code == 404 else "Yahoo answered %d" % e.code
    except Exception as e:  # network down, timeout, bad JSON
        return "err", "no answer from Yahoo (%s)" % type(e).__name__
    try:
        meta = data["chart"]["result"][0]["meta"]
        price = float(meta["regularMarketPrice"])
    except (KeyError, IndexError, TypeError, ValueError):
        return "err", "no price in Yahoo's answer"
    if not price > 0:
        return "err", "no price in Yahoo's answer"
    # The date the quote is as of, on the exchange's own calendar — not when we asked.
    try:
        when = datetime.fromtimestamp(int(meta["regularMarketTime"]), timezone.utc)
        when += timedelta(seconds=int(meta.get("gmtoffset") or 0))
        as_of = when.strftime("%Y-%m-%d")
    except (KeyError, TypeError, ValueError, OverflowError, OSError):
        as_of = ""
    return "ok", {
        "symbol": symbol,
        "name": str(meta.get("longName") or meta.get("shortName") or "")[:80],
        "price": price,
        "currency": str(meta.get("currency") or "USD")[:8],
        "asOf": as_of,
    }


def lookup(symbols):
    quotes, errors = [], []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for symbol, (kind, body) in zip(symbols, pool.map(fetch_one, symbols)):
            if kind == "ok":
                quotes.append(body)
            else:
                errors.append({"symbol": symbol, "reason": body})
    return {"quotes": quotes, "errors": errors}


class Handler(BaseHTTPRequestHandler):
    server_version = "SomiFinanceQuotes/1"

    def _send(self, status, body):
        raw = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        origin = self.headers.get("Origin")
        if origin and ORIGIN_OK.match(origin):
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        # A Host that is not loopback means the request was aimed here by a hostile DNS name.
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0]
        if host not in ("127.0.0.1", "localhost", "[::1]"):
            return self._send(403, {"error": "loopback only"})
        url = urllib.parse.urlsplit(self.path)
        if url.path != "/quote":
            return self._send(404, {"error": "only /quote?symbols=… is served"})
        raw = urllib.parse.parse_qs(url.query).get("symbols", [""])[0]
        symbols = []
        for s in raw.split(","):
            s = s.strip().upper()
            if s and s not in symbols:
                symbols.append(s)
        if not symbols or len(symbols) > MAX_SYMBOLS or not all(SYMBOL_RE.match(s) for s in symbols):
            return self._send(400, {"error": "pass 1-%d valid symbols" % MAX_SYMBOLS})
        self._send(200, lookup(symbols))

    def log_message(self, fmt, *args):
        # Symbols are your holdings list. Log that a request happened, not what it asked for.
        sys.stderr.write("%s  quote request\n" % self.log_date_time_string())


def main():
    port = DEFAULT_PORT
    args = sys.argv[1:]
    if args[:1] == ["--port"] and len(args) == 2 and args[1].isdigit():
        port = int(args[1])
    elif args:
        sys.exit(__doc__)
    try:
        server = ThreadingHTTPServer((HOST, port), Handler)
    except OSError as e:
        sys.exit("quotes.py: can't listen on %s:%d (%s) — try --port" % (HOST, port, e))
    print("SomiFinance quote helper on http://%s:%d — Ctrl+C to stop." % (HOST, port))
    print("Only ticker symbols are sent to Yahoo Finance.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
