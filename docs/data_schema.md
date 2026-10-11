# Data schema

## Ground truth CSV (`data/ground_truth/zurich_garages_2026.csv`)
| column | type | meaning |
|---|---|---|
| gt_id | str | GT01 … GT23 |
| name, address | str | as signed at the entrance |
| facility_type | enum | underground, multi-storey, surface_deck |
| lat, lon | float | WGS84 |
| coord_source | enum | exif_gps, ogd_wfs |
| survey_date | date | ISO |
| posted_maxheight_m | float or empty | posted customer-parking limit; empty = no sign |
| height_capture | enum | posted_sign, no_sign, public_record |
| height_note | str | what was signed, incl. secondary values |
| bay_width_cm | int | tape reading, outer line edge to outer line edge |
| width_capture | enum | tape_measure |
| clino_top_deg, clino_bottom_deg | int | clinometer display, verbatim |
| other_restrictions | str | weight, speed, vehicle-class bans |
| expected_osm_id, expected_ogd_name | str | identifiers used to evaluate the matcher |
| photo_prefix | str | file prefix of the survey photographs |

## Canonical records (`parkfit/schema.py`)
`SourceRecord(source, source_id, name, lat, lon, facility_type, observations[])` where each
`Observation(attribute, value, confidence, kind, provenance)` carries `Provenance(source,
source_id, url, retrieved_at, source_timestamp, version, raw_value)`.

`FusedFeature.attributes[attr] = FusedAttribute(value, confidence, kind, supporting[],
conflicting[], method, conflict)` — the evidence chain returned by the API.

## Fused attributes
maxheight (m), capacity, facility_type, name — fused from sources;
bay_width (m), slope_class — inferred only (no source publishes them), always `kind=inferred`.
