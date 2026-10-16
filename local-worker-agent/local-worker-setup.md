# Local Worker Agent: setup prompt and manual guide

## How it works

1. **Claude (the manager)** writes `PLAN.md`: small numbered steps, each with a check command.
2. **A local Ollama model (the worker)** runs the plan in a headless `claude -p` process. It uses only models you have installed and never downloads one.
3. **The manager verifies the work.** It re-runs every check itself, reviews every changed and new file, and gives each step a verdict: ACCEPT, REJECT or OUT OF SCOPE. Rejected steps go back to the worker as a fix plan, for at most 2 rounds.
4. **You commit.** Neither agent ever commits or pushes.

The worker's own summary is a claim, not evidence. Work counts as done only after the manager has verified it.

## Part 1: Prompt to paste into Claude Code (VS Code)

Paste everything inside the block. Run it from the project root, with Ollama running.

```
I added a skill called local-worker-agent to this project. It hands a plan file to a local Ollama model running inside a headless Claude Code process. Some parts are unfinished. Your job: understand it, fill in the gaps, and test it end to end.

LOCAL-ONLY RULE: Use only models that are already installed, as shown by `ollama list`. Never run `ollama pull`, never run any command that downloads a model, and never use a network model provider. Pulling models is my job, done by hand.

ROLES: The Ollama model is only a worker. You (Claude) are the manager: you plan, hand off, and verify. Nothing the worker produces counts as done until you have re-run its checks and reviewed its changes yourself. Its summary is a claim, not evidence.

PROJECT RULES (SomiFinance):
- SomiFinanceDemo.html is the only HTML file anyone edits. After any change to it, run `python3 build.py`; it regenerates SomiFinance.html and the CSP script hashes. `python3 build.py --check` is the check command (it fails if the builds on disk are stale).
- Never hand-edit SomiFinance.html or SomiFinancePersonal.html, and never edit personal.variant.json. The personal files hold real financial data. The manager rejects any run that touches them other than through build.py.

STEP 1: UNDERSTAND
- local-worker-agent/ in the repo root is the vanilla template that is tracked in git. Never edit it. All setup changes go in the installed copy.
- Find the installed skill folder (look in .claude/skills/local-worker-agent/ and ~/.claude/skills/local-worker-agent/). If neither exists, install it with `mkdir -p .claude/skills && cp -R local-worker-agent .claude/skills/local-worker-agent && chmod u+wx .claude/skills/local-worker-agent/scripts/local-exec.sh` (git ignores this copy). Read SKILL.md and scripts/local-exec.sh in the installed copy in full.
- Explain back to me in 5 lines or fewer how the handoff works. Do not change anything yet.

STEP 2: DISCOVER PROJECT FACTS (do not guess; read the repo)
- Language, framework, package manager.
- The exact commands to test, build and lint this project (check package.json, pyproject.toml, Makefile, *.csproj, README, CI config).
- Whether a git repo exists and which branch I am on.

STEP 3: DISCOVER OLLAMA FACTS
- Run `ollama --version` (must be 0.14.0 or newer) and `ollama list`.
- If Ollama is not reachable at http://localhost:11434, tell me and stop.
- Pick the best INSTALLED model for agentic coding (prefer qwen3-coder, glm-4.7-flash or similar over 7B models). Ignore embedding-only models. Choose the model by task type, complexity and the context window needed for this plan.
- If no installed model is suitable, stop and issue a MODEL REQUEST (see below). Do not pull anything.

STEP 4: FILL IN THE GAPS
a. In scripts/local-exec.sh, set the default MODEL to the model chosen in Step 3.
b. Add this project's test/build/lint commands to --allowedTools, in the form Bash(<command>:*). For this repo that includes Bash(python3 build.py:*). Keep the list minimal. No rm, no git push, no git commit, no network tools. Add the same check commands to allowed-tools in the installed SKILL.md, so the manager can re-run them.
c. Copy local-worker-agent/Modelfile.example to Modelfile in the project root (git ignores it) and set it to raise num_ctx to at least 32768 for the chosen model. Its FROM line must name a model that is already in `ollama list`; if it is not, stop. Then run `ollama create <name>-32k -f Modelfile` (this builds locally and does not download) and make the script use that model name.
d. Fix any bug or mismatch you find (wrong paths, a script that is not executable, line endings, Windows incompatibility). On Windows, tell me whether Git Bash or WSL is needed.
e. Add a short "Local worker" section to CLAUDE.md (create it if missing). Use the block in Part 2, section 6 of this document: the manager/worker roles, how plans must be written, and the PROJECT RULES above.
Show me each change as you make it.

MODEL REQUESTS
You may ask for a different model when the task, its complexity, or the context window it needs does not fit the current model. A request must include:
- The reason (task type, complexity, or context size, with numbers where you have them).
- The recommended model name and its approximate size.
- The exact commands I must run by hand: `ollama pull <model>`, then a Modelfile with `FROM <model>` and `PARAMETER num_ctx <n>`, then `ollama create <name>-<ctx> -f Modelfile`.
- The exact edits needed in the installed copy's scripts/local-exec.sh (the MODEL default, or the LOCAL_MODEL override) and in its SKILL.md if any name or path changes. Never edit the vanilla template in local-worker-agent/.
Then stop and wait for me. Do not pull the model, and do not carry on with an unsuitable one. Once I have installed it, you may use it, since it is then in `ollama list`.

STEP 5: TEST
1. Write a tiny PLAN.md with 2 harmless steps in a scratch file, for example: create scratch/hello.txt containing "hello", then create scratch/world.txt containing "world", each with a check command that confirms the file exists.
2. Make sure the working tree is clean or committed first.
3. Run the skill: /local-worker-agent PLAN.md
4. Verify: .claude/local-exec.log exists, the worker's final summary matches the format in the script, and the manager's report has a verdict for each step backed by checks it re-ran itself. scratch/ is git-ignored, so confirm the files with `test -f scratch/hello.txt && test -f scratch/world.txt`, and confirm `git status --porcelain` shows nothing else changed.
5. Run the negative tests: point the script at a nonexistent plan file, then run it with LOCAL_MODEL set to a name that is not installed. Both must exit with a clear error, and the second must not pull anything. Confirm the Ollama-not-running error path by reading the code (do not stop Ollama).
6. Clean up the scratch files and the test plan.

STEP 6: REPORT
Give me a short table: what you changed, what passed, what failed, and anything I must do by hand. Include a "Model fit" row: the chosen model, its context window, and any MODEL REQUEST issued. If the headless run hangs or fails, show the last 40 lines of the log and propose a fix before retrying. Do not retry the same failing command more than twice.

RULES
- Never run git commit, git push, or delete files outside scratch/.
- Do not edit anything outside the installed skill folder, Modelfile, CLAUDE.md, and the scratch files without asking. The vanilla local-worker-agent/ template is read-only.
- Never pull or download a model. If you need a different one, issue a MODEL REQUEST instead.
- Use only models listed by `ollama list`. To try one for a single run without editing files, you may suggest `LOCAL_MODEL=<name>`.
```

