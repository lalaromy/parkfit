from parkfit.ingest.parsers import parse_height_m, parse_int


def test_height_formats():
    assert parse_height_m("2.10") == 2.1
    assert parse_height_m("2,05 m") == 2.05
    assert parse_height_m("210") == 2.1
    assert parse_height_m("6'6\"") == 1.98
    assert parse_height_m("default") is None
    assert parse_height_m("none") is None
    assert parse_height_m("") is None


def test_capacity():
    assert parse_int("620") == 620
    assert parse_int("approx. 50") == 50
    assert parse_int(None) is None
