import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile


SOURCE = Path(__file__).resolve().parents[1] / "audit_epub_source.py"
SPEC = importlib.util.spec_from_file_location("audit_epub_source", SOURCE)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def make_epub(path: Path, sections: dict[str, str]) -> None:
    container = ('<container xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                 '<rootfiles><rootfile full-path="OPS/book.opf"/></rootfiles></container>')
    manifest = "".join(f'<item id="s{i}" href="{name}" media-type="application/xhtml+xml"/>'
                       for i, name in enumerate(sections))
    spine = "".join(f'<itemref idref="s{i}"/>' for i in range(len(sections)))
    opf = f'<package xmlns="http://www.idpf.org/2007/opf"><manifest>{manifest}</manifest><spine>{spine}</spine></package>'
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("META-INF/container.xml", container)
        archive.writestr("OPS/book.opf", opf)
        for name, html in sections.items():
            archive.writestr(f"OPS/{name}", html)
        archive.writestr("OPS/appendix.png", b"image")


class EpubSourceAuditTest(unittest.TestCase):
    def test_image_only_appendix_and_fragmented_text_are_flagged(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.epub"
            make_epub(path, {
                "chapter.xhtml": "<html><body><p>完整正文说明管理决策的条件和证据。</p></body></html>",
                "appendix.xhtml": '<html><body><img src="appendix.png"/></body></html>',
                "broken.xhtml": "<html><body>" + "".join(f"<b>{i % 10}</b>" for i in range(30)) + "</body></html>",
            })
            report = MODULE.inspect_epub(path)
            self.assertEqual(report["spine_sections"], 3)
            self.assertEqual({w["kind"] for w in report["warnings"]},
                             {"image_only_section", "fragmented_text"})
            out = Path(directory) / "audit.json"
            self.assertEqual(MODULE.main([str(path), "--json-out", str(out)]), 2)
            self.assertEqual(json.loads(out.read_text())["source_sha256"], report["source_sha256"])

    def test_clean_text_and_empty_spine(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.epub"
            make_epub(path, {"chapter.xhtml": "<p>" + "完整的正文内容。" * 30 + "</p>"})
            self.assertEqual(MODULE.main([str(path)]), 0)
            make_epub(path, {})
            self.assertEqual(MODULE.main([str(path)]), 2)

    def test_missing_image_is_blocking(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "book.epub"
            make_epub(path, {"chapter.xhtml": "<p>" + "完整正文。" * 30
                     + '</p><img src="not-in-archive.png"/>'})
            self.assertIn("missing_image", {w["kind"] for w in MODULE.inspect_epub(path)["warnings"]})
            self.assertEqual(MODULE.main([str(path), "--json-out", str(Path(directory) / "report.json")]), 2)


if __name__ == "__main__":
    unittest.main()
