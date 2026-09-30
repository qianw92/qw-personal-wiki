# Test 1: Direct question, one source

**Command:** `python3 wiki.py ask "What is Fremont's approximate population, and what company's vehicle assembly plant is there?"`

**Model:** `gemma3n:e2b` (ID `719372f8c7de`), Ollama 0.34.4, local mode.

## Retrieved passage
**Fremont** (`vault/raw/bay-area-cities.md`):
> - Population: 230,504 (2020 Census).
> - Location: at the southeastern edge of the Bay, south of Oakland/Hayward, directly across the Bay from Palo Alto and Menlo Park.
> - Highlight: home to Tesla's primary vehicle assembly plant and a large, diverse South Asian immigrant community.

## Actual answer
> Fremont's population is 230,504 [Fremont], and it is home to Tesla's primary vehicle assembly plant [Fremont]. [Fremont]

## Citation check
`[citations checked: ['Fremont', 'Fremont', 'Fremont']]` — every citation matches a retrieved heading.

## Assessment
**Pass.** Both material claims (population, Tesla plant) are directly and correctly supported by the cited passage. No invented details.
