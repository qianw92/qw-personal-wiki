# Ask-Mode Test Questions

Written before building retrieval/ingestion, per the assignment's evaluation requirement. Kept outside `vault/` so the harness must retrieve the underlying sources rather than this answer key. Each test records the question, expected source and passage, and expected behavior; actual retrieved passages, Gemma's real answer, and citations get filled in once `wiki ask` exists (see `evidence/ask/`).

## Test 1: Direct question, one source

**Question:** "What is Fremont's approximate population, and what company's vehicle assembly plant is there?"

**Expected source:** `vault/raw/bay-area-cities.md`, Fremont entry:
> Population: 230,504 (2020 Census). ... Highlight: home to Tesla's primary vehicle assembly plant and a large, diverse South Asian immigrant community.

**Expected behavior:** retrieval returns the Fremont passage; Gemma answers "about 230,504 (2020 Census)" and "Tesla," with a citation to `bay-area-cities.md`.

## Test 2: Answerable, rephrased away from the source wording

**Question:** "Which city in Marin County has the biggest population?"

**Expected source:** `vault/raw/bay-area-cities.md`, San Rafael entry:
> Location: in Marin County, north of San Francisco across the Golden Gate Bridge, the largest city in Marin.

**Expected behavior:** the source says "the largest city in Marin," not "biggest population" — this checks whether retrieval matches on meaning, not just keyword overlap. Correct answer: San Rafael, with a citation.

## Test 3: Answerable, connects two sources

**Question:** "Which bridge would you cross to get from the Presidio to Marin County, and which Bay Area sub-region is Marin part of?"

**Expected sources:**
- `vault/raw/sf-neighborhoods.md`, Presidio entry: "northwest corner of SF, at the foot of the Golden Gate Bridge."
- `vault/raw/bay-area-regions-overview.md`: "North Bay: Marin, Sonoma, and Napa Counties, north of San Francisco across the Golden Gate Bridge..." and the bridge list naming "the Golden Gate Bridge (SF to Marin/North Bay)."

**Expected behavior:** retrieval pulls passages from both files; Gemma answers "the Golden Gate Bridge" and "the North Bay," with citations to both sources. Tests whether the harness can combine evidence across documents in a single answer.

## Test 4: Unanswerable

**Question:** "Who is the current mayor of Oakland?"

**Expected source:** none. None of the three source files record any city's elected officials.

**Expected behavior:** retrieval finds no supporting passage (or only weakly related passages about Oakland that don't mention a mayor); Gemma must respond that the wiki does not contain this information, rather than guessing from general knowledge. This is the required "insufficient evidence" check.

## Notes

- Tests 1-3 deliberately span all three sources at least once (Test 1 and 2 use `bay-area-cities.md`; Test 3 uses `sf-neighborhoods.md` + `bay-area-regions-overview.md`), so both cities and neighborhoods content get exercised.
- Once ingestion exists, re-run all four after any indexing change and keep the earlier result as evidence of what improved (per the assignment's evaluation rules).
- These are separate from the "mode boundary" checks (chat capabilities, chat follow-up, search-vs-ask separation), which get their own short transcript per the plan.