---

## Part 2: Manual setup guide

### 1. Prerequisites

| Item | Check | Needed |
|---|---|---|
| Ollama 0.14.0 or newer | `ollama --version` | Anthropic Messages API support |
| Claude Code CLI | `claude --version` | The worker is a headless `claude -p` process |
| A coding model | `ollama list` | Tool-calling capable. Use roughly 30B class or `glm-4.7-flash`; 7B models are unreliable. You pull models yourself; the worker never does |
| Git | `git --version` | The manager's review uses `git status` and `git diff` |
| Bash | Git Bash or WSL on Windows | The script is a bash script |

### 2. Install the skill

`local-worker-agent/` in this repo is the vanilla template. Copy it and customize the copy, never the template, so your model choice and tool list stay out of git.

Per project (git-ignored):

```
mkdir -p .claude/skills
cp -R local-worker-agent .claude/skills/local-worker-agent
```

The script paths in SKILL.md already point at `.claude/skills/...`, so nothing else needs changing.

Or personal (all projects): copy it to `~/.claude/skills/local-worker-agent/` instead, then change the two `.claude/skills/...` script paths in the copy's SKILL.md to `~/.claude/skills/...`.

Then make the copy's script writable and executable: `chmod u+wx <install-dir>/scripts/local-exec.sh`

Git ignores these working files: `.claude/skills/local-worker-agent/`, `.claude/local-exec.log`, `Modelfile`, `PLAN.md`, `PLAN.fix-*.md` and `scratch/`.

### 3. Pull a model (manual, by you)

The worker uses only local models and never pulls one. You run this yourself:

```
ollama pull qwen3-coder:30b
```

If the worker issues a MODEL REQUEST, follow the commands it gives you. See "Switching models" below.

### 4. Raise the context window

Ollama's default context is too small for Claude Code's system prompt plus tool definitions. Copy `local-worker-agent/Modelfile.example` to `Modelfile` in the project root (git-ignored) and edit it:

```
FROM qwen3-coder:30b
PARAMETER num_ctx 32768
```

Then:

