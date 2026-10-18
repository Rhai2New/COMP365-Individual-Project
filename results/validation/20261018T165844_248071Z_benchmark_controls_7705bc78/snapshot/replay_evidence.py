"""Recompile and retest saved patches without calling any model or cloud API."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from evidence import ROOT, environment, new_run, save_json, seal
from runtime_support import evaluate_java
from summarize_results import read_records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path)
    args = parser.parse_args()
    rows = read_records(args.run)
    output = new_run(ROOT / 'results' / 'replays', 'saved_patches')
    save_json(output / 'config.json', {'source_run': str(args.run), 'environment': environment(),
                                     'purpose': 'verification_only_not_new_model_outputs'})
    checks = []
    for row in rows:
        if not row['repair_attempted']:
            continue
        folder = args.run / row['artifact_dir']
        tests = json.loads((folder / 'evaluation_tests.json').read_text(encoding='utf-8'))
        actual = evaluate_java((folder / 'patch' / row['source']).read_text(encoding='utf-8'), row['source'], tests)
        saved = json.loads((folder / 'validation.json').read_text(encoding='utf-8'))
        ok = (actual['compilation']['success'] == saved['compilation']['success']
              and actual['functional_success'] == saved['functional_success']
              and [t['success'] for t in actual['tests']] == [t['success'] for t in saved['tests']]
              and not actual['infrastructure_error'])
        save_json(output / row['case_id'] / row['provider'] / 'evaluation.json', actual)
        checks.append({'case_id': row['case_id'], 'provider': row['provider'], 'matches_saved_outcomes': ok})
        print(row['case_id'], row['provider'], 'matches:', ok, flush=True)
    passed = bool(checks) and all(c['matches_saved_outcomes'] for c in checks)
    save_json(output / 'summary.json', {'passed': passed, 'patches_replayed': len(checks), 'checks': checks})
    seal(output)
    print('Replay evidence:', output)
    return 0 if passed else 1


if __name__ == '__main__':
    raise SystemExit(main())
