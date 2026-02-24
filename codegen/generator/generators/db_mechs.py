"""Генератор DB_Mechs.scl — масиви механізмів."""
from __future__ import annotations

from typing import Any, Dict, List

from ..defaults import TYPE_MAPPING
from ..mapper import MapResult

GROUP_ORDER = ["redler", "noria", "gate2p", "fan"]


def generate_db_mechs(result: MapResult, ctx: Dict[str, Any]) -> str:
    lines: List[str] = []
    total = len(result.devices)

    # --- Заголовок ---
    sep = "// " + "=" * 78
    lines += [
        sep,
        "// DB_Mechs - Масиви механізмів",
        sep,
        f"// Project  : {ctx['project_name']} v{ctx['version']}",
        f"// Generated: {ctx['timestamp']}",
        f"// Source   : {ctx['source']}",
        f"// Devices  : {total} / {total}",
        sep,
        "",
        'DATA_BLOCK "DB_Mechs"',
        "{ S7_Optimized_Access := 'TRUE' }",
        "VERSION : 1.0",
        "",
        "VAR",
        '    Mechs  : ARRAY [0.."MECHS_COUNT"]   OF "UDT_BaseMechanism";',
    ]

    # --- VAR: типізовані масиви ---
    for type_key in GROUP_ORDER:
        group = result.by_type.get(type_key, [])
        if not group:
            continue
        info = TYPE_MAPPING[type_key]
        count_const = info["count_const"]
        array_name = info["array_name"]
        udt = info["udt"]
        lines.append(f'    {array_name:<6} : ARRAY [0.."{count_const}"] OF "{udt}";')

    lines += ["END_VAR", "", "BEGIN", "    // === ІНІЦІАЛІЗАЦІЯ СЛОТІВ ==="]

    # --- BEGIN: ініціалізація ---
    for type_key in GROUP_ORDER:
        group = result.by_type.get(type_key, [])
        if not group:
            continue
        info = TYPE_MAPPING[type_key]
        tia_type = info["tia_type"]
        type_name = info["array_name"]
        group_sorted = sorted(group, key=lambda d: d.id)

        if len(group_sorted) == 1:
            id_range = f"slot {group_sorted[0].id}"
        else:
            id_range = f"slots {group_sorted[0].id}..{group_sorted[-1].id}"

        lines.append("")
        lines.append(f"    // --- {type_name} ({id_range}) ---")

        for dev in group_sorted:
            lines.append(f'    // {dev.raw_type} "{dev.name}" (id={dev.id})')
            lines.append(f"    Mechs[{dev.id}].SlotId     := {dev.id};")
            lines.append(f'    Mechs[{dev.id}].DeviceType := "{tia_type}";')
            lines.append(f"    Mechs[{dev.id}].TypedIndex := {dev.typed_index};")
            lines.append(f"    Mechs[{dev.id}].Enable_OK  := TRUE;")
            lines.append("")

    lines.append("END_DATA_BLOCK")
    lines.append("")

    return "\n".join(lines)
