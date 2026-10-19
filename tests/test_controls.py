"""Offline tests for the generic Linux process supervisor."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('bounded', ROOT/'scripts/run_bounded.py')
bounded = importlib.util.module_from_spec(spec); spec.loader.exec_module(bounded)


class Controls(unittest.TestCase):
    def run_command(self, text, **limits):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = bounded.run([sys.executable, '-c', text], root, root/'evidence',
                                 limits.get('seconds', 2), limits.get('disk', 1000000),
                                 limits.get('output', 10000), root, limits.get('file'))
            persisted = json.loads((root/'evidence/run.json').read_text())
            self.assertEqual(result, persisted)
            stdout = (root/'evidence/stdout.log').read_bytes()
            return result, stdout

    def test_success_and_failure_evidence(self):
        result, output = self.run_command("print('done')")
        self.assertEqual(result['status'], 'passed'); self.assertEqual(output, b'done\n')
        result, _ = self.run_command("raise SystemExit(7)")
        self.assertEqual(result['returncode'], 7); self.assertEqual(result['status'], 'failed')

    def test_timeout(self):
        result, _ = self.run_command('import time; time.sleep(30)', seconds=0.15)
        self.assertEqual(result['reason'], 'time_limit'); self.assertLess(result['seconds'], 2)

    def test_output_limit(self):
        result, output = self.run_command("print('x'*100000)", output=256)
        self.assertEqual(result['reason'], 'output_limit'); self.assertLessEqual(len(output), 256)

    def test_disk_limit(self):
        result, _ = self.run_command("from pathlib import Path; Path('large').write_bytes(b'x'*20000)", disk=10000)
        self.assertEqual(result['reason'], 'disk_limit')

    def test_candidate_size_limit(self):
        result, _ = self.run_command("from pathlib import Path; Path('candidate.sqlite3').write_bytes(b'x'*20000)", file=10000)
        self.assertEqual(result['reason'], 'file_limit')

    def test_descendant_timeout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            code="import subprocess,sys,time; from pathlib import Path; p=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'],start_new_session=True); Path('child').write_text(str(p.pid)); time.sleep(30)"
            result=bounded.run([sys.executable,'-c',code],root,root/'evidence',0.3,1000000,10000,root)
            self.assertEqual(result['reason'],'time_limit')
            stat=Path('/proc')/(root/'child').read_text()/'stat'
            if stat.exists(): self.assertEqual(stat.read_text().rsplit(')',1)[1].split()[0], 'Z')

    def test_evidence_cannot_be_reused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'evidence').mkdir()
            with self.assertRaises(FileExistsError):
                bounded.run([sys.executable,'-c','pass'],root,root/'evidence',1,10000,1000,root)

if __name__ == '__main__': unittest.main()
