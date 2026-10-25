"""Independently written Python peer for WORK-0004's loopback lab protocol.

Run after building the Rust peer:
    python -m unittest discover -s tests/interop -p 'test_*.py'

Set P2P_LAB_PEER_BIN to the Rust executable path. This client uses only the
published wire contract and Python sockets; it does not import Rust bindings.
All on-wire values are public synthetic fixtures.
"""

from __future__ import annotations

import os
import queue
import socket
import subprocess
import threading
import unittest
from pathlib import Path


MAX_FRAME = 256
TIMEOUT = 5.0


class WirePeer:
    def __init__(self, endpoint: tuple[str, int]):
        self.socket = socket.create_connection(endpoint, timeout=TIMEOUT)
        self.socket.settimeout(TIMEOUT)
        self.pending = bytearray()

    def close(self) -> None:
        self.socket.close()

    def send(self, text: str) -> None:
        self.socket.sendall(text.encode("ascii") + b"\n")

    def send_bytes(self, data: bytes) -> None:
        self.socket.sendall(data)

    def receive(self) -> str:
        while b"\n" not in self.pending:
            part = self.socket.recv(512)
            if not part:
                raise EOFError("peer closed before complete response")
            self.pending.extend(part)
            if len(self.pending) > MAX_FRAME:
                raise AssertionError("peer response exceeds wire frame bound")
        frame, _, remainder = self.pending.partition(b"\n")
        self.pending = bytearray(remainder)
        return frame.decode("ascii")

    def hello(self) -> str:
        self.send("P2P1 HELLO python-peer")
        result = self.receive()
        if not result.startswith("P2P1 HELLO "):
            raise AssertionError(f"unexpected HELLO category: {result.split(' ', 2)[:2]}")
        return result


class LabServer:
    def __init__(self, executable: Path):
        self.process = subprocess.Popen(
            [str(executable), "127.0.0.1:0"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=0,
        )
        self.lines: queue.Queue[bytes] = queue.Queue()
        assert self.process.stdout is not None
        threading.Thread(target=self._read_line, daemon=True).start()
        try:
            line = self.lines.get(timeout=TIMEOUT)
        except queue.Empty as exc:
            self.stop()
            raise RuntimeError("Rust peer did not announce loopback listener") from exc
        if not line.startswith(b"LISTEN 127.0.0.1:"):
            self.stop()
            raise RuntimeError("Rust peer announced an unexpected endpoint")
        try:
            port = int(line.removeprefix(b"LISTEN 127.0.0.1:").strip())
        except ValueError as exc:
            self.stop()
            raise RuntimeError("Rust peer announced a malformed port") from exc
        if not 0 < port < 65536:
            self.stop()
            raise RuntimeError("Rust peer announced an invalid port")
        self.endpoint = ("127.0.0.1", port)

    def _read_line(self) -> None:
        assert self.process.stdout is not None
        self.lines.put(self.process.stdout.readline(128))

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=TIMEOUT)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=TIMEOUT)
        if self.process.stdout is not None:
            self.process.stdout.close()


