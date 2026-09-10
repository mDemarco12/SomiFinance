# Choosing a model for the ✦ Assistant

*Already set up? This page helps you pick a better model than the `qwen3.5:4b` the setup guides
install. If you haven't installed Ollama yet, start with **[macOS & Ubuntu](ASSISTANT-SETUP.md)**
or **[Windows](ASSISTANT-SETUP-WINDOWS.md)** and come back here later.*

---

## What the assistant actually asks a model to do

This matters more than any benchmark, because it sets how much model you need.

The assistant receives a **short summary** of your figures — category totals, net worth, cash flow,
savings rate, goal progress. Not your ledger, not individual holdings, not your notes. It then
answers questions about that summary in plain English.

That's a small job. The model isn't crunching your numbers (SomiFinance computes those itself,
in the page, deterministically) and it isn't reading a long document. It's reading maybe a page of
figures and talking about them.

**The practical consequence: a small model is genuinely fine here.** The difference between a 4B
model and a 30B model on this task is the difference between a serviceable answer and a slightly
better-organised one — not between wrong and right. Don't feel you need to download something huge.

Where model size *does* show up: how well it holds several of your goals in mind at once, whether it
notices tensions between them, and how much its advice reflects your actual numbers rather than
generic personal-finance boilerplate.

---

## Quick pick

| Your computer's memory (RAM) | Model | Download | Memory while running |
|---|---|---|---|
| **8 GB** | `qwen3.5:4b` — what the setup guides install | 3.4 GB | ~5–6 GB |
| **8 GB, with a lot else open** | `granite4.2:3b` | ~2 GB | ~3–4 GB |
| **16 GB** ← most people | `qwen3.5:9b` | 6.6 GB | ~9–11 GB |
| **32 GB or more** | `qwen3.5:27b` | 17 GB | ~19–21 GB |

If you followed a setup guide you already have the first one. **On a 16 GB machine, moving up to
`qwen3.5:9b` is the single upgrade worth making** — it's the same family, so nothing about how you
use the assistant changes.

The running-size figures are estimates for a typical conversation, not hard limits.

If you're not sure how much memory you have:

- **Mac:** open the Apple menu in the top-left corner → **About This Mac**. Look for "Memory".
- **Windows:** Ctrl+Shift+Esc → Performance tab → Memory.
- **Ubuntu:** run `free -h` in a terminal and read the "total" column.

Install any of them the same way — the model's name, a colon, then its size:

```
ollama pull <modelName:parameterSize>
```

So for the 16 GB pick:

```
ollama pull qwen3.5:9b
```

Then click the model name at the top of the ✦ panel in SomiFinance to switch to it.

---

## Download size is not the number that matters

This trips up almost everyone, so it's worth being explicit.

A model's **download size** is how much disk space it takes. Its **running size** is how much memory
it needs while it's actually answering — always larger, because the model plus your conversation
have to be held in RAM at once.

A 5 GB model on an 8 GB machine will technically load. It will also be competing with your browser,
your operating system, and everything else you have open, and answers will crawl. Use the table
above, which is based on running size, not download size.

**A related trap:** some models advertise something like "30B total, 3B active." Those are
mixture-of-experts models, and the small number is how many parameters are used per word generated —
it makes them *faster*, not smaller. All the weights still have to be in memory. Read the total, not
the active count.

---

## The models in more detail

### `qwen3.5:4b` — where you start

3.4 GB down, workable on 8 GB of RAM. This is what both setup guides install, so unless you've
changed it, this is the model the assistant is using right now.

For the assistant's actual job — reading a page of your figures and talking about them — it is
genuinely adequate. It tracks a couple of goals at once and keeps its answers tied to your numbers.
Where it thins out is holding *several* goals in mind simultaneously and noticing tensions between
them; that's what the 9b buys you.

Apache 2.0, and a thinking-capable model that SomiFinance runs with thinking switched off, so you
get answers rather than paragraphs of the model reasoning out loud.

