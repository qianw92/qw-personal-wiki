# Test 4: Unanswerable

**Command:** `python3 wiki.py ask "Who is the current mayor of Oakland?"`

**Model:** `gemma3n:e2b` (ID `719372f8c7de`), Ollama 0.34.4, local mode.

None of the three source files record any city's elected officials, so this question has no supported answer anywhere in the wiki.

## Retrieved passages
Loosely Oakland-adjacent passages came back on keyword overlap alone (Bay Area Sub-Regions Overview, South San Francisco, Alameda, Pleasanton, Fremont) — none of them mention a mayor or any elected official, confirming there is genuinely no supporting evidence anywhere in the corpus.

## Actual answer
> The wiki does not contain enough information to answer this question. [Bay Area Sub-Regions Overview]

## Result
`[insufficient evidence: no supporting passage found]`

## Assessment
**Pass.** The model correctly refused to guess from its own general knowledge and produced the exact required insufficient-evidence sentence, instead of inventing a name. Confirmed separately (see `evidence/modes/mode-boundary-checks.md`) that this refusal holds even when a *chat* session had earlier stated an unrelated invented claim about Fremont — ask mode never sees chat history, so it can't be contaminated by it.
