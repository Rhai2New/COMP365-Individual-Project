"""Compare only cases with delivered responses from all three selected systems.

This conditional subset is descriptive, not an estimate for unavailable cases.
Invalid delivered outputs remain in the denominator. No API calls.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from evidence import ROOT, new_run, save_csv, save_json, save_text, seal, sha256
from finalize_results import verify_comparison
from summarize_results import metrics, read_records, table

PROVIDERS = {'demo', 'llama_cpp', 'gemini'}


def common_rows(rows: list[dict]) -> tuple[list[str], list[dict]]:
    if len({(r['provider'], r['case_id']) for r in rows}) != len(rows):
        raise ValueError('Duplicate case/system observations')
    delivered = {p: {r['case_id'] for r in rows if r['provider'] == p and r['response_received']}
                 for p in PROVIDERS}
    ids = sorted(set.intersection(*delivered.values()))
    return ids, [r for r in rows if r['provider'] in PROVIDERS and r['case_id'] in ids]


def generate(source: Path, destination: Path) -> None:
    verify_comparison(source)
    sources = json.loads((source / 'sources.json').read_text())['sources']
    primary = ROOT / sources['demo']['run']
    cloud = sources['gemini'].get('runs', [sources['gemini']])
    rows = [r for r in read_records(primary) if r['provider'] in {'demo', 'llama_cpp'}]
    rows += [r for item in cloud for r in read_records(ROOT / item['run']) if r['provider'] == 'gemini']
    ids, selected = common_rows(rows)
    if not ids:
        raise ValueError('No common delivered cases; no repair comparison available')
    summary = metrics(selected)
    save_json(destination / 'selection.json', {
        'source_comparison': source.relative_to(ROOT).as_posix(),
        'source_seal_sha256': sha256(source / 'artifact_sha256.json'),
        'case_ids': ids, 'cases_per_system': len(ids),
        'selection_rule': 'Delivered response from every system; invalid delivered outputs included',
        'limitation': 'Conditional observed subset; excludes unavailable cases; not full-suite Gemini performance or a randomized subset'})
    save_json(destination / 'metrics.json', summary)
    save_csv(destination / 'metrics.csv', summary)
    save_csv(destination / 'case_results.csv', selected)
    save_text(destination / 'tables.md', table(summary))
    seal(destination)


def verify(directory: Path) -> None:
    selection = json.loads((directory / 'selection.json').read_text())
    source = ROOT / selection['source_comparison']
    if sha256(source / 'artifact_sha256.json') != selection['source_seal_sha256']:
        raise ValueError('Source comparison seal changed')
    for name, digest in json.loads((directory / 'artifact_sha256.json').read_text()).items():
        if sha256(directory / name) != digest:
            raise ValueError('Available-case artifact hash changed')
    with tempfile.TemporaryDirectory(prefix='comp365_available_check_') as td:
        generated = Path(td)
        generate(source, generated)
        for name in ('selection.json', 'metrics.json', 'metrics.csv', 'case_results.csv', 'tables.md'):
            if (directory / name).read_bytes() != (generated / name).read_bytes():
                raise ValueError('Available-case results do not reproduce: ' + name)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', type=Path)
    parser.add_argument('--comparison', type=Path)
    args = parser.parse_args()
    if args.check:
        verify(args.check.resolve())
        print('PASS: common-case selection, metrics, CSVs, tables, and source evidence reproduce')
        return 0
    index = json.loads((ROOT / 'docs/handoff_sources.json').read_text())
    source = args.comparison or ROOT / index['comparison']
    output = new_run(ROOT / 'results/availability_comparisons', 'common_responses')
    generate(source.resolve(), output)
    print(output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
