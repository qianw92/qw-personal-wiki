"""Checks whether an answer's [bracket] citations actually match retrieved passages."""

import re


def extract_citations(answer: str) -> list[str]:
    return re.findall(r"\[([^\]]+)\]", answer)


def check_citations(answer: str, retrieved_headings: list[str]) -> dict:
    cited = extract_citations(answer)
    headings_lower = {h.strip().lower() for h in retrieved_headings}
    valid = [c for c in cited if c.strip().lower() in headings_lower]
    invalid = [c for c in cited if c.strip().lower() not in headings_lower]
    return {"cited": cited, "valid": valid, "invalid": invalid}
