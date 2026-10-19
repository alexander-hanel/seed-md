#!/usr/bin/env python3
"""Bound a local process group; preserve start, streams and terminal evidence. No retries."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import time


def write(path, value):
    temporary = path.with_suffix('.tmp')
    with temporary.open('w') as stream:
        json.dump(value, stream, indent=2)
        stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
    temporary.replace(path)


def size(root):
    # Do not follow symlink directories; count logical file lengths, including sparse files.
    return footprint(root)[0]


def footprint(root):
    total = largest = 0
    for path in root.rglob('*'):
        try:
            if path.is_symlink() or not path.is_file(): continue
            length = path.stat().st_size
        except FileNotFoundError:
            continue  # Atomic replacement may remove a candidate during sampling.
        total += length; largest = max(largest, length)
    return total, largest


def kill_tree(pid):
    # Linux nested supervisors may create their own sessions. Include descendants
    # before killing the parent so their process groups are not left behind.
    parents = {}
    for entry in Path('/proc').glob('[0-9]*/stat'):
        try:
            rest = entry.read_text().rsplit(')', 1)[1].split()
            parents[int(entry.parent.name)] = int(rest[1])
        except (OSError, ValueError, IndexError):
            continue
    descendants = {pid}
    while True:
        expanded = descendants | {child for child, parent in parents.items() if parent in descendants}
        if expanded == descendants: break
        descendants = expanded
    for child in descendants - {pid}:
        try: os.kill(child, signal.SIGKILL)
        except ProcessLookupError: pass
    try: os.killpg(pid, signal.SIGKILL)
    except ProcessLookupError: pass


def run(argv, cwd, evidence, seconds, max_bytes, max_output_bytes, watch, max_file_bytes=None):
    if os.name != 'posix' or not Path('/proc/self/stat').is_file():
        raise ValueError('Linux process supervision required')
    if not argv or min(seconds, max_bytes, max_output_bytes) <= 0:
        raise ValueError('Command and positive limits required')
    evidence.mkdir(parents=True, exist_ok=False)  # An attempt cannot overwrite earlier evidence.
    start = time.monotonic()
    record = {'status': 'starting', 'argv': argv, 'started_unix': time.time(),
              'limits': {'seconds': seconds, 'watched_bytes': max_bytes, 'output_bytes': max_output_bytes, 'file_bytes': max_file_bytes},
              'usage': None, 'usage_note': 'No provider token accounting; wall time is not a token budget.'}
    write(evidence / 'run.json', record)
    proc = None; reason = None; peak = 0; output = 0; signalled = []
    old_handlers = {}
    def interrupted(number, frame):
        signalled.append(number)
    for number in (signal.SIGINT, signal.SIGTERM):
        old_handlers[number] = signal.signal(number, interrupted)
    try:
        initial_total, initial_largest = footprint(watch)
        if initial_total > max_bytes or max_file_bytes is not None and initial_largest > max_file_bytes:
            raise ValueError('Watched directory already exceeds budget')
        proc = subprocess.Popen(argv, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                start_new_session=True)
        record.update(status='running', pid=proc.pid); write(evidence / 'run.json', record)
        selector = selectors.DefaultSelector()
        with (evidence/'stdout.log').open('wb') as out, (evidence/'stderr.log').open('wb') as err:
            selector.register(proc.stdout, selectors.EVENT_READ, out)
            selector.register(proc.stderr, selectors.EVENT_READ, err)
            last_disk = 0
            while selector.get_map() or proc.poll() is None:
                now = time.monotonic()
                if signalled: reason = 'interrupted'
                if now-start >= seconds: reason = reason or 'time_limit'
                if now-last_disk >= 1:
                    total, largest = footprint(watch); peak = max(peak, total); last_disk = now
                    if max_file_bytes is not None and largest > max_file_bytes: reason = reason or 'file_limit'
                    if peak > max_bytes: reason = reason or 'disk_limit'
                if reason:
                    kill_tree(proc.pid)
                for key, _ in selector.select(0.05):
                    block = os.read(key.fileobj.fileno(), 65536)
                    if not block:
                        selector.unregister(key.fileobj); key.fileobj.close(); continue
                    remaining = max(0, max_output_bytes-output)
                    key.data.write(block[:remaining]); key.data.flush()
                    output += len(block)
                    if output > max_output_bytes: reason = reason or 'output_limit'
            selector.close()
            proc.wait()
        # Do not leave background descendants running after their parent returns.
        kill_tree(proc.pid)
        total, largest = footprint(watch); peak = max(peak, total)
        if max_file_bytes is not None and largest > max_file_bytes: reason = reason or 'file_limit'
        if peak > max_bytes: reason = reason or 'disk_limit'
        record.update(status='stopped' if reason else 'passed' if proc.returncode == 0 else 'failed',
                      reason=reason, returncode=proc.returncode)
    except BaseException as error:
        if proc:
            kill_tree(proc.pid)
            proc.wait()
        record.update(status='failed', reason=type(error).__name__ + ': ' + str(error))
    finally:
        for number, previous in old_handlers.items(): signal.signal(number, previous)
        record.update(seconds=round(time.monotonic()-start, 3), peak_watched_bytes=peak,
                      observed_output_bytes=output, ended_unix=time.time())
        write(evidence/'run.json', record)
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cwd', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--watch', type=Path, required=True)
    parser.add_argument('--seconds', type=float, required=True)
    parser.add_argument('--max-bytes', type=int, required=True)
    parser.add_argument('--max-file-bytes', type=int)
    parser.add_argument('--max-output-bytes', type=int, default=16777216)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.command[1:] if args.command[:1] == ['--'] else args.command
    result = run(argv, args.cwd, args.evidence, args.seconds, args.max_bytes, args.max_output_bytes, args.watch, args.max_file_bytes)
    print(json.dumps(result))
    return 0 if result['status'] == 'passed' else 1

if __name__ == '__main__':
    raise SystemExit(main())
