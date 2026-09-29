#!/usr/bin/env python3
"""Check a signed stage receipt's input files before considering reuse.

Matching file hashes are necessary, not sufficient: also verify the task prompt,
model parameters, output receipt, and stage-specific quality checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_receipt(receipt: Path, book_dir: Path, path_map: dict[str, Path] | None = None) -> dict:
    data = json.loads(receipt.read_text(encoding="utf-8"))
    inputs = data.get("inputs_sha256")
    if data.get("status") != "ok" or not isinstance(inputs, dict) or not inputs:
        raise ValueError("receipt must have status=ok and nonempty inputs_sha256")
    path_map = path_map or {}
    checks = []
    for key, expected in inputs.items():
        if not isinstance(key, str) or not isinstance(expected, str) or not SHA256.fullmatch(expected):
            raise ValueError(f"invalid input hash entry: {key!r}")
        if key in path_map:
            candidates = [path_map[key]]
        elif Path(key).is_absolute():
            candidates = [Path(key)]
        else:
            candidates = [book_dir / key, receipt.parent / key]
        existing = [path for path in candidates if path.is_file()]
        if len({path.resolve() for path in existing}) != 1:
            checks.append({"input": key, "status": "unverified",
                           "reason": "missing_or_ambiguous_path"})
            continue
        path = existing[0]
        actual = sha256_file(path)
        checks.append({"input": key, "status": "match" if actual == expected else "stale",
                       "path": str(path), "expected_sha256": expected,
                       "actual_sha256": actual})
    return {"stage": data.get("stage"), "receipt": str(receipt),
            "status": "pass" if all(item["status"] == "match" for item in checks) else "blocked",
            "checks": checks,
            "note": "Only input file hashes were checked; prompt, model, output and editorial approval still require review."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--book-dir", type=Path, required=True)
    parser.add_argument("--map", action="append", default=[], metavar="KEY=PATH",
                        help="Resolve symbolic or external input keys explicitly")
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args(argv)
    path_map = {}
    for entry in args.map:
        if "=" not in entry or not entry.split("=", 1)[0]:
            parser.error("--map requires KEY=PATH")
        key, path = entry.split("=", 1)
        path_map[key] = Path(path)
    try:
        report = inspect_receipt(args.receipt, args.book_dir, path_map)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"无法核对阶段回执：{exc}", file=sys.stderr)
        return 3
    output = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 0 if report["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
