# Setting up the ✦ Assistant — macOS & Ubuntu

*Using Windows? Follow [ASSISTANT-SETUP-WINDOWS.md](ASSISTANT-SETUP-WINDOWS.md) instead.*

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

**What it costs you:** about 4 GB of hard drive space, and your computer works a little harder while
it's answering (you may hear the fan).

---

## Before you start

You'll need:

- **A Mac running macOS 14 (Sonoma) or newer**, or **a computer running Ubuntu**
- **About 4 GB of free space** on your hard drive
- **8 GB of memory (RAM)** to run comfortably — 16 GB is better, but 8 GB works
- An internet connection for the setup (afterwards it works offline)

Not sure which macOS you have? Click the **Apple menu** in the top-left corner of your screen →
**About This Mac**. The version number is near the top.

---

## Three words explained first

You'll see these three words throughout. Here's what they mean, in plain English:

**Ollama** — a free program that runs AI models on your own computer. Think of it as the engine.
SomiFinance is the dashboard; Ollama is what's under the hood. It runs quietly in the background.

**Model** — the AI's "brain". It's a large file you download once. We'll use one called
`qwen3:4b`, which is about 2.5 GB. Different models are better at different things, a bit like
different apps.

**Terminal** — a plain window where you type commands instead of clicking buttons. It looks
intimidating, but you'll only ever paste in text that this guide gives you. Nothing here can damage
your computer, and you can close the window at any time.

---

## Step 1 — Install Ollama

### On a Mac

1. Go to **<https://ollama.com/download>** in your web browser.
2. Click the **Download for macOS** button. A file ending in `.dmg` will download.
3. Open the downloaded file (it's usually in your **Downloads** folder, or click it in your
   browser's downloads bar).
4. A window opens showing the Ollama icon. **Drag the Ollama icon onto the Applications folder**
   shown next to it.
5. Open your **Applications** folder and **double-click Ollama**.
6. macOS will ask if you're sure you want to open an app downloaded from the internet. Click
   **Open**.
7. Ollama may ask permission to install a command line helper. Allow it.

**How to tell it worked:** a small **llama icon appears in your menu bar**, along the top-right of
your screen near the clock. Ollama is now running quietly in the background. It will start
automatically each time you turn on your Mac.

> **Prefer the terminal?** If you're comfortable with it, you can skip all of the above and run this
> single command instead (see Step 2 for how to open a terminal):
>
> ```
> curl -fsSL https://ollama.com/install.sh | sh
> ```

### On Ubuntu

1. Open a terminal by pressing <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>T</kbd>.
2. Copy the line below, paste it into the terminal window, and press <kbd>Enter</kbd>:

```
curl -fsSL https://ollama.com/install.sh | sh
```

3. You'll be asked for your password. Type it and press <kbd>Enter</kbd> — **the letters won't
   appear on screen as you type**, which is normal, not a fault.
4. Wait for it to finish. It prints progress as it goes.

**How to tell it worked:** the last lines mention that the Ollama service has been installed and
started. Ollama now runs in the background and starts automatically when you turn your computer on.

---

## Step 2 — Open a terminal

You'll need a terminal window for the next few steps (Steps 3 through 5).

**On a Mac:** press <kbd>Command</kbd> + <kbd>Space</kbd> to open Spotlight search, type
`Terminal`, and press <kbd>Enter</kbd>.

**On Ubuntu:** press <kbd>Ctrl</kbd> + <kbd>Alt</kbd> + <kbd>T</kbd>.

A window opens with some text and a blinking cursor. That's it — that's a terminal. Leave it open
for the next few steps.

To run any command in this guide: copy it, click once inside the terminal window, paste
(<kbd>Command</kbd> + <kbd>V</kbd> on Mac, <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>V</kbd> on
Ubuntu), and press <kbd>Enter</kbd>.

---

## Step 3 — Check that Ollama is working

Paste this into the terminal and press <kbd>Enter</kbd>:

```
ollama --version
```

**What success looks like:** it prints a version number, something like
`ollama version is 0.12.3`. The exact number doesn't matter.

**If it says `command not found`:** Ollama either isn't installed yet, or this terminal window was
already open before you installed it. Close the terminal window completely, open a fresh one, and
try again. If it still fails, go back to Step 1.

---

## Step 4 — Download the AI model

This is the big download — about 2.5 GB, so it takes a few minutes on a normal connection. You only
ever do this once.

Paste this and press <kbd>Enter</kbd>:

```
ollama pull qwen3:4b
```

You'll see progress bars filling up as it downloads. It's finished when it prints `success` and
gives you back a normal cursor.

**What success looks like:** run this command to see what you now have installed:

```
ollama list
```

It should list `qwen3:4b` along with its size.

> **Optional — other models.** `qwen3:4b` is the recommended default and what the rest of this guide
> assumes. If you're short on memory, `gemma3:4b` is lighter (note it uses the Gemma Terms licence
> rather than Apache 2.0). If you have around 8 GB of memory free and want better answers,
> `qwen3:8b` is noticeably stronger. Install either the same way, swapping the name in the command
> above.

