"""Unit-тести для generator/mapper.py."""
import pytest

from generator.mapper import map_devices
from generator.parser import RawDevice


def _dev(id_: int, name: str, type_key: str) -> RawDevice:
    return RawDevice(id=id_, name=name, type_key=type_key, raw_type=type_key.capitalize())


# ── Порожній список ───────────────────────────────────────────────────────────
def test_empty():
    r = map_devices([])
    assert r.mechs_count == 0
    assert r.devices == []
    assert r.gap_slots == []


# ── TypedIndex: сортування за id ─────────────────────────────────────────────
def test_typed_index_sorted_by_id():
    devs = [
        _dev(2, "Noria 2", "noria"),
        _dev(1, "Noria",   "noria"),
        _dev(3, "Redler",  "redler"),
    ]
    r = map_devices(devs)
    by_id = {d.id: d for d in r.devices}
    assert by_id[1].typed_index == 0
    assert by_id[2].typed_index == 1
    assert by_id[3].typed_index == 0


# ── MECHS_COUNT = max(id) ─────────────────────────────────────────────────────
def test_mechs_count():
    devs = [_dev(1, "Noria", "noria"), _dev(5, "Fan", "fan")]
    r = map_devices(devs)
    assert r.mechs_count == 5


# ── Прогалини ────────────────────────────────────────────────────────────────
def test_gap_slots():
    devs = [_dev(1, "Noria", "noria"), _dev(5, "Fan", "fan")]
    r = map_devices(devs)
    assert set(r.gap_slots) == {0, 2, 3, 4}


# ── Константи ─────────────────────────────────────────────────────────────────
def test_counts_full():
    devs = [
        _dev(1, "Noria",   "noria"),
        _dev(2, "Noria 2", "noria"),
        _dev(3, "Redler",  "redler"),
        _dev(4, "Gate2P",  "gate2p"),
        _dev(5, "Fan",     "fan"),
    ]
    r = map_devices(devs)
    assert r.counts["MECHS_COUNT"]    == 5   # max(id)
    assert r.counts["NORIAS_COUNT"]   == 2   # 2 норії
    assert r.counts["REDLERS_COUNT"]  == 1   # 1 редлер
    assert r.counts["GATES2P_COUNT"]  == 1   # 1 засувка
    assert r.counts["FANS_COUNT"]     == 1   # 1 вентилятор


# ── Порожній тип → count = 0 ─────────────────────────────────────────────────
def test_count_empty_type():
    devs = [_dev(1, "Noria", "noria")]
    r = map_devices(devs)
    assert r.counts["REDLERS_COUNT"] == 0
    assert r.counts["FANS_COUNT"]    == 0


# ── gate2p: has_simulator = False ─────────────────────────────────────────────
def test_no_simulator_gate2p():
    r = map_devices([_dev(4, "Gate2P", "gate2p")])
    assert r.devices[0].has_simulator is False


# ── noria: has_simulator = True ──────────────────────────────────────────────
def test_has_simulator_noria():
    r = map_devices([_dev(1, "Noria", "noria")])
    assert r.devices[0].has_simulator is True


# ── by_type grouping ─────────────────────────────────────────────────────────
def test_by_type_grouping():
    devs = [
        _dev(1, "N1", "noria"),
        _dev(2, "N2", "noria"),
        _dev(3, "R1", "redler"),
    ]
    r = map_devices(devs)
    assert len(r.by_type["noria"])  == 2
    assert len(r.by_type["redler"]) == 1


# ── TIA-типи ─────────────────────────────────────────────────────────────────
def test_tia_types():
    devs = [
        _dev(1, "Noria",  "noria"),
        _dev(2, "Redler", "redler"),
        _dev(3, "G",      "gate2p"),
        _dev(4, "Fan",    "fan"),
    ]
    r = map_devices(devs)
    by_id = {d.id: d for d in r.devices}
    assert by_id[1].tia_type == "TYPE_NORIA"
    assert by_id[2].tia_type == "TYPE_REDLER"
    assert by_id[3].tia_type == "TYPE_GATE2P"
    assert by_id[4].tia_type == "TYPE_FAN"
