#!/usr/bin/env python3
"""Capture incubator CSV text and extract binary MH-Z16 0x86 response frames."""

import argparse
import os
import select
import sys
import termios
import tty


def checksum_ok(frame: bytes) -> bool:
    return len(frame) == 9 and frame[0] == 0xFF and frame[1] == 0x86 and sum(frame[1:9]) & 0xFF == 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("port", nargs="?", default="/dev/ttyACM0")
    args = parser.parse_args()
    fd = os.open(args.port, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    try:
        attrs = termios.tcgetattr(fd)
        tty.setraw(fd)
        attrs = termios.tcgetattr(fd)
        attrs[4] = termios.B9600
        attrs[5] = termios.B9600
        attrs[6][termios.VMIN] = 0
        attrs[6][termios.VTIME] = 1
        termios.tcsetattr(fd, termios.TCSANOW, attrs)
        pending = bytearray()
        while True:
            # The port is nonblocking: wait for bytes instead of spinning at 100% CPU.
            ready, _, _ = select.select([fd], [], [], 1.0)
            if not ready:
                continue
            try:
                chunk = os.read(fd, 512)
            except BlockingIOError:
                continue
            if not chunk:
                print("Porta serial desconectada; captura encerrada.", file=sys.stderr)
                return 1
            pending.extend(chunk)
            while pending:
                marker = pending.find(b"\xff\x86")
                if marker >= 0 and len(pending) >= marker + 9:
                    frame = bytes(pending[marker : marker + 9])
                    if checksum_ok(frame):
                        if marker:
                            sys.stdout.buffer.write(pending[:marker])
                        sys.stdout.write("CO2_RAW," + frame.hex(" ").upper() + "\n")
                        del pending[: marker + 9]
                        sys.stdout.flush()
                        continue
                    if marker:
                        sys.stdout.buffer.write(pending[:marker])
                        del pending[:marker]
                    else:
                        sys.stdout.buffer.write(pending[:1])
                        del pending[:1]
                    sys.stdout.flush()
                    continue
                safe = len(pending) - 1
                if marker >= 0:
                    safe = min(safe, marker)
                if safe > 0:
                    sys.stdout.buffer.write(pending[:safe])
                    del pending[:safe]
                    sys.stdout.flush()
                break
    except KeyboardInterrupt:
        return 0
    finally:
        os.close(fd)


if __name__ == "__main__":
    raise SystemExit(main())
