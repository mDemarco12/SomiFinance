---
name: local-worker-agent
description: Hand a finished plan file (PLAN.md by default) to a local Ollama worker model for execution, then verify its work as the manager. Use only when the user asks to run a plan locally, hand off to the local worker, or execute with Ollama.
argument-hint: [plan-file, default PLAN.md]
allowed-tools: Bash(bash .claude/skills/local-worker-agent/scripts/local-exec.sh:*), Bash(git status:*), Bash(git diff:*), Read
---

# Local Worker Agent

Roles:
- **Worker:** a local model running in Ollama. It implements the plan. Its summary is a claim, not evidence.
- **Manager:** you (Claude). You plan, hand off, and verify. Nothing the worker produces counts as done until you have verified it.
- **The user** commits. Neither of you ever runs git commit or git push.

Do not implement any part of the plan yourself. Corrections go back to the worker.

Plan file: $ARGUMENTS (use PLAN.md if empty).

## Steps

1. Confirm the plan file exists in the repo root. If it doesn't, stop and say so.
2. Run `git status --porcelain`. If it shows any change, stop and ask me to commit first,
   so a bad run can be undone with `git restore .`.
3. Run the worker in the background and wait for it to finish:
   `bash .claude/skills/local-worker-agent/scripts/local-exec.sh <plan-file>`
   Its full log goes to `.claude/local-exec.log`; only the tail comes back to you.
   Do not read the full log unless the tail shows an error you can't explain.
4. Verify, as the manager:
   a. Run `git status --porcelain` and `git diff`. `git diff` alone misses new untracked
      files, so read every new file `git status` lists. Files in git-ignored paths (such as
      `scratch/`) show in neither; check those with `test -f` or `git status --porcelain --ignored`.
   b. Re-run every step's check command yourself. Do not trust the worker's CHECK RESULTS;
      compare them with what you got.
   c. Apply the project rules in the "Local worker" section of CLAUDE.md, if there is one.
   d. Give each plan step one verdict:
      - ACCEPT: done as planned, and its check passed when you ran it
      - REJECT: missing, wrong, or its check failed (say why)
      - OUT OF SCOPE: the worker changed a file or behaviour the plan did not ask for
5. If any step is REJECT or OUT OF SCOPE, write `PLAN.fix-<n>.md` covering only those steps,
   in the same format as the plan, and hand it to the worker (step 3), then verify again
   (step 4). Stop after 2 fix rounds and report.
6. Report back briefly:
   - a table: step, verdict, evidence (the check you ran and its result)
   - any place the worker's claims disagree with what you verified
   - a final verdict: ACCEPTED, or NEEDS YOU (with what is left)
   - if the run should be thrown away: `git restore .` plus the new files to delete.
     Do not delete them yourself.
7. Do not fix anything yourself unless I ask. If I ask, fix only what you flagged.

## Writing plans for this worker

When I ask you to plan for the local worker, write the plan file with:
- numbered steps, each small enough to finish in a few edits
- exact file paths and function names
- one check command per step (a test, build, or lint command) that you can re-run yourself
  and that gives the same answer every time
- no open design decisions; settle them in the plan
