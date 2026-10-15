import threading
import unittest

from lemqo.progress import Heartbeat


class ProgressTests(unittest.TestCase):
    def test_heartbeat_runs_while_work_waits_and_stops_on_exit(self):
        repeated = threading.Event()
        messages = []

        def progress(message):
            messages.append(message)
            if len(messages) >= 3:
                repeated.set()

        with Heartbeat(progress, interval=0.01) as heartbeat:
            heartbeat.update("Nanoda running on 66000 declarations (total)")
            self.assertTrue(repeated.wait(timeout=2))
        self.assertFalse(heartbeat.thread.is_alive())
        self.assertIn("66000", messages[-1])
        self.assertIn("elapsed", messages[-1])

    def test_invalid_intervals_are_rejected(self):
        for interval in (0, -1, True, float("inf"), float("nan")):
            with self.subTest(interval=interval), self.assertRaises(ValueError):
                Heartbeat(interval=interval)
