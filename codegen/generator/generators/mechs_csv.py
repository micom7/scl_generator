"""Генератор Mechs.csv — константи розмірів масивів механізмів для TIA Portal."""
from __future__ import annotations

from typing import Any, Dict

from ..mapper import MapResult

# Порядок рядків у CSV (відповідає логіці Mechs.csv у проекті)
_CONST_ORDER = [
    "GATES2P_COUNT",
    "REDLERS_COUNT",
    "NORIAS_COUNT",
    "FANS_COUNT",
    "RECEIVING_PITS_COUNT",
    "SEPARATORS_COUNT",
    "VALVES3P_COUNT",
    "SILOS_COUNT",
    "SUSHKAS_COUNT",
    "MECHS_COUNT",
]

_COMMENTS = {
    "MECHS_COUNT":          "Верхня межа масиву Mechs[] (max SlotId серед усіх пристроїв)",
    "REDLERS_COUNT":        "Верхня межа масиву Redler[] (кількість редлерів - 1)",
    "NORIAS_COUNT":         "Верхня межа масиву Noria[] (кількість норій - 1)",
    "GATES2P_COUNT":        "Верхня межа масиву Gate2P[] (кількість засувок - 1)",
    "FANS_COUNT":           "Верхня межа масиву Fan[] (кількість вентиляторів - 1)",
    "RECEIVING_PITS_COUNT": "Верхня межа масиву ReceivingPit[] (кількість приймальних ям - 1)",
    "SEPARATORS_COUNT":     "Верхня межа масиву Separator[] (кількість сепараторів - 1)",
    "VALVES3P_COUNT":       "Верхня межа масиву Valve3P[] (кількість клапанів 3П - 1)",
    "SILOS_COUNT":          "Верхня межа масиву Silos[] (кількість силосів - 1)",
    "SUSHKAS_COUNT":        "Верхня межа масиву Sushka[] (кількість сушарок - 1)",
}


def generate_mechs_csv(result: MapResult, ctx: Dict[str, Any]) -> str:
    """Генерує вміст Mechs.csv для імпорту констант у TIA Portal.

    Формат: Name;Path;Data Type;Value;Comment
    Файл записується з UTF-8 BOM (додається у main.py).
    """
    lines = [
        "Name;Path;Data Type;Value;Comment",
    ]
    for const in _CONST_ORDER:
        val = result.counts.get(const, 0)
        comment = _COMMENTS.get(const, "")
        lines.append(f"{const};Mechs_;UInt;{val};{comment}")

    lines.append("")  # порожній рядок в кінці
    return "\n".join(lines)
