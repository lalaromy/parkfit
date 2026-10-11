# Design decisions and deviations from the proposal

| Topic | Proposal | Implemented | Why |
|---|---|---|---|
| Structured sources | OSM + Google Places | OSM, City of Zurich OGD register, operator (PLS) pages, Google Places | Places was added last (key obtained 10 Oct). The register is the anchor for matching (91 % completeness, curated); PLS is the only source besides OSM that publishes heights; Places adds the long tail (the only source for two surveyed garages) but needs type/name filtering and carries no dimension evidence. |
| Spatial store | PostGIS | PostGIS **or** SQLite behind one `Store` interface | A marker must be able to run the evaluation with Python alone; PostGIS is verified via docker compose. |
| Fusion model | weighted vs Dempster–Shafer, choose one | both implemented, both evaluated | They agree on every multi-source feature in the study area (conflict mass K = 0 when sources agree within 5 cm). The weighted model is used by default because its output is easier to explain in the evidence chain. |
| Inferred attributes | context priors | per-facility-type median of observed heights in the study area; Swiss norm values for bay width and slope | No source publishes bay width or slope; the ground truth is the only measurement, so these remain *inferred* and are evaluated as such. |
| Ground truth size | ≥ 80 | 23 field-surveyed facilities | Three survey days; risk R3. Each facility yields 5 labelled cases (one per profile), i.e. 115 classification decisions. |

| Evaluation join | nearest feature within 150 m | verified identifiers per source, explicit unmatched outcome; baselines rebuilt from their own sources | The proximity join scored four facilities against the wrong feature and let baselines inherit groupings from excluded sources (found when the first draft of the report was reviewed, 11 Oct 2026). |
