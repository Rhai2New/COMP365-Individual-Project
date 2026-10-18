"""Authentication configuration tests use temporary files and fake values only."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import repair_providers as providers
from prepare_submission import deliverable_files


class LocalCredentialTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        self.file = self.root / '.env'
        fixture = patch('repair_providers.LOCAL_ENV_PATH', self.file)
        fixture.start()
        self.addCleanup(fixture.stop)
        environment = patch.dict(os.environ, {'GEMINI_API_KEY': 'stale-test-value',
                                              'GOOGLE_API_KEY': 'stale-alias-test-value'})
        environment.start()
        self.addCleanup(environment.stop)

    def test_quotes_comments_bom_and_only_named_key(self):
        self.file.write_text('\ufeff# Local fixture\nOPENAI_API_KEY=ignored-test-value\n'
                             'export GEMINI_API_KEY = "local-test-value" # comment\n', encoding='utf-8')
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'unchanged-test-value'}):
            self.assertTrue(providers.load_saved_gemini_key())
            self.assertEqual('local-test-value', os.environ['GEMINI_API_KEY'])
            self.assertEqual('unchanged-test-value', os.environ['OPENAI_API_KEY'])

    def test_empty_local_value_blocks_stale_alias_and_network(self):
        self.file.write_text('GEMINI_API_KEY=\n')
        with patch('google.genai.Client') as client:
            with self.assertRaises(providers.ProviderError) as error:
                providers.generate('gemini', 'test-model', {'system': 'test', 'user': 'test'})
        client.assert_not_called()
        self.assertFalse(error.exception.request_made)
        self.assertIn('empty', str(error.exception))

    def test_reload_and_working_directory_independence(self):
        self.file.write_text('GEMINI_API_KEY=first-test-value\n')
        self.assertTrue(providers.load_saved_gemini_key())
        self.file.write_text('GEMINI_API_KEY=second-test-value\n')
        other = self.root / 'other'
        other.mkdir()
        previous = Path.cwd()
        try:
            os.chdir(other)
            self.assertTrue(providers.load_saved_gemini_key())
            self.assertEqual('second-test-value', os.environ['GEMINI_API_KEY'])
        finally:
            os.chdir(previous)

    def test_invalid_files_fail_without_echoing_values(self):
        for content in ['GEMINI_API_KEY="private-test-value\n',
                        'GEMINI_API_KEY=private-test-value\nGEMINI_API_KEY=duplicate-test-value\n',
                        'GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE\n', 'GEMINI_API_KEY\n']:
            with self.subTest(content_type=content.split('=', 1)[0]):
                self.file.write_text(content)
                self.assertFalse(providers.load_saved_gemini_key())
                check = providers.preflight('gemini', 'test-model')
                self.assertFalse(check['available'])
                self.assertNotIn('private-test-value', check['reason'])

    def test_sdk_uses_local_value_and_errors_are_redacted(self):
        self.file.write_text('GEMINI_API_KEY=sdk-test-value\n')
        response = MagicMock(text='exact mock response', model_version='test-model')
        response.model_dump.return_value = {'mock': True}
        with patch('google.genai.Client') as factory:
            factory.return_value.__enter__.return_value.models.generate_content.return_value = response
            reply = providers.generate('gemini', 'test-model', {'system': 'test', 'user': 'test'})
        self.assertEqual('sdk-test-value', factory.call_args.kwargs['api_key'])
        self.assertEqual('exact mock response', reply.text)
        self.assertNotIn('sdk-test-value', providers.redact('failed sdk-test-value'))

    def test_local_env_and_backups_are_excluded_from_package(self):
        for name in ('.env', '.env.backup', '.env.local', '.env.example', 'README.md'):
            (self.root / name).write_text('fixture')
        with patch('prepare_submission.ROOT', self.root):
            names = {p.name for p in deliverable_files()}
        self.assertEqual({'.env.example', 'README.md'}, names)


if __name__ == '__main__':
    unittest.main()
