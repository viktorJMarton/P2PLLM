"""Cross-platform source identity must not alter binary artifact identity."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "source_inventory", Path(__file__).resolve().parents[1] / "tools/source_inventory.py"
)
inventory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inventory)


class InventoryTests(unittest.TestCase):
    def test_utf8_line_endings_have_one_source_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "source.md"
            path.write_bytes("Állapot\r\nready\r\n".encode("utf-8"))
            windows = inventory.inventory_bytes(path)
            path.write_bytes("Állapot\nready\n".encode("utf-8"))
            self.assertEqual(windows, inventory.inventory_bytes(path))

    def test_binary_and_legacy_raw_bytes_are_unchanged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "artifact.bin"
            for data in (b"\x00\r\n", b"\xff\r\n"):
                path.write_bytes(data)
                self.assertEqual(data, inventory.inventory_bytes(path))
            path.write_bytes(b"text\r\n")
            self.assertEqual(b"text\r\n", inventory.inventory_bytes(path, "raw"))
            with self.assertRaises(ValueError):
                inventory.inventory_bytes(path, "unknown")


if __name__ == "__main__":
    unittest.main()
