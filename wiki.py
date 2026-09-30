#!/usr/bin/env python3
"""Personal Wiki CLI: local Gemma + RAG over vault/raw sources.

Modes: ingest, search, ask, chat. Local execution is the default and the
only mode implemented; --mode online is rejected by `ask` on purpose.
"""

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_RAW = PROJECT_ROOT / "vault" / "raw"


def cmd_ingest(args: argparse.Namespace) -> None:
    from harness.ingest import run_ingest

    raw_dir = Path(args.path).resolve() if args.path else DEFAULT_RAW
    if not raw_dir.is_dir():
        print(f"error: no such directory: {raw_dir}", file=sys.stderr)
        sys.exit(1)
    run_ingest(raw_dir)


def cmd_search(args: argparse.Namespace) -> None:
    from harness.retrieval import search

    try:
        results = search(args.query, top_k=args.top_k)
    except FileNotFoundError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    if not results:
        print("No matching passages found.")
        return

    for i, r in enumerate(results, 1):
        print(f"[{i}] {r['heading']}  (source: {r['source_file']})")
        for line in r["text"].splitlines():
            if line.strip():
                print(f"    {line}")
        print()


def cmd_ask(args: argparse.Namespace) -> None:
    if args.mode == "online":
        print("error: online mode is not implemented; only --mode local is supported.", file=sys.stderr)
        sys.exit(1)

    from harness.ask_mode import ask
    from harness.model import MODEL_NAME

    print(f"[model: {MODEL_NAME} · mode: {args.mode}]", flush=True)
    try:
        result = ask(args.query)
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)

    print(result["answer"])
    print()
    if result["insufficient_evidence"]:
        print("[insufficient evidence: no supporting passage found]")
    else:
        rep = result["citations"]
        line = f"[citations checked: {rep['valid']}]" if rep["valid"] else "[no citations found in answer]"
        if rep["invalid"]:
            line += f"  [unverified citations: {rep['invalid']}]"
        print(line)


def cmd_chat(args: argparse.Namespace) -> None:
    from harness.chat_mode import reply
    from harness.model import MODEL_NAME

    print(f"Bay Wiki Assistant (chat mode) · model: {MODEL_NAME} · mode: local")
    print("Type 'exit' to quit.\n")
    history: list[tuple[str, str]] = []
    while True:
        try:
            message = input("You: ").strip()
        except EOFError:
            print()
            break
        if not message:
            continue
        if message.lower() in ("exit", "quit", "bye"):
            break
        try:
            answer, retrieved = reply(history, message)
        except RuntimeError as e:
            print(f"error: {e}", file=sys.stderr)
            break
        tag = " [used a wiki note]" if retrieved else ""
        print(f"Assistant{tag}: {answer}\n")
        history.append(("User", message))
        history.append(("Assistant", answer))


def main() -> None:
    parser = argparse.ArgumentParser(prog="wiki", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="read vault/raw sources and (re)build vault/wiki + index.md")
    p_ingest.add_argument("path", nargs="?", default=None, help="source directory (default: ./vault/raw)")
    p_ingest.set_defaults(func=cmd_ingest)

    p_search = sub.add_parser("search", help="show original matching passages, no generated answer")
    p_search.add_argument("query")
    p_search.add_argument("--top-k", type=int, default=5, dest="top_k")
    p_search.set_defaults(func=cmd_search)

    p_ask = sub.add_parser("ask", help="standalone factual answer with citations, or insufficient evidence")
    p_ask.add_argument("query")
    p_ask.add_argument("--mode", choices=["local", "online"], default="local")
    p_ask.set_defaults(func=cmd_ask)

    p_chat = sub.add_parser("chat", help="start the personal assistant")
    p_chat.set_defaults(func=cmd_chat)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
