"""Reject evidence corruption and explanation-rating provenance drift."""
import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evidence import ROOT, new_run, save_csv, save_json
from explanation_review import DIMENSIONS, evaluate, export
from summarize_results import read_records


class IntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.primary = ROOT / json.loads((ROOT / 'docs/handoff_sources.json').read_text())['primary_run']

    def copy_record(self, root):
        run = new_run(root, 'integrity')
        row = next(r for r in read_records(self.primary) if r['case_id'] == 'J01' and r['provider'] == 'demo')
        shutil.copytree(self.primary / row['artifact_dir'], run / row['artifact_dir'])
        row['run_id'] = run.name
        folder = run / row['artifact_dir']
        (folder / 'record.json').write_text(json.dumps(row))
        (folder / 'record.csv').unlink()
        save_csv(folder / 'record.csv', [row])
        save_csv(run / 'results.csv', [row])
        return run, folder, row

    def test_modified_patch_rejected_without_relying_on_hashes(self):
        with tempfile.TemporaryDirectory() as td:
            run, folder, row = self.copy_record(Path(td))
            read_records(run)
            (folder / 'patch' / row['source']).write_text('public class J01 {}\n')
            with self.assertRaisesRegex(ValueError, 'Patch or diff'):
                read_records(run)

    def test_split_success_cannot_drift_from_process_records(self):
        with tempfile.TemporaryDirectory() as td:
            run, folder, row = self.copy_record(Path(td))
            row['hidden_test_success'] = False
            (folder / 'record.json').write_text(json.dumps(row))
            (folder / 'record.csv').unlink()
            save_csv(folder / 'record.csv', [row])
            with self.assertRaisesRegex(ValueError, 'Split result'):
                read_records(run)

    def test_rating_model_identity_is_verified(self):
        with tempfile.TemporaryDirectory() as td, patch('explanation_review.new_run',
                side_effect=lambda *args: new_run(Path(td), 'rating_test')):
            worksheet = export(self.primary) / 'ratings.csv'
            with worksheet.open(newline='', encoding='utf-8') as handle:
                rows = list(csv.DictReader(handle))
            row = rows[0]
            row.update(rater='test_only', rater_type='AI_assisted', rationale='provenance test',
                       evidence_quote=row['root_cause_text'], model='wrong-model')
            row.update({d:'0' for d in DIMENSIONS})
            ratings = Path(td) / 'wrong.csv'
            save_csv(ratings, [row])
            with self.assertRaisesRegex(ValueError, 'model or explanation text'):
                evaluate(self.primary, ratings)


if __name__ == '__main__':
    unittest.main()
