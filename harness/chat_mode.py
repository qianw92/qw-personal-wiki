"""Chat mode: personal-assistant conversation with the wiki's persona.

Uses recent conversation context for follow-ups. Retrieves a wiki note only
when the harness decides the message needs one - never for a meta/capability
question or a follow-up like "make that shorter", so the harness doesn't
force an unnecessary notes search or an insufficient-evidence refusal onto
ordinary conversation (the assignment's chat mode-boundary requirement).
"""

import json
import re
from pathlib import Path

from . import model
from .ingest import CHUNKS_FILE, clean_title
from .retrieval import search

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PERSONA = PROJECT_ROOT / "instructions" / "persona.md"

META_PATTERNS = [
    "what can you",
    "what can we do",
    "help me with",
    "make that shorter",
    "make it shorter",
    "make that longer",
    "make it longer",
    "summarize that",
    "simplify that",
]
FACTUAL_STARTERS = (
    "what",
    "where",
    "who",
    "when",
    "how many",
    "how much",
    "which",
    "does",
    "is there",
    "are there",
)


def load_persona() -> str:
    return PERSONA.read_text(encoding="utf-8")


def known_titles() -> list[str]:
    titles = []
    if CHUNKS_FILE.exists():
        with CHUNKS_FILE.open(encoding="utf-8") as f:
            for line in f:
                c = json.loads(line)
                titles.append(clean_title(c["heading"]))
    return titles


def should_retrieve(message: str, titles: list[str]) -> bool:
    lower = message.lower()
    if any(p in lower for p in META_PATTERNS):
        return False
    for title in titles:
        if re.search(r"\b" + re.escape(title.lower()) + r"\b", lower):
            return True
    return lower.strip().startswith(FACTUAL_STARTERS)


def build_prompt(history: list[tuple[str, str]], message: str, passages_text: str | None) -> str:
    parts = []
    if history:
        convo = "\n".join(f"{role}: {text}" for role, text in history[-6:])
        parts.append(f"Conversation so far:\n{convo}")
    if passages_text:
        parts.append(f"Retrieved wiki notes (cite with [Passage Title] if you use one):\n{passages_text}")
    parts.append(f"User: {message}\nAssistant:")
    return "\n\n".join(parts)


def reply(history: list[tuple[str, str]], message: str, top_k: int = 4) -> tuple[str, bool]:
    titles = known_titles()
    retrieve = should_retrieve(message, titles)

    passages_text = None
    if retrieve:
        try:
            results = search(message, top_k=top_k)
        except FileNotFoundError:
            results = []
        if results:
            passages_text = "\n\n".join(
                f"[{r['heading']}] ({r['source_file']})\n{r['text']}" for r in results
            )
        else:
            retrieve = False  # nothing relevant came back; don't claim we searched

    system = load_persona()
    prompt = build_prompt(history, message, passages_text)
    answer = model.generate(prompt, system=system, temperature=0.4)
    return answer, retrieve