### `granite4.2:3b` — the light option

IBM's small model, Apache 2.0 licensed. Roughly 2 GB down, comfortable on 8 GB of RAM.

It will answer questions about where your money is going and how your savings rate looks, and it'll
do it quickly. What you'll notice missing is depth on the harder questions — ask it how your
spending pattern affects a 10-year goal and you'll get sensible-sounding general advice rather than
something anchored in your specific numbers.

Good choice if your machine is modest, or if you mainly want quick reads on your budget rather than
planning conversations.

### `qwen3.5:9b` — the upgrade worth making

6.6 GB down, comfortable on 16 GB of RAM. This is also the tag you get if you run `ollama pull
qwen3.5` with no size, since it's the family default.

If your machine has 16 GB and you only ever change one thing on this page, make it this.

It's the sweet spot for the assistant's workload. It handles multi-part questions ("I want to grow
the business *and* keep six months of runway — how am I doing?") without losing the thread, and its
answers stay tied to the figures it was given rather than drifting into generic advice.

It also has a very large context window (256K), which matters less than it sounds like it should
here — the assistant only ever sends a short summary — but it means a long back-and-forth
conversation won't start forgetting its own earlier answers.

### `qwen3.5:27b` — if you have the machine for it

17 GB down, and you want 32 GB of RAM. On a 24 GB machine it loads but leaves you nothing to work
with alongside it.

Worth it only if you use the assistant for real planning conversations rather than quick questions.
For "where did my money go this month," it's slower for no visible gain.

### Others worth knowing about

- **`gemma4:e4b`** — Google's small model, another alternative on limited hardware. Note it ships
  under Google's own licence terms rather than Apache 2.0.
- **`qwen3:4b`** — the previous generation. Still perfectly usable if you already have it, but
  there's no reason to install it now; `qwen3.5:4b` is the same size and simply newer.

> **Note:** the `qwen3.5` family also has a `:cloud` tag and larger sizes (35b, 122b). Those either
> run on Ollama's servers or need far more hardware than a laptop. The assistant won't connect to a
> cloud tag — see below.

---

## Licensing, if you care

`granite4.2` is Apache 2.0, which is about as permissive as it gets — no usage restrictions worth
worrying about for personal use. Gemma models ship under Google's own terms, which carry use
restrictions. Qwen models are generally Apache 2.0 but check the specific tag.

For running a model on your own machine to talk about your own budget, none of this is likely to
constrain you. It matters if you're forking SomiFinance and redistributing something.

---

## Cloud models won't work here

If you browse Ollama's site you'll see models like `kimi-k3` and other very large names. Those are
**cloud** models — they run on Ollama's servers, are billed per token, and require a subscription.
They carry a `:cloud` tag.

The ✦ assistant only talks to `127.0.0.1` — your own machine — and enforces that in code. A cloud
model won't connect, by design. That's the whole point of the feature: your figures don't leave your
computer.

---

## Switching models

You can have several installed at once and switch between them freely.

```
ollama list                    # see what you have, with real sizes
ollama pull qwen3.5:9b         # add one
ollama rm qwen3.5:4b           # remove one to reclaim disk space
```

In SomiFinance, click the model's name at the top of the ✦ panel to pick a different one. Your
conversation history is kept when you switch.

If you remove a model that SomiFinance was using, the panel notices and asks you to choose again
rather than silently picking something else.

---

## A note on trusting the answers

This is a small AI model running on your laptop. It can be confidently, fluently wrong, and a bigger
model is *less* often wrong rather than *never* wrong.

It sees a summary of what you typed in. It doesn't know the markets, your tax situation, or anything
you didn't enter. Nothing it says is financial advice.

The numbers in SomiFinance itself — your net worth, your savings rate, the future-spend projection —
are computed by the page, not by the model, so those are as accurate as the figures you entered. The
model is only ever interpreting them.
