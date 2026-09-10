# Setting up the ✦ Assistant — Windows

*Using a Mac or Ubuntu? Follow [ASSISTANT-SETUP.md](ASSISTANT-SETUP.md) instead.*

This guide takes you from having never heard of Ollama to asking the SomiFinance assistant a
question about your own finances. You do not need to know how to code. Every command you need is
written out for you to copy and paste.

---

## What you're about to set up

SomiFinance's ✦ Assistant is an AI that reads a summary of the figures you've entered and answers
questions about them in plain English — "how am I doing against my goals?", "where is most of my
money going each month?"

It runs **on your own computer**. To make that possible you install one free extra program called
Ollama, which does the actual thinking.

**What this means in practice:**

- **It's free.** No account, no sign-up, no credit card, no API key. Nothing to subscribe to.
- **Nothing you type leaves your computer.** Your figures are never uploaded anywhere.
- **It works offline** once it's set up.
- **It takes about 15 minutes**, most of which is waiting for one download to finish.

**What it costs you:** about 5 GB of hard drive space, and your computer works a little harder while
it's answering (you may hear the fan).

---

## Before you start

You'll need:

- **Windows 10 (version 22H2 or newer) or Windows 11**, Home or Pro
- **About 5 GB of free space** on your hard drive
- **8 GB of memory (RAM)** to run comfortably — 16 GB is better, but 8 GB works
- An internet connection for the setup (afterwards it works offline)

Good news: **you don't need administrator rights.** Ollama installs into your own user account.

Not sure which Windows you have? Press <kbd>Windows</kbd> + <kbd>R</kbd>, type `winver`, press
<kbd>Enter</kbd>.

---

## Three words explained first

You'll see these three words throughout. Here's what they mean, in plain English:

**Ollama** — a free program that runs AI models on your own computer. Think of it as the engine.
SomiFinance is the dashboard; Ollama is what's under the hood. It runs quietly in the background.

**Model** — the AI's "brain". It's a large file you download once. We'll use one called
`qwen3.5:4b`, which is about 3.4 GB. Different models are better at different things, a bit like
different apps.

**Command Prompt** — a plain window where you type commands instead of clicking buttons. It looks
intimidating, but you'll only ever paste in text that this guide gives you. Nothing here can damage
your computer, and you can close the window at any time.

---

## Step 1 — Install Ollama

1. Go to **<https://ollama.com/download>** in your web browser.
2. Click the **Download for Windows** button. A file called **OllamaSetup.exe** will download.
3. Open the downloaded file — it's usually in your **Downloads** folder, or you can click it in
   your browser's downloads bar.
4. Windows may show a blue **"Windows protected your PC"** box. If it does, click **More info**,
   then **Run anyway**. (This appears for many newly-downloaded programs.)
5. The installer is a single page. Click **Install** and wait — it usually takes under a minute.

**How to tell it worked:** Ollama starts automatically and a **llama icon appears in your system
tray**, at the bottom-right of your screen near the clock. You may need to click the small **^**
arrow there to see hidden icons.

**You may also see a Windows Firewall prompt** asking whether to allow Ollama. Allowing it on
**private networks** is expected and is what lets SomiFinance reach it on your own machine.

---

## Step 2 — Open a Command Prompt

> ### ⚠️ It must be a *new* window
>
> If you already had a Command Prompt open before installing Ollama, **close it**. Windows only
> tells programs about newly installed commands when a window opens, so an older window won't
> recognise `ollama` and you'll get a confusing error.

1. Click the **Start** button.
2. Type `cmd`.
3. Click **Command Prompt** in the results.

A black window opens with a blinking cursor. That's it.

To run any command in this guide: copy it, click once inside the window, right-click to paste (or
press <kbd>Ctrl</kbd> + <kbd>V</kbd>), and press <kbd>Enter</kbd>.

---

## Step 3 — Check that Ollama is working

Paste this and press <kbd>Enter</kbd>:

```
ollama --version
```

**What success looks like:** it prints a version number, something like
`ollama version is 0.12.3`. The exact number doesn't matter.

**If it says `'ollama' is not recognized…`:** almost always this window was open before you
installed. Close it completely, open a new Command Prompt (Step 2), and try again. If it still
fails, go back to Step 1.

---

## Step 4 — Download the AI model

This is the big download — about 3.4 GB, so it takes a few minutes on a normal connection. You only
ever do this once.

