"""No paid API requests. Provider tests use mocks; controls are explicitly authored."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import benchmark_runner as runner
from bug_explainer import extract_patched_code
from evidence import new_run, save_csv, save_text
from repair_providers import ProviderError, Reply, classify_exception, generate, make_prompt
from runtime_support import evaluate_java, execute, failure_context
from summarize_results import metrics, read_records
from validate_benchmarks import oracle, reference_source


class EvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases, cls.hidden = runner.load_cases()

    def test_twenty_cases_oracles_and_split(self):
        self.assertEqual(20, len(self.cases))
        self.assertEqual(58, sum(map(len, self.hidden.values())))
        for case in self.cases:
            tests = runner.split_tests(case, self.hidden)
            for test in tests:
                self.assertEqual(test['expected'], oracle(case['case_id'], test['input']))
        self.assertEqual({'syntax': 4, 'logic': 14, 'runtime': 2},
                         {c: sum(x['bug_type'].startswith(c) for x in self.cases) for c in ('syntax', 'logic', 'runtime')})

    def test_patch_parser_rejects_empty_and_malformed(self):
        for response in ('', '```java\nclass X{}\n```', 'PATCHED CODE:\n```java\n \n```'):
            self.assertIsNone(extract_patched_code(response))
        self.assertEqual('class X{}\n', extract_patched_code('PATCHED CODE:\n```java\nclass X{}\n```'))

    def test_unique_runs_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            a, b = new_run(Path(td), 'test'), new_run(Path(td), 'test')
            self.assertNotEqual(a, b)
            save_text(a / 'response.txt', 'first')
            with self.assertRaises(FileExistsError): save_text(a / 'response.txt', 'second')
            self.assertEqual('first', (a / 'response.txt').read_text())

    def test_explicit_denominators(self):
        base = dict(provider='test', model='mock', category='logic', status='successful_repair',
                    request_made=True, response_received=True, repair_attempted=True,
                    patch_compile_success=True, test_success=True, response_seconds=2)
        rows = [base, dict(base, status='api_quota_failure', response_received=False,
                          repair_attempted=False, patch_compile_success=None, test_success=None, response_seconds=1),
                dict(base, status='invalid_response', repair_attempted=False,
                     patch_compile_success=None, test_success=None, response_seconds=4),
                dict(base, status='configuration_unavailable', request_made=False, response_received=False,
                     repair_attempted=False, patch_compile_success=None, test_success=None, response_seconds=None)]
        result = metrics(rows)[0]
        self.assertEqual(1, result['repair_attempts'])
        self.assertEqual(3, result['requests_made'])
        self.assertEqual(2/3, result['service_availability'])
        self.assertEqual(3, result['mean_successful_response_seconds'])
        self.assertEqual(1, result['functional_success_rate'])

    def test_error_classification(self):
        for code, expected in [(429, 'api_quota_failure'), (503, 'api_service_error'),
                               (401, 'api_access_error'), (404, 'api_access_error')]:
            error = RuntimeError('test error')
            error.status_code = code
            self.assertEqual(expected, classify_exception(error).status)

    def test_hidden_output_not_in_prompt(self):
        case = self.cases[4]
        source = (runner.BENCHMARK_DIR / case['source']).read_text()
        visible = evaluate_java(source, case['source'], case['tests'])
        prompt = make_prompt(source, 'java', failure_context(visible))
        self.assertNotIn('100 -99', json.dumps(prompt))
        self.assertNotIn('wrong_operator', json.dumps(prompt))
        self.assertNotIn('Addition implemented', json.dumps(prompt))
        self.assertNotIn('REFERENCE_EDITS', json.dumps(prompt))

    def test_wrong_compiling_program_fails_hidden_tests(self):
        case = self.cases[4]
        hardcoded = 'public class J05 { public static void main(String[] a) { System.out.println(12); } }'
        evaluation = evaluate_java(hardcoded, case['source'], runner.split_tests(case, self.hidden))
        self.assertTrue(evaluation['compilation']['success'])
        self.assertFalse(evaluation['functional_success'])
        self.assertTrue(any(t['split'] == 'hidden' and not t['success'] for t in evaluation['tests']))

    def test_compilation_failure_is_distinct(self):
        evaluation = evaluate_java('public class Bad {', 'Bad.java', [{'input':'','expected':''}])
        self.assertFalse(evaluation['compilation']['success'])
        self.assertEqual([], evaluation['tests'])

    def test_process_timeout(self):
        import sys
        with tempfile.TemporaryDirectory() as td:
            output = execute([sys.executable, '-c', 'while True: pass'], Path(td), timeout=0.2)
        self.assertTrue(output['timed_out'])
        self.assertIsNone(output['returncode'])

    def test_api_error_and_invalid_not_repairs(self):
        case = self.cases[0]
        source = (runner.BENCHMARK_DIR / case['source']).read_text()
        original = evaluate_java(source, case['source'], case['tests'])
        for name, response, expected in [('quota', ProviderError('api_quota_failure', 'quota', request_made=True), 'api_quota_failure'),
                                         ('invalid', Reply('  no patch\n', {'text':'  no patch\n'}, 'mock'), 'invalid_response')]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as td:
                run = new_run(Path(td), 'test')
                mock_args = {'side_effect':response} if isinstance(response, Exception) else {'return_value':response}
                with patch('benchmark_runner.generate', **mock_args):
                    row = runner.run_provider(case, 'gemini', 'mock', run, self.hidden, original)
                save_csv(run/'results.csv', [row])
                self.assertEqual(expected, row['status'])
                self.assertFalse(row['repair_attempted'])
                self.assertIsNone(row['patch_compile_success'])
                self.assertEqual([row], read_records(run))
                if name == 'invalid':
                    self.assertEqual(response.text, (run/row['artifact_dir']/'response.txt').read_text())

    def test_reference_control_is_not_baseline(self):
        from bug_explainer import demo_response
        source = (runner.BENCHMARK_DIR / 'J05.java').read_text()
        baseline = extract_patched_code(demo_response(source, 'java', 'test failure'))
        self.assertEqual(source, baseline)
        self.assertNotEqual(source, reference_source('J05', source))

    def test_cloud_sdk_request_contracts_without_network(self):
        prompt = make_prompt('class X {}', 'java', 'failure')
        try:
            import openai
            from google import genai
        except ImportError:
            self.skipTest('Install requirements.txt for SDK contract tests')
        for provider, target in [('openai', 'openai.OpenAI'), ('gemini', 'google.genai.Client')]:
            response = MagicMock()
            response.output_text = response.text = ' exact text\n'
            response.model = response.model_version = 'resolved-test-model'
            response.model_dump.return_value = {'text': ' exact text\n'}
            client = MagicMock()
            client.responses.create.return_value = response
            client.models.generate_content.return_value = response
            with self.subTest(provider=provider), patch.dict('os.environ',
                    {'GEMINI_API_KEY':'test-placeholder', 'OPENAI_API_KEY':'test-placeholder'}), \
                    patch(target) as factory:
                factory.return_value.__enter__.return_value = client
                reply = generate(provider, 'test-model', prompt, max_tokens=1024, timeout=30)
                self.assertEqual(' exact text\n', reply.text)
                method = client.responses.create if provider == 'openai' else client.models.generate_content
                kwargs = method.call_args.kwargs.copy()
                if provider == 'gemini':
                    kwargs['config'] = kwargs['config'].model_dump(exclude_none=True)
                    self.assertEqual(1, factory.call_args.kwargs['http_options'].retry_options.attempts)
                else:
                    self.assertEqual(0, factory.call_args.kwargs['max_retries'])
                self.assertEqual(runner.request_payload(provider, 'test-model', prompt, 1024), kwargs)

    def test_circuit_breaker_makes_only_one_failed_api_call(self):
        with tempfile.TemporaryDirectory() as td:
            args = ['benchmark_runner.py', '--providers', 'gemini', '--limit', '3',
                    '--allow-live', '--max-requests', '3', '--results-root', td]
            error = ProviderError('api_quota_failure', 'mock quota', request_made=True)
            with patch('sys.argv', args), patch('benchmark_runner.preflight', return_value={'available': True}), \
                 patch('benchmark_runner.generate', side_effect=error) as provider:
                self.assertEqual(0, runner.main())
            self.assertEqual(1, provider.call_count)
            run = next(Path(td).iterdir())
            rows = read_records(run)
            self.assertEqual(['api_quota_failure', 'skipped_after_api_error', 'skipped_after_api_error'],
                             [r['status'] for r in rows])

    def test_child_process_does_not_receive_api_key(self):
        import sys
        with tempfile.TemporaryDirectory() as td, patch.dict('os.environ', {'GEMINI_API_KEY':'test-placeholder'}):
            output = execute([sys.executable, '-c', "import os; print('GEMINI_API_KEY' in os.environ)"], Path(td))
        self.assertEqual('False', output['stdout'].strip())


if __name__ == '__main__':
    unittest.main()
