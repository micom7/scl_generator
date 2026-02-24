"""Парсинг та валідація graph.json."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .defaults import NON_MECHANISM_TYPES, TYPE_MAPPING


@dataclass
class RawDevice:
    id: int
    name: str
    type_key: str   # normalized lowercase
    raw_type: str   # original string from JSON


@dataclass
class ParseResult:
    devices: List[RawDevice] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def parse_graph(data: dict) -> ParseResult:
    """Валідує структуру graph.json і повертає список пристроїв або помилки."""
    result = ParseResult()
    seen_ids: dict[int, str] = {}  # id → device name

    raw_devices = data.get("devices", [])
    if not isinstance(raw_devices, list):
        result.errors.append("Поле 'devices' повинно бути масивом.")
        return result

    for dev in raw_devices:
        if not isinstance(dev, dict):
            result.errors.append("Кожен елемент 'devices' повинен бути об'єктом.")
            continue

        name = dev.get("name") or "<без назви>"

        # --- Validate id ---
        raw_id = dev.get("id")
        if raw_id is None:
            result.errors.append(f'Пристрій "{name}": відсутній або null id.')
            continue

        try:
            dev_id = int(raw_id)
        except (ValueError, TypeError):
            result.errors.append(
                f'Пристрій "{name}" (id={raw_id!r}): id має бути невід\'ємним цілим числом.'
            )
            continue

        if dev_id < 0:
            result.errors.append(
                f'Пристрій "{name}" (id={dev_id}): id не може бути від\'ємним.'
            )
            continue

        if dev_id in seen_ids:
            result.errors.append(
                f'Пристрій "{name}" (id={dev_id}): дублікат id — '
                f'вже зайнятий пристроєм "{seen_ids[dev_id]}".'
            )
            continue

        seen_ids[dev_id] = name

        # --- Validate type ---
        raw_type = dev.get("type")
        if raw_type is None:
            result.errors.append(
                f'Пристрій "{name}" (id={dev_id}): тип відсутній або null '
                f'(нетипізований механізм).'
            )
            continue

        type_key = str(raw_type).lower()

        if type_key in NON_MECHANISM_TYPES:
            result.warnings.append(
                f'Пристрій "{name}" (id={dev_id}): тип "{raw_type}" є не-механізмом → пропущено.'
            )
            continue

        if type_key not in TYPE_MAPPING:
            result.errors.append(
                f'Пристрій "{name}" (id={dev_id}): тип "{raw_type}" не підтримується TIA Portal.'
            )
            continue

        result.devices.append(
            RawDevice(id=dev_id, name=name, type_key=type_key, raw_type=raw_type)
        )

    return result
