import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SOURCE = Path(__file__).resolve().parents[1] / "check_receipt_inputs.py"
SPEC = importlib.util.spec_from_file_location("check_receipt_inputs", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReceiptInputTest(unittest.TestCase):
    def test_matching_changed_and_missing_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            source = book / "source-map.json"
            source.write_text("original", encoding="utf-8")
            expected = hashlib.sha256(source.read_bytes()).hexdigest()
            receipt = book / "stage-B.json"
            receipt.write_text(json.dumps({"status": "ok", "stage": "B",
                                           "inputs_sha256": {"source-map.json": expected}}),
                               encoding="utf-8")
            self.assertEqual(MODULE.main([str(receipt), "--book-dir", str(book),
                                          "--json-out", str(book / "report.json")]), 0)
            source.write_text("changed", encoding="utf-8")
            self.assertEqual(MODULE.inspect_receipt(receipt, book)["checks"][0]["status"], "stale")
            self.assertEqual(MODULE.main([str(receipt), "--book-dir", str(book)]), 2)
            source.unlink()
            self.assertEqual(MODULE.inspect_receipt(receipt, book)["checks"][0]["status"], "unverified")

    def test_symbolic_input_must_be_mapped_and_invalid_receipt_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            book = Path(directory)
            source = book / "source.epub"
            source.write_bytes(b"epub")
            expected = hashlib.sha256(source.read_bytes()).hexdigest()
            receipt = book / "stage-A.json"
            receipt.write_text(json.dumps({"status": "ok", "inputs_sha256": {"epub": expected}}),
                               encoding="utf-8")
            self.assertEqual(MODULE.inspect_receipt(receipt, book)["status"], "blocked")
            self.assertEqual(MODULE.inspect_receipt(receipt, book, {"epub": source})["status"], "pass")
            receipt.write_text(json.dumps({"status": "draft", "inputs_sha256": {"epub": expected}}),
                               encoding="utf-8")
            with self.assertRaises(ValueError):
                MODULE.inspect_receipt(receipt, book, {"epub": source})


if __name__ == "__main__":
    unittest.main()
