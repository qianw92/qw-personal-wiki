#!/bin/bash
# Offline demonstration for Assignment 4.
# Run this AFTER disconnecting from the internet (Wi-Fi off).
# Usage:
#   cd "/Users/QW/Desktop/Claude/Assignment 5 Personal Wiki"
#   bash evidence/offline/run_offline_demo.sh 2>&1 | tee evidence/offline/offline-demo-transcript.txt

set -x  # echo every command as it runs, so the transcript shows exactly what was executed

echo "###############################################"
echo "# OFFLINE DEMONSTRATION"
echo "# Started: $(date)"
echo "###############################################"

echo
echo "=== Step 0: Prove there is no internet connection ==="
echo "(This command SHOULD fail/timeout. That failure is the actual proof.)"
curl -s -o /dev/null --max-time 5 -w "HTTP status: %{http_code}\n" https://www.google.com
echo "curl exit code: $?  (a non-zero code, or 'HTTP status: 000', means it could not reach the internet - expected)"

echo
echo "=== Step 1: Restart the CLI's model server in local mode ==="
pkill -f "ollama serve" 2>/dev/null
sleep 1
nohup ollama serve > /tmp/ollama-offline.log 2>&1 &
disown
sleep 3
ollama list
echo "(Model is already downloaded locally - this works with no internet.)"

echo
echo "=== Step 2: wiki --help ==="
python3 wiki.py --help

echo
echo "=== Step 3: Ingest local sources ==="
python3 wiki.py ingest ./vault/raw

echo
echo "=== Step 4: Four required ask-mode tests ==="

echo "--- Test 1: direct question, one source ---"
python3 wiki.py ask "What is Fremont's approximate population, and what company's vehicle assembly plant is there?"

echo
echo "--- Test 2: answerable, rephrased away from source wording ---"
python3 wiki.py ask "Which city in Marin County has the biggest population?"

echo
echo "--- Test 3: answerable, connects two sources ---"
python3 wiki.py ask "Which bridge would you cross to get from the Presidio to Marin County, and which Bay Area sub-region is Marin part of?"

echo
echo "--- Test 4: unanswerable ---"
python3 wiki.py ask "Who is the current mayor of Oakland?"

echo
echo "=== Step 5: Chat and search mode-boundary checks ==="

echo "--- 5a: wiki search (no generated answer) ---"
python3 wiki.py search "Golden Gate Bridge Presidio"

echo
echo "--- 5b: chat capabilities, follow-up, and chat-claim isolation from ask ---"
python3 - <<'PYEOF'
import sys
sys.path.insert(0, ".")
from harness.chat_mode import reply

history = []

print("[chat] User: what can you help me with?")
msg = "what can you help me with?"
ans, retrieved = reply(history, msg)
print(f"[chat] retrieved={retrieved}")
print("[chat] Assistant:", ans)

print()
print("[chat] User: draft a one-sentence plan for a weekend trip to Fremont")
history = []
msg = "draft a one-sentence plan for a weekend trip to Fremont"
ans, retrieved = reply(history, msg)
print(f"[chat] retrieved={retrieved}")
print("[chat] Assistant:", ans)
history += [("User", msg), ("Assistant", ans)]

print()
print("[chat] User: make that shorter")
msg = "make that shorter"
ans2, retrieved2 = reply(history, msg)
print(f"[chat] retrieved={retrieved2}")
print("[chat] Assistant:", ans2)
PYEOF

echo
echo "--- 5c: standalone ask must ignore anything only said in chat ---"
python3 wiki.py ask "Does Fremont have a place called Mission San Jose?"

echo
echo "=== Step 6: Stop the model server ==="
pkill -f "ollama serve"
sleep 1
pgrep -fl "ollama serve" || echo "ollama server stopped"

echo
echo "###############################################"
echo "# OFFLINE DEMONSTRATION COMPLETE"
echo "# Finished: $(date)"
echo "###############################################"
