"""Маппінг пристроїв: призначення TypedIndex, SlotId, підрахунок констант."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .defaults import TYPE_MAPPING

# Порядок типів у виводі (відповідає GROUP_ORDER у генераторах)
TYPE_ORDER = ["redler", "noria", "gate2p", "fan"]
_CONST_MAP = {
    "noria":  "NORIAS_COUNT",
    "redler": "REDLERS_COUNT",
    "gate2p": "GATES2P_COUNT",
    "fan":    "FANS_COUNT",
}


@dataclass
class MappedDevice:
    id: int
    name: str
    type_key: str        # normalized lowercase
    raw_type: str        # original string
    tia_type: str        # e.g. "TYPE_NORIA"
    array_name: str      # e.g. "Noria"
    typed_index: int     # index within type group
    has_simulator: bool
    sim_state_udt: str
    sim_config_udt: str


@dataclass
class MapResult:
    devices: List[MappedDevice]
    mechs_count: int                           # max(id) among supported devices
    counts: Dict[str, int]                     # MECHS_COUNT, NORIAS_COUNT, …; -1 = пустий тип
    gap_slots: List[int]                       # слоти 0..mechs_count без пристроїв
    by_type: Dict[str, List[MappedDevice]]     # type_key → список (sorted by id)


def map_devices(raw_devices: list) -> MapResult:
    """Приймає список RawDevice, повертає MapResult."""
    if not raw_devices:
        return MapResult(
            devices=[],
            mechs_count=0,
            counts={
                "MECHS_COUNT":    0,
                "REDLERS_COUNT": 0,
                "NORIAS_COUNT":  0,
                "GATES2P_COUNT": 0,
                "FANS_COUNT":    0,
            },
            gap_slots=[],
            by_type={},
        )

    # --- Групуємо за type_key, сортуємо кожну групу за id ---
    by_type_raw: Dict[str, list] = {}
    for dev in raw_devices:
        by_type_raw.setdefault(dev.type_key, []).append(dev)
    for key in by_type_raw:
        by_type_raw[key].sort(key=lambda d: d.id)

    # --- Призначаємо TypedIndex ---
    typed_index_map: Dict[int, int] = {}
    for group in by_type_raw.values():
        for i, dev in enumerate(group):
            typed_index_map[dev.id] = i

    # --- Будуємо MappedDevice ---
    mapped: List[MappedDevice] = []
    for dev in raw_devices:
        info = TYPE_MAPPING[dev.type_key]
        mapped.append(MappedDevice(
            id=dev.id,
            name=dev.name,
            type_key=dev.type_key,
            raw_type=dev.raw_type,
            tia_type=info["tia_type"],
            array_name=info["array_name"],
            typed_index=typed_index_map[dev.id],
            has_simulator=info.get("has_simulator", False),
            sim_state_udt=info.get("sim_state_udt", ""),
            sim_config_udt=info.get("sim_config_udt", ""),
        ))

    mechs_count = max(d.id for d in mapped)

    # --- Прогалини ---
    occupied = {d.id for d in mapped}
    gap_slots = [i for i in range(0, mechs_count + 1) if i not in occupied]

    # --- Константи (верхня межа ARRAY[0..N], тобто len-1; 0 якщо типу немає) ---
    counts: Dict[str, int] = {"MECHS_COUNT": mechs_count}
    for type_key, const_name in _CONST_MAP.items():
        group = by_type_raw.get(type_key, [])
        counts[const_name] = len(group) - 1 if group else 0

    # --- by_type для генераторів (MappedDevice, sorted by id) ---
    by_type_mapped: Dict[str, List[MappedDevice]] = {}
    for dev in mapped:
        by_type_mapped.setdefault(dev.type_key, []).append(dev)
    for key in by_type_mapped:
        by_type_mapped[key].sort(key=lambda d: d.id)

    return MapResult(
        devices=mapped,
        mechs_count=mechs_count,
        counts=counts,
        gap_slots=gap_slots,
        by_type=by_type_mapped,
    )
