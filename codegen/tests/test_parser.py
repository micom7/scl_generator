"""Unit-тести для generator/parser.py (T1–T10 з ТЗ)."""
import json
import pathlib

import pytest

from generator.parser import ParseResult, parse_graph

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def _graph(devices, device_types=None):
    if device_types is None:
        device_types = [
            {"name": "noria"}, {"name": "redler"},
            {"name": "gate2P"}, {"name": "Fan"}, {"name": "Silo"},
        ]
    return {"devices": devices, "deviceTypes": device_types}


# ── T1: всі типи ─────────────────────────────────────────────────────────────
def test_t1_all_types():
    data = json.loads((FIXTURES / "graph_full.json").read_text())
    result = parse_graph(data)
    assert result.errors == [], result.errors
    # Silo → warn
    assert any("Silo" in w for w in result.warnings)
    # 5 механізмів (noria×2, redler, gate2p, fan); Silo пропущено
    assert len(result.devices) == 5


# ── T2: лише Silo ────────────────────────────────────────────────────────────
def test_t2_only_silos():
    data = _graph([
        {"name": "Silo A", "id": "1", "type": "Silo"},
        {"name": "Silo B", "id": "2", "type": "Silo"},
    ])
    result = parse_graph(data)
    assert result.errors == []
    assert result.devices == []
    assert len(result.warnings) == 2


# ── T3: 2 норії + 1 редлер ────────────────────────────────────────────────────
def test_t3_two_norias_one_redler():
    data = _graph([
        {"name": "Noria",   "id": "1", "type": "noria"},
        {"name": "Noria 2", "id": "2", "type": "noria"},
        {"name": "Redler",  "id": "3", "type": "redler"},
    ])
    result = parse_graph(data)
    assert result.errors == []
    assert len(result.devices) == 3
    ids = {d.id for d in result.devices}
    assert ids == {1, 2, 3}


# ── T4: порожній devices ───────────────────────────────────────────────────────
def test_t4_empty_devices():
    data = json.loads((FIXTURES / "graph_empty.json").read_text())
    result = parse_graph(data)
    assert result.errors == []
    assert result.devices == []


# ── T5: дублікат id ──────────────────────────────────────────────────────────
def test_t5_duplicate_id():
    data = _graph([
        {"name": "Noria",  "id": "1", "type": "noria"},
        {"name": "Redler", "id": "1", "type": "redler"},
    ])
    result = parse_graph(data)
    assert len(result.errors) == 1
    assert "дублікат" in result.errors[0]


# ── T6: невалідний JSON (перевірка на рівні main.py, але parser — через dict) ─
def test_t6_invalid_json_not_handled_by_parser():
    """Parser приймає dict; невалідний JSON обробляється в main.py."""
    raw = (FIXTURES / "graph_invalid.json").read_bytes()
    with pytest.raises(Exception):
        json.loads(raw)


# ── T7: type=null ─────────────────────────────────────────────────────────────
def test_t7_null_type():
    data = _graph([{"name": "X", "id": "1", "type": None}])
    result = parse_graph(data)
    assert len(result.errors) == 1
    assert "null" in result.errors[0] or "нетипізований" in result.errors[0]


# ── T8: невідомий тип (не в маппінгу, не в NON_MECHANISM_TYPES) ───────────────
def test_t8_unknown_type():
    data = _graph([{"name": "Насос", "id": "1", "type": "Pump"}])
    result = parse_graph(data)
    assert len(result.errors) == 1
    assert "Pump" in result.errors[0]


# ── T9: нечисловий id ─────────────────────────────────────────────────────────
def test_t9_non_numeric_id():
    data = _graph([{"name": "X", "id": "abc", "type": "noria"}])
    result = parse_graph(data)
    assert len(result.errors) == 1


# ── T10: від'ємний id ─────────────────────────────────────────────────────────
def test_t10_negative_id():
    data = _graph([{"name": "X", "id": "-1", "type": "noria"}])
    result = parse_graph(data)
    assert len(result.errors) == 1


# ── Null id ───────────────────────────────────────────────────────────────────
def test_null_id():
    data = _graph([{"name": "X", "id": None, "type": "noria"}])
    result = parse_graph(data)
    assert len(result.errors) == 1


# ── Відсутній id ─────────────────────────────────────────────────────────────
def test_missing_id():
    data = _graph([{"name": "X", "type": "noria"}])
    result = parse_graph(data)
    assert len(result.errors) == 1


# ── Числовий (не рядковий) id ─────────────────────────────────────────────────
def test_numeric_id_as_int():
    data = _graph([{"name": "Noria", "id": 1, "type": "noria"}])
    result = parse_graph(data)
    assert result.errors == []
    assert result.devices[0].id == 1
