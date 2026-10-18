"""Local review security and functional behavior; all generation is offline."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import web_app
from evidence import new_run, sha256


class ReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), web_app.Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def post(self, endpoint, data, origin=None):
        request = urllib.request.Request(self.url + endpoint, data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json', 'X-Local-Review': '1', 'Origin': origin or self.url})
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)

    def test_cases_and_static_routes(self):
        with urllib.request.urlopen(self.url + '/api/cases') as response:
            self.assertEqual(20, len(json.load(response)))
        with urllib.request.urlopen(self.url + '/') as response:
            page = response.read().decode()
            self.assertIn('Approve current patch and retest', page)
            self.assertIn("frame-ancestors 'none'", response.headers['Content-Security-Policy'])
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(self.url + '/../../repair_providers.py')
        self.assertEqual(404, error.exception.code)

    def test_cross_origin_and_cloud_generation_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post('/api/retest', {'case_id': 'J01', 'patch': 'x'}, 'https://example.com')
        self.assertEqual(403, error.exception.code)
        with self.assertRaises(ValueError):
            web_app.explain('J01', 'gemini')

    def test_edit_retest_preserves_source_and_experiment(self):
        source = web_app.ROOT / 'benchmarks' / 'J05.java'
        before = sha256(source)
        correct = source.read_text().replace('a - b', 'a + b')
        wrong = 'public class J05 {public static void main(String[] a){System.out.println(12);}}'
        with tempfile.TemporaryDirectory() as td, patch('web_app.new_run',
                side_effect=lambda *args: new_run(Path(td), 'review_test')):
            failure = self.post('/api/retest', {'case_id': 'J05', 'patch': wrong})
            success = self.post('/api/retest', {'case_id': 'J05', 'patch': correct})
            self.assertFalse(failure['validation']['functional_success'])
            self.assertTrue(success['validation']['functional_success'])
            self.assertTrue(any(t['split'] == 'hidden' and not t['success'] for t in failure['validation']['tests']))
            self.assertEqual(2, len(list(Path(td).iterdir())))
        self.assertEqual(before, sha256(source))

    def test_saved_replay_keeps_exact_response(self):
        result = web_app.explain('J01', 'saved_qwen')
        self.assertIn('replay', result['mode'])
        folder = web_app.ROOT / result['evidence']
        self.assertEqual((folder / 'response.txt').read_text(encoding='utf-8'), result['response'])


if __name__ == '__main__':
    unittest.main()
