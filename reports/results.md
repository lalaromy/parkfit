# parkfit evaluation results

Ground-truth facilities: 23. Each configuration runs matching, fusion and inference on its own sources only; facilities are joined to fused features by verified record identifiers.

## Label balance (facilities that really fit, per profile)

| profile | fits | of |
|---|---|---|
| compact car (VW Golf) | 23 | 23 |
| mid-size SUV (VW Tiguan) | 23 | 23 |
| large SUV (Range Rover) | 20 | 23 |
| standard-roof van (VW T6.1) | 21 | 23 |
| high-roof van (Sprinter H2) | 2 | 23 |

## Source completeness (facility present under a verified identifier)

| source | present | share |
|---|---|---|
| osm | 16/23 | 70% |
| zurich_ogd | 21/23 | 91% |
| pls | 14/23 | 61% |
| places | 20/23 | 87% |

## Matching quality, all-sources configuration (facilities with verified ids in >= 2 sources)

precision 1.0, recall 1.0, F1 1.0 (tp 20, fp 0, fn 0)

## Suitability classification, pooled over the five profiles (115 decisions)

| configuration | features | unmatched | TP | FP | FN | TN | precision | recall | F1 | accuracy | false-admission rate | balanced accuracy | height MAE obs (n) | errors by stage |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| always fits | - | - | 89 | 26 | 0 | 0 | 0.774 | 1.0 | 0.873 | 0.774 | 1.0 | 0.5 | - | - |
| osm_only | 69 | 7 | 62 | 2 | 27 | 24 | 0.969 | 0.697 | 0.81 | 0.748 | 0.077 | 0.81 | 0.135 (10) | {'completeness': 26, 'inference': 1, 'fusion': 1, 'granularity': 1} |
| ogd_only | 52 | 2 | 79 | 5 | 10 | 21 | 0.94 | 0.888 | 0.913 | 0.87 | 0.192 | 0.848 | None (0) | {'completeness': 8, 'inference': 6, 'granularity': 1} |
| places_only | 133 | 3 | 77 | 3 | 12 | 23 | 0.963 | 0.865 | 0.911 | 0.87 | 0.115 | 0.875 | None (0) | {'completeness': 10, 'inference': 4, 'granularity': 1} |
| osm+ogd | 95 | 2 | 80 | 4 | 9 | 22 | 0.952 | 0.899 | 0.925 | 0.887 | 0.154 | 0.873 | 0.135 (10) | {'completeness': 8, 'inference': 3, 'fusion': 1, 'granularity': 1} |
| osm+ogd+pls | 95 | 2 | 80 | 4 | 9 | 22 | 0.952 | 0.899 | 0.925 | 0.887 | 0.154 | 0.873 | 0.1 (15) | {'completeness': 8, 'fusion': 2, 'inference': 2, 'granularity': 1} |
| all_weighted | 188 | 2 | 80 | 4 | 9 | 22 | 0.952 | 0.899 | 0.925 | 0.887 | 0.154 | 0.873 | 0.1 (15) | {'completeness': 8, 'fusion': 2, 'inference': 2, 'granularity': 1} |
| all_dempster_shafer | 188 | 2 | 80 | 4 | 9 | 22 | 0.952 | 0.899 | 0.925 | 0.887 | 0.154 | 0.873 | 0.1 (15) | {'completeness': 8, 'fusion': 2, 'inference': 2, 'granularity': 1} |

## Per-profile F1 / false-admission rate

