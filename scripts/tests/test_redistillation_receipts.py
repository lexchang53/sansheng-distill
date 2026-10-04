import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import pytest

SCRIPTS = Path(__file__).parents[1]


def module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / (name + ".py"))
    obj = importlib.util.module_from_spec(spec); spec.loader.exec_module(obj)
    return obj


upgrade = module("verify_upgrade_manifest")
science = module("verify_science_review")


def package(tmp_path):
    (tmp_path / "source.txt").write_text("source")
    (tmp_path / "distill.json").write_text(json.dumps({"slug": "book"}))
    source_hash = upgrade.digest(tmp_path / "source.txt")
    (tmp_path / "boundaries.json").write_text(json.dumps({"source_sha256": source_hash}))
    artifacts = []
    for role, filename in [("source", "source.txt"), ("content", "distill.json"), ("boundaries", "boundaries.json")]:
        artifacts.append({"role": role, "path": filename, "action": "updated", "sha256": upgrade.digest(tmp_path / filename)})
    content_hash = artifacts[1]["sha256"]
    artifacts[1]["inputs_sha256"] = {"source": source_hash}
    artifacts[2].update(content_sha256=content_hash, inputs_sha256={"source": source_hash},
                        json_bindings={"/source_sha256": "source"})
    return {"schema": "distill-upgrade-v1", "book_slug": "book", "content_sha256": content_hash,
            "required_roles": ["source", "content", "boundaries"], "artifacts": artifacts}


def test_package_valid_and_actual_consumer_mutation_rejected(tmp_path):
    data = package(tmp_path)
    assert upgrade.verify(data, tmp_path)["checked_artifacts"] == 3
    (tmp_path / "boundaries.json").write_text(json.dumps({"source_sha256": "a" * 64}))
    # Even an updated manifest hash cannot disguise a stale embedded binding.
    data["artifacts"][2]["sha256"] = upgrade.digest(tmp_path / "boundaries.json")
    with pytest.raises(ValueError, match="embedded binding"): upgrade.verify(data, tmp_path)


@pytest.mark.parametrize("mutation", ["missing", "stale", "dependency", "version", "preserved", "outside", "cycle", "archived", "content_type", "missing_pointer", "archived_pointer"])
def test_package_rejects_invalid_declarations(tmp_path, mutation):
    data = package(tmp_path); artifact = data["artifacts"][2]
    if mutation == "missing": data["artifacts"].pop()
    if mutation == "stale": (tmp_path / "source.txt").write_text("changed source")
    if mutation == "dependency": artifact["inputs_sha256"]["source"] = "a" * 64
    if mutation == "version": artifact["content_sha256"] = "a" * 64
    if mutation == "preserved": artifact.update(action="preserved", reason="unchanged", previous_path="source.txt", previous_sha256=artifact["sha256"])
    if mutation == "outside": artifact["path"] = "../outside"
    if mutation == "cycle": artifact["inputs_sha256"]["content"] = data["content_sha256"]; data["artifacts"][1]["inputs_sha256"]["boundaries"] = artifact["sha256"]
    if mutation == "archived": artifact.update(action="archived", reason="old")
    if mutation == "content_type": data["artifacts"][1]["inputs_sha256"] = []
    if mutation == "missing_pointer": artifact["json_bindings"] = {"/missing": "source"}
    if mutation == "archived_pointer":
        data["artifacts"].append({"role": "old", "path": "source.txt", "sha256": data["artifacts"][0]["sha256"], "action": "archived", "reason": "historical"})
        artifact["json_bindings"] = {"/source_sha256": "old"}
    with pytest.raises(ValueError): upgrade.verify(data, tmp_path)


def records():
    d = {"slug": "book", "core_ideas": [{"claim_id": "c1"}], "decision_rules": []}
    source = {"url": "https://example.org/study", "title": "Study", "year": 2020, "doi": "10.1234/a"}
    e = {"evidence_page": {"claims": {"c1": {"status": "supported", "sources": [source]}}}}
    record = {"url": source["url"], "access_level": "abstract", "locator_basis": "abstract",
              "checked_on": "2026-09-30", "locator": "abstract results sentence",
              "support": "supports narrow claim", "scope_limit": "only stated population",
              "correction_check": "no correction located", "support_excerpt": "A narrow result.",
              "support_sha256": hashlib.sha256(b"A narrow result.").hexdigest(),
              "metadata": {"title": "Study", "year": 2020, "authors": "A. Author", "doi": "10.1234/a"}}
    r = {"schema": "distill-science-review-v1", "book_slug": "book", "inputs_sha256": {"distill": "a" * 64, "enrich": "b" * 64},
         "claims": {"c1": {"status": "reviewed", "reviewer": "main reviewer", "reviewed_on": "2026-09-30", "conclusion": "limited support", "sources": [record]}}}
    return r, d, e


def test_abstract_can_support_narrow_claim_with_honest_access_boundary():
    r, d, e = records()
    assert science.verify(r, d, e, "a" * 64, "b" * 64)["sources_checked"] == 1


@pytest.mark.parametrize("mutation", ["locator", "false_full_text", "doi", "missing_doi", "blank_doi", "excerpt", "stale", "claim", "source", "terminal", "date"])
def test_science_mutation_rejected(mutation):
    r, d, e = records(); rec = r["claims"]["c1"]["sources"][0]
    if mutation == "locator": rec["locator"] = " "
    if mutation == "false_full_text": rec["locator_basis"] = "publisher_full_text"
    if mutation == "doi": rec["metadata"]["doi"] = "10.1234/different"
    if mutation == "missing_doi": del rec["metadata"]["doi"]
    if mutation == "blank_doi": rec["doi"] = ""
    if mutation == "excerpt": rec["support_excerpt"] = "changed"
    if mutation == "stale": r["inputs_sha256"]["distill"] = "c" * 64
    if mutation == "claim": d["core_ideas"].append({"claim_id": "c2"})
    if mutation == "source": r["claims"]["c1"]["sources"] = []
    if mutation == "terminal": r["claims"]["c1"]["status"] = "pending"
    if mutation == "date": rec["checked_on"] = "yesterday"
    with pytest.raises(ValueError): science.verify(r, d, e, "a" * 64, "b" * 64)


def test_empty_inputs_rejected(tmp_path):
    with pytest.raises(ValueError): upgrade.verify({}, tmp_path)
    with pytest.raises(ValueError): science.verify({}, {}, {}, "a" * 64, "b" * 64)
    r, d, e = records(); d["core_ideas"] = []; e["evidence_page"]["claims"] = {}; r["claims"] = {}
    with pytest.raises(ValueError): science.verify(r, d, e, "a" * 64, "b" * 64)


@pytest.mark.parametrize("token", ["-1", "01", "-", "9", "~9"])
def test_invalid_pointer_tokens_rejected_on_actual_consumer(tmp_path, token):
    data = package(tmp_path); artifact = data["artifacts"][2]
    (tmp_path / "boundaries.json").write_text(json.dumps({"arr": [data["artifacts"][0]["sha256"]]}))
    artifact["sha256"] = upgrade.digest(tmp_path / "boundaries.json")
    artifact["json_bindings"] = {"/arr/" + token: "source"}
    with pytest.raises(ValueError): upgrade.verify(data, tmp_path)


def test_shared_claim_id_between_core_idea_and_rule_is_one_denominator():
    r, d, e = records(); d["decision_rules"] = [{"claim_id": "c1"}]
    assert science.verify(r, d, e, "a" * 64, "b" * 64)["claims_checked"] == 1
