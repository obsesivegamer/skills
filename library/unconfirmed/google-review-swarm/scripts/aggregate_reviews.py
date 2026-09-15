#!/usr/bin/env python3
"""Aggregate Google Review Swarm records without circular seed scoring."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_CATEGORY_TARGETS = {
    "accommodations": 8,
    "food": 15,
    "attractions": 8,
    "tours": 4,
    "nightlife": 5,
    "shopping": 5,
    "wellness": 3,
}
VALID_CATEGORY_GROUPS = set(DEFAULT_CATEGORY_TARGETS) | {"practical", "other"}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")


def load_payload(path: str) -> tuple[list[dict[str, Any]], dict[str, int], dict[str, Any]]:
    if path == "-":
        data = json.load(sys.stdin)
    else:
        with Path(path).open(encoding="utf-8") as handle:
            data = json.load(handle)
    if isinstance(data, list):
        return data, dict(DEFAULT_CATEGORY_TARGETS), {}
    if not isinstance(data, dict) or not isinstance(data.get("records"), list):
        raise ValueError("Input must be a JSON array or an object with a records array")
    targets = dict(DEFAULT_CATEGORY_TARGETS)
    supplied_targets = data.get("category_targets", {})
    if not isinstance(supplied_targets, dict):
        raise ValueError("category_targets must be an object")
    for key, value in supplied_targets.items():
        normalized = slug(str(key)).replace("-", "_")
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"invalid category target for {key}")
        targets[normalized] = value
    screening = data.get("screening", {})
    if not isinstance(screening, dict):
        raise ValueError("screening must be an object")
    return data["records"], targets, screening


def record_place_key(record: dict[str, Any]) -> str:
    explicit = str(record.get("place_key") or "").strip()
    if explicit:
        return explicit
    name = str(record.get("place_name") or "").strip()
    address = str(record.get("address") or "").strip()
    return slug(f"{name}|{address}")


def is_recruitment(record: dict[str, Any]) -> bool:
    if "is_recruiting_seed_endorsement" in record:
        return record.get("is_recruiting_seed_endorsement") is True
    return record.get("is_seed") is True


def aggregate(
    records: list[dict[str, Any]],
    minimum_rating: int,
    category_targets: dict[str, int],
    screening: dict[str, Any],
) -> dict[str, Any]:
    warnings: list[str] = []
    edges: dict[tuple[str, str, str, bool], dict[str, Any]] = {}

    for index, record in enumerate(records):
        reviewer = str(record.get("reviewer_profile_url") or "").strip()
        name = str(record.get("place_name") or "").strip()
        origin = str(record.get("origin_seed") or "").strip()
        rating = record.get("rating")
        if not reviewer or not name or not origin:
            warnings.append(f"record {index}: missing reviewer, place, or origin_seed")
            continue
        if not isinstance(rating, (int, float)) or not 1 <= rating <= 5:
            warnings.append(f"record {index}: invalid rating")
            continue
        if rating < minimum_rating:
            continue
        if record.get("city_validated") is not True:
            warnings.append(f"record {index}: city_validated is not true")
            continue
        if record.get("evidence_status") != "verified":
            warnings.append(f"record {index}: evidence_status is not verified")
            continue

        group = slug(str(record.get("category_group") or "other")).replace("-", "_")
        if group not in VALID_CATEGORY_GROUPS:
            warnings.append(f"record {index}: unknown category_group {group}; using other")
            group = "other"
        key = record_place_key(record)
        recruitment = is_recruitment(record)
        edge_key = (reviewer, key, origin, recruitment)
        if edge_key in edges:
            if edges[edge_key].get("rating") != rating:
                warnings.append(f"record {index}: conflicting duplicate rating for {name}")
            continue
        edges[edge_key] = dict(record, _place_key=key, _category_group=group, _recruitment=recruitment)

    by_place: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges.values():
        by_place[edge["_place_key"]].append(edge)

    places: list[dict[str, Any]] = []
    for key, rows in by_place.items():
        representative = rows[0]
        recruitment_rows = [row for row in rows if row["_recruitment"]]
        organic_rows = [row for row in rows if not row["_recruitment"]]
        recruitment_reviewers = {row["reviewer_profile_url"] for row in recruitment_rows}
        organic_reviewers = {row["reviewer_profile_url"] for row in organic_rows}
        organic_branches = {row["origin_seed"] for row in organic_rows}

        organic_rating_by_reviewer: dict[str, int] = {}
        overlap_by_reviewer: dict[str, int] = {}
        for row in organic_rows:
            reviewer = row["reviewer_profile_url"]
            rating = int(row["rating"])
            previous = organic_rating_by_reviewer.get(reviewer)
            if previous is not None and previous != rating:
                warnings.append(f"conflicting organic ratings for {row.get('place_name')} by {reviewer}")
            organic_rating_by_reviewer[reviewer] = max(previous or rating, rating)
            overlap = row.get("reviewer_overlap_seed_count", 1)
            if not isinstance(overlap, int) or overlap < 0:
                overlap = 0
            overlap_by_reviewer[reviewer] = max(overlap_by_reviewer.get(reviewer, 0), overlap)

        organic_stars = Counter(organic_rating_by_reviewer.values())
        organic_tally = len(organic_reviewers)
        branch_count = len(organic_branches)
        anchor = bool(recruitment_rows)
        if organic_tally >= 2 and branch_count >= 2:
            tier = "cross_branch_consensus"
        elif organic_tally >= 2:
            tier = "multi_reviewer_discovery"
        elif organic_tally == 1:
            tier = "promising_discovery"
        else:
            tier = "affinity_anchor" if anchor else "unsupported"

        aliases = sorted({str(row.get("reviewer_alias") or "").strip() for row in organic_rows} - {""})
        summaries = sorted({str(row.get("review_summary") or "").strip() for row in organic_rows} - {""})
        assignment_types = sorted({str(row.get("assignment_type") or "first_hop") for row in organic_rows})
        places.append(
            {
                "place_key": key,
                "place_name": representative.get("place_name"),
                "place_url": representative.get("place_url"),
                "category": representative.get("category"),
                "category_group": representative["_category_group"],
                "address": representative.get("address"),
                "neighborhood": representative.get("neighborhood"),
                "is_affinity_anchor": anchor,
                "recruitment_tally": len(recruitment_reviewers),
                "organic_tally": organic_tally,
                "organic_seed_branch_count": branch_count,
                "organic_five_star_count": organic_stars.get(5, 0),
                "organic_four_star_count": organic_stars.get(4, 0),
                "taste_overlap_score": sum(overlap_by_reviewer.values()),
                "supporting_origin_seeds": sorted(organic_branches),
                "assignment_types": assignment_types,
                "evidence_tier": tier,
                "reviewer_aliases": aliases,
                "review_summaries": summaries,
            }
        )

    ranked_places = [place for place in places if place["organic_tally"] > 0]
    ranked_places.sort(
        key=lambda item: (
            -item["organic_tally"],
            -item["organic_seed_branch_count"],
            -item["taste_overlap_score"],
            -item["organic_five_star_count"],
            str(item["place_name"]).casefold(),
        )
    )
    affinity_anchors = sorted(
        [place for place in places if place["is_affinity_anchor"]],
        key=lambda item: str(item["place_name"]).casefold(),
    )

    seed_sampling: dict[str, int] = defaultdict(int)
    seed_reviewer_sets: dict[str, set[str]] = defaultdict(set)
    for edge in edges.values():
        if edge["_recruitment"]:
            seed_reviewer_sets[edge["origin_seed"]].add(edge["reviewer_profile_url"])
    for seed, reviewers in seed_reviewer_sets.items():
        seed_sampling[seed] = len(reviewers)
    sample_sizes = list(seed_sampling.values())
    balanced_sampling = len(set(sample_sizes)) <= 1 if sample_sizes else True
    if not balanced_sampling:
        warnings.append("seed reviewer samples are unequal; recruitment tallies are not comparable")

    coverage: dict[str, dict[str, int]] = {}
    for group, target in category_targets.items():
        group_places = [place for place in places if place["category_group"] == group and place["evidence_tier"] != "unsupported"]
        organic_places = [place for place in group_places if place["organic_tally"] > 0]
        consensus_places = [place for place in group_places if place["evidence_tier"] == "cross_branch_consensus"]
        coverage[group] = {
            "target": target,
            "verified_places": len(group_places),
            "organic_places": len(organic_places),
            "consensus_places": len(consensus_places),
            "gap": max(0, target - len(group_places)),
        }

    unique_reviewers = {reviewer for reviewer, _, _, _ in edges}
    unique_pairs = {(reviewer, place) for reviewer, place, _, _ in edges}
    recruitment_edges = sum(1 for edge in edges.values() if edge["_recruitment"])
    organic_edges = len(edges) - recruitment_edges
    return {
        "summary": {
            "unique_reviewers": len(unique_reviewers),
            "qualifying_reviewer_place_pairs": len(unique_pairs),
            "qualifying_support_edges": len(edges),
            "recruitment_edges": recruitment_edges,
            "organic_edges": organic_edges,
            "unique_places": len(places),
            "minimum_rating": minimum_rating,
            "balanced_seed_sampling": balanced_sampling,
        },
        "seed_sampling": dict(sorted(seed_sampling.items())),
        "screening": screening,
        "category_coverage": coverage,
        "affinity_anchors": affinity_anchors,
        "ranked_places": ranked_places,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", help="Input JSON path, or - for stdin")
    parser.add_argument("output", nargs="?", help="Output JSON path; omit for stdout")
    parser.add_argument("--minimum-rating", type=int, default=4, choices=(1, 2, 3, 4, 5))
    args = parser.parse_args()
    try:
        records, targets, screening = load_payload(args.input)
        result = aggregate(records, args.minimum_rating, targets, screening)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        Path(args.output).write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