---

## Step 5 — Let SomiFinance talk to Ollama

**Why this step exists.** For safety, Ollama ignores web pages by default unless it's been told to
trust them. SomiFinance is a file you open directly from your own hard drive, and that's one of the
kinds of page Ollama doesn't recognise. This step grants that one permission. Without it, everything
is installed correctly but the assistant will say it can't connect.

### On a Mac

Paste this into the terminal and press <kbd>Enter</kbd>:

```
launchctl setenv OLLAMA_ORIGINS "nul*"
```

Nothing visible happens — that's correct, this command doesn't print anything.

Then **restart Ollama so it picks up the change**:

1. Click the **llama icon** in your menu bar (top-right of the screen).
2. Choose **Quit Ollama**.
3. Open **Ollama** again from your Applications folder.

> ### ⚠️ Important: this resets when you restart your Mac
>
> The command above lasts until you shut down or restart. After a restart, the assistant will stop
> connecting and you'd need to run it again.
>
> **To make it permanent**, paste this whole block into the terminal and press <kbd>Enter</kbd>. It
> creates a small settings file that reapplies the permission automatically every time you log in:
>
> ```
> mkdir -p ~/Library/LaunchAgents && cat > ~/Library/LaunchAgents/com.somifinance.ollamaorigins.plist << 'EOF'
> <?xml version="1.0" encoding="UTF-8"?>
> <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
> <plist version="1.0">
> <dict>
>   <key>Label</key><string>com.somifinance.ollamaorigins</string>
>   <key>ProgramArguments</key>
>   <array>
>     <string>/bin/launchctl</string>
>     <string>setenv</string>
>     <string>OLLAMA_ORIGINS</string>
>     <string>nul*</string>
>   </array>
>   <key>RunAtLoad</key><true/>
> </dict>
> </plist>
> EOF
> ```
>
> To undo it later, delete that file:
>
> ```
> rm ~/Library/LaunchAgents/com.somifinance.ollamaorigins.plist
> ```

### On Ubuntu

Ollama runs as a background service on Ubuntu, so the setting goes in a small configuration file.
Paste these three commands **one at a time**, pressing <kbd>Enter</kbd> after each. You'll be asked
for your password on the first one.

```
sudo mkdir -p /etc/systemd/system/ollama.service.d
```

```
printf '[Service]\nEnvironment="OLLAMA_ORIGINS=nul*"\n' | sudo tee /etc/systemd/system/ollama.service.d/somifinance.conf
```

