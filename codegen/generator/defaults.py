# Типи, що є не-механізмами — ігноруються з попередженням [WARN]
NON_MECHANISM_TYPES = {"silo", "sensor", "label"}

# Маппінг JSON-типів → TIA Portal (ключі lowercase)
TYPE_MAPPING = {
    "noria": {
        "tia_type": "TYPE_NORIA",
        "udt": "UDT_Noria",
        "array_name": "Noria",
        "count_const": "NORIAS_COUNT",
        "has_simulator": True,
        "sim_state_udt": "UDT_SimNoriaState",
        "sim_config_udt": "UDT_SimNoriaConfig",
    },
    "redler": {
        "tia_type": "TYPE_REDLER",
        "udt": "UDT_Redler",
        "array_name": "Redler",
        "count_const": "REDLERS_COUNT",
        "has_simulator": True,
        "sim_state_udt": "UDT_SimRedlerState",
        "sim_config_udt": "UDT_SimRedlerConfig",
    },
    "gate2p": {
        "tia_type": "TYPE_GATE2P",
        "udt": "UDT_Gate2P",
        "array_name": "Gate2P",
        "count_const": "GATES2P_COUNT",
        "has_simulator": True,
        "sim_state_udt": "UDT_SimGate2PState",
        "sim_config_udt": "UDT_SimGate2PConfig",
    },
    "fan": {
        "tia_type": "TYPE_FAN",
        "udt": "UDT_Fan",
        "array_name": "Fan",
        "count_const": "FANS_COUNT",
        "has_simulator": True,
        "sim_state_udt": "UDT_SimFanState",
        "sim_config_udt": "UDT_SimFanConfig",
    },
}

# Значення за замовчуванням для DB_SimConfig
# Список кортежів (field_name, value) — зберігає порядок полів
SIM_CONFIG_DEFAULTS: dict[str, list[tuple[str, str]]] = {
    "redler": [
        ("Enable",                  "TRUE"),
        ("StartupTime_ms",          "3000"),
        ("StopTime_ms",             "2000"),
        ("SimFault_Breaker",        "FALSE"),
        ("FaultTime_Breaker_ms",    "10000"),
        ("SimFault_Overflow",       "FALSE"),
        ("FaultTime_Overflow_ms",   "15000"),
        ("ManualReset",             "FALSE"),
    ],
    "noria": [
        ("Enable",                    "TRUE"),
        ("StartupTime_ms",            "4000"),
        ("StopTime_ms",               "3000"),
        ("SimFault_Breaker",          "FALSE"),
        ("FaultTime_Breaker_ms",      "10000"),
        ("SimFault_Alignment",        "FALSE"),
        ("FaultTime_Alignment_ms",    "20000"),
        ("SimFault_Overflow",         "FALSE"),
        ("FaultTime_Overflow_ms",     "15000"),
        ("ManualReset",               "FALSE"),
    ],
    "fan": [
        ("Enable",               "TRUE"),
        ("StartupTime_ms",       "3000"),
        ("StopTime_ms",          "2000"),
        ("SimFault_Breaker",     "FALSE"),
        ("FaultTime_Breaker_ms", "10000"),
        ("ManualReset",          "FALSE"),
    ],
    "gate2p": [
        ("Enable",               "FALSE"),   # вимкнено за замовчуванням
        ("InitAtPos0",           "TRUE"),
        ("TravelTime_ms",        "5000"),
        ("SimFault_Breaker",     "FALSE"),
        ("FaultTime_Breaker_ms", "10000"),
        ("ManualReset",          "FALSE"),
    ],
}
