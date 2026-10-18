"""Free-tier-only staged Gemini evaluation: one smoke case, then remaining 19.

No retries or model fallback. A key does not establish billing status. Run only
after personally verifying this key's project is Free Tier with billing disabled.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from evidence import ROOT, new_run, save_json, seal
from repair_providers import load_saved_gemini_key
from summarize_results import read_records


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--model', required=True, help='Exact accessible text model ID; no guessed default')
    parser.add_argument('--free-tier-confirmed', action='store_true')
    args = parser.parse_args()
    if not args.free_tier_confirmed:
        parser.error('Verify the saved key project is Free Tier with billing disabled before running')
    if not load_saved_gemini_key():
        parser.error('No usable Gemini credential loaded; local .env may still be empty. No request made.')
    session = new_run(ROOT / 'results' / 'gemini_sessions', 'staged')
    runs = session / 'runs'
    command = [sys.executable, str(ROOT / 'benchmark_runner.py'), '--providers', 'gemini',
               '--gemini-model', args.model, '--allow-live', '--gemini-free-tier-confirmed',
               '--timeout', '120', '--max-tokens', '2048', '--gemini-min-interval', '65',
               '--results-root', str(runs)]
    smoke = subprocess.run([*command, '--case', 'J01', '--max-requests', '1'], cwd=ROOT)
    sources = sorted(runs.iterdir())
    delivered = bool(smoke.returncode == 0 and sources and
                     read_records(sources[0])[0]['response_received'])
    report = {'model': args.model, 'free_tier_attested': True, 'automatic_retries': 0,
              'smoke_response_delivered': delivered,
              'runs': [str(p.relative_to(ROOT)) for p in sources]}
    if delivered:
        # Preserve a conservative interval across the two subprocesses as well.
        time.sleep(65)
        remaining = [item for n in range(2, 21) for item in ('--case', f'J{n:02d}')]
        proc = subprocess.run([*command, '--max-requests', '19', *remaining], cwd=ROOT)
        report['remaining_batch_exit_code'] = proc.returncode
        report['runs'] = [str(p.relative_to(ROOT)) for p in sorted(runs.iterdir())]
    else:
        report['not_evaluated'] = [f'J{n:02d}' for n in range(2, 21)]
        report['reason'] = 'Smoke request did not return a response; no additional requests authorized by this helper'
        if sources:
            smoke_rows = read_records(sources[0])
            if smoke_rows and smoke_rows[0]['request_made']:
                remaining = [item for n in range(2, 21) for item in ('--case', f'J{n:02d}')]
                skipped = subprocess.run([sys.executable, str(ROOT / 'benchmark_runner.py'),
                    '--providers', 'gemini', '--gemini-model', args.model,
                    '--blocked-by-run', str(sources[0]), '--timeout', '120',
                    '--results-root', str(runs), *remaining], cwd=ROOT)
                report['skipped_records_exit_code'] = skipped.returncode
                report['runs'] = [str(p.relative_to(ROOT)) for p in sorted(runs.iterdir())]
    save_json(session / 'session.json', report)
    seal(session)
    print('Session evidence:', session)
    return 0 if delivered else 1


if __name__ == '__main__':
    raise SystemExit(main())
