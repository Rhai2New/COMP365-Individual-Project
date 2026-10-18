"""Inventory historical CSV claims without upgrading them into validated findings."""
from __future__ import annotations

import csv
import json
from pathlib import Path

from evidence import ROOT, new_run, save_csv, save_json, save_text


def main() -> int:
    source = ROOT / "results" / "historical_checkpoint2_checkout" / "results"
    output = new_run(ROOT / "results" / "historical_audits", "csv_inventory")
    rows, successful_cases = [], set()
    for path in sorted(source.glob("*.csv")):
        with path.open(newline="", encoding="utf-8-sig") as handle:
            records = list(csv.DictReader(handle))
        for index, record in enumerate(records, 2):
            if record.get("provider") != "gemini":
                continue
            case_id = record["case_id"]
            claim = record.get("test_success") == "True"
            if claim:
                successful_cases.add(case_id)
            response = source / "outputs" / f"{case_id}_gemini.txt"
            text = response.read_text(encoding="utf-8") if response.exists() else ""
            rows.append({"file": path.name, "csv_line": index, "case_id": case_id,
                         "model_as_recorded": record.get("model", ""),
                         "csv_claims_test_success": claim, "error_present": bool(record.get("error")),
                         "response_file_exists": response.exists(), "saved_file_has_patch_block": "PATCHED CODE:" in text,
                         "saved_file_has_quota_error": "429" in text or "RESOURCE_EXHAUSTED" in text,
                         "evidence_status": "historical_unverified_not_a_new_experiment"})
    save_csv(output / "gemini_csv_inventory.csv", rows)
    save_json(output / "summary.json", {"historical_csv_success_case_ids": sorted(successful_cases),
              "historical_csv_distinct_success_count": len(successful_cases),
              "success_claim_rows": sum(r["csv_claims_test_success"] for r in rows),
              "preserved_response_files_containing_patches": sum("PATCHED CODE:" in p.read_text(encoding="utf-8")
                  for p in (source / "outputs").glob("*_gemini.txt")),
              "validated_live_gemini_repairs_in_this_session": 0,
              "reported_eight_successes": "unverified historical claim; not reproduced"})
    save_text(output / "notes.md", "# Historical evidence inventory\n\n"
              "CSV success claims cover J01, J02, and J03. J01 appears in two successful CSV rows. "
              "The copied Gemini output files contain quota errors rather than the successful patches. "
              "A later 20-case CSV contains 20 Gemini error rows and zero successes. "
              "These files cannot establish an eight-repair result or its claimed mean latency. "
              "They are preserved unchanged, excluded from current-run tables, and not used as live model evidence.\n")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
