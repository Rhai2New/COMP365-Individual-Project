"""Export explanation-review worksheets; validate anchored ratings and compute means.

Scores are entered by a named rater. This program does not infer semantic quality.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from evidence import new_run, save_csv, save_json, save_text
from summarize_results import read_records

DIMENSIONS = ("root_cause_accuracy", "repair_reasoning", "beginner_clarity", "case_specificity")


def sections(response: str) -> tuple[str, str]:
    root = re.search(r"ROOT CAUSE:\s*(.*?)\s*BEGINNER EXPLANATION:", response, re.S | re.I)
    beginner = re.search(r"BEGINNER EXPLANATION:\s*(.*?)(?:\s*PATCHED CODE:|$)", response, re.S | re.I)
    return root.group(1).strip() if root else "", beginner.group(1).strip() if beginner else ""


def export(run: Path, output_root: Path | None = None) -> Path:
    destination = new_run(output_root or run.parent.parent / "explanation_reviews", "worksheet")
    rows = []
    for row in read_records(run):
        if not row["response_received"]:
            continue
        response = (run / row["artifact_dir"] / "response.txt").read_text(encoding="utf-8")
        root, beginner = sections(response)
        rows.append({"run_id": run.name, "case_id": row["case_id"], "provider": row["provider"],
                     "model": row["model"], "root_cause_text": root, "beginner_text": beginner,
                     "category": row['category'],
                     "response_path": str(run / row['artifact_dir'] / 'response.txt'),
                     "original_source_path": str(run / row['artifact_dir'] / 'original.java'),
                     "visible_context_path": str(run / row['artifact_dir'] / 'failure_context.txt'),
                     "validation_path": str(run / row['artifact_dir'] / 'validation.json'),
                     "rater": "", "rater_type": "", **{d: "" for d in DIMENSIONS},
                     "evidence_quote": "", "rationale": ""})
    save_csv(destination / "ratings.csv", rows)
    save_json(destination / "source.json", {"source_run": str(run.resolve()), "rubric": "docs/EXPLANATION_RUBRIC.md"})
    structural = [{"case_id": r["case_id"], "provider": r["provider"],
                   "root_section_present": bool(r["root_cause_text"]),
                   "beginner_section_present": bool(r["beginner_text"]),
                   "explanation_words": len(r["beginner_text"].split())} for r in rows]
    save_csv(destination / "structural_checks.csv", structural)
    return destination


def evaluate(run: Path, ratings_path: Path) -> Path:
    records = {(r["case_id"], r["provider"]): r for r in read_records(run) if r["response_received"]}
    with ratings_path.open(newline="", encoding="utf-8-sig") as handle:
        ratings = list(csv.DictReader(handle))
    identities = [(r["case_id"], r["provider"]) for r in ratings]
    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate ratings; use one worksheet per rater")
    scored = []
    for r in ratings:
        if not any(r[d] for d in DIMENSIONS):
            continue
        if r["run_id"] != run.name or (r["case_id"], r["provider"]) not in records:
            raise ValueError("Rating does not match a saved response")
        if not r["rater"].strip() or r["rater_type"] not in {"human", "AI_assisted"} or not r["rationale"].strip():
            raise ValueError("Each rating needs rater, rater_type, and rationale")
        for d in DIMENSIONS:
            if r[d] not in {"0", "1", "2"}:
                raise ValueError("Complete all four rubric dimensions with integer 0, 1, or 2")
        record = records[(r["case_id"], r["provider"])]
        response = (run / record["artifact_dir"] / "response.txt").read_text(encoding="utf-8")
        root, beginner = sections(response)
        if (r["model"] != record["model"] or r["root_cause_text"] != root or r["beginner_text"] != beginner):
            raise ValueError("Rating model or explanation text differs from the saved response")
        if not r["evidence_quote"] or r["evidence_quote"] not in response:
            raise ValueError("Evidence quote must be an exact substring of the saved response")
        r["total_out_of_8"] = sum(int(r[d]) for d in DIMENSIONS)
        scored.append(r)
    destination = new_run(run.parent.parent / "explanation_reviews", "scored")
    if scored:
        save_csv(destination / "scored_ratings.csv", scored)
    summaries = []
    for provider, rater, kind in sorted({(r["provider"], r["rater"], r["rater_type"]) for r in scored}):
        subset = [r for r in scored if (r["provider"], r["rater"], r["rater_type"]) == (provider, rater, kind)]
        summaries.append({"provider": provider, "rater": rater, "rater_type": kind, "rated_responses": len(subset),
                          "available_responses": sum(k[1] == provider for k in records),
                          **{d: sum(int(r[d]) for r in subset) / len(subset) for d in DIMENSIONS},
                          "mean_total_out_of_8": sum(r["total_out_of_8"] for r in subset)/len(subset)})
    save_json(destination / "summary.json", summaries)
    if summaries:
        save_csv(destination / "summary.csv", summaries)
    save_text(destination / "ratings_source.csv", ratings_path.read_text(encoding="utf-8-sig"))
    save_json(destination / "source.json", {"source_run": str(run.resolve()), "ratings_file": str(ratings_path.resolve()),
                  "unrated_responses": len(records) - len(scored), "rubric": "docs/EXPLANATION_RUBRIC.md"})
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run", type=Path)
    parser.add_argument("--ratings", type=Path)
    parser.add_argument("--output-root", type=Path, help="Worksheet root, useful for nested Gemini run shards")
    args = parser.parse_args()
    print(evaluate(args.run, args.ratings) if args.ratings else export(args.run, args.output_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
