"""Ingestion: vault/raw/*.md -> reviewed wiki pages in vault/wiki/, plus index.md.

One "### " heading (a city, a neighborhood) becomes one wiki note. Gemma
drafts a short natural-language introduction from the source facts; the
facts themselves are copied verbatim into the note, so a fabricated detail
from the model can only ever appear in the introduction, never in the facts
a reader or the retrieval tool relies on. Filenames are deterministic
(derived from the heading), so re-ingesting updates the same notes instead
of creating duplicates.
"""

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import model
from .parsing import Chunk, parse_source_file

PROJECT_ROOT = Path(__file__).resolve().parent.parent
VAULT = PROJECT_ROOT / "vault"
WIKI = VAULT / "wiki"
INDEX = VAULT / "index.md"
DATA = PROJECT_ROOT / "data"
CATALOG = DATA / "source_catalog.json"
CHUNKS_FILE = DATA / "chunks.jsonl"

FOLDER_FOR_SOURCE = {
    "bay-area-regions-overview": "Regions",
    "bay-area-cities": "Cities",
    "sf-neighborhoods": "San Francisco Neighborhoods",
}

INGEST_SYSTEM_PROMPT = (
    "You are drafting one short personal-wiki note from reference facts the "
    "user already wrote and verified. Write 2-3 plain sentences that "
    "introduce the topic in natural language, using only the facts given "
    "below. Do not invent any fact, number, or name that is not present in "
    "the facts. Do not add a heading, a list, or a facts section - the "
    "caller adds those separately. Return only the introduction sentences."
)


def clean_title(raw_heading: str) -> str:
    """Drops a trailing parenthetical, e.g. 'SoMa (South of Market)' -> 'SoMa'."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", raw_heading).strip()


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def load_catalog() -> dict:
    if CATALOG.exists():
        return json.loads(CATALOG.read_text(encoding="utf-8"))
    return {}


def save_catalog(catalog: dict) -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    CATALOG.write_text(json.dumps(catalog, indent=2, sort_keys=True), encoding="utf-8")


def draft_intro(chunk: Chunk) -> str:
    prompt = f"Topic: {chunk.heading}\nFacts:\n{chunk.text}\n\nIntroduction:"
    try:
        return model.generate(prompt, system=INGEST_SYSTEM_PROMPT, temperature=0.2)
    except RuntimeError as e:
        print(f"  ! Gemma unavailable, note will use facts only ({e})", file=sys.stderr)
        return ""


def find_mentions(chunk: Chunk, all_titles: list[str], self_title: str) -> list[tuple[str, str]]:
    """Links to any other note whose title is literally named in this chunk's facts."""
    related = []
    for other in sorted(all_titles, key=len, reverse=True):
        if other == self_title:
            continue
        if re.search(r"\b" + re.escape(other) + r"\b", chunk.text):
            related.append((other, f"mentioned directly in {self_title}'s source facts"))
    return related


def build_note(
    chunk: Chunk, title: str, source_id: str, related: list[tuple[str, str]]
) -> str:
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
    intro = draft_intro(chunk)
    source_stem = Path(chunk.source_file).stem

    lines = [
        "---",
        f"source_id: {source_id}",
        f"source_file: {chunk.source_file}",
        f"source_heading: {chunk.heading}",
        f"generated: {ts}",
        "---",
        "",
        f"# {title}",
        "",
    ]
    if intro:
        lines += [intro, ""]
    lines.append("## Facts")
    for line in chunk.text.splitlines():
        if line.strip():
            lines.append(line)
    lines += ["", "## Source", f"[[{source_stem}#{chunk.heading}]]"]
    if related:
        lines += ["", "## Related notes"]
        for rel_title, reason in related:
            lines.append(f"- [[{rel_title}]] — {reason}")
    lines.append("")
    return "\n".join(lines)


def rebuild_index(entries: dict[str, list[tuple[str, str]]]) -> None:
    lines = [
        "# Personal Wiki Index",
        "",
        "Bay Area cities and San Francisco neighborhoods, grouped by topic.",
        "",
    ]
    for folder in ["Regions", "Cities", "San Francisco Neighborhoods"]:
        notes = sorted(entries.get(folder, []), key=lambda t: t[0])
        if not notes:
            continue
        lines.append(f"## {folder}")
        lines.append("")
        for title, desc in notes:
            suffix = f" — {desc}" if desc else ""
            lines.append(f"- [[{title}]]{suffix}")
        lines.append("")
    INDEX.write_text("\n".join(lines), encoding="utf-8")


def run_ingest(raw_dir: Path) -> None:
    all_chunks: list[Chunk] = []
    for path in sorted(raw_dir.glob("*.md")):
        all_chunks.extend(parse_source_file(path, PROJECT_ROOT))

    if not all_chunks:
        print(f"No source files found in {raw_dir}")
        return

    all_titles = [clean_title(c.heading) for c in all_chunks]

    regions_chunks = [c for c in all_chunks if Path(c.source_file).stem == "bay-area-regions-overview"]
    regions_title = clean_title(regions_chunks[0].heading) if regions_chunks else None

    DATA.mkdir(parents=True, exist_ok=True)
    with CHUNKS_FILE.open("w", encoding="utf-8") as cf:
        for chunk in all_chunks:
            cf.write(
                json.dumps(
                    {
                        "source_file": chunk.source_file,
                        "heading": chunk.heading,
                        "group": chunk.group,
                        "text": chunk.text,
                    }
                )
                + "\n"
            )

    catalog = load_catalog()
    index_entries: dict[str, list[tuple[str, str]]] = {}

    for chunk in all_chunks:
        title = clean_title(chunk.heading)
        source_stem = Path(chunk.source_file).stem
        source_id = f"{source_stem}#{slugify(chunk.heading)}"
        folder = FOLDER_FOR_SOURCE.get(source_stem, "Misc")
        folder_path = WIKI / folder
        folder_path.mkdir(parents=True, exist_ok=True)
        note_path = folder_path / f"{title}.md"

        related = find_mentions(chunk, all_titles, title)
        if folder == "Cities" and regions_title:
            group_label = clean_title(chunk.group) if chunk.group else "Bay Area"
            related.insert(
                0,
                (regions_title, f"defines the {group_label} sub-region {title} belongs to"),
            )
        elif folder == "San Francisco Neighborhoods" and regions_title:
            related.insert(
                0,
                (
                    regions_title,
                    "defines San Francisco as the orientation reference point used to place "
                    f"{title} within the Bay Area",
                ),
            )

        print(f"  drafting: {folder}/{title}.md")
        note_path.write_text(build_note(chunk, title, source_id, related), encoding="utf-8")

        catalog[source_id] = str(note_path.relative_to(PROJECT_ROOT))
        first_line = chunk.text.strip().splitlines()[0] if chunk.text.strip() else ""
        desc = first_line.split(":", 1)[-1].strip().rstrip(".") if ":" in first_line else ""
        if len(desc) > 80:
            desc = desc[:80].rsplit(" ", 1)[0]
        index_entries.setdefault(folder, []).append((title, desc))

    rebuild_index(index_entries)
    save_catalog(catalog)

    from .retrieval import build_index

    indexed = build_index()

    print(f"\nIngested {len(all_chunks)} source passages into {len(all_chunks)} wiki notes.")
    print(f"Wiki index rebuilt at {INDEX.relative_to(PROJECT_ROOT)}")
    print(f"Retrieval index rebuilt: {indexed} passages searchable via `wiki search`.")
