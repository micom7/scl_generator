"""Генератор DB_SimConfig.scl — конфігурація симуляторів (RETAIN)."""
from __future__ import annotations

from typing import Any, Dict, List

from ..defaults import SIM_CONFIG_DEFAULTS, TYPE_MAPPING
from ..mapper import MapResult

GROUP_ORDER = ["redler", "noria", "gate2p", "fan"]


def generate_db_sim_config(result: MapResult, ctx: Dict[str, Any]) -> str:
    lines: List[str] = []

    # --- Заголовок ---
    sep = "// " + "=" * 78
    lines += [
        sep,
        "// DB_SimConfig - Конфігурація симуляторів механізмів",
        sep,
        f"// Generated: {ctx['timestamp']}",
        f"// Source   : {ctx['source']}",
        sep,
        "",
        'DATA_BLOCK "DB_SimConfig"',
        "{ S7_Optimized_Access := 'TRUE' }",
        "VERSION : 2.1",
        "",
        "VAR",
    ]

    # --- VAR: масиви конфігів ---
    for type_key in GROUP_ORDER:
        group = result.by_type.get(type_key, [])
        if not group:
            continue
        info = TYPE_MAPPING[type_key]
        array_name = info["array_name"]
        sim_config_udt = info["sim_config_udt"]
        count_const = info["count_const"]
        lines.append(f'    {array_name:<6} : ARRAY[0.."{count_const}"] OF "{sim_config_udt}";')

    lines += ["END_VAR", "", "BEGIN"]

    # --- BEGIN: значення за замовчуванням ---
    for type_key in GROUP_ORDER:
        group = result.by_type.get(type_key, [])
        if not group:
            continue
        info = TYPE_MAPPING[type_key]
        array_name = info["array_name"]
        defaults = SIM_CONFIG_DEFAULTS.get(type_key, [])
        group_sorted = sorted(group, key=lambda d: d.typed_index)

        lines.append(f"    // === {array_name} ===")
        for dev in group_sorted:
            lines.append(
                f'    // {dev.raw_type} "{dev.name}" (id={dev.id}, TypedIndex={dev.typed_index})'
            )
            for field_name, value in defaults:
                lines.append(f"    {array_name}[{dev.typed_index}].{field_name} := {value};")
            lines.append("")

    lines.append("END_DATA_BLOCK")
    lines.append("")

    return "\n".join(lines)
