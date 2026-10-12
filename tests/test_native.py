import sys
import tempfile
import time
import unittest
from pathlib import Path

from lemqo import Rejection
from lemqo.native import MAX_OUTPUT_BYTES, run_backend


class NativeRunnerTests(unittest.TestCase):
    def run_program(self, source, seconds=5):
        with tempfile.TemporaryDirectory() as directory:
            work = Path(directory)
            program = work / "controlled-backend.py"
            program.write_text(source)
            return run_backend(Path(sys.executable), program, work, time.monotonic() + seconds)

    def test_completed_success(self):
        self.assertEqual(self.run_program('import sys; sys.stdout.buffer.write(b"hello\\n")'), b"hello\n")

    def test_exit_error_and_stderr_rejected(self):
        for program in ('raise SystemExit(1)', 'import sys; print("error",file=sys.stderr)'):
            with self.subTest(program=program), self.assertRaises(Rejection):
                self.run_program(program)

    def test_output_bound(self):
        with self.assertRaises(Rejection):
            self.run_program(f'import sys; sys.stdout.write("x" * {MAX_OUTPUT_BYTES + 4096})')

    def test_deadline_kills_process(self):
        start = time.monotonic()
        with self.assertRaises(Rejection) as error:
            self.run_program('import time; time.sleep(20)', seconds=1)
        self.assertEqual(error.exception.code, "lean-timeout")
        self.assertLess(time.monotonic() - start, 8)
