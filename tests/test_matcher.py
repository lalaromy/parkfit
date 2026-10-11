from parkfit.matching.matcher import (
    build_groups,
    match_source_pair,
    name_similarity,
    normalise_name,
)


def test_normalise_strips_generic_words():
    assert normalise_name("Parkhaus Urania") == "urania"
    assert normalise_name("Parking Hohe Promenade AG") == "hohe promenade"
    assert name_similarity("Parkhaus Opéra", "Opéra") > 0.9


def test_spatial_and_name_match(rec_factory):
    a = [rec_factory("osm", "n1", "Parkhaus Urania", 47.3744, 8.5408)]
    b = [rec_factory("zurich_ogd", "p1", "Urania", 47.37437, 8.54075),
         rec_factory("zurich_ogd", "p2", "Jelmoli", 47.37384, 8.5365)]
    mapping, amb = match_source_pair(a, b)
    assert mapping == {"osm:n1": "zurich_ogd:p1"} and not amb


def test_far_apart_does_not_match(rec_factory):
    a = [rec_factory("osm", "n1", "Urania", 47.39, 8.55)]
    b = [rec_factory("zurich_ogd", "p1", "Urania", 47.37437, 8.54075)]
    mapping, _ = match_source_pair(a, b)
    assert mapping == {}


def test_ambiguous_flagged_not_guessed(rec_factory):
    a = [rec_factory("osm", "n1", "Migros", 47.3751, 8.5362)]
    b = [rec_factory("zurich_ogd", "p1", "Migros", 47.37512, 8.53625),
         rec_factory("zurich_ogd", "p2", "Migros", 47.37530, 8.53640)]
    mapping, amb = match_source_pair(a, b)
    assert mapping == {} and amb == {"osm:n1"}


def test_build_groups_singletons_preserved(rec_factory):
    by = {"zurich_ogd": [rec_factory("zurich_ogd", "p1", "Urania", 47.37437, 8.54075)],
          "osm": [rec_factory("osm", "n1", "Parkhaus Urania", 47.3744, 8.5408),
                  rec_factory("osm", "n2", "Tiefgarage Müllerstrasse", 47.37425, 8.53111)]}
    groups = build_groups(by)
    assert len(groups) == 2
    assert sorted(len(g.members) for g in groups) == [1, 2]
