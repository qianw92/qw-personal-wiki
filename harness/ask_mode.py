"""Ask mode: standalone factual answer with citations, or insufficient evidence.

Independent of chat history and of the chat persona - each question is
retrieved and answered fresh, per the assignment's ask/chat separation.
"""

from pathlib import Path

from . import model
from .citations import check_citations
from .retrieval import search

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INSTRUCTIONS = PROJECT_ROOT / "instructions" / "wiki-instructions.md"

INSUFFICIENT_EVIDENCE = "The wiki does not contain enough information to answer this question."


def load_instructions() -> str:
    return INSTRUCTIONS.read_text(encoding="utf-8")


def format_passages(results: list[dict]) -> str:
    return "\n\n".join(f"[{r['heading']}] ({r['source_file']})\n{r['text']}" for r in results)


def ask(query: str, top_k: int = 5) -> dict:
    try:
        results = search(query, top_k=top_k)
    except FileNotFoundError:
        results = []

    system = load_instructions()
    passages_text = format_passages(results) if results else "(no passages retrieved)"
    prompt = (
        f"Retrieved passages:\n{passages_text}\n\n"
        f"Question: {query}\n\n"
        "Answer (cite each factual sentence with [Passage Title], or reply with the "
        f'exact sentence "{INSUFFICIENT_EVIDENCE}" if the passages do not answer the question):'
    )
    answer = model.generate(prompt, system=system, temperature=0.1)

    headings = [r["heading"] for r in results]
    citation_report = check_citations(answer, headings)
    insufficient = INSUFFICIENT_EVIDENCE.lower() in answer.lower()

    return {
        "query": query,
        "retrieved": results,
        "answer": answer,
        "citations": citation_report,
        "insufficient_evidence": insufficient,
    }
