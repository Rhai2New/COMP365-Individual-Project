"""Generate a traceable comparison from explicitly selected saved runs.

Never pool repeated historical observations or edit the source experiment files.
This is technical data, not research-paper prose.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from evidence import ROOT, new_run, save_csv, save_json, save_text, seal, sha256
from summarize_results import metrics, read_records, table

PRIMARY = 'results/runs/20261018T131412_396245Z_benchmark_41bb2533'
GEMINI = 'results/runs/20261018T153859_032470Z_benchmark_60bcc2f4'


def comparison(primary: Path, gemini: Path, destination: Path) -> list[dict]:
    rows = [r for r in read_records(primary) if r['provider'] in {'demo', 'llama_cpp'}]
    rows += [r for r in read_records(gemini) if r['provider'] == 'gemini']
    if len(rows) != 60 or len({(r['provider'], r['case_id']) for r in rows}) != 60:
        raise ValueError('Require exactly one observation per case and system, 20 cases and three systems')
    paths = {'demo': primary, 'llama_cpp': primary, 'gemini': gemini}
    for n in range(1, 21):
        subset = [r for r in rows if r['case_id'] == f'J{n:02d}']
        for filename in ('original.java', 'prompt.json', 'evaluation_tests.json'):
            digests = {sha256(paths[r['provider']] / r['artifact_dir'] / filename) for r in subset}
            if len(digests) != 1:
                raise ValueError(f'Comparison conditions differ: J{n:02d} / {filename}')
    configs = [json.loads((p / 'config.json').read_text(encoding='utf-8')) for p in (primary, gemini)]
    if len({c['max_output_tokens'] for c in configs}) != 1:
        raise ValueError('Output limits differ')
    summary = metrics(rows)
    save_json(destination / 'metrics.json', summary)
    save_csv(destination / 'metrics.csv', summary)
    save_text(destination / 'tables.md', table(summary))
    save_csv(destination / 'case_results.csv', [{**r, 'source_evidence':
        (paths[r['provider']] / r['artifact_dir']).relative_to(ROOT).as_posix()} for r in rows])
    save_csv(destination / 'figure_ready_data.csv', [{k: m[k] for k in ('provider', 'model', 'category',
        'scheduled_cases', 'responses_received', 'repair_attempts', 'compile_successes',
        'visible_test_successes', 'hidden_test_successes', 'functional_successes',
        'invalid_responses', 'mean_successful_response_seconds')} for m in summary])
    sources = {name: {'run': p.relative_to(ROOT).as_posix(), 'seal_sha256': sha256(p / 'artifact_sha256.json')}
               for name, p in paths.items()}
    save_json(destination / 'sources.json', {'sources': sources, 'identical_source_prompt_tests_verified': True,
         'comparison_note': 'Gemini is configured but unevaluated. Its model ID is unverified; no generation requests.',
         'excluded': 'Historical claims, authored controls, replays, UI edits, duplicate runs'})
    save_text(destination / 'generator.py', Path(__file__).read_text(encoding='utf-8'))
    seal(destination)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--primary', type=Path, default=ROOT / PRIMARY)
    parser.add_argument('--gemini', type=Path, default=ROOT / GEMINI)
    args = parser.parse_args()
    destination = new_run(ROOT / 'results' / 'comparisons', 'final')
    comparison(args.primary.resolve(), args.gemini.resolve(), destination)
    print(destination)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
