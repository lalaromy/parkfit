# Matching calibration (pilot) and iterations

**Buffer.** On the pilot slice (the 16 ground-truth garages present in both OSM and the city
register) the distance between the OSM object and the register point ranges 3–105 m
(entrances vs. building points; polygons vs. points). A 120 m buffer captures all of them;
200 m starts to pull in neighbouring garages in the Löwenstrasse cluster (Globus, Migros City,
Jelmoli within ~250 m of each other).

**Name threshold 0.55.** Token-set ratio on names with generic words removed ("Parkhaus",
"Parking", "AG", "Zürich"…). Below 0.5 the matcher starts pairing unrelated garages that
happen to share a street name.

**Iteration 1 → 2.** With score = 0.35·proximity + 0.55·name + 0.10·type, the register's
"Globus" was paired with OSM "Globus Valet Parking" (closer, identical token set) and the
real garage node — the one carrying `maxheight=1.90` — was flagged ambiguous. Adding a 0.05
bonus for exact normalised-name equality fixed this without changing any other pair.
Matching precision/recall on the ground truth went from 1.00 / 0.94 to 1.00 / 1.00.

**Ambiguity rule.** If the second-best candidate is within 0.10 of the best, or two records
claim the same anchor, the loser is flagged `ambiguous` and excluded from evaluation
(proposal risk R4). After iteration 2 one record remains ambiguous (the valet-parking node).
