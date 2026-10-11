from datetime import UTC, datetime

import pytest

from parkfit.schema import Observation, Provenance, SourceRecord


def prov(source, sid="1", version=None, ts=None):
    return Provenance(source=source, source_id=sid, retrieved_at=datetime.now(UTC),
                      version=version, source_timestamp=ts)


def obs(attr, value, conf, source="osm", kind="observed"):
    return Observation(attribute=attr, value=value, confidence=conf, kind=kind, provenance=prov(source))


@pytest.fixture
def rec_factory():
    def make(source, sid, name, lat, lon, ftype="underground", **attrs):
        o = [Observation(attribute="name", value=name, confidence=0.9, provenance=prov(source, sid))] if name else []
        for a, v in attrs.items():
            o.append(Observation(attribute=a, value=v, confidence=0.8, provenance=prov(source, sid)))
        return SourceRecord(source=source, source_id=sid, name=name, lat=lat, lon=lon,
                            facility_type=ftype, observations=o)
    return make
