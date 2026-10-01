"""Whole-book replacement; legacy register semantics stay in update_index.py."""
from __future__ import annotations
import copy
from contextlib import contextmanager
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


@contextmanager
def exclusive_lock(path):
    # Persistent lock inode: never unlink it, which could split concurrent writers
    # across two inodes. The OS releases the actual lock even after a crash.
    with open(path, "a+b") as handle:
        if os.name == "nt":
            import msvcrt
            if path.stat().st_size == 0:
                handle.write(b"0"); handle.flush()
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
            try: yield
            finally:
                handle.seek(0); msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            try: yield
            finally: fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def replacement(index, items, slug, distill):
    from update_index import apply, validate
    if not isinstance(slug, str) or not slug.strip() or distill.get("slug") != slug:
        raise ValueError("book_slug must match distill.slug")
    if not isinstance(items, list) or not items:
        raise ValueError("replacement merge must be a nonempty list")
    if not isinstance(index, dict) or not isinstance(index.get("concepts"), list):
        raise ValueError("invalid index concepts")
    expected = distill.get("concepts")
    if not isinstance(expected, list) or not expected:
        raise ValueError("distill concepts must be nonempty")
    if any(not isinstance(c, dict) or not isinstance(c.get("concept"), str)
           or not c["concept"].strip() for c in expected):
        raise ValueError("invalid distill concept")
    by_name = {c["concept"]: c for c in expected}
    if len(by_name) != len(expected):
        raise ValueError("duplicate distill concept")
    seen = set()
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("entry"), dict):
            raise ValueError("merge item/entry must be objects")
        name, entry = item.get("concept"), item["entry"]
        if not isinstance(name, str) or name in seen or name not in by_name:
            raise ValueError("duplicate or unknown merge concept")
        seen.add(name)
        if entry.get("book_slug") != slug or entry.get("book_title") != distill.get("title"):
            raise ValueError("mixed book slug or mismatched title")
        for key in ("stance", "anchor"):
            if not entry.get(key) or entry[key] != by_name[name].get(key):
                raise ValueError(f"{name}: {key} must match final distill concept")
    if seen != set(by_name):
        raise ValueError("merge must cover all final distill concepts")
    candidate = copy.deepcopy(index)
    old_names, preserved, stripped = [], [], []
    # Keep empty shells only for existing-concept relations or external metadata.
    existing_relations = {i["concept"] for i in items if i.get("relation") != "NEW_CONCEPT"}
    for concept in candidate["concepts"]:
        if not isinstance(concept, dict) or not isinstance(concept.get("entries"), list) or not isinstance(concept.get("concept"), str) or not concept["concept"].strip():
            raise ValueError("invalid index concept/entries")
        if any(not isinstance(e, dict) or not e.get("book_slug") for e in concept["entries"]):
            raise ValueError("invalid existing entry")
        original = concept["entries"]
        concept["entries"] = [e for e in original if e["book_slug"] != slug]
        if len(original) != len(concept["entries"]):
            old_names.append(concept["concept"])
        if concept["entries"] or concept["concept"] in existing_relations or set(concept) - {"concept", "one_liner", "entries"}:
            stripped.append(concept)
        preserved.extend((concept["concept"], e) for e in concept["entries"])
    candidate["concepts"] = stripped
    names = [c.get("concept") for c in stripped]
    if any(not isinstance(n, str) or not n.strip() for n in names) or len(set(names)) != len(names):
        raise ValueError("invalid or duplicate existing concept")
    errors = validate(candidate, items)
    if errors:
        raise ValueError("\n".join(errors))
    result = apply(candidate, items)
    others = [(c["concept"], e) for c in result["concepts"] for e in c["entries"] if e["book_slug"] != slug]
    if preserved != others:
        raise ValueError("other-book contributions changed")
    return result, {"book_slug": slug, "removed": sorted(set(old_names) - seen),
                    "replaced": sorted(set(old_names) & seen), "added": sorted(seen - set(old_names)),
                    "other_entries_preserved": len(others)}


def replace_cli(args):
    from update_index import load_index
    path = Path(args.index)
    try:
        original = path.read_bytes() if path.exists() else None
        index = load_index(path)
        items = json.loads(Path(args.merge).read_text(encoding="utf-8"))
        distill = json.loads(Path(args.distill).read_text(encoding="utf-8"))
        if not isinstance(distill, dict):
            raise ValueError("distill must be an object")
        result, receipt = replacement(index, items, args.book_slug, distill)
        receipt["dry_run"] = args.dry_run
        receipt["changed"] = result != index
        if not args.dry_run and receipt["changed"]:
            # Validate before writing; atomic replace and compare the loaded snapshot
            # under a cooperative exclusive lock. Never overwrite a concurrent update.
            lock = Path(str(path) + ".replace.lock")
            temporary = None
            try:
                with exclusive_lock(lock):
                    if (path.read_bytes() if path.exists() else None) != original:
                        raise ValueError("index changed since validation; reload and retry")
                    if original is not None:
                        shutil.copy2(path, str(path) + ".bak")
                    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                                     prefix=path.name + ".", delete=False) as handle:
                        temporary = Path(handle.name)
                        json.dump(result, handle, ensure_ascii=False, indent=1)
                        handle.flush(); os.fsync(handle.fileno())
                    if path.exists():
                        os.chmod(temporary, path.stat().st_mode & 0o777)
                    os.replace(temporary, path)
            finally:
                if temporary is not None and temporary.exists(): temporary.unlink()
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
