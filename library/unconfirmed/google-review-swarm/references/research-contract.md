# Research contract

Use this contract for seed investigators, category-gap investigators, second-hop confirmation investigators, and the merged dataset.

## Assignment fields

- `sample_reviewer_url`
- `origin_seed` and `origin_seed_key`
- `seed_url`
- `target_location`
- `candidate_screening_budget` (default `25`)
- `selected_reviewer_quota` (default `8`)
- `downstream_min_rating` (default `4`)
- `assignment_type`: `first_hop`, `category_backfill`, or `second_hop_confirmation`
- `target_category` when applicable
- `max_depth` (default `2`)

Use direct, read-only Google Maps evidence. Exclude the sample reviewer and places outside the target boundary.

## Required investigator report

Return:

1. Candidates screened, public profiles usable, profiles selected, private/inaccessible profiles, and truncated profiles.
2. Reviewer alias, profile URL, recruiting-seed rating, and review age for every selected reviewer.
3. One recruiting-anchor record and one record for every qualifying downstream endorsement.
4. The number of original anchors that each reviewer independently endorsed.
5. Category, boundary, access, truncation, and backfill limitations.

Do not silently replace inaccessible reviewers. Continue screening until the quota or candidate budget is exhausted.

## Merged JSON schema

The aggregator accepts a top-level array or an object containing `records`, optional `category_targets`, and optional `screening`.

```json
{
  "category_targets": {
    "accommodations": 8,
    "food": 15,
    "attractions": 8,
    "tours": 4,
    "nightlife": 5,
    "shopping": 5,
    "wellness": 3
  },
  "screening": {
    "Seed A": {
      "candidates_screened": 25,
      "usable_profiles": 10,
      "selected_profiles": 8,
      "private_or_inaccessible": 12,
      "truncated_profiles": 3
    }
  },
  "records": [
    {
      "origin_seed": "Seed A",
      "origin_seed_key": "google-place-id-seed-a",
      "is_recruiting_seed_endorsement": false,
      "assignment_type": "first_hop",
      "discovery_hop": 1,
      "reviewer_alias": "Public alias",
      "reviewer_profile_url": "https://www.google.com/maps/contrib/.../reviews",
      "reviewer_overlap_seed_count": 1,
      "place_name": "Example Place",
      "place_key": "google place id or normalized name-address key",
      "place_url": "https://www.google.com/maps/...",
      "category": "Museum",
      "category_group": "attractions",
      "address": "Street, postal code, City, Country",
      "neighborhood": "District",
      "target_location": "City",
      "city_validated": true,
      "rating": 5,
      "review_age": "2 months ago",
      "review_summary": "Specific one-sentence paraphrase.",
      "source_url": "https://www.google.com/maps/contrib/.../place/...",
      "evidence_status": "verified"
    }
  ]
}
```

## Record semantics

- Set `is_recruiting_seed_endorsement: true` only when the reviewer was recruited from the same place's review page. This evidence belongs to `recruitment_tally`, not organic consensus.
- Set it to `false` when the place was found through another seed or network path, even when the place is also an original affinity anchor.
- Use `discovery_hop: 0` for recruiting-anchor records, `1` for first-hop or backfill discoveries, and `2` for confirmations.
- Use `assignment_type: category_backfill` for targeted coverage work and disclose that selection bias in the final report.
- `reviewer_overlap_seed_count` is the number of original affinity anchors the reviewer independently rated highly; never infer missing overlap.

## Normalization

- Prefer a Google place ID for each place and origin seed key. Otherwise use exact name plus full address.
- Use the contributor profile URL as reviewer identity.
- Use one of these category groups: `accommodations`, `food`, `attractions`, `tours`, `nightlife`, `shopping`, `wellness`, `practical`, or `other`.
- Set `city_validated` only after address-level municipality verification.
- Set `evidence_status: verified` only when reviewer, rating, and place are visible together.
- Preserve relative dates and paraphrase review text.
- Return one support record per reviewer-place-origin-branch combination. The aggregator preserves branch intersections while deduplicating exact support edges.

