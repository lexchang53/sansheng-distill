import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SOURCE = Path(__file__).resolve().parents[1] / "audit_book_source.py"
SPEC = importlib.util.spec_from_file_location("audit_book_source", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SourceAuditTest(unittest.TestCase):
    def test_missing_printed_pages_and_duplicate_scan_are_flagged(self):
        a = "这是第一段经营分析，有独立细节。" * 12
        b = "这是五年计划的论证，有企业案例。" * 12
        result = MODULE.inspect_pages([f"{a}\n145", f"{b}\n148", f"{b}\n148", "新章节" * 25 + "\n149"])
        self.assertEqual(result["printed_page_jumps"][0]["printed_before"], 145)
        self.assertTrue(any(x["pdf_pages"] == [2, 3] for x in result["near_duplicate_pages"]))

    def test_empty_document_and_low_text_are_visible(self):
        self.assertEqual(MODULE.inspect_pages([])["errors"], ["PDF has no pages"])
        self.assertEqual(MODULE.inspect_pages(["封面"])["low_text_pages"][0]["pdf_page"], 1)

    def test_image_only_page_requires_review(self):
        report = MODULE.inspect_pages(["正文" * 50, "附录"], image_counts=[0, 1])
        self.assertEqual(report["image_only_candidates"],
                         [{"pdf_page": 2, "text_chars": 2, "image_count": 1}])
        self.assertEqual(MODULE.inspect_pages(["正文" * 50], image_counts=[1])["image_only_candidates"], [])

    @unittest.skipUnless(importlib.util.find_spec("pymupdf"), "PyMuPDF not installed")
    def test_pdf_cli_blocks_image_only_page(self):
        import pymupdf

        with tempfile.TemporaryDirectory() as directory:
            pdf = Path(directory) / "scan.pdf"
            report = Path(directory) / "report.json"
            doc = pymupdf.open()
            page = doc.new_page()
            pixmap = pymupdf.Pixmap(pymupdf.csRGB, pymupdf.IRect(0, 0, 2, 2), False)
            page.insert_image(pymupdf.Rect(0, 0, 40, 40), pixmap=pixmap)
            doc.save(pdf)
            doc.close()
            self.assertEqual(MODULE.main([str(pdf), "--json-out", str(report)]), 2)
            self.assertEqual(json.loads(report.read_text())["image_only_candidates"][0]["pdf_page"], 1)


if __name__ == "__main__":
    unittest.main()
