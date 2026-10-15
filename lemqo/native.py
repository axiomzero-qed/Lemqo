"""Bounded execution of caller-selected trusted native backends. No shell."""

import os
import signal
import subprocess
import sys
import threading
import time

from .errors import Rejection
from .lean_export import deadline_check

MAX_OUTPUT_BYTES = 64 * 1024
MAX_ADDRESS_SPACE = 10 * 1024**3
_LINUX_LIMITS = """import os, resource, sys
resource.setrlimit(resource.RLIMIT_AS, (int(sys.argv[3]), int(sys.argv[3])))
resource.setrlimit(resource.RLIMIT_CPU, (int(sys.argv[4]), int(sys.argv[4]) + 1))
resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
os.execv(sys.argv[1], sys.argv[1:3])
"""


def run_backend(executable, config, directory, deadline):
    deadline_check(deadline)
    env = {key: value for key, value in os.environ.items()
           if key.upper() in ("SYSTEMROOT", "WINDIR", "TMP", "TEMP")}
    env.update(PATH=os.defpath, LANG="C", LC_ALL="C", HOME=str(directory))
    options = {"start_new_session": True} if os.name == "posix" else {
        "creationflags": subprocess.CREATE_NO_WINDOW}
    argv = [str(executable), str(config)]
    if sys.platform == "linux":
        argv = [sys.executable, "-I", "-c", _LINUX_LIMITS, *argv,
                str(MAX_ADDRESS_SPACE), str(max(1, int(deadline - time.monotonic()) + 1))]
    try:
        process = subprocess.Popen(argv, cwd=directory,
                                   env=env, stdin=subprocess.DEVNULL,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, **options)
    except OSError:
        raise Rejection("lean-backend", "could not start a selected backend") from None
    output, errors, overflow, read_error = bytearray(), bytearray(), threading.Event(), threading.Event()

    def drain(stream, buffer):
        try:
            with stream:
                while chunk := stream.read(4096):
                    if len(buffer) + len(chunk) > MAX_OUTPUT_BYTES:
                        overflow.set()
                        return
                    buffer.extend(chunk)
        except OSError:
            read_error.set()

    readers = [threading.Thread(target=drain, args=(stream, buffer), daemon=True)
               for stream, buffer in ((process.stdout, output), (process.stderr, errors))]
    for reader in readers:
        reader.start()
    try:
        while process.poll() is None:
            if overflow.is_set():
                raise Rejection("lean-backend", "backend output exceeds the limit")
            deadline_check(deadline)
            time.sleep(0.025)
    finally:
        # Also close any inherited pipe writers in a failed POSIX process group.
        if os.name == "posix":
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
        elif process.poll() is None:
            process.kill()
        process.wait()
        for reader in readers:
            reader.join(timeout=1)
    if overflow.is_set() or read_error.is_set() or any(reader.is_alive() for reader in readers):
        raise Rejection("lean-backend", "backend output did not complete within limits")
    if process.returncode != 0:
        if os.name == "posix" and process.returncode < 0:
            number = -process.returncode
            if number == getattr(signal, "SIGXCPU", None):
                raise Rejection("backend-cpu-limit", "backend exceeded its CPU time limit (SIGXCPU)")
            label = signal.Signals(number).name
            raise Rejection("backend-signal", f"backend terminated by {label} ({number}); SIGKILL may indicate an external resource limit")
        raise Rejection("backend-exit", f"backend exited with status {process.returncode}")
    if errors:
        raise Rejection("lean-backend", "backend emitted unexpected error output")
    return bytes(output)