class IndependentPeerTests(unittest.TestCase):
    def setUp(self) -> None:
        binary = os.environ.get("P2P_LAB_PEER_BIN")
        if not binary:
            raise RuntimeError("P2P_LAB_PEER_BIN must name the built Rust lab peer")
        self.server = LabServer(Path(binary))
        self.peer = WirePeer(self.server.endpoint)

    def tearDown(self) -> None:
        self.peer.close()
        self.server.stop()

    def test_hello_square_and_duplicate_are_same_result(self) -> None:
        self.peer.hello()
        self.peer.send("P2P1 OFFER one SQUARE 23")
        self.assertEqual("P2P1 RESULT one 529", self.peer.receive())
        self.peer.send("P2P1 OFFER one SQUARE 23")
        self.assertEqual("P2P1 RESULT one 529", self.peer.receive())

    def test_same_id_different_input_conflicts(self) -> None:
        self.peer.hello()
        self.peer.send("P2P1 OFFER replay SQUARE 4")
        self.assertEqual("P2P1 RESULT replay 16", self.peer.receive())
        self.peer.send("P2P1 OFFER replay SQUARE 5")
        self.assertEqual("P2P1 ERROR STEP_CONFLICT", self.peer.receive())

    def test_major_version_rejected_before_offer(self) -> None:
        self.peer.send("P2P2 HELLO python-peer")
        self.assertEqual("P2P1 ERROR VERSION_UNSUPPORTED", self.peer.receive())

    def test_oversize_frame_rejected(self) -> None:
        self.peer.hello()
        self.peer.send_bytes(b"P2P1 OFFER " + b"x" * MAX_FRAME + b"\n")
        self.assertEqual("P2P1 ERROR RESOURCE_LIMIT", self.peer.receive())
        try:
            closed = self.peer.socket.recv(1)
        except ConnectionResetError:
            closed = b""  # Windows resets after close with unread request bytes.
        self.assertEqual(b"", closed)

    def test_exact_frame_boundary_is_parsed_but_unterminated_is_rejected(self) -> None:
        self.peer.send_bytes(b"P2P1 " + b"X" * (MAX_FRAME - 6) + b"\n")
        self.assertEqual("P2P1 ERROR OPERATION_UNSUPPORTED", self.peer.receive())
        self.peer.close()
        second = WirePeer(self.server.endpoint)
        try:
            second.send_bytes(b"X" * MAX_FRAME)
            self.assertEqual("P2P1 ERROR RESOURCE_LIMIT", second.receive())
        finally:
            second.close()

    def test_non_loopback_bind_rejected(self) -> None:
        binary = Path(os.environ["P2P_LAB_PEER_BIN"])
        result = subprocess.run(
            [str(binary), "0.0.0.0:0"],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=TIMEOUT,
            check=False,
        )
        self.assertNotEqual(0, result.returncode)
        self.assertNotIn(b"LISTEN", result.stdout)

    def test_fragmented_offer_waits_for_newline(self) -> None:
        self.peer.hello()
        self.peer.send_bytes(b"P2P1 OFFER split SQUARE ")
        self.peer.send_bytes(b"12\n")
        self.assertEqual("P2P1 RESULT split 144", self.peer.receive())

    def test_cancel_task(self) -> None:
        self.peer.hello()
        self.peer.send("P2P1 OFFER canceled SQUARE 9")
        self.assertEqual("P2P1 RESULT canceled 81", self.peer.receive())
        self.peer.send("P2P1 CANCEL canceled")
        self.assertEqual("P2P1 CANCELLED canceled", self.peer.receive())
        self.peer.send("P2P1 OFFER canceled SQUARE 9")
        self.assertEqual("P2P1 CANCELLED canceled", self.peer.receive())
        self.peer.send("P2P1 OFFER canceled SQUARE 10")
        self.assertEqual("P2P1 ERROR STEP_CONFLICT", self.peer.receive())

    def test_cancel_before_offer_is_tombstone(self) -> None:
        self.peer.hello()
        self.peer.send("P2P1 CANCEL future")
        self.assertEqual("P2P1 CANCELLED future", self.peer.receive())
        self.peer.send("P2P1 OFFER future SQUARE 2")
        self.assertEqual("P2P1 CANCELLED future", self.peer.receive())

    def test_replay_cache_is_scoped_to_connection(self) -> None:
        self.peer.hello()
        self.peer.send("P2P1 OFFER common SQUARE 3")
        self.assertEqual("P2P1 RESULT common 9", self.peer.receive())
        self.peer.close()
        second = WirePeer(self.server.endpoint)
        try:
            second.hello()
            second.send("P2P1 OFFER common SQUARE 4")
            self.assertEqual("P2P1 RESULT common 16", second.receive())
        finally:
            second.close()

    def test_task_limit_preserves_existing_cache(self) -> None:
        self.peer.hello()
        for number in range(64):
            task_id = f"t{number}"
            self.peer.send(f"P2P1 OFFER {task_id} SQUARE {number}")
            self.assertEqual(
                f"P2P1 RESULT {task_id} {number * number}", self.peer.receive()
            )
        self.peer.send("P2P1 OFFER extra SQUARE 65")
        self.assertEqual("P2P1 ERROR RESOURCE_LIMIT", self.peer.receive())
        self.peer.send("P2P1 OFFER t63 SQUARE 63")
        self.assertEqual("P2P1 RESULT t63 3969", self.peer.receive())


if __name__ == "__main__":
    unittest.main()