The command always takes the same shape: the model's name, a colon, then its size.

```
ollama pull <modelName:parameterSize>
```

If you don't have a preference, use the one this guide recommends. Paste this and press
<kbd>Enter</kbd>:

```
ollama pull qwen3.5:4b
```

You'll see progress bars filling up as it downloads. It's finished when it prints `success` and
gives you back a normal cursor.

**What success looks like:** run this to see what you now have installed:

```
ollama list
```

It should list `qwen3.5:4b` along with its size.

> **Optional — other models.** `qwen3.5:4b` is the recommended default and what the rest of this
> guide assumes. The `4b` is the size, and the same model comes in others you can drop straight into
> the command above: `qwen3.5:2b` (2.7 GB) is lighter if you're short on memory, and `qwen3.5:9b`
> (6.6 GB) gives noticeably better answers if your computer has 16 GB of RAM. `gemma3:4b` is a
> different model at a similar size — note it uses the Gemma Terms licence rather than Apache 2.0.
>
> For a fuller comparison — which model suits your machine, and why running size matters more than
> download size — see **[Choosing a model](MODELS.md)**.

---

## Step 5 — Let SomiFinance talk to Ollama

**Why this step exists.** For safety, Ollama ignores web pages by default unless it's been told to
trust them. SomiFinance is a file you open directly from your own hard drive, and that's one of the
kinds of page Ollama doesn't recognise. This step grants that one permission. Without it, everything
is installed correctly but the assistant will say it can't connect.

**This step is all clicking — no commands.** And unlike the equivalent step on a Mac, **it stays set
permanently.** You only do this once.

1. **Quit Ollama first.** Find the llama icon in your system tray (bottom-right, near the clock —
   you may need to click the **^** arrow to see it). Right-click it and choose **Quit Ollama**.

2. **Open the environment variables screen:**
   - **Windows 11:** click **Start**, type `environment variables`, and choose **Edit environment
     variables for your account**.
   - **Windows 10:** click **Start**, type `environment variables`, and choose **Edit environment
     variables for your account** from the Control Panel results.

3. A window titled **Environment Variables** opens. In the **top box** — the one labelled *User
   variables for [your name]* — click **New…**.

4. Fill in the two fields exactly:
   - **Variable name:** `OLLAMA_ORIGINS`
   - **Variable value:** `nul*`

5. Click **OK** to close the New Variable box, then **OK** again to close the Environment Variables
   window.

6. **Start Ollama again** from the Start menu.

**How to tell it worked:** you'll find out in Step 6 — if the assistant connects, this worked.

### If `nul*` doesn't work

`nul*` is the narrow setting: it lets in only pages opened from a file on this computer. On some
versions of Ollama it may not take effect. If you've completed Step 6 below and the assistant still
says *"Ollama is running, but it refused this page"*, repeat the steps above and change the
**Variable value** to a single asterisk:

```
*
```

Quit and restart Ollama again afterwards.

**Be aware of the difference.** `nul*` allows only local files. `*` allows **any website you visit**
to talk to Ollama on your computer — such a site could see which models you have and use your
machine to run them. It cannot see your SomiFinance data, which never leaves the page. Use `*` only
if `nul*` didn't work, and consider switching back later.

> **Never set this to the bare word `null`.** Ollama refuses to start at all if you do, which turns
> a small problem into a much larger one. The `*` on the end of `nul*` is what makes it valid.

---

## Step 6 — Connect it in SomiFinance

1. Open **SomiFinance.html** in your browser, the way you normally do.
2. Click the **✦** button in the **bottom-right corner** of the page.
3. A panel opens with a notice explaining what the assistant is and what it can't do. Read it and
   click **I understand**. You'll only see this once.
4. You'll now see **Connect the assistant**. Click **Connect**.
5. After a moment you'll see **Choose a model**, with a list of what you installed. Click
   **qwen3.5:4b**.

**What success looks like:** the message box at the bottom of the panel becomes typeable, and the
model's name appears next to "✦ Assistant" at the top of the panel.

