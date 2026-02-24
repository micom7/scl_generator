"""Генератор DB_SimMechs.scl — runtime-стани симуляторів (NON_RETAIN)."""
from __future__ import annotations

from typing import Any, Dict, List

from ..defaults import TYPE_MAPPING
from ..mapper import MapResult

GROUP_ORDER = ["redler", "noria", "fan"]  # Gate2P без симулятора


def generate_db_sim_mechs(result: MapResult, ctx: Dict[str, Any]) -> str:
    lines: List[str] = []
    has_gate2p = bool(result.by_type.get("gate2p"))

    # --- Заголовок ---
    sep = "// " + "=" * 78
    lines += [
        sep,
        "// DB_SimMechs - Стани симуляторів механізмів (runtime)",
        sep,
        f"// Generated: {ctx['timestamp']}",
        f"// Source   : {ctx['source']}",
    ]
    if has_gate2p:
        lines.append("// NOTE: Gate2P не включено (симулятор не реалізований)")
    lines += [
        sep,
        "",
        'DATA_BLOCK "DB_SimMechs"',
        "{ S7_Optimized_Access := 'TRUE' }",
        "VERSION : 2.0",
        "NON_RETAIN",
        "",
        "VAR",
    ]
    if has_gate2p:
        lines.append("    // NOTE: Gate2P виключено — FC_SimGate2P не реалізовано.")

    # --- VAR: масиви станів ---
    for type_key in GROUP_ORDER:
        group = result.by_type.get(type_key, [])
        if not group:
            continue
        info = TYPE_MAPPING[type_key]
        count_const = info["count_const"]
        array_name = info["array_name"]
        sim_state_udt = info["sim_state_udt"]
        lines.append(f'    {array_name:<6} : ARRAY[0.."{count_const}"] OF "{sim_state_udt}";')

    # BEGIN завжди порожній — NON_RETAIN, ініціалізується CPU при старті
    lines += ["END_VAR", "", "BEGIN", "END_DATA_BLOCK", ""]

    return "\n".join(lines)
