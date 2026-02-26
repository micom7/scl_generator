"""FastAPI-сервіс: JSON → SCL кодогенератор."""
from __future__ import annotations

import base64
import io
import json
import os
import zipfile
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse

from generator.generators.db_mechs import generate_db_mechs
from generator.generators.db_sim_config import generate_db_sim_config
from generator.generators.db_sim_mechs import generate_db_sim_mechs
from generator.generators.mechs_csv import generate_mechs_csv
from generator.mapper import map_devices
from generator.parser import parse_graph

_BOM = b"\xef\xbb\xbf"

app = FastAPI(title="JSON → SCL Codegen")

_UI_PATH = Path(__file__).parent / "ui.html"

_CONST_ORDER = ["MECHS_COUNT", "REDLERS_COUNT", "NORIAS_COUNT", "GATES2P_COUNT", "FANS_COUNT"]


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return _UI_PATH.read_text(encoding="utf-8")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/generate")
async def generate(
    file: UploadFile,
    project_name: str = Form(default=None),
    version: str = Form(default="1.0.0"),
) -> JSONResponse:
    if project_name is None or project_name.strip() == "":
        project_name = os.environ.get("DEFAULT_PROJECT_NAME", "Elevator_System")

    # --- Розмір файлу ---
    max_mb = int(os.environ.get("MAX_UPLOAD_SIZE_MB", "10"))
    content = await file.read()
    if len(content) > max_mb * 1024 * 1024:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "errors": [f"Файл перевищує максимальний розмір {max_mb} MB."]},
        )

    # --- Парсинг JSON ---
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JSONResponse(
            status_code=400,
            content={"ok": False, "errors": ["Невалідний JSON у завантаженому файлі."]},
        )

    if not isinstance(data, dict):
        return JSONResponse(
            status_code=400,
            content={"ok": False, "errors": ["JSON повинен бути об'єктом {}."]},
        )

    # --- Обов'язкові поля ---
    missing = []
    if "devices" not in data:
        missing.append("Відсутнє поле 'devices'.")
    if "deviceTypes" not in data:
        missing.append("Відсутнє поле 'deviceTypes'.")
    if missing:
        return JSONResponse(status_code=400, content={"ok": False, "errors": missing})

    # --- Валідація пристроїв ---
    parse_result = parse_graph(data)
    if parse_result.errors:
        return JSONResponse(
            status_code=422,
            content={
                "ok": False,
                "errors": parse_result.errors,
                "warnings": parse_result.warnings,
            },
        )

    # --- Маппінг ---
    map_result = map_devices(parse_result.devices)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source_name = file.filename or "graph.json"
    ctx = {
        "project_name": project_name,
        "version": version,
        "timestamp": timestamp,
        "source": source_name,
    }

    # --- Генерація SCL + CSV ---
    try:
        db_mechs = generate_db_mechs(map_result, ctx)
        db_sim_config = generate_db_sim_config(map_result, ctx)
        db_sim_mechs = generate_db_sim_mechs(map_result, ctx)
        mechs_csv = generate_mechs_csv(map_result, ctx)
    except Exception as exc:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "errors": [f"Внутрішня помилка: {type(exc).__name__}"]},
        )

    report_text = _build_report_text(ctx, map_result, parse_result.warnings)

    # --- ZIP в пам'яті (SCL-файли з UTF-8 BOM для TIA Portal) ---
    zip_buf = io.BytesIO()
    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("DB_Mechs.scl",        _BOM + db_mechs.encode("utf-8"))
        zf.writestr("DB_SimConfig.scl",    _BOM + db_sim_config.encode("utf-8"))
        zf.writestr("DB_SimMechs.scl",     _BOM + db_sim_mechs.encode("utf-8"))
        zf.writestr("Mechs.csv",           _BOM + mechs_csv.encode("utf-8"))
        zf.writestr("generation_report.txt", report_text.encode("utf-8"))
    zip_buf.seek(0)
    zip_b64 = base64.b64encode(zip_buf.read()).decode("ascii")

    ts_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"scl_{project_name}_{ts_file}.zip"

    return JSONResponse(
        status_code=200,
        content={
            "ok": True,
            "zip_base64": zip_b64,
            "zip_filename": zip_filename,
            "devices": _build_device_rows(map_result, parse_result.warnings),
            "constants": {k: map_result.counts.get(k, -1) for k in _CONST_ORDER},
            "warnings": parse_result.warnings,
            "gap_slots": map_result.gap_slots,
        },
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _build_device_rows(map_result, non_mech_warnings: list) -> list:
    rows = []
    for dev in sorted(map_result.devices, key=lambda d: d.id):
        status = "skip" if not dev.has_simulator else "ok"
        rows.append({
            "status":       status,
            "id":           dev.id,
            "display_name": dev.name,
            "type_name":    dev.raw_type,
            "tia_type":     dev.tia_type,
            "slot_id":      dev.id,
            "typed_index":  dev.typed_index,
            "has_simulator": dev.has_simulator,
        })
    for w in non_mech_warnings:
        rows.append({"status": "warn", "message": w})
    return rows


def _build_report_text(ctx: dict, map_result, warnings: list) -> str:
    lines = [
        f"Generated: {ctx['timestamp']}",
        f"Source: {ctx['source']}",
        f"Project: {ctx['project_name']} v{ctx['version']}",
        "",
        "Devices:",
    ]

    for dev in sorted(map_result.devices, key=lambda d: d.id):
        if dev.has_simulator:
            status = "[OK]  "
            suffix = ""
        else:
            status = "[SKIP]"
            suffix = " (no simulator)"
        lines.append(
            f"  {status} id={dev.id:<3} {dev.raw_type:<6} \"{dev.name}\""
            f"  -> {dev.tia_type}, SlotId={dev.id}, TypedIndex={dev.typed_index}{suffix}"
        )

    for w in warnings:
        lines.append(f"  [WARN] {w}")

    lines += ["", "Constants:"]
    for key in _CONST_ORDER:
        val = map_result.counts.get(key, -1)
        lines.append(f"  {key:<18} = {val}")

    if map_result.gap_slots:
        lines += ["", "Warnings:"]
        slots_str = ", ".join(str(s) for s in map_result.gap_slots)
        lines.append(f"  [WARN] Порожні слоти у Mechs[]: {slots_str}")

    lines += ["", "Files:", "  DB_Mechs.scl     OK", "  DB_SimConfig.scl OK", "  DB_SimMechs.scl  OK", "  Mechs.csv        OK", ""]
    return "\n".join(lines)