```
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

The middle command prints back the two lines it wrote, which is how you know it worked. Unlike the
Mac version, this setting **survives restarts** — you only do it once.

To check Ollama is running afterwards:

```
systemctl status ollama
```

Look for the word **active (running)** in green. Press <kbd>q</kbd> to exit that view.

### If `nul*` doesn't work

`nul*` is the narrow setting: it lets in only pages opened from a file on this computer. On some
versions of Ollama it may not take effect. If you've completed Step 6 below and the assistant still
says *"Ollama is running, but it refused this page"*, use the broader setting instead:

**Mac:**

```
launchctl setenv OLLAMA_ORIGINS "*"
```

**Ubuntu:**

```
printf '[Service]\nEnvironment="OLLAMA_ORIGINS=*"\n' | sudo tee /etc/systemd/system/ollama.service.d/somifinance.conf
```

```
sudo systemctl daemon-reload && sudo systemctl restart ollama
```

Restart Ollama afterwards, the same way as before.

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
   **qwen3:4b**.

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

**To change model later**, click the model's name at the top of the panel.

**A word of caution:** this is a small AI model running on your computer. It can be confidently
wrong. It sees only a summary of your figures — not the markets, not your tax situation — and
nothing it says is financial advice. Treat it as a thinking aid, not an adviser.

---

## If something goes wrong

The assistant tells you what's wrong in its own words. Find the message you're seeing:

| What you see | What it means | What to do |
|---|---|---|
| **"Nothing answered at http://127.0.0.1:11434."** | Ollama isn't running. | Check for the llama icon in your menu bar (Mac). If it's missing, open Ollama from Applications. On Ubuntu, run `systemctl status ollama`. |
| **"Ollama is running, but it refused this page."** | Ollama is installed and working, but hasn't been given permission for this page. | You've missed Step 5, or didn't restart Ollama afterwards. Redo Step 5. If you've already done it, try the `*` fallback. |
| **It worked yesterday, and today says it refused the page** | On a Mac, the Step 5 setting is cleared by a restart. | Run the Step 5 command again, or set up the permanent version in the box in Step 5. |
| **"Ollama didn't answer in time."** | It's probably still loading the model. | Wait a few seconds and click **Try again**. |
| **"No models installed"** | Ollama is connected but has no model. | Go back to Step 4 and run `ollama pull qwen3:4b`. |
| **"Model "…" isn't installed."** | The model you'd chosen has been removed. | Click the model name at the top of the panel and pick another, or reinstall it with `ollama pull`. |
| **"That isn't a loopback address…"** | The address under **Change address** was edited to something that isn't your own computer. | Open **Change address** in the panel and set it back to `http://127.0.0.1:11434`. |
| **`command not found` in the terminal** | The terminal can't find Ollama. | Close the terminal completely, open a new one, and try again. If it persists, reinstall from Step 1. |

### One setting that looks like the answer but isn't

Ollama's own Settings has a switch called **"Expose Ollama to the network"**. It sounds exactly like
what you want. **It isn't, and turning it on will not fix this.**

That switch controls whether *other devices on your wi-fi* can reach Ollama. What you need is
permission for a *web page* to reach it, which is a different setting entirely — the one in Step 5.
Leaving the network switch off is the safer choice anyway.

---

## A second way, if you'd rather not change Ollama's settings

If you'd prefer to leave Ollama's configuration completely alone, you can instead open SomiFinance
through a small local web server. Ollama already trusts pages served that way, so Step 5 becomes
unnecessary.

In a terminal, move to the folder containing your SomiFinance file, then run:

```
python3 -m http.server 8000
```

Leave that terminal window open, and in your browser go to:

```
http://localhost:8000/SomiFinance.html
```

**The trade-off:** nothing to configure, but you must run that command and keep the window open
**every time** you want to use SomiFinance. Closing the terminal stops the assistant working. For
most people Step 5 is the better one-off investment; this route suits you if you'd rather not change
a setting at all.

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
ollama rm qwen3:4b
```

**Uninstall Ollama entirely:**

- *Mac:* quit Ollama from the menu bar, then drag it from Applications to the Trash. To also remove
  downloaded models, delete the `.ollama` folder in your home folder.
- *Ubuntu:* `sudo systemctl stop ollama && sudo systemctl disable ollama`, then
  `sudo rm /etc/systemd/system/ollama.service /usr/local/bin/ollama`. Downloaded models are **not**
  in your own home folder on Ubuntu — the service runs as its own `ollama` user, so remove them with
  `sudo rm -r /usr/share/ollama`.

If you set up the permanent Mac setting in Step 5, remove it too:

```
rm ~/Library/LaunchAgents/com.somifinance.ollamaorigins.plist
```

---

## Still stuck?

- Ollama's own documentation: <https://docs.ollama.com>
- SomiFinance issues: <https://github.com/mDemarco12/SomiFinance/issues>

When asking for help, it's useful to include what the assistant panel says, and the output of
`ollama --version` and `ollama list`.
