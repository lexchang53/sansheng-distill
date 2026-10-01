import copy
import json
import subprocess
import sys
from pathlib import Path
import pytest

SCRIPT = Path(__file__).parents[1] / "update_index.py"


def entry(slug="target", stance="old"):
    return {"book_slug": slug, "book_title": "Book", "stance": stance, "anchor": "ch1",
            "relation": "NEW_CONCEPT"}


def fixture(tmp_path):
    index = {"version": 1, "concepts": [
        {"concept": "A", "one_liner": "A", "entries": [entry(), entry("other")]},
        {"concept": "B", "one_liner": "B", "entries": [entry()]}]}
    distill = {"slug": "target", "title": "Book", "concepts": [
        {"concept": "B", "stance": "new", "anchor": "ch1"}]}
    merge = [{"concept": "B", "relation": "REFINES", "entry": entry(stance="new")}]
    paths = [tmp_path / n for n in ("index.json", "distill.json", "merge.json")]
    for p, data in zip(paths, (index, distill, merge)):
        p.write_text(json.dumps(data))
    return paths, index, distill, merge


def run(paths, *extra):
    index, distill, merge = paths
    return subprocess.run([sys.executable, str(SCRIPT), "replace-book", "--index", str(index),
        "--distill", str(distill), "--merge", str(merge), "--book-slug", "target", *extra],
        capture_output=True, text=True)


def test_replacement_removes_cancelled_contribution_preserves_other_and_is_idempotent(tmp_path):
    paths, old, _, _ = fixture(tmp_path)
    assert run(paths).returncode == 0
    result = json.loads(paths[0].read_text())
    assert result["concepts"][0]["entries"] == [old["concepts"][0]["entries"][1]]
    assert result["concepts"][1]["entries"] == [entry(stance="new") | {"relation": "REFINES"}]
    assert json.loads(Path(str(paths[0]) + ".bak").read_text()) == old
    first = paths[0].read_bytes()
    assert run(paths).returncode == 0
    assert paths[0].read_bytes() == first


def test_dry_run_lists_diff_without_writing(tmp_path):
    paths, _, _, _ = fixture(tmp_path); before = paths[0].read_bytes()
    r = run(paths, "--dry-run")
    assert r.returncode == 0 and json.loads(r.stdout)["removed"] == ["A"]
    assert paths[0].read_bytes() == before and not Path(str(paths[0]) + ".bak").exists()


@pytest.mark.parametrize("mutation", ["empty", "mixed", "relation", "duplicate", "missing", "stance", "slug"])
def test_invalid_replacement_never_writes(tmp_path, mutation):
    paths, _, distill, merge = fixture(tmp_path); before = paths[0].read_bytes()
    if mutation == "empty": merge = []
    if mutation == "mixed": merge[0]["entry"]["book_slug"] = "other"
    if mutation == "relation": merge[0]["relation"] = "AGREES"
    if mutation == "duplicate": merge.append(copy.deepcopy(merge[0]))
    if mutation == "missing": distill["concepts"].append({"concept": "C", "stance": "new", "anchor": "ch1"})
    if mutation == "stance": merge[0]["entry"]["stance"] = "made up"
    if mutation == "slug": distill["slug"] = "other"
    paths[1].write_text(json.dumps(distill)); paths[2].write_text(json.dumps(merge))
    assert run(paths).returncode == 1
    assert paths[0].read_bytes() == before and not Path(str(paths[0]) + ".bak").exists()


def test_new_concept_validated_after_old_book_contribution_removed(tmp_path):
    paths, _, _, merge = fixture(tmp_path)
    merge[0]["relation"] = "NEW_CONCEPT"; paths[2].write_text(json.dumps(merge))
    assert run(paths).returncode == 0
    first = paths[0].read_bytes()
    assert run(paths).returncode == 0 and paths[0].read_bytes() == first


def test_empty_concept_external_annotation_preserved(tmp_path):
    paths, index, _, _ = fixture(tmp_path)
    index["concepts"][0]["entries"] = [entry()]
    index["concepts"][0]["editor_note"] = "keep this"
    paths[0].write_text(json.dumps(index))
    assert run(paths).returncode == 0
    assert json.loads(paths[0].read_text())["concepts"][0]["editor_note"] == "keep this"


def test_held_lock_rejects_without_overwrite(tmp_path):
    fcntl = pytest.importorskip("fcntl")
    paths, _, _, _ = fixture(tmp_path); before = paths[0].read_bytes()
    lock = Path(str(paths[0]) + ".replace.lock")
    with lock.open("a+b") as handle:
        fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        assert run(paths).returncode == 1 and paths[0].read_bytes() == before


def test_crashed_writer_lock_released_by_os(tmp_path):
    pytest.importorskip("fcntl")
    paths, _, _, _ = fixture(tmp_path)
    lock = str(paths[0]) + ".replace.lock"
    code = "import fcntl,os,sys; h=open(sys.argv[1],'a+b'); fcntl.flock(h.fileno(),fcntl.LOCK_EX); os._exit(0)"
    subprocess.run([sys.executable, "-c", code, lock], check=True)
    assert run(paths).returncode == 0
