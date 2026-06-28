"""Command line interface for pseudo-repair-toolkit."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import List

from .classifier import classify_trajectory
from .io import load_trajectories, write_json, write_text
from .report import batch_markdown, result_to_markdown, results_to_json
from .taxonomy import OUTCOME_GUIDE, REPOSITORY_STATUS, SUBTYPE_GUIDE


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pseudo-repair",
        description="Classify iterative LLM code-repair trajectories using the Pseudo-Repair taxonomy.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    taxonomy = sub.add_parser("taxonomy", help="Print taxonomy definitions.")
    taxonomy.add_argument("--format", choices=["text", "json"], default="text")

    classify = sub.add_parser("classify", help="Classify one trajectory JSON file.")
    classify.add_argument("input", help="Path to a trajectory JSON file.")
    classify.add_argument("--format", choices=["json", "md"], default="json")
    classify.add_argument("--out", help="Optional output file path.")

    batch = sub.add_parser("batch", help="Classify a directory of JSON files or a JSON list.")
    batch.add_argument("input", help="Path to a directory, a trajectory JSON file, or a JSON list.")
    batch.add_argument("--format", choices=["json", "md"], default="md")
    batch.add_argument("--out", help="Optional output file path.")

    validate = sub.add_parser("validate", help="Load and validate trajectory JSON structure.")
    validate.add_argument("input", help="Path to a trajectory JSON file or directory.")

    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "taxonomy":
        payload = {
            "outcomes": {k.name: v.__dict__ for k, v in OUTCOME_GUIDE.items()},
            "pseudo_repair_subtypes": {k.name: v.__dict__ for k, v in SUBTYPE_GUIDE.items()},
            "repository_status": REPOSITORY_STATUS,
        }
        if args.format == "json":
            print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            print("Pseudo-Repair Taxonomy\n")
            print("Top-level outcomes:")
            for entry in OUTCOME_GUIDE.values():
                print(f"- {entry.code} / {entry.name}: {entry.definition}")
            print("\nPseudo-Repair subtypes:")
            for entry in SUBTYPE_GUIDE.values():
                print(f"- {entry.code} / {entry.name}: {entry.definition}")
            print(f"\nRepository status: {REPOSITORY_STATUS}")
        return 0

    if args.command == "validate":
        trajectories = load_trajectories(args.input)
        print(f"Loaded {len(trajectories)} trajectory/trajectories successfully.")
        return 0

    if args.command == "classify":
        trajectories = load_trajectories(args.input)
        if len(trajectories) != 1:
            parser.error("classify expects exactly one trajectory; use batch for multiple inputs")
        result = classify_trajectory(trajectories[0])
        if args.format == "json":
            payload = result.to_dict()
            if args.out:
                write_json(args.out, payload)
            else:
                print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            text = result_to_markdown(result)
            if args.out:
                write_text(args.out, text)
            else:
                print(text)
        return 0

    if args.command == "batch":
        results = [classify_trajectory(item) for item in load_trajectories(args.input)]
        if args.format == "json":
            payload = results_to_json(results)
            if args.out:
                write_json(args.out, payload)
            else:
                print(json.dumps(payload, indent=2, ensure_ascii=False))
        else:
            text = batch_markdown(results)
            if args.out:
                write_text(args.out, text)
            else:
                print(text)
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