| configuration | compact car (VW Golf) | mid-size SUV (VW Tiguan) | large SUV (Range Rover) | standard-roof van (VW T6.1) | high-roof van (Sprinter H2) |
|---|---|---|---|---|---|
| always fits | 1.0 / None | 1.0 / None | 0.93 / 1.0 | 0.955 / 1.0 | 0.16 / 1.0 |
| osm_only | 0.821 / None | 0.821 / None | 0.778 / 0.667 | 0.833 / 0.0 | 0.667 / 0.0 |
| ogd_only | 0.955 / None | 0.955 / None | 0.878 / 1.0 | 0.905 / 1.0 | 0.0 / 0.0 |
| places_only | 0.93 / None | 0.93 / None | 0.9 / 0.667 | 0.927 / 0.5 | 0.0 / 0.0 |
| osm+ogd | 0.955 / None | 0.955 / None | 0.878 / 1.0 | 0.927 / 0.5 | 0.667 / 0.0 |
| osm+ogd+pls | 0.955 / None | 0.955 / None | 0.878 / 1.0 | 0.927 / 0.5 | 0.667 / 0.0 |
| all_weighted | 0.955 / None | 0.955 / None | 0.878 / 1.0 | 0.927 / 0.5 | 0.667 / 0.0 |
| all_dempster_shafer | 0.955 / None | 0.955 / None | 0.878 / 1.0 | 0.927 / 0.5 | 0.667 / 0.0 |

## Per-profile confusion (TP/FP/FN/TN), all four sources weighted

- compact car (VW Golf): 21/0/2/0
- mid-size SUV (VW Tiguan): 21/0/2/0
- large SUV (Range Rover): 18/3/2/0
- standard-roof van (VW T6.1): 19/1/2/1
- high-roof van (Sprinter H2): 1/0/1/21

## Unmatched facilities per configuration

- osm_only: GT03, GT10, GT11, GT13, GT14, GT17, GT19
- ogd_only: GT10, GT14
- places_only: GT10, GT11, GT14
- osm+ogd: GT10, GT14
- osm+ogd+pls: GT10, GT14
- all_weighted: GT10, GT14
- all_dempster_shafer: GT10, GT14

## Weighted vs Dempster-Shafer

10 features have >= 2 height observations; models agree on 10, disagree on 0.

- City Parking: values ['2.1@osm', '2.1@pls'] -> weighted 2.1 (conf 0.975), DS 2.1 (bel 0.975, K=0.0)
- Parkhaus Feldegg: values ['2.05@osm', '2.05@pls'] -> weighted 2.05 (conf 0.975), DS 2.05 (bel 0.975, K=0.0)
- Globus: values ['1.9@osm', '1.9@pls'] -> weighted 1.9 (conf 0.975), DS 1.9 (bel 0.975, K=0.0)
- Helvetiaplatz: values ['2.1@osm', '2.1@pls'] -> weighted 2.1 (conf 0.97), DS 2.1 (bel 0.97, K=0.0)
- Parkhaus Hohe Promenade: values ['2.1@osm', '2.1@pls'] -> weighted 2.1 (conf 0.98), DS 2.1 (bel 0.98, K=0.0)
- Parkhaus Jelmoli: values ['2.0@osm', '2.0@pls'] -> weighted 2.0 (conf 0.98), DS 2.0 (bel 0.98, K=0.0)
- Parkhaus Opéra: values ['2.1@osm', '2.1@pls'] -> weighted 2.1 (conf 0.98), DS 2.1 (bel 0.98, K=0.0)
- Parkhaus Stampfenbach: values ['2.0@osm', '2.0@pls'] -> weighted 2.0 (conf 0.965), DS 2.0 (bel 0.965, K=0.0)
- Parkhaus Urania: values ['2.1@osm', '2.1@pls'] -> weighted 2.1 (conf 0.975), DS 2.1 (bel 0.975, K=0.0)
- Parkhaus Zürichhorn: values ['2.0@osm', '2.0@pls'] -> weighted 2.0 (conf 0.975), DS 2.0 (bel 0.975, K=0.0)

## Error listing (all configurations)