```
ollama create qwen3-coder-32k -f Modelfile
```

### 5. Edit the script

Open the installed copy's `scripts/local-exec.sh` (not the template) and change:

1. **Default model:** the template already uses `MODEL="${LOCAL_MODEL:-qwen3-coder-32k}"`. Change it if you built a different model. The script refuses to start, and never pulls, if the model isn't in `ollama list`.
2. **Allowed tools:** add your test/build commands, for example
   - This repo: `Bash(python3 build.py:*)`
   - Node: `Bash(npm test:*),Bash(npm run build:*),Bash(npm run lint:*)`
   - Python: `Bash(pytest:*),Bash(ruff:*)`
   - .NET: `Bash(dotnet test:*),Bash(dotnet build:*)`
   - Rust: `Bash(cargo test:*),Bash(cargo check:*)`
   Leave out `git commit`, `git push` and `rm`. Add the same check commands to `allowed-tools` in the installed SKILL.md, so the manager can re-run them without a prompt each time.
3. **Max turns:** `--max-turns 60` is a reasonable ceiling; lower it if runs wander.

### 6. Add planning rules to CLAUDE.md

```
## Local worker
Ollama models are worker agents only. Claude is the manager: it plans, hands off with
/local-worker-agent, and verifies. Worker output is not done until the manager has re-run
every check itself and reviewed every changed and new file. Only the user commits.

When asked to plan for the local worker, write PLAN.md with:
- numbered steps small enough for a few edits each
- exact file paths and function names
- one check command per step that the manager can re-run and that gives the same answer every time
- no open design decisions

Project rules (the manager rejects any run that breaks them):
- Edit only SomiFinanceDemo.html, never SomiFinance.html or SomiFinancePersonal.html.
  Any plan that changes it ends with `python3 build.py`, checked by `python3 build.py --check`.
- Never edit personal.variant.json; it holds real financial data.
```

### 7. Test it

1. Start Ollama (`ollama serve`, or the desktop app).
2. Commit or stash your changes.
3. Create `PLAN.md`:
   ```
   1. Create scratch/hello.txt containing "hello". Check: test -f scratch/hello.txt
   2. Create scratch/world.txt containing "world". Check: test -f scratch/world.txt
   ```
4. In Claude Code, run `/local-worker-agent PLAN.md`.
5. Confirm both files exist (`scratch/` is git-ignored, so use `ls scratch/` rather than `git diff`), `.claude/local-exec.log` has the full log, and Claude's manager report gives each step a verdict backed by checks it re-ran itself.
6. Delete the scratch files and `PLAN.md`.

### 8. Switching models

When the worker issues a MODEL REQUEST, do these steps by hand:

1. Pull the model: `ollama pull <model>`
2. Optional, for a larger context window: write a Modelfile with `FROM <model>` and `PARAMETER num_ctx <n>`, then run `ollama create <name>-<ctx> -f Modelfile`
3. Confirm the name with `ollama list`
4. Point the worker at it, either by editing the `MODEL` default in `scripts/local-exec.sh` (and SKILL.md if names change) or by setting `LOCAL_MODEL=<name>` for one run

### 9. Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| "Ollama is not reachable" | Ollama not running | Start it; check `OLLAMA_URL` |
| "Model '...' is not installed in Ollama" | The default `qwen3-coder-32k` isn't built yet, or `LOCAL_MODEL` is misspelled | Build it (sections 3 and 4), or set `LOCAL_MODEL` to a name from `ollama list`. The script never pulls |
| Model not found errors during a run | Model name mismatch | Names must match `ollama list` exactly; the script maps all tiers to one model |
| Manager REJECTs a step the worker said passed | The worker misreported, or its check depends on state | Trust the manager's re-run; tighten the step or its check in the plan |
| Run hangs with no output | Context too small, or model weak at tool calls | Raise `num_ctx`, try a larger model, check the log |
| Executor ignores later steps | Context overflow | Shorter plan, bigger `num_ctx` |
| "cannot be launched inside another session" | Nested Claude Code guard | The script unsets `CLAUDECODE`; if it persists, run the worker via `env -u CLAUDECODE` |
| Permission denied on a test command | Not in `--allowedTools` | Add it to the list |
| Script fails on Windows | Not running in bash | Use Git Bash or WSL, or ask Claude Code for a PowerShell version |
| Claude stops with a MODEL REQUEST | No installed model fits the task, complexity or context | Follow "Switching models"; Claude never pulls models itself |
| Context overflow even at 32k | Plan or repo too large for the model | Rebuild with a bigger `num_ctx` (for example 65536) if RAM allows, or pull a larger-context model by hand |
