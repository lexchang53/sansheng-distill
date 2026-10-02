"""Exercise real failure boundaries added by the distillation skill health review."""
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1]


def module_at(filename):
    spec = importlib.util.spec_from_file_location("health_export", filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def series(tmp_path, texts):
    raw = tmp_path / "raw"
    raw.mkdir()
    videos = []
    for i, text in enumerate(texts, 1):
        (raw / f"{i}.txt").write_text(text, encoding="utf-8")
        videos.append({"no": i, "title": "有效标题不能替代正文", "url": f"https://example.org/{i}",
                       "transcript": f"raw/{i}.txt"})
    manifest = tmp_path / "input.json"
    manifest.write_text(json.dumps({"slug": "series", "series_title": "例子", "author": "某作者",
                                    "platform": "youtube", "videos": videos}), encoding="utf-8")
    return subprocess.run([sys.executable, str(SCRIPTS / "build_series.py"), "--manifest", str(manifest),
                           "--outdir", str(tmp_path)], capture_output=True, text=True)


@pytest.mark.parametrize("text", ["", " \n\t ", "——……", "1\n00:00:01,000 --> 00:00:02,000\n"])
def test_series_has_no_body_not_success(tmp_path, text):
    result = series(tmp_path, [text])
    assert result.returncode == 3
    assert not (tmp_path / "book.txt").exists()
    assert not (tmp_path / "series.json").exists()
    assert json.loads((tmp_path / "diagnose.json").read_text())["chars_total"] == 0


def test_series_garbled_body_not_diluted_by_title(tmp_path):
    result = series(tmp_path, ["\ufffd\ufffd\ufffd一个正文"])
    assert result.returncode == 3
    assert not (tmp_path / "book.txt").exists()
    assert json.loads((tmp_path / "diagnose.json").read_text())["garbled_ratio"] > .02


def test_series_partial_empty_has_explicit_gap(tmp_path):
    result = series(tmp_path, ["真实完整的正文。", ""])
    assert result.returncode == 0  # Preserve the existing partial-series interface.
    diag = json.loads((tmp_path / "diagnose.json").read_text())
    assert diag["videos_missing_transcript"] == [2]
    assert diag["recommendation"] == "需人工确认"
    assert "【视频2】" not in (tmp_path / "book.txt").read_text()


def checker_project(tmp_path):
    tools = tmp_path / "07_工具"
    tools.mkdir()
    checker = tools / "verify_deepread.py"
    shutil.copyfile(SCRIPTS / "verify_deepread.py", checker)
    work = tmp_path / "03_工作数据"
    return checker, work


def test_empty_deepread_cannot_pass(tmp_path):
    checker, work = checker_project(tmp_path)
    drafts = work / "深读初稿"
    drafts.mkdir(parents=True)
    (drafts / "state.json").write_text("{}")
    (drafts / "fake.md").mkdir()  # A directory is not a manuscript.
    result = subprocess.run([sys.executable, str(checker)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "没有可校验" in result.stderr


def test_real_deepread_can_pass(tmp_path):
    checker, work = checker_project(tmp_path)
    drafts, packs = work / "深读初稿", work / "深读料包"
    drafts.mkdir(parents=True)
    packs.mkdir()
    (packs / "T01.md").write_text("相关来源中的真实论证。", encoding="utf-8")
    body = "\n".join(f"## {n}、论证\n相关来源中的真实论证。" for n in "一二三四五")
    (drafts / "T01.md").write_text(body, encoding="utf-8")
    result = subprocess.run([sys.executable, str(checker), "T01"], capture_output=True, text=True)
    assert result.returncode == 0, result.stdout + result.stderr


def export_project(tmp_path, monkeypatch, entries=None, checker_body="pass"):
    mod = module_at(SCRIPTS / "export_deepread.py")
    tools, work, web = tmp_path / "07_工具", tmp_path / "03_工作数据", tmp_path / "web"
    tools.mkdir()
    drafts = work / "深读初稿"
    drafts.mkdir(parents=True)
    web.mkdir()
    (tools / "normalize_punct.py").write_text("pass", encoding="utf-8")
    (tools / "verify_deepread.py").write_text(checker_body, encoding="utf-8")
    if entries is None:
        entries = [{"id": "T01", "type": "theme", "title": "专题正文"}]
    (work / "深读清单.json").write_text(json.dumps({"entries": entries}), encoding="utf-8")
    (drafts / "T01.md").write_text("完整正文。", encoding="utf-8")
    for key, val in {"BASE": tmp_path, "WORK": work, "WEB": web, "DRAFTS": drafts}.items():
        monkeypatch.setattr(mod, key, str(val))
    monkeypatch.setattr(mod, "build_facts", lambda _: {})
    return mod, web


@pytest.mark.parametrize("checker_body", ["raise RuntimeError('checker crashed')", "raise SystemExit(7)",
                                         "print('[红] T01 invalid'); raise SystemExit(1)",
                                         "print('[红] T01 invalid')"])
def test_export_stops_on_checker_failure_before_writing(tmp_path, monkeypatch, checker_body):
    mod, web = export_project(tmp_path, monkeypatch, checker_body=checker_body)
    assert mod.main() == 1
    assert list(web.iterdir()) == []


@pytest.mark.parametrize("entries", [[], [{"id": "T01", "type": "unrecognized"}],
                                    [{"id": "T01", "type": "theme"}] * 2])
def test_export_rejects_invalid_manifest(tmp_path, monkeypatch, entries):
    mod, web = export_project(tmp_path, monkeypatch, entries=entries)
    assert mod.main() == 1
    assert list(web.iterdir()) == []


def test_export_checks_manifest_ids_and_writes_complete_index(tmp_path, monkeypatch):
    mod, web = export_project(tmp_path, monkeypatch,
                              checker_body="import sys; assert sys.argv[1:] == ['T01']")
    assert mod.main() == 0
    index = json.loads((web / "deepread-index.json").read_text())
    assert index["entry_ids"] == ["T01"]
    assert index["total_count"] == 1
    assert json.loads((web / "deepread-themes.json").read_text())["entries"][0]["body_md"] == "完整正文。"


def test_series_corrupt_member_not_hidden_by_valid_long_member(tmp_path):
    result = series(tmp_path, ["足够长而完整的正文。" * 1000, "\ufffd\ufffd坏正文"])
    assert result.returncode == 3
    diag = json.loads((tmp_path / "diagnose.json").read_text())
    assert diag["videos_garbled_transcript"] == [2]
    assert diag["recommendation"] == "需人工确认"
    assert not (tmp_path / "book.txt").exists()


def test_deepread_empty_source_pack_cannot_pass(tmp_path):
    checker, work = checker_project(tmp_path)
    drafts, packs = work / "深读初稿", work / "深读料包"
    drafts.mkdir(parents=True)
    packs.mkdir()
    (packs / "T01.md").write_text(" \n ", encoding="utf-8")
    (drafts / "T01.md").write_text("\n".join(f"## {n}、论证\n无来源的正文。" for n in "一二三四五"), encoding="utf-8")
    result = subprocess.run([sys.executable, str(checker), "T01"], capture_output=True, text=True)
    assert result.returncode == 1
    assert "料包不存在或为空" in result.stdout
