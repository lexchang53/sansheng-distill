#!/usr/bin/env python3
"""Read-only EPUB preflight for image-only sections and fragmented text.

Warnings are triage signals, not a completeness certificate. Review the source
pages, appendix, and figures before signing a book's source stage.
"""
from __future__ import annotations

import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import posixpath
import sys
import xml.etree.ElementTree as ET
import zipfile


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class SectionParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text_nodes: list[str] = []
        self.images: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in {"script", "style"}:
            self._skip += 1
        if tag in {"img", "image"}:
            values = dict(attrs)
            ref = values.get("src") or values.get("href") or values.get("xlink:href")
            if ref:
                self.images.append(ref)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style"} and self._skip:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if not self._skip:
            value = data.strip()
            if value:
                self.text_nodes.append(value)


def _relative(base: str, href: str) -> str:
    return posixpath.normpath(posixpath.join(posixpath.dirname(base), href.split("#", 1)[0]))


def inspect_epub(path: Path, *, min_text_chars: int = 80,
                 fragmented_ratio: float = .5, min_nodes: int = 20) -> dict:
    source_sha256 = sha256_file(path)
    sections: list[dict] = []
    warnings: list[dict] = []
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        container = ET.fromstring(archive.read("META-INF/container.xml"))
        rootfile = container.find(".//{*}rootfile")
        if rootfile is None or not rootfile.get("full-path"):
            raise ValueError("EPUB container has no rootfile")
        opf_path = rootfile.attrib["full-path"]
        opf = ET.fromstring(archive.read(opf_path))
        manifest = {
            item.attrib["id"]: item.attrib.get("href", "")
            for item in opf.findall(".//{*}manifest/{*}item")
        }
        for itemref in opf.findall(".//{*}spine/{*}itemref"):
            item_id = itemref.attrib.get("idref", "")
            href = manifest.get(item_id)
            if not href:
                warnings.append({"kind": "missing_spine_item", "idref": item_id})
                continue
            section_path = _relative(opf_path, href)
            if section_path not in names:
                warnings.append({"kind": "missing_spine_file", "path": section_path})
                continue
            parser = SectionParser()
            parser.feed(archive.read(section_path).decode("utf-8-sig", errors="replace"))
            text_chars = sum(len("".join(node.split())) for node in parser.text_nodes)
            short_nodes = sum(len("".join(node.split())) <= 3 for node in parser.text_nodes)
            image_paths = [_relative(section_path, ref) for ref in parser.images
                           if not ref.startswith(("http://", "https://", "data:"))]
            missing_images = [ref for ref in image_paths if ref not in names]
            section = {"path": section_path, "text_chars": text_chars,
                       "text_nodes": len(parser.text_nodes), "short_nodes": short_nodes,
                       "image_refs": len(parser.images), "missing_images": missing_images}
            sections.append(section)
            if text_chars < min_text_chars and parser.images:
                warnings.append({"kind": "image_only_section", "path": section_path,
                                 "text_chars": text_chars, "image_refs": len(parser.images)})
            if (len(parser.text_nodes) >= min_nodes
                    and short_nodes / len(parser.text_nodes) >= fragmented_ratio):
                warnings.append({"kind": "fragmented_text", "path": section_path,
                                 "short_nodes": short_nodes, "text_nodes": len(parser.text_nodes)})
            for ref in missing_images:
                warnings.append({"kind": "missing_image", "path": section_path,
                                 "image": ref})
    if not sections:
        warnings.append({"kind": "empty_spine"})
    return {"source": str(path), "source_sha256": source_sha256,
            "spine_sections": len(sections), "sections": sections, "warnings": warnings}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("epub", type=Path)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)
    try:
        report = inspect_epub(args.epub)
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(f"无法预检 EPUB：{exc}", file=sys.stderr)
        return 3
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 2 if report["warnings"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
