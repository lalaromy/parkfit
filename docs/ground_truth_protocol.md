# Ground-truth survey protocol (objective 5)

Dataset: `data/ground_truth/zurich_garages_2026.csv` (23 facilities). Schema: `docs/data_schema.md`.

## Study area
WGS84 bounding box 47.355 N – 47.395 N, 8.515 E – 8.565 E (Zurich inner city: Kreis 1 and the
adjoining parts of Kreis 4, 5, 6, 7 and 8). Chosen so that (a) it contains the densest cluster
of public garages in the city and (b) all three survey days could be walked.

## Enumeration
Facilities were enumerated from the City of Zurich register of publicly accessible garages and
then visited; two facilities not in the register (Müllerstrasse 7a, Parking Kongress) were
added when encountered on foot, so that *source completeness* can be measured and not only
attribute accuracy. 23 of the 52 register entries inside the box were surveyed in three
sessions (9 Sep, 10 Sep, 21 Sep 2026). The proposal's target of 80 features was not reached;
the shortfall and its effect on statistical power are discussed in the report (risk R3).

## Instrument (one visit ≈ 8 minutes)
1. **Entrance photograph** showing the posted height-restriction sign (Swiss signal 2.19 /
   "Durchfahrtshöhe" bar) and any other restriction signs (weight, speed, motorcycles, trailers).
   Recorded: `posted_maxheight_m`, `height_capture` (= `posted_sign` | `no_sign`), `other_restrictions`.
   Where an entrance carries a higher limit for a shared service lane and a lower one for the
   parking level (Park Hyatt, Neumünster), the *customer parking* value is recorded and the other
   value is noted.
2. **Bay width**: a 5 m tape laid across one ordinary bay on the first parking level reached,
   from the outer edge of one line marking to the outer edge of the next, photographed with the
   reading visible. Recorded to the centimetre (`bay_width_cm`). Accessible bays were avoided.
3. **Ramp slope**: a clinometer app (iPhone, "Angle/Car" mode) held flat on the steepest
   straight section of the entrance ramp; the two displayed angles are recorded verbatim
   (`clino_top_deg`, `clino_bottom_deg`). The top value is used as the ramp pitch.
4. **Interior photograph** of the parking level for context (lighting, columns, marking colour).
5. **Position**: EXIF GPS of the entrance photo where the phone recorded it (`coord_source =
   exif_gps`), otherwise the register coordinate (`ogd_wfs`).

## Known limitations of the instrument
* One bay per facility; widths vary within a garage, so `bay_width_cm` is a sample, not a mean.
* A facility can have two areas with different limits (Talgarten: outdoor area via the 3.4 m ramp,
  underground level 2.1 m). The survey records the higher limit, because a tall vehicle can park in the
  outdoor area, and notes both; the sources model only one value per facility, which the error
  taxonomy reports as a *granularity* error.
* Clinometer readings are hand-held and ±2° at best.

## Reproduction
Walk the facilities in the CSV with the instrument above; new rows need the same columns.
Photographs are kept outside the repository (file prefix in `photo_prefix`) for privacy and size.
