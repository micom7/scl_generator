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


# ── MECHS_COUNT = len(devices) - 1 (послідовні слоти, без прогалин) ──────────
def test_mechs_count():
    devs = [_dev(1, "Noria", "noria"), _dev(5, "Fan", "fan")]
    r = map_devices(devs)
    assert r.mechs_count == 1   # 2 devices → slots 0..1


# ── Прогалини завжди відсутні ────────────────────────────────────────────────
def test_gap_slots():
    devs = [_dev(1, "Noria", "noria"), _dev(5, "Fan", "fan")]
    r = map_devices(devs)
    assert r.gap_slots == []


# ── Послідовне призначення slot за зростанням id ─────────────────────────────
def test_sequential_slots():
    devs = [
        _dev(10, "Fan",   "fan"),
        _dev(3,  "Noria", "noria"),
        _dev(7,  "Gate",  "gate2p"),
    ]
    r = map_devices(devs)
    by_id = {d.id: d for d in r.devices}
    # сортування за id: 3→slot0, 7→slot1, 10→slot2
    assert by_id[3].slot  == 0
    assert by_id[7].slot  == 1
    assert by_id[10].slot == 2
    assert r.mechs_count  == 2


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
    assert r.counts["MECHS_COUNT"]    == 4   # len-1=4 — верхня межа Mechs[]
    assert r.counts["NORIAS_COUNT"]   == 1   # 2-1=1 — верхня межа Noria[0..1]
    assert r.counts["REDLERS_COUNT"]  == 0   # 1-1=0 — верхня межа Redler[0..0]
    assert r.counts["GATES2P_COUNT"]  == 0   # 1-1=0 — верхня межа Gate2P[0..0]
    assert r.counts["FANS_COUNT"]     == 0   # 1-1=0 — верхня межа Fan[0..0]


# ── Порожній тип → count = 0 ─────────────────────────────────────────────────
def test_count_empty_type():
    devs = [_dev(1, "Noria", "noria")]
    r = map_devices(devs)
    assert r.counts["REDLERS_COUNT"] == 0
    assert r.counts["FANS_COUNT"]    == 0


# ── gate2p: has_simulator = True (FC_SimGate2P реалізовано) ──────────────────
def test_has_simulator_gate2p():
    r = map_devices([_dev(4, "Gate2P", "gate2p")])
    assert r.devices[0].has_simulator is True


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
