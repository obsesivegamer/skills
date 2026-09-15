---
name: google-review-swarm
description: Build a category-balanced, city-specific tourist recommendation heat map from a sample Google Maps contributor. Find the reviewer's highly rated affinity anchors, cross-reference information-rich reviewers, expand underrepresented categories with bounded second-hop research, and rank organic intersections across hotels, restaurants, museums, attractions, tours, bars, shops, and experiences. Use for reviewer-network recommendations, collaborative-filtering travel research, best-of-the-best city lists, hotel discovery, or Google-review-derived destination heat maps.
---

# Google Review Swarm

Turn one public Google Maps reviewer into a bounded collaborative-filtering network. Separate recruitment evidence from organic discovery so the heat map rewards genuine intersections instead of sampling quotas.

## Establish inputs and budgets

Require a public Google Maps contributor URL and a target city, municipality, or clearly bounded location. Ask only when either is missing.

Use these defaults unless the user changes them:

- Affinity anchors: every 5-star place from the sample reviewer inside the target.
- Candidate reviewers screened per anchor: `25`.
- Usable reviewers selected per anchor: `8`, equal across anchors where public data permits.
- Qualifying downstream rating: 4 or 5 stars with positive or neutral-positive text.
- Maximum discovery depth: `2`.
- Maximum public profiles inspected: `120`.
- Category targets: accommodations `8`, food `15`, attractions/museums `8`, tours/experiences `4`, nightlife `5`, shopping `5`, wellness `3`.

Treat the municipality as the boundary unless the user requests a metro area or radius. Record any target changes before research.

## Use the model topology

- Run orchestration with GPT-5.6 Sol at high reasoning effort when available.
- Use GPT-5.6 Sol at low reasoning effort for seed, category-gap, and confirmation investigators.
- Give one isolated assignment to each investigator. Run batches or reuse completed investigators when concurrency is limited.
- Never claim unavailable model or effort settings.

The orchestrator owns reviewer selection, category coverage, deduplication, scoring, stopping, and the final recommendation.

## Phase 1: Audit affinity anchors

Use the browser surface selected by the user, or the browser chosen for the supplied URL. Work read-only.

Inspect the complete relevant Reviews history and place-specific contribution pages. Load older cards far enough to cover the target visit. Do not infer that a photo lacks a review from the initially visible feed.

Capture each target-place review's place, address, rating, relative date, text, category, and Maps link. The sample reviewer's 5-star places are **affinity anchors**, not consensus winners.

## Phase 2: Build balanced first-hop branches

For each anchor:

1. Screen the same candidate budget, normally 25 other 4- or 5-star reviewers.
2. Exclude the sample reviewer.
3. Prefer public profiles with accessible histories, at least two additional target-city reviews, multiple tourist categories, substantive review text, or a coherent target-city trip window.
4. Select the same usable-reviewer quota per anchor. If an anchor cannot reach it, exhaust the candidate budget and record the shortfall.
5. Inspect each selected profile's complete relevant target-city history and collect every qualifying place.

Selection may favor information richness, never a desired hotel or restaurant outcome. Record candidates screened, profiles usable, profiles selected, private/inaccessible profiles, and truncated profiles for every branch.

Give investigators [references/research-contract.md](references/research-contract.md). Use public aliases and profile URLs only; do not infer personal identity or demographics.

## Phase 3: Audit category coverage

Aggregate the first hop before ranking. Compare verified places with the category targets.

Preserve every qualifying tourist-category discovery in the category inventory even when its organic tally is one. Do not let the consensus tier hide category variety.

For each underfilled category, dispatch a category-gap investigator. It must remain rooted in the affinity network:

- Re-screen unused reviewers from every anchor branch.
- Prioritize profiles whose public target-city history contains the missing category.
- Label resulting records as targeted backfill so they are not mistaken for an unbiased category-frequency sample.
- Stop when the target is met, the global profile cap is reached, or the accessible reviewer pool is exhausted.

## Phase 4: Use bounded second-hop confirmation

Second-hop research confirms candidate quality and creates real intersections; it must not inflate recruitment counts.

For accommodations:

1. Mine restaurant, attraction, museum, and nightlife branches specifically for target-city hotel or apartment reviews.
2. Treat every verified accommodation as a candidate, including tally-one candidates.
3. For up to five strongest candidates, inspect up to five positive reviewers from the candidate's place page.
4. Count a confirmation organically only when that reviewer also gave high marks to an original affinity anchor or at least two existing network places.
5. Record the confirming branch and overlap count. Do not count reviewers merely because they liked the candidate hotel.

Apply the same bounded confirmation method to another underfilled category when useful. Do not exceed depth two or the global profile cap.

## Evidence rules

- Count only an individual visible review card or place-specific contribution.
- Do not treat profile place counters as verified reviews.
- Verify the address is inside the requested boundary.
- Keep reviewer ratings separate from Google aggregate ratings.
- Exclude unverifiable rating/reviewer/place combinations.
- Record private, deleted, inaccessible, truncated, and lazy-loaded histories.
- Do not bypass CAPTCHA, access controls, privacy settings, or Google UI limits.

## Normalize and aggregate

Merge records into the schema in `references/research-contract.md`, then run:

```bash
python3 scripts/aggregate_reviews.py INPUT.json OUTPUT.json
```

Interpret metrics as follows:

- `recruitment_tally`: reviewers recruited from that same anchor's review page; audit only, never a ranking signal.
- `organic_tally`: unique reviewers who endorsed the place after entering through another anchor or network path.
- `organic_seed_branch_count`: independent origin-anchor branches supporting the place.
- `taste_overlap_score`: summed original-anchor overlap among organic reviewers.
- `cross_branch_consensus`: at least two organic reviewers across at least two origin branches.

Resolve ambiguous name/address variants manually. Do not compare affinity anchors by recruitment tally.

## Rank and report

Rank only organic support using this order:

1. Organic unique-reviewer tally.
2. Independent organic branch count.
3. Taste-overlap score.
4. Organic five-star count and share.
5. Review specificity, tourist usefulness, and recency.

Use four output sections:

1. **Affinity anchors** — unranked starting places; show recruitment counts only as sampling audit.
2. **True network consensus** — cross-branch consensus only.
3. **Category discoveries** — all qualifying tally-one and same-branch discoveries grouped by category.
4. **Coverage audit** — target, verified options, organic options, consensus options, gap, and access limitations per category.

For every recommended place include its Maps link, category, neighborhood, organic tally, organic branch count, star distribution, evidence tier, and condensed review signal. State when no place achieves consensus.

Remove generic chains and practical services from the primary tourist list unless requested, but retain them in an optional appendix. Do not promote mixed or negative 4-star text merely because it clears the numeric threshold.

Render a geographic heat map only with verified coordinates. Otherwise provide a neighborhood-density table. Heat equals organic tally; branch count is the secondary signal.

## Integrity checks

Before finalizing:

- Confirm equal per-anchor reviewer quotas or explain each shortfall.
- Confirm affinity-anchor recruitment ratings did not become consensus votes.
- Confirm every consensus place has at least two organic reviewers and two independent origin branches.
- Confirm each primary entry is within the target boundary and has direct Maps evidence.
- Confirm the category inventory preserves qualified accommodations, tours, and attractions even at tally one.
- Report total screened, usable, selected, private/inaccessible, and truncated profiles.
- Explain that targeted backfill improves category coverage but is not an unbiased popularity sample.
- Explain that the swarm is bounded collaborative filtering, not a statistically representative survey.

