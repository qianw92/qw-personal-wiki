"""Splits a vault/raw/*.md source file into topic-sized chunks.

Each "### " heading becomes one chunk (one future wiki note). A source file
with no "### " headings (e.g. a single-topic overview note) is treated as one
chunk covering the whole file. A "## Sources" section is always dropped: it
is citation metadata, not wiki content.
"""

from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chunk:
    source_file: str  # relative path, e.g. "vault/raw/bay-area-cities.md"
    group: str  # nearest enclosing "## " heading, e.g. "East Bay"
    heading: str  # the "### " heading, e.g. "Fremont" (or the H1 title if whole-file)
    text: str  # the body text under that heading


def _read_title(lines: list[str]) -> str | None:
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    return None


def parse_source_file(path: Path, project_root: Path) -> list[Chunk]:
    rel = str(path.relative_to(project_root))
    lines = path.read_text(encoding="utf-8").splitlines()
    has_h3 = any(line.startswith("### ") for line in lines)

    chunks: list[Chunk] = []

    if has_h3:
        group = ""
        heading: str | None = None
        body: list[str] = []
        in_sources = False

        def flush() -> None:
            if heading and body:
                chunks.append(Chunk(rel, group, heading, "\n".join(body).strip()))

        for line in lines:
            if line.startswith("## "):
                flush()
                heading, body = None, []
                group = line[3:].strip()
                in_sources = group.lower() == "sources"
            elif line.startswith("### ") and not in_sources:
                flush()
                heading, body = line[4:].strip(), []
            elif heading is not None and not in_sources:
                body.append(line)
        flush()
    else:
        title = _read_title(lines) or path.stem
        body = []
        in_sources = False
        for line in lines:
            if line.startswith("# "):
                continue
            if line.startswith("## "):
                in_sources = line[3:].strip().lower() == "sources"
                if in_sources:
                    continue
            if not in_sources:
                body.append(line)
        chunks.append(Chunk(rel, "", title, "\n".join(body).strip()))

    return chunks
