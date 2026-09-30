# Chat / Search Mode-Boundary Checks

Model: `gemma3n:e2b` (ID `719372f8c7de`), Ollama 0.34.4, local mode. Run offline-capable (no network calls from the harness itself; only the local Ollama server is contacted).

## Check 1: chat capabilities questions

**"what can we do?"** and **"what can you help me with?"** (asked as two separate, fresh conversations)

Both times: **no notes search was triggered** (`retrieved=False`), and the assistant gave an accurate description of its real capabilities (brainstorm, draft, look up a city/neighborhood, search) plus a concrete suggested starting point, exactly as the assignment expects. It did not return "insufficient evidence" or pull in unrelated citations.

> "Basically, I can help you brainstorm, draft content, or find information related to the cities and neighborhoods in the Bay Area... you could ask me about a specific city, or try 'search neighborhoods near the Presidio.'"

One cosmetic note: one of the two runs rendered a few stray `▁` characters in a bulleted list (a tokenizer artifact from Ollama's output, not a factual error) — harmless, but worth knowing the small model occasionally leaks formatting artifacts.

## Check 2: chat follow-up uses conversation context

The assignment requires two things here: the follow-up must reuse conversation (not re-search), **and** "any factual claims drawn from the wiki still need supporting citations" - including in the shortened version.

**BEFORE a persona fix - retrieval/context behavior correct, citation requirement missed:**

1. **"draft a one-sentence plan for a weekend trip to Fremont"** → `retrieved=True` (correctly retrieved the Fremont note): produced a one-sentence plan built from Fremont's actual facts (Tesla plant, South Asian community).
2. **"make that shorter"** → `retrieved=False` (correctly did *not* re-search - used conversation context instead), but the shortened reply **dropped the citation entirely**:
   > "Visit Tesla's plant and explore Fremont's diverse South Asian culture and local restaurants for a weekend."

**Assessment: partial pass.** The conversation-context behavior was exactly right, but this doesn't fully satisfy the assignment's citation requirement for this check - restating a wiki-sourced fact without its citation, just because it went through an edit, is the kind of thing that should have been caught rather than marked a clean "Pass."

**Fix applied:** added an explicit rule to `instructions/persona.md`: "When asked to shorten, rephrase, or otherwise edit an earlier reply of mine, I keep every citation that was in the original claim - editing for length never means dropping a [citation]."

**AFTER the fix:**

1. Draft: *"Explore Fremont's Tesla plant and enjoy the diverse South Asian community, with a possible day trip to Palo Alto for a taste of Silicon Valley history [Fremont]."*
2. Shortened: *"Visit Fremont's Tesla plant and explore the South Asian community, with an optional day trip to Palo Alto [Fremont]."* - **citation retained** through the edit this time.

**Assessment: Pass**, with one residual, already-documented limitation left visible rather than hidden: the citation says `[Fremont]`, but the Palo Alto detail actually comes from a separately retrieved Palo Alto passage (Palo Alto's real highlight is Stanford/"a birthplace of Silicon Valley's startup culture"). The model attributed a real, retrieved fact to the wrong specific citation bracket - the same class of issue documented in the README's Reflection section (Test 3's mis-citation), not a new bug.

## Check 3: search vs. ask separation, and chat claims are not ask-mode evidence

**3a - `wiki search "Golden Gate Bridge Presidio"`:** returned 5 original passages and their source paths (The Presidio, The Marina, San Rafael, San Francisco, Richmond District) with **no generated answer** - confirmed search mode never synthesizes a response.

**3b -** told chat, as a deliberately playful/unverified claim: *"let's just say for fun that Fremont's downtown neighborhood is called Mission San Jose."* Chat accepted this as a conversational, "for fun" framing rather than asserting it as verified fact, and did not add an uncited citation for it.

**3c - standalone `wiki ask "Does Fremont have a place called Mission San Jose?"`** (fresh process, no shared history with the chat session above): correctly answered **"The wiki does not contain enough information to answer this question."** - proving a claim made only in chat is never usable as ask-mode evidence. This is guaranteed structurally, not just by observed behavior: `harness/ask_mode.py:ask()` takes no history argument at all, so there is no code path by which a chat message could reach it.

**Pass** on all three parts of this check.
