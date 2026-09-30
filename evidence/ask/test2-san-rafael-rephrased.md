# Test 2: Answerable, rephrased away from the source wording

**Command:** `python3 wiki.py ask "Which city in Marin County has the biggest population?"`

**Model:** `gemma3n:e2b` (ID `719372f8c7de`), Ollama 0.34.4, local mode.

The source never says "biggest population" — it says "the largest city in Marin." This test checks whether retrieval and the model handle a meaning match, not just a keyword match.

## Retrieved passage
**San Rafael** (`vault/raw/bay-area-cities.md`):
> - Population: 61,271 (2020 Census).
> - Location: in Marin County, north of San Francisco across the Golden Gate Bridge, the largest city in Marin.
> - Highlight: Marin County's government and commercial center, at the base of hills leading to Mount Tamalpais.

## Actual answer
> Marin County's largest city is San Rafael with a population of 61,271 in 2020 [San Rafael]. The city is north of San Francisco across the Golden Gate Bridge and is the largest city in Marin [San Rafael]. [San Rafael]

## Citation check
`[citations checked: ['San Rafael', 'San Rafael', 'San Rafael']]` — all valid.

## Assessment
**Pass.** Retrieval correctly matched despite the reworded question, and the answer correctly identifies San Rafael with a supported citation.
