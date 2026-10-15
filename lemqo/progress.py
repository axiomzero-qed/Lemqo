"""Optional elapsed-time heartbeats; never invent kernel declaration progress."""

import threading
import time
import math


class Heartbeat:
    def __init__(self, callback=None, interval=10):
        if not isinstance(interval, (int, float)) or isinstance(interval, bool) or not math.isfinite(interval) or interval <= 0:
            raise ValueError("progress interval must be positive")
        self.callback = callback
        self.interval = interval
        self.started = time.monotonic()
        self.phase = "preparing"
        self.stopped = threading.Event()
        self.thread = None

    def emit(self):
        if self.callback is not None:
            self.callback(f"{self.phase}; elapsed {time.monotonic() - self.started:.1f}s")

    def update(self, phase):
        self.phase = phase
        self.emit()

    def __enter__(self):
        if self.callback is not None:
            self.emit()

            def pulse():
                while not self.stopped.wait(self.interval):
                    self.emit()

            self.thread = threading.Thread(target=pulse, daemon=True)
            self.thread.start()
        return self

    def __exit__(self, *_):
        self.stopped.set()
        if self.thread is not None:
            self.thread.join()
