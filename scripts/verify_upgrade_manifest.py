#!/usr/bin/env python3
"""Verify a declared re-distillation package, without assuming project paths."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SHA = re.compile(r"[0-9a-f]{64}\Z")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def file_at(root, value):
    if not isinstance(value, str) or not value or Path(value).is_absolute():
        raise ValueError("paths must be nonempty and relative to root")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"missing or outside-root file: {value}")
    return path


def verify(data, root):
    if not isinstance(data, dict) or data.get("schema") != "distill-upgrade-v1":
        raise ValueError("expected distill-upgrade-v1 object")
    slug = data.get("book_slug")
    if not isinstance(slug, str) or not slug.strip():
        raise ValueError("missing book_slug")
    artifacts = data.get("artifacts")
    required = data.get("required_roles")
    if not isinstance(artifacts, list) or not artifacts or not isinstance(required, list) or not required:
        raise ValueError("nonempty artifacts and required_roles required")
    roles = {}
    for artifact in artifacts:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("role"), str) or not artifact["role"].strip():
            raise ValueError("invalid artifact role")
        if artifact["role"] in roles:
            raise ValueError("duplicate artifact role")
        roles[artifact["role"]] = artifact
    if any(not isinstance(r, str) or not r.strip() for r in required) or len(set(required)) != len(required):
        raise ValueError("invalid required_roles")
    if not set(required) <= roles.keys() or not {"source", "content"} <= set(required):
        raise ValueError("required roles must include source/content and exist")
    hashes, paths = {}, {}
    for role, artifact in roles.items():
        action = artifact.get("action")
        if action not in {"updated", "preserved", "archived", "not_applicable"}:
            raise ValueError(f"{role}: invalid action")
        if action != "updated" and (not isinstance(artifact.get("reason"), str) or not artifact["reason"].strip()):
            raise ValueError(f"{role}: non-update needs reason")
        if action == "not_applicable":
            if role in required: raise ValueError(f"{role}: required role cannot be not_applicable")
            continue
        path = file_at(root, artifact.get("path"))
        expected = artifact.get("sha256")
        if not isinstance(expected, str) or not SHA.fullmatch(expected) or digest(path) != expected:
            raise ValueError(f"{role}: file SHA mismatch")
        hashes[role], paths[role] = expected, path
        if action == "preserved":
            old = file_at(root, artifact.get("previous_path"))
            if digest(old) != expected or artifact.get("previous_sha256") != expected:
                raise ValueError(f"{role}: preservation requires byte-equivalent previous artifact")
    if any(roles[r]["action"] not in {"updated", "preserved"} for r in required):
        raise ValueError("required roles must be active")
    if data.get("content_sha256") != hashes["content"]:
        raise ValueError("content version mismatch")
    content_inputs = roles["content"].get("inputs_sha256")
    if not isinstance(content_inputs, dict) or content_inputs.get("source") != hashes["source"]:
        raise ValueError("content must be bound to current source")
    content = json.loads(paths["content"].read_text(encoding="utf-8"))
    if not isinstance(content, dict) or content.get("slug") != slug:
        raise ValueError("content slug mismatch")
    for role, artifact in roles.items():
        if artifact["action"] not in {"updated", "preserved"}: continue
        deps = artifact.get("inputs_sha256", {})
        if not isinstance(deps, dict): raise ValueError(f"{role}: invalid dependencies")
        if role not in {"source", "content"}:
            if not deps or artifact.get("content_sha256") != hashes["content"]:
                raise ValueError(f"{role}: missing dependencies/content version")
        for source_role, expected in deps.items():
            if source_role == role or source_role not in hashes or roles[source_role]["action"] == "archived" or hashes[source_role] != expected:
                raise ValueError(f"{role}: stale or unknown dependency {source_role}")
        # Optional JSON pointer checks read actual bindings from the consumer file,
        # rather than trusting a manifest's claim that an old file is newly bound.
        bindings = artifact.get("json_bindings", {})
        if not isinstance(bindings, dict): raise ValueError(f"{role}: invalid json_bindings")
        for pointer, source_role in bindings.items():
            if not isinstance(pointer, str) or not pointer.startswith("/") or source_role not in hashes or roles[source_role]["action"] not in {"updated", "preserved"}:
                raise ValueError(f"{role}: invalid binding")
            value = json.loads(paths[role].read_text(encoding="utf-8"))
            try:
                for key in pointer[1:].split("/"):
                    if re.search(r"~(?![01])", key): raise ValueError("invalid pointer escape")
                    key = key.replace("~1", "/").replace("~0", "~")
                    if isinstance(value, list):
                        if not re.fullmatch(r"0|[1-9][0-9]*", key): raise ValueError("invalid pointer array index")
                        value = value[int(key)]
                    else: value = value[key]
            except (KeyError, IndexError, TypeError) as error:
                raise ValueError(f"{role}: missing binding path {pointer}") from error
            if value != hashes[source_role]: raise ValueError(f"{role}: embedded binding is stale: {pointer}")
    visiting, visited = set(), set()
    def visit(role):
        if role in visiting: raise ValueError("cyclic artifact dependencies")
        if role in visited: return
        visiting.add(role)
        for dependency in roles[role].get("inputs_sha256", {}): visit(dependency)
        visiting.remove(role); visited.add(role)
    for role, artifact in roles.items():
        if artifact["action"] in {"updated", "preserved"}: visit(role)
    return {"status": "pass", "book_slug": slug, "content_sha256": hashes["content"],
            "checked_artifacts": len(hashes), "required_roles": required,
            "boundary": "declared package integrity; not semantic correctness or publication"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path); parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(verify(json.loads(args.manifest.read_text(encoding="utf-8")), args.root), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, IndexError) as error:
        print(str(error), file=sys.stderr); return 1


if __name__ == "__main__": sys.exit(main())
