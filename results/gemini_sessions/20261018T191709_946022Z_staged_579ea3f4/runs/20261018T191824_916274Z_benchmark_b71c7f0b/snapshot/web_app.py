"""Loopback-only patch review UI. Cloud generation is deliberately unavailable.

Run with Python 3.10+: python web_app.py, then open http://127.0.0.1:8365.
Only the project's trusted 20 Java cases are available. Retesting executes Java
with local user permissions; this is a local teaching prototype, not a sandbox
for hostile code or a public hosting service.
"""
from __future__ import annotations

import argparse
import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from benchmark_runner import load_cases, run_provider, split_tests
from bug_explainer import extract_patched_code, make_diff
from evidence import ROOT, new_run, save_csv, save_json, save_text, seal, sha256
from repair_providers import DEFAULT_MODELS, LOCAL_MODEL, redact
from runtime_support import evaluate_java
from summarize_results import read_records

CASES, HIDDEN = load_cases()
CASE_MAP = {c['case_id']: c for c in CASES}
WORK_LOCK = threading.Lock()


def saved_qwen_run():
    index = json.loads((ROOT / 'docs' / 'handoff_sources.json').read_text(encoding='utf-8'))
    return ROOT / index['primary_run']


def explain(case_id: str, provider: str) -> dict:
    case = CASE_MAP[case_id]
    source = (ROOT / 'benchmarks' / case['source']).read_text(encoding='utf-8')
    if provider == 'saved_qwen':
        run = saved_qwen_run()
        row = next(r for r in read_records(run) if r['case_id'] == case_id and r['provider'] == 'llama_cpp')
        folder = run / row['artifact_dir']
        if (folder / 'original.java').read_text(encoding='utf-8') != source:
            raise ValueError('Replay source does not match current benchmark')
        response = (folder / 'response.txt').read_text(encoding='utf-8')
        return {'mode': 'SAVED QWEN RESPONSE - replay; no new model request',
                'response': response, 'patch': extract_patched_code(response),
                'diff': (folder / 'patch.diff').read_text(encoding='utf-8') if row['repair_attempted'] else '',
                'validation': json.loads((folder / 'validation.json').read_text(encoding='utf-8')),
                'evidence': str(folder.relative_to(ROOT)), 'response_seconds': row['response_seconds']}
    if provider not in {'demo', 'llama_cpp'}:
        raise ValueError('Choose baseline, saved Qwen replay, or live local Qwen. Cloud requests are disabled.')
    output = new_run(ROOT / 'results' / 'web_reviews', 'generation')
    save_json(output / 'config.json', {'purpose': 'interactive_generation_not_primary_experiment',
              'case_id': case_id, 'provider': provider, 'max_output_tokens': 2048, 'cloud_requests': 0})
    original = evaluate_java(source, case['source'], [dict(t, split='visible') for t in case['tests']])
    row = run_provider(case, provider, DEFAULT_MODELS['demo'] if provider == 'demo' else LOCAL_MODEL,
                       output, HIDDEN, original, timeout=120)
    save_csv(output / 'results.csv', [row])
    seal(output)
    folder = output / row['artifact_dir']
    response = (folder / 'response.txt').read_text(encoding='utf-8') if row['response_received'] else ''
    return {'mode': 'FRESH LOCAL GENERATION', 'response': response, 'patch': extract_patched_code(response),
            'diff': (folder / 'patch.diff').read_text(encoding='utf-8') if row['repair_attempted'] else '',
            'validation': json.loads((folder / 'validation.json').read_text(encoding='utf-8')),
            'evidence': str(folder.relative_to(ROOT)), 'status': row['status'], 'error': row['error'],
            'response_seconds': row['response_seconds']}


def retest(case_id: str, patch: str) -> dict:
    if not isinstance(patch, str) or not patch.strip() or len(patch) > 20000 or len(patch.splitlines()) > 100:
        raise ValueError('Patch must contain 1-100 lines and at most 20,000 characters')
    case = CASE_MAP[case_id]
    output = new_run(ROOT / 'results' / 'web_reviews', 'human_retest')
    original = (ROOT / 'benchmarks' / case['source']).read_text(encoding='utf-8')
    save_json(output / 'config.json', {'purpose': 'user_approved_patch_retest_not_model_result',
              'case_id': case_id, 'cloud_requests': 0,
              'note': 'Approval is the UI button action; no claim of independent human ratings'})
    save_text(output / 'original.java', original)
    save_text(output / 'patch' / case['source'], patch)
    save_text(output / 'patch.diff', make_diff(original, patch, case['source']))
    tests = split_tests(case, HIDDEN)
    save_json(output / 'evaluation_tests.json', tests)
    result = evaluate_java(patch, case['source'], tests)
    save_json(output / 'validation.json', result)
    seal(output)
    return {'validation': result, 'diff': make_diff(original, patch, case['source']),
            'evidence': str(output.relative_to(ROOT)) if output.is_relative_to(ROOT) else str(output),
            'mode': 'USER PATCH RETEST - excluded from benchmark results'}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def valid_host(self):
        port = self.server.server_port
        return self.headers.get('Host') in {f'127.0.0.1:{port}', f'localhost:{port}'}

    def send_body(self, status, body: bytes, mime: str):
        self.send_response(status)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; style-src 'self'; script-src 'self'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, value):
        self.send_body(status, json.dumps(value).encode('utf-8'), 'application/json; charset=utf-8')

    def do_GET(self):
        if not self.valid_host():
            return self.send_json(403, {'error': 'Loopback Host required'})
        if self.path == '/api/cases':
            return self.send_json(200, [{'case_id': c['case_id'], 'title': c['title'], 'category': c['bug_type'].split(':')[0],
                        'source': (ROOT / 'benchmarks' / c['source']).read_text(encoding='utf-8')} for c in CASES])
        files = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
                 '/style.css': ('style.css', 'text/css')}
        if self.path not in files:
            return self.send_json(404, {'error': 'Not found'})
        name, mime = files[self.path]
        self.send_body(200, (ROOT / 'web' / name).read_bytes(), mime + '; charset=utf-8')

    def do_POST(self):
        port = self.server.server_port
        origins = {f'http://127.0.0.1:{port}', f'http://localhost:{port}'}
        if (not self.valid_host() or self.headers.get('Origin') not in origins
                or self.headers.get('X-Local-Review') != '1'
                or self.headers.get('Content-Type', '').split(';')[0] != 'application/json'):
            return self.send_json(403, {'error': 'Local application request required'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 80000:
                raise ValueError('Request size outside limit')
            data = json.loads(self.rfile.read(length))
            if data.get('case_id') not in CASE_MAP:
                raise ValueError('Unknown benchmark case')
            with WORK_LOCK:
                if self.path == '/api/explain':
                    result = explain(data['case_id'], data.get('provider', 'demo'))
                elif self.path == '/api/retest':
                    result = retest(data['case_id'], data.get('patch'))
                else:
                    return self.send_json(404, {'error': 'Not found'})
            self.send_json(200, result)
        except (ValueError, KeyError, TypeError) as exc:
            self.send_json(400, {'error': redact(str(exc))})
        except Exception as exc:
            self.send_json(500, {'error': redact(str(exc))})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8365)
    args = parser.parse_args()
    with ThreadingHTTPServer(('127.0.0.1', args.port), Handler) as server:
        print(f'Local review: http://127.0.0.1:{server.server_port} (Ctrl+C to stop)', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    main()
