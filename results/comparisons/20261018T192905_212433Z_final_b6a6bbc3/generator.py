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


def comparison(primary: Path, gemini: Path | list[Path], destination: Path) -> list[dict]:
    legacy = isinstance(gemini, Path)
    gemini_runs = [gemini] if legacy else gemini
    rows = [r for r in read_records(primary) if r['provider'] in {'demo', 'llama_cpp'}]
    rows += [r for run in gemini_runs for r in read_records(run) if r['provider'] == 'gemini']
    if len(rows) != 60 or len({(r['provider'], r['case_id']) for r in rows}) != 60:
        raise ValueError('Require exactly one observation per case and system, 20 cases and three systems')
    paths = {run.name: run for run in [primary, *gemini_runs]}
    for n in range(1, 21):
        subset = [r for r in rows if r['case_id'] == f'J{n:02d}']
        for filename in ('original.java', 'prompt.json', 'evaluation_tests.json'):
            digests = {sha256(paths[r['run_id']] / r['artifact_dir'] / filename) for r in subset}
            if len(digests) != 1:
                raise ValueError(f'Comparison conditions differ: J{n:02d} / {filename}')
    configs = [json.loads((p / 'config.json').read_text(encoding='utf-8')) for p in (primary, *gemini_runs)]
    if len({c['max_output_tokens'] for c in configs}) != 1:
        raise ValueError('Output limits differ')
    summary = metrics(rows)
    save_json(destination / 'metrics.json', summary)
    save_csv(destination / 'metrics.csv', summary)
    save_text(destination / 'tables.md', table(summary))
    save_csv(destination / 'case_results.csv', [{**r, 'source_evidence':
        (paths[r['run_id']] / r['artifact_dir']).relative_to(ROOT).as_posix()} for r in rows])
    save_csv(destination / 'figure_ready_data.csv', [{k: m[k] for k in ('provider', 'model', 'category',
        'scheduled_cases', 'responses_received', 'repair_attempts', 'compile_successes',
        'visible_test_successes', 'hidden_test_successes', 'functional_successes',
        'invalid_responses', 'mean_successful_response_seconds')} for m in summary])
    def source(p):
        return {'run': p.relative_to(ROOT).as_posix(), 'seal_sha256': sha256(p / 'artifact_sha256.json')}
    sources = {'demo': source(primary), 'llama_cpp': source(primary),
               'gemini': source(gemini_runs[0]) if legacy else {'runs': [source(p) for p in gemini_runs]}}
    cloud = [r for r in rows if r['provider'] == 'gemini']
    note = ('Gemini is configured but unevaluated. Its model ID is unverified; no generation requests.' if legacy else
            f"Gemini: {sum(r['request_made'] for r in cloud)} submitted requests, "
            f"{sum(r['response_received'] for r in cloud)} delivered responses, "
            f"{sum(not r['request_made'] for r in cloud)} cases skipped. Access failures are not repair failures.")
    save_json(destination / 'sources.json', {'sources': sources, 'identical_source_prompt_tests_verified': True,
         'comparison_note': note,
         'excluded': 'Historical claims, authored controls, replays, UI edits, duplicate runs'})
    save_text(destination / 'generator.py', Path(__file__).read_text(encoding='utf-8'))
    seal(destination)
    return summary


def verify_comparison(directory: Path, root: Path = ROOT) -> None:
    """Recompute CSVs/tables from sealed input runs without rewriting outputs."""
    import tempfile
    source = json.loads((directory / 'sources.json').read_text(encoding='utf-8'))
    for provider in source['sources'].values():
        for entry in provider.get('runs', [provider]):
            if sha256(root / entry['run'] / 'artifact_sha256.json') != entry['seal_sha256']:
                raise ValueError('Comparison source seal differs')
    for name, digest in json.loads((directory / 'artifact_sha256.json').read_text(encoding='utf-8')).items():
        if sha256(directory / name) != digest:
            raise ValueError('Comparison artifact hash differs: ' + name)
    # comparison() uses module ROOT to generate relative links. Temporarily load
    # the generator from the extracted project when checking a packaged copy.
    if root != ROOT:
        import subprocess, sys
        proc = subprocess.run([sys.executable, str(root / 'finalize_results.py'), '--check', str(directory)],
                              cwd=root, capture_output=True, text=True)
        if proc.returncode:
            raise ValueError('Extracted comparison reproduction failed: ' + proc.stderr)
        return
    with tempfile.TemporaryDirectory(prefix='comp365_comparison_check_') as td:
        regenerated = Path(td)
        cloud_source = source['sources']['gemini']
        gemini = ([root / entry['run'] for entry in cloud_source['runs']] if 'runs' in cloud_source else
                  root / cloud_source['run'])
        comparison(root / source['sources']['demo']['run'], gemini, regenerated)
        for name in ('metrics.json', 'metrics.csv', 'tables.md', 'case_results.csv', 'figure_ready_data.csv', 'sources.json'):
            if (directory / name).read_bytes() != (regenerated / name).read_bytes():
                raise ValueError('Comparison cannot be reproduced: ' + name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--primary', type=Path, default=ROOT / PRIMARY)
    parser.add_argument('--gemini', type=Path, action='append', help='Repeat for smoke and remaining-case shards')
    parser.add_argument('--check', type=Path)
    args = parser.parse_args()
    if args.check:
        verify_comparison(args.check.resolve())
        print('PASS: comparison, source seals, all CSVs, and figure data reproduce exactly')
        return 0
    destination = new_run(ROOT / 'results' / 'comparisons', 'final')
    selected = args.gemini
    if selected is None:
        index = json.loads((ROOT / 'docs/handoff_sources.json').read_text(encoding='utf-8'))
        selected = [ROOT / p for p in index.get('gemini_runs', [GEMINI])]
    comparison(args.primary.resolve(), [p.resolve() for p in selected], destination)
    print(destination)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
