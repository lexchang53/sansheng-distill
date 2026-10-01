import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verify_page
from verify_reader_review import sha256, validate_reader_review


def package(tmp_path):
    source = tmp_path / "book.txt"
    source.write_text("一个很短的引言，说明本书问题。", encoding="utf-8")
    data = {"quality_profile": "reader", "chapters": [{"no": 1, "narrative": "引言提出全书问题。"}]}
    distill = tmp_path / "distill.json"
    distill.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
    receipt = {
        "schema": "reader-review-v1", "authorization": "测试夹具：用户接受读者档",
        "reviewer": "test reviewer", "reviewed_at": "2026-10-01T00:00:00Z",
        "review_evidence": "测试夹具，不用于正式签收", "unresolved_material_errors": 0,
        "distill_sha256": sha256(distill.read_bytes()), "source_sha256": sha256(source.read_bytes()),
        "chapters": [{"no": 1, "narrative_sha256": sha256(data["chapters"][0]["narrative"].encode()),
                      "fidelity": "reviewed", "evidence": "book.txt 第1行",
                      "coverage": {key: {"status": "reviewed" if key == "argument" else "not_applicable",
                                         "note": "全书问题已呈现" if key == "argument" else "原引言无此项"}
                                   for key in ("argument", "cases", "counterexamples", "limits")}}],
    }
    review = tmp_path / "reader-review.json"
    review.write_text(json.dumps(receipt, ensure_ascii=False), encoding="utf-8")
    return distill, source, review, data, receipt


def test_source_short_reader_and_strict_floor(tmp_path):
    distill, source, review, data, _ = package(tmp_path)
    assert validate_reader_review(distill, source, review) == []
    assert not any("G9" in error or "G14 每章" in error for error in verify_page.lint_distill(data))
    strict = copy.deepcopy(data)
    del strict["quality_profile"]
    assert any("G9" in error for error in verify_page.lint_distill(strict))
    assert any("G14 每章" in error for error in verify_page.lint_distill(strict))


@pytest.mark.parametrize("mutation", ["missing", "old_hash", "pending", "empty_rows", "duplicate", "missing_facet", "empty_source", "empty_body", "bad_time"])
def test_reject_mutations(tmp_path, mutation):
    distill, source, review, data, receipt = package(tmp_path)
    if mutation == "missing":
        review.unlink()
    elif mutation == "old_hash":
        distill.write_text(distill.read_text() + "\n", encoding="utf-8")
    elif mutation == "empty_source":
        source.write_text("", encoding="utf-8")
        receipt["source_sha256"] = sha256(source.read_bytes())
    elif mutation == "empty_body":
        data["chapters"][0]["narrative"] = " ……-- "
        distill.write_text(json.dumps(data), encoding="utf-8")
        receipt["distill_sha256"] = sha256(distill.read_bytes())
        receipt["chapters"][0]["narrative_sha256"] = sha256(" ……-- ".encode())
    elif mutation == "pending":
        receipt["unresolved_material_errors"] = 1
    elif mutation == "bad_time":
        receipt["reviewed_at"] = "yesterday"
    elif mutation == "empty_rows":
        receipt["chapters"] = []
    elif mutation == "duplicate":
        receipt["chapters"] *= 2
    elif mutation == "missing_facet":
        del receipt["chapters"][0]["coverage"]["limits"]
    if mutation not in ("missing", "old_hash"):
        review.write_text(json.dumps(receipt), encoding="utf-8")
    assert validate_reader_review(distill, source, review)


def test_page_command_enforces_receipt_even_skip_interact(tmp_path, monkeypatch, capsys):
    distill, source, review, _, _ = package(tmp_path)
    page = tmp_path / "page.html"
    page.write_text("<html></html>", encoding="utf-8")
    # Isolate unrelated HTML checks; exercise the production command's review branch.
    monkeypatch.setattr(verify_page, "lint_html", lambda *args, **kwargs: [])
    monkeypatch.setattr(verify_page, "lint_source_grounding", lambda *args: [])
    monkeypatch.setattr(sys, "argv", ["verify_page", str(page), "--distill", str(distill),
                                      "--source", str(source), "--skip-interact"])
    assert verify_page.main() == 0
    review.unlink()
    assert verify_page.main() == 1
    assert "审阅记录不可读取" in capsys.readouterr().out
