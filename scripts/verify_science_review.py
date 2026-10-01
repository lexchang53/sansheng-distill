#!/usr/bin/env python3
"""Check version-bound science review receipts; never infer scientific truth."""
import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlparse

ACCESS = {"publisher_full_text", "author_manuscript", "preprint", "abstract", "official_material"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def doi(value):
    return re.sub(r"^(https?://(dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I).lower()


def verify(receipt, distill, enrich, distill_sha, enrich_sha):
    if not isinstance(receipt, dict) or receipt.get("schema") != "distill-science-review-v1":
        raise ValueError("expected distill-science-review-v1 object")
    if not nonempty(distill.get("slug")) or receipt.get("book_slug") != distill["slug"]:
        raise ValueError("book slug mismatch")
    if receipt.get("inputs_sha256") != {"distill": distill_sha, "enrich": enrich_sha}:
        raise ValueError("stale science review input")
    claim_ids = [c.get("claim_id") for group in ("core_ideas", "decision_rules") for c in distill.get(group, [])]
    if not claim_ids or any(not nonempty(c) for c in claim_ids):
        raise ValueError("nonempty claim denominator required")
    claims = enrich.get("evidence_page", {}).get("claims")
    reviews = receipt.get("claims")
    if not isinstance(claims, dict) or not isinstance(reviews, dict) or set(claim_ids) != set(claims) or set(claims) != set(reviews):
        raise ValueError("science receipt/evidence/claim denominator mismatch")
    checked_sources = 0
    for claim_id, claim in claims.items():
        review = reviews[claim_id]
        if not isinstance(review, dict) or review.get("status") != "reviewed" or not nonempty(review.get("reviewer")) or not nonempty(review.get("conclusion")):
            raise ValueError(f"{claim_id}: missing terminal human review")
        date.fromisoformat(review.get("reviewed_on", ""))
        sources = claim.get("sources")
        source_reviews = review.get("sources")
        if not isinstance(sources, list) or not isinstance(source_reviews, list) or len(sources) != len(source_reviews):
            raise ValueError(f"{claim_id}: missing source reviews")
        urls = [s.get("url") for s in sources]
        if len(set(urls)) != len(urls) or {s.get("url") for s in source_reviews} != set(urls):
            raise ValueError(f"{claim_id}: source URL set mismatch")
        if not sources and (claim.get("status") != "not_testable" or not nonempty(review.get("nonempirical_reason"))):
            raise ValueError(f"{claim_id}: empty empirical sources")
        by_url = {s["url"]: s for s in source_reviews}
        for source in sources:
            record = by_url[source["url"]]
            url = urlparse(source["url"])
            if url.scheme not in {"http", "https"} or not url.hostname:
                raise ValueError(f"{claim_id}: invalid source URL")
            if not nonempty(source.get("title")) or type(source.get("year")) is not int or not 1000 <= source["year"] <= 9999:
                raise ValueError(f"{claim_id}: missing publication metadata")
            if record.get("access_level") not in ACCESS or record.get("locator_basis") != record.get("access_level"):
                raise ValueError(f"{claim_id}: access/locator basis mismatch")
            date.fromisoformat(record.get("checked_on", ""))
            for key in ("locator", "support", "scope_limit", "correction_check"):
                if not nonempty(record.get(key)): raise ValueError(f"{claim_id}: missing {key}")
            metadata = record.get("metadata")
            if not isinstance(metadata, dict) or metadata.get("title") != source.get("title") or metadata.get("year") != source.get("year") or not nonempty(metadata.get("authors")):
                raise ValueError(f"{claim_id}: source metadata mismatch")
            if "doi" in source and (not nonempty(source["doi"]) or not nonempty(metadata.get("doi"))):
                raise ValueError(f"{claim_id}: DOI missing from verified metadata")
            if any("doi" in obj and not nonempty(obj["doi"]) for obj in (metadata, record)):
                raise ValueError(f"{claim_id}: blank DOI")
            identifiers = [s.get("doi") for s in (source, metadata, record) if s.get("doi")]
            if any(not nonempty(x) or not re.fullmatch(r"10\.\d{4,9}/\S+", doi(x)) for x in identifiers) or len({doi(x) for x in identifiers}) > 1:
                raise ValueError(f"{claim_id}: DOI metadata mismatch")
            excerpt = record.get("support_excerpt")
            if not nonempty(excerpt) or record.get("support_sha256") != hashlib.sha256(excerpt.encode()).hexdigest():
                raise ValueError(f"{claim_id}: missing or altered supporting excerpt")
            checked_sources += 1
    return {"status": "pass", "claims_checked": len(claims), "sources_checked": checked_sources,
            "boundary": "receipt structure and versions; scientific correctness requires reviewer judgment"}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("receipt", type=Path); p.add_argument("--distill", type=Path, required=True)
    p.add_argument("--enrich", type=Path, required=True)
    a = p.parse_args()
    try:
        load = lambda f: json.loads(f.read_text(encoding="utf-8"))
        h = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
        print(json.dumps(verify(load(a.receipt), load(a.distill), load(a.enrich), h(a.distill), h(a.enrich)), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, AttributeError, OSError) as error:
        print(str(error), file=sys.stderr); return 1


if __name__ == "__main__": sys.exit(main())