- [osm_only] compact car (VW Golf) / GT03 Parkhaus Europaallee Haus F (Eisgasse): completeness: facility absent from every source in this configuration
- [osm_only] compact car (VW Golf) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm_only] compact car (VW Golf) / GT11 Parkhaus Migros Limmatplatz: completeness: facility absent from every source in this configuration
- [osm_only] compact car (VW Golf) / GT13 Parkhaus Migros Kreuzplatz: completeness: facility absent from every source in this configuration
- [osm_only] compact car (VW Golf) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm_only] compact car (VW Golf) / GT17 Parkhaus Kantonsschule Rämibühl: completeness: facility absent from every source in this configuration
- [osm_only] compact car (VW Golf) / GT19 Parkhaus Unispital Nord (USZ Nord): completeness: facility absent from every source in this configuration
- [osm_only] mid-size SUV (VW Tiguan) / GT03 Parkhaus Europaallee Haus F (Eisgasse): completeness: facility absent from every source in this configuration
- [osm_only] mid-size SUV (VW Tiguan) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm_only] mid-size SUV (VW Tiguan) / GT11 Parkhaus Migros Limmatplatz: completeness: facility absent from every source in this configuration
- [osm_only] mid-size SUV (VW Tiguan) / GT13 Parkhaus Migros Kreuzplatz: completeness: facility absent from every source in this configuration
- [osm_only] mid-size SUV (VW Tiguan) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm_only] mid-size SUV (VW Tiguan) / GT17 Parkhaus Kantonsschule Rämibühl: completeness: facility absent from every source in this configuration
- [osm_only] mid-size SUV (VW Tiguan) / GT19 Parkhaus Unispital Nord (USZ Nord): completeness: facility absent from every source in this configuration
- [osm_only] large SUV (Range Rover) / GT02 Parking Bleicherweg: inference: fused height 2.1 (inferred, conf 0.35) vs posted 2.0; bay 2.17 m; verdict tight
- [osm_only] large SUV (Range Rover) / GT03 Parkhaus Europaallee Haus F (Eisgasse): completeness: facility absent from every source in this configuration
- [osm_only] large SUV (Range Rover) / GT09 Parkhaus Jelmoli: fusion: fused height 2.0 (observed, conf 0.8) vs posted 2.0; bay 2.18 m; verdict tight
- [osm_only] large SUV (Range Rover) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm_only] large SUV (Range Rover) / GT13 Parkhaus Migros Kreuzplatz: completeness: facility absent from every source in this configuration
- [osm_only] large SUV (Range Rover) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm_only] large SUV (Range Rover) / GT17 Parkhaus Kantonsschule Rämibühl: completeness: facility absent from every source in this configuration
- [osm_only] large SUV (Range Rover) / GT19 Parkhaus Unispital Nord (USZ Nord): completeness: facility absent from every source in this configuration
- [osm_only] standard-roof van (VW T6.1) / GT03 Parkhaus Europaallee Haus F (Eisgasse): completeness: facility absent from every source in this configuration
- [osm_only] standard-roof van (VW T6.1) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm_only] standard-roof van (VW T6.1) / GT13 Parkhaus Migros Kreuzplatz: completeness: facility absent from every source in this configuration
- [osm_only] standard-roof van (VW T6.1) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm_only] standard-roof van (VW T6.1) / GT17 Parkhaus Kantonsschule Rämibühl: completeness: facility absent from every source in this configuration
- [osm_only] standard-roof van (VW T6.1) / GT19 Parkhaus Unispital Nord (USZ Nord): completeness: facility absent from every source in this configuration
- [osm_only] high-roof van (Sprinter H2) / GT18 Parking Talgarten: granularity: fused height 2.1 (observed, conf 0.8) vs posted 3.4; bay 2.35 m; verdict does_not_fit
- [ogd_only] compact car (VW Golf) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [ogd_only] compact car (VW Golf) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [ogd_only] mid-size SUV (VW Tiguan) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [ogd_only] mid-size SUV (VW Tiguan) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [ogd_only] large SUV (Range Rover) / GT02 Parking Bleicherweg: inference: fused height 2.0 (inferred, conf 0.35) vs posted 2.0; bay 2.17 m; verdict tight
- [ogd_only] large SUV (Range Rover) / GT09 Parkhaus Jelmoli: inference: fused height 2.0 (inferred, conf 0.35) vs posted 2.0; bay 2.18 m; verdict tight
- [ogd_only] large SUV (Range Rover) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [ogd_only] large SUV (Range Rover) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.0 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict tight
- [ogd_only] large SUV (Range Rover) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [ogd_only] standard-roof van (VW T6.1) / GT05 Parkhaus Globus: inference: fused height 2.0 (inferred, conf 0.35) vs posted 1.9; bay 2.58 m; verdict tight
- [ogd_only] standard-roof van (VW T6.1) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [ogd_only] standard-roof van (VW T6.1) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.0 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict tight
- [ogd_only] standard-roof van (VW T6.1) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [ogd_only] high-roof van (Sprinter H2) / GT18 Parking Talgarten: granularity: fused height 2.0 (inferred, conf 0.35) vs posted 3.4; bay 2.35 m; verdict does_not_fit
- [ogd_only] high-roof van (Sprinter H2) / GT22 Parkhaus Vorderberg: inference: fused height 2.0 (inferred, conf 0.35) vs posted None; bay 2.42 m; verdict does_not_fit
- [places_only] compact car (VW Golf) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [places_only] compact car (VW Golf) / GT11 Parkhaus Migros Limmatplatz: completeness: facility absent from every source in this configuration
- [places_only] compact car (VW Golf) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [places_only] mid-size SUV (VW Tiguan) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [places_only] mid-size SUV (VW Tiguan) / GT11 Parkhaus Migros Limmatplatz: completeness: facility absent from every source in this configuration
- [places_only] mid-size SUV (VW Tiguan) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [places_only] large SUV (Range Rover) / GT02 Parking Bleicherweg: inference: fused height 2.0 (inferred, conf 0.35) vs posted 2.0; bay 2.17 m; verdict tight
- [places_only] large SUV (Range Rover) / GT09 Parkhaus Jelmoli: inference: fused height 2.0 (inferred, conf 0.35) vs posted 2.0; bay 2.18 m; verdict tight
- [places_only] large SUV (Range Rover) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [places_only] large SUV (Range Rover) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [places_only] standard-roof van (VW T6.1) / GT05 Parkhaus Globus: inference: fused height 2.0 (inferred, conf 0.35) vs posted 1.9; bay 2.58 m; verdict tight
- [places_only] standard-roof van (VW T6.1) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [places_only] standard-roof van (VW T6.1) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [places_only] high-roof van (Sprinter H2) / GT18 Parking Talgarten: granularity: fused height 2.0 (inferred, conf 0.35) vs posted 3.4; bay 2.35 m; verdict does_not_fit
- [places_only] high-roof van (Sprinter H2) / GT22 Parkhaus Vorderberg: inference: fused height 2.0 (inferred, conf 0.35) vs posted None; bay 2.42 m; verdict does_not_fit
- [osm+ogd] compact car (VW Golf) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm+ogd] compact car (VW Golf) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm+ogd] mid-size SUV (VW Tiguan) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm+ogd] mid-size SUV (VW Tiguan) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm+ogd] large SUV (Range Rover) / GT02 Parking Bleicherweg: inference: fused height 2.1 (inferred, conf 0.35) vs posted 2.0; bay 2.17 m; verdict tight
- [osm+ogd] large SUV (Range Rover) / GT09 Parkhaus Jelmoli: fusion: fused height 2.0 (observed, conf 0.8) vs posted 2.0; bay 2.18 m; verdict tight
- [osm+ogd] large SUV (Range Rover) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm+ogd] large SUV (Range Rover) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.1 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict tight
- [osm+ogd] large SUV (Range Rover) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm+ogd] standard-roof van (VW T6.1) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm+ogd] standard-roof van (VW T6.1) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.1 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict fits
- [osm+ogd] standard-roof van (VW T6.1) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm+ogd] high-roof van (Sprinter H2) / GT18 Parking Talgarten: granularity: fused height 2.1 (observed, conf 0.8) vs posted 3.4; bay 2.35 m; verdict does_not_fit
- [osm+ogd+pls] compact car (VW Golf) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm+ogd+pls] compact car (VW Golf) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm+ogd+pls] mid-size SUV (VW Tiguan) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm+ogd+pls] mid-size SUV (VW Tiguan) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm+ogd+pls] large SUV (Range Rover) / GT02 Parking Bleicherweg: fusion: fused height 2.1 (observed, conf 0.9) vs posted 2.0; bay 2.17 m; verdict tight
- [osm+ogd+pls] large SUV (Range Rover) / GT09 Parkhaus Jelmoli: fusion: fused height 2.0 (observed, conf 0.98) vs posted 2.0; bay 2.18 m; verdict tight
- [osm+ogd+pls] large SUV (Range Rover) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm+ogd+pls] large SUV (Range Rover) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.1 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict tight
- [osm+ogd+pls] large SUV (Range Rover) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm+ogd+pls] standard-roof van (VW T6.1) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [osm+ogd+pls] standard-roof van (VW T6.1) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.1 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict fits
- [osm+ogd+pls] standard-roof van (VW T6.1) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [osm+ogd+pls] high-roof van (Sprinter H2) / GT18 Parking Talgarten: granularity: fused height 2.1 (observed, conf 0.8) vs posted 3.4; bay 2.35 m; verdict does_not_fit
- [all_weighted] compact car (VW Golf) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [all_weighted] compact car (VW Golf) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [all_weighted] mid-size SUV (VW Tiguan) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [all_weighted] mid-size SUV (VW Tiguan) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [all_weighted] large SUV (Range Rover) / GT02 Parking Bleicherweg: fusion: fused height 2.1 (observed, conf 0.9) vs posted 2.0; bay 2.17 m; verdict tight
- [all_weighted] large SUV (Range Rover) / GT09 Parkhaus Jelmoli: fusion: fused height 2.0 (observed, conf 0.98) vs posted 2.0; bay 2.18 m; verdict tight
- [all_weighted] large SUV (Range Rover) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [all_weighted] large SUV (Range Rover) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.08 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict tight
- [all_weighted] large SUV (Range Rover) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [all_weighted] standard-roof van (VW T6.1) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [all_weighted] standard-roof van (VW T6.1) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.08 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict fits
- [all_weighted] standard-roof van (VW T6.1) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [all_weighted] high-roof van (Sprinter H2) / GT18 Parking Talgarten: granularity: fused height 2.1 (observed, conf 0.8) vs posted 3.4; bay 2.35 m; verdict does_not_fit
- [all_dempster_shafer] compact car (VW Golf) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [all_dempster_shafer] compact car (VW Golf) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [all_dempster_shafer] mid-size SUV (VW Tiguan) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [all_dempster_shafer] mid-size SUV (VW Tiguan) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [all_dempster_shafer] large SUV (Range Rover) / GT02 Parking Bleicherweg: fusion: fused height 2.1 (observed, conf 0.9) vs posted 2.0; bay 2.17 m; verdict tight
- [all_dempster_shafer] large SUV (Range Rover) / GT09 Parkhaus Jelmoli: fusion: fused height 2.0 (observed, conf 0.98) vs posted 2.0; bay 2.18 m; verdict tight
- [all_dempster_shafer] large SUV (Range Rover) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [all_dempster_shafer] large SUV (Range Rover) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.1 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict tight
- [all_dempster_shafer] large SUV (Range Rover) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [all_dempster_shafer] standard-roof van (VW T6.1) / GT10 Parking Kongress (AMAG): completeness: facility absent from every source in this configuration
- [all_dempster_shafer] standard-roof van (VW T6.1) / GT11 Parkhaus Migros Limmatplatz: inference: fused height 2.1 (inferred, conf 0.35) vs posted 1.85; bay 2.41 m; verdict fits
- [all_dempster_shafer] standard-roof van (VW T6.1) / GT14 Tiefgarage Müllerstrasse 7a: completeness: facility absent from every source in this configuration
- [all_dempster_shafer] high-roof van (Sprinter H2) / GT18 Parking Talgarten: granularity: fused height 2.1 (observed, conf 0.8) vs posted 3.4; bay 2.35 m; verdict does_not_fit
