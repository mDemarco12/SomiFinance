#!/usr/bin/env bash
# Hands a plan file to a headless Claude Code session running on local Ollama.
# Usage: bash scripts/local-exec.sh [PLAN.md]
# Override the model with: LOCAL_MODEL=glm-4.7-flash bash scripts/local-exec.sh
# Local models only: this script never pulls a model. Install models yourself with `ollama pull`.
set -euo pipefail

PLAN="${1:-PLAN.md}"
# Built from Modelfile.example (qwen3-coder:30b with num_ctx 32768). The stock model's small
# default context makes runs hang, so the default points at the 32k build.
MODEL="${LOCAL_MODEL:-qwen3-coder-32k}"
OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
LOG=".claude/local-exec.log"

[ -f "$PLAN" ] || { echo "Plan file not found: $PLAN"; exit 1; }
TAGS="$(curl -sf "$OLLAMA_URL/api/tags")" || { echo "Ollama is not reachable at $OLLAMA_URL"; exit 1; }
# Ollama lists untagged names as name:latest, so accept either form.
if ! printf '%s' "$TAGS" | grep -qF "\"name\":\"$MODEL\"" \
   && ! printf '%s' "$TAGS" | grep -qF "\"name\":\"$MODEL:latest\""; then
  echo "Model '$MODEL' is not installed in Ollama, and this worker never pulls models."
  echo "Pull or build it yourself (see 'Switching models' in local-worker-setup.md),"
  echo "or set LOCAL_MODEL to a name from 'ollama list'."
  exit 1
fi
mkdir -p .claude

# Newer Claude Code versions refuse to start inside another session; clear the marker.
unset CLAUDECODE

# Point THIS child process only at Ollama. The parent Claude session is unaffected.
export ANTHROPIC_BASE_URL="$OLLAMA_URL"
export ANTHROPIC_AUTH_TOKEN="ollama"
export ANTHROPIC_API_KEY=""
export ANTHROPIC_DEFAULT_OPUS_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_SONNET_MODEL="$MODEL"
export ANTHROPIC_DEFAULT_HAIKU_MODEL="$MODEL"
export CLAUDE_CODE_SUBAGENT_MODEL="$MODEL"

PROMPT="You are a worker agent. A manager agent will re-run every check and review every
changed file, so report exactly what happened. Never mark a check as passed unless you ran it
and it passed. Change only the files the plan names.
Execute the plan in $PLAN exactly, one step at a time, in order.
Do not redesign anything or add work the plan does not ask for.
After each step, run that step's check if it has one. If a check fails twice, stop.
Finish with a short summary in this format:
STEPS DONE: <numbers>
STEPS SKIPPED OR FAILED: <numbers and why>
FILES CHANGED: <paths>
CHECK RESULTS: <pass/fail per check>"

echo "Running $PLAN on $MODEL (log: $LOG)..."

# Add your project's test/build commands to --allowedTools, e.g. "Bash(npm test:*)" or "Bash(pytest:*)".
claude -p "$PROMPT" \
  --model "$MODEL" \
  --max-turns 60 \
  --allowedTools "Read,Edit,Write,Glob,Grep,Bash(git status:*),Bash(git diff:*)" \
  > "$LOG" 2>&1 || echo "Local executor exited with an error; see $LOG"

# Only the tail comes back to the parent session, which keeps Claude's token cost low.
tail -n 40 "$LOG"