If it doesn't connect, the panel tells you what went wrong and shows the fix. See
[If something goes wrong](#if-something-goes-wrong) below.

---

## Step 7 — Ask it something

Type a question into the box at the bottom of the panel and press <kbd>Enter</kbd>. Try:

- *How am I doing against my goals?*
- *Where is most of my spending going each month?*
- *Is my savings rate reasonable?*

**The first answer is slow** — usually 10 to 30 seconds — because the model is being loaded into
memory. Answers after that come much faster. You'll see the reply appear a few words at a time.

**To change model later**, click the model's name at the top of the panel. If you have the memory
for a bigger one, **[Choosing a model](MODELS.md)** walks through the options.

**A word of caution:** this is a small AI model running on your computer. It can be confidently
wrong. It sees only a summary of your figures — not the markets, not your tax situation — and
nothing it says is financial advice. Treat it as a thinking aid, not an adviser.

---

## If something goes wrong

The assistant tells you what's wrong in its own words. Find the message you're seeing:

| What you see | What it means | What to do |
|---|---|---|
| **"Nothing answered at http://127.0.0.1:11434."** | Ollama isn't running. | Look for the llama icon in your system tray (click the **^** arrow to see hidden icons). If it's missing, start Ollama from the Start menu. |
| **"Ollama is running, but it refused this page."** | Ollama is installed and working, but hasn't been given permission for this page. | You've missed Step 5, or didn't restart Ollama afterwards. Redo Step 5 — including quitting and restarting Ollama. If you've already done it, try the `*` fallback. |
| **"Ollama didn't answer in time."** | It's probably still loading the model. | Wait a few seconds and click **Try again**. |
| **"No models installed"** | Ollama is connected but has no model. | Go back to Step 4 and run `ollama pull qwen3.5:4b`. |
| **"Model "…" isn't installed."** | The model you'd chosen has been removed. | Click the model name at the top of the panel and pick another, or reinstall it with `ollama pull`. |
| **"That isn't a loopback address…"** | The address under **Change address** was edited to something that isn't your own computer. | Open **Change address** in the panel and set it back to `http://127.0.0.1:11434`. |
| **`'ollama' is not recognized…`** | The Command Prompt window was open before Ollama was installed. | Close it completely, open a new one (Step 2), and try again. |

### One setting that looks like the answer but isn't

Ollama's own Settings has a switch called **"Expose Ollama to the network"**. It sounds exactly like
what you want. **It isn't, and turning it on will not fix this.**

That switch controls whether *other devices on your wi-fi* can reach Ollama. What you need is
permission for a *web page* to reach it, which is a different setting entirely — the one in Step 5.
Leaving the network switch off is the safer choice anyway.

### Double-checking the variable was saved

If Step 5 doesn't seem to have taken effect, confirm Windows really stored it. Open a **new**
Command Prompt and run:

```
echo %OLLAMA_ORIGINS%
```

It should print `nul*`. If it prints `%OLLAMA_ORIGINS%` instead, the variable wasn't saved — go back
through Step 5, making sure you clicked **OK** on both windows.

---

## What is and isn't shared

- **Nothing goes to the internet.** The assistant only ever talks to Ollama on your own computer.
- **It receives a summary, not your ledger.** Category totals, your net worth, cash flow, savings
  rate and goal progress. **The names of individual accounts and holdings, and any notes you've
  written, are never sent** — the only names included are your savings goals', so it can refer to
  them.
- **It cannot change anything.** The assistant can read and suggest; it can't edit a single figure.
- **Your conversation is saved in your browser**, alongside the rest of your SomiFinance data, and
  is included in Export files. Clear it any time with the **⌫** button at the top of the panel.

---

## Turning it off or removing it

**Stop using the assistant:** close the panel. It does nothing unless you open it.

**Clear the conversation:** click **⌫** at the top of the assistant panel.

**Remove the model** to reclaim the disk space:

```
ollama rm qwen3.5:4b
```

**Uninstall Ollama entirely:** open **Settings → Apps → Installed apps**, find **Ollama**, and
choose **Uninstall**. To also remove downloaded models, delete the `.ollama` folder in your user
folder (`C:\Users\YourName\.ollama`).

**Remove the setting from Step 5:** return to the Environment Variables screen, select
`OLLAMA_ORIGINS` in the top box, and click **Delete**.

---

## Still stuck?

- Ollama's own documentation: <https://docs.ollama.com>
- SomiFinance issues: <https://github.com/mDemarco12/SomiFinance/issues>

When asking for help, it's useful to include what the assistant panel says, and the output of
`ollama --version` and `ollama list`.
