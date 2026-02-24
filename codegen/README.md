# Кодогенератор JSON → SCL

Веб-сервіс для генерації SCL-файлів TIA Portal 19 з файлу опису схеми елеватора `graph.json`.

---

## Зміст

- [Запуск без Docker](#запуск-без-docker)
- [Запуск через Docker](#запуск-через-docker)
- [Запуск через docker-compose](#запуск-через-docker-compose)
- [Використання веб-інтерфейсу](#використання-веб-інтерфейсу)
- [HTTP API](#http-api)
- [Формат graph.json](#формат-graphjson)
- [Типи пристроїв](#типи-пристроїв)
- [Опис SCL-файлів](#опис-scl-файлів)
- [Тестування](#тестування)
- [Змінні середовища](#змінні-середовища)

---

## Запуск без Docker

**Вимоги:** Python 3.12+

```bash
cd codegen
pip install -r requirements.txt
uvicorn main:app --reload --port 8080
```

Сервіс доступний на **http://localhost:8080**

`--reload` — автоматичний перезапуск при зміні файлів (зручно для розробки).

---

## Запуск через Docker

```bash
cd codegen

# Зібрати образ
docker build -t codegen .

# Запустити
docker run -p 8080:8080 codegen
```

З передачею змінних середовища:

```bash
docker run -p 8080:8080 \
  -e DEFAULT_PROJECT_NAME=MyProject \
  -e LOG_LEVEL=debug \
  codegen
```

---

## Запуск через docker-compose

Якщо граф-редактор (`frontend`) розгорнутий у тому ж `docker-compose.yml`:

```yaml
# docker-compose.yml (корінь проекту)
services:
  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    restart: unless-stopped

  codegen:
    build: ./codegen
    ports:
      - "8080:8080"
    restart: unless-stopped
    environment:
      - LOG_LEVEL=info
    healthcheck:
      test: ["CMD", "python", "-c",
             "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
```

```bash
# Запустити обидва сервіси
docker compose up -d --build

# Лише кодогенератор
docker compose up -d --build codegen
```

---

## Використання веб-інтерфейсу

Відкрийте **http://localhost:8080** у браузері.

```
┌─────────────────────────────────────────────────────┐
│  ⚙️  Кодогенератор  JSON → SCL  TIA Portal 19        │
├─────────────────────────────────────────────────────┤
│  Файл graph.json                                    │
│  ┌──────────────────────────────────┐               │
│  │  📂 Перетягни або натисни        │               │
│  │     graph.json сюди              │               │
│  └──────────────────────────────────┘               │
│     ✅ graph.json завантажено (4.2 KB)               │
│                                                     │
│  Назва проекту  [Elevator_System  ]                 │
│  Версія         [1.0.0            ]                 │
│                                                     │
│  [⚙️  Згенерувати SCL]                               │
├─────────────────────────────────────────────────────┤
│  Результат                                          │
│  ✅ noria   id=1  →  TYPE_NORIA,  Slot=1, TIdx=0    │
│  ✅ noria   id=2  →  TYPE_NORIA,  Slot=2, TIdx=1    │
│  ✅ redler  id=3  →  TYPE_REDLER, Slot=3, TIdx=0    │
│  ⏭  gate2P  id=4  →  TYPE_GATE2P, Slot=4 (no sim)  │
│  ✅ Fan     id=5  →  TYPE_FAN,    Slot=5, TIdx=0    │
│                                                     │
│  MECHS_COUNT=5  NORIAS_COUNT=1  REDLERS_COUNT=0 … │
│                                                     │
│  [⬇️  Скачати SCL-файли (ZIP)]                       │
└─────────────────────────────────────────────────────┘
```

**Кроки:**
1. Перетягніть або виберіть `graph.json`
2. За бажанням змініть назву проекту та версію
3. Натисніть **Згенерувати SCL**
4. Перегляньте звіт з розподілом пристроїв по слотах
5. Натисніть **Скачати SCL-файли (ZIP)** — отримаєте архів із трьома SCL-файлами та звітом

**Іконки у звіті:**
| Іконка | Значення |
|---|---|
| ✅ | Механізм із симулятором — OK |
| ⏭ | Механізм без симулятора (Gate2P) |
| ⚠️ | Не-механізм: пропущено (наприклад, Silo) |
| ❌ | Помилка валідації |

---

## HTTP API

### `GET /`
Повертає HTML-сторінку інтерфейсу.

---

### `GET /health`
Healthcheck для Docker.

**Відповідь:**
```json
{"status": "ok"}
```

---

### `POST /generate`

Генерує SCL-файли з `graph.json`.

**Тип запиту:** `multipart/form-data`

| Поле | Тип | Обов'язковий | За замовч. |
|---|---|---|---|
| `file` | `.json` файл | ✅ | — |
| `project_name` | string | ні | `Elevator_System` |
| `version` | string | ні | `1.0.0` |

**Успішна відповідь (HTTP 200):**
```json
{
  "ok": true,
  "zip_base64": "<base64 ZIP-архіву>",
  "zip_filename": "scl_Elevator_System_20260220_154311.zip",
  "devices": [
    {
      "status": "ok",
      "id": 1,
      "display_name": "Noria",
      "type_name": "noria",
      "tia_type": "TYPE_NORIA",
      "slot_id": 1,
      "typed_index": 0,
      "has_simulator": true
    },
    {
      "status": "skip",
      "id": 4,
      "display_name": "Gate2P",
      "type_name": "gate2P",
      "tia_type": "TYPE_GATE2P",
      "slot_id": 4,
      "typed_index": 0,
      "has_simulator": false
    },
    {
      "status": "warn",
      "message": "Пристрій \"Силос 1\" (id=6): тип \"Silo\" є не-механізмом → пропущено."
    }
  ],
  "constants": {
    "MECHS_COUNT": 5,
    "REDLERS_COUNT": 0,
    "NORIAS_COUNT": 1,
    "GATES2P_COUNT": 0,
    "FANS_COUNT": 0
  },
  "warnings": ["Пристрій \"Силос 1\" (id=6): тип \"Silo\" є не-механізмом → пропущено."],
  "gap_slots": [0]
}
```

**Помилка валідації (HTTP 422):**
```json
{
  "ok": false,
  "errors": [
    "Пристрій \"Redler\" (id=1): дублікат id — вже зайнятий пристроєм \"Noria\"."
  ],
  "warnings": []
}
```

**Помилка формату (HTTP 400):**
```json
{
  "ok": false,
  "errors": ["Невалідний JSON у завантаженому файлі."]
}
```

**Приклад через curl:**
```bash
# Успішна генерація — зберегти ZIP
curl -s -X POST http://localhost:8080/generate \
  -F "file=@graph.json" \
  -F "project_name=MyProject" \
  | python -c "
import sys, json, base64
d = json.load(sys.stdin)
if d['ok']:
    open(d['zip_filename'], 'wb').write(base64.b64decode(d['zip_base64']))
    print('Saved:', d['zip_filename'])
else:
    print('Errors:', d['errors'])
"

# Health check
curl http://localhost:8080/health
```

---

## Формат graph.json

```json
{
  "deviceTypes": [
    { "name": "noria",  "label": "Noria" },
    { "name": "redler", "label": "Redler" },
    { "name": "gate2P", "label": "Gate2P" },
    { "name": "Fan",    "label": "Fan" },
    { "name": "Silo",   "label": "Silo" }
  ],
  "devices": [
    { "name": "Noria",   "id": "1", "type": "noria"  },
    { "name": "Noria 2", "id": "2", "type": "noria"  },
    { "name": "Redler",  "id": "3", "type": "redler" },
    { "name": "Gate2P",  "id": "4", "type": "gate2P" },
    { "name": "Fan",     "id": "5", "type": "Fan"    }
  ],
  "connections": []
}
```

**Правила для поля `id`:**
- Невід'ємне ціле число (або рядок з числом: `"1"` або `1`)
- Унікальне серед усіх пристроїв у файлі
- Визначає індекс у масиві `Mechs[]` у TIA Portal

Поля `pos_x`, `pos_y`, `ports`, `internal_connections`, `connections` генератором **ігноруються**.

---

## Типи пристроїв

Маппінг виконується **без урахування регістру** (`noria` = `Noria` = `NORIA`):

| JSON `type` | TIA Portal тип | Симулятор |
|---|---|---|
| `noria` | `TYPE_NORIA` | ✅ UDT_SimNoriaState / UDT_SimNoriaConfig |
| `redler` | `TYPE_REDLER` | ✅ UDT_SimRedlerState / UDT_SimRedlerConfig |
| `gate2p` | `TYPE_GATE2P` | ❌ (FC_SimGate2P не реалізовано) |
| `fan` | `TYPE_FAN` | ✅ UDT_SimFanState / UDT_SimFanConfig |
| `silo`, `sensor`, `label` | — | ⚠️ Не-механізм, пропускається |

Якщо тип не в таблиці і не є не-механізмом → **помилка** (HTTP 422).

---

## Опис SCL-файлів

### DB_Mechs.scl
Масиви механізмів. Для кожного пристрою ініціалізується слот у базовому масиві `Mechs[]` та типізованому масиві (`Noria[]`, `Redler[]` тощо).

```scl
DATA_BLOCK "DB_Mechs"
{ S7_Optimized_Access := 'TRUE' }
VERSION : 1.0

VAR
    Mechs  : ARRAY [0.."MECHS_COUNT"]   OF "UDT_BaseMechanism";
    Redler : ARRAY [0.."REDLERS_COUNT"] OF "UDT_Redler";
    Noria  : ARRAY [0.."NORIAS_COUNT"]  OF "UDT_Noria";
    ...
END_VAR

BEGIN
    // Noria "Noria" (id=1)
    Mechs[1].SlotId     := 1;
    Mechs[1].DeviceType := "TYPE_NORIA";
    Mechs[1].TypedIndex := 0;
    Mechs[1].Enable_OK  := TRUE;
    ...
END_DATA_BLOCK
```

### DB_SimConfig.scl
Конфігурація симуляторів (часи запуску/зупинки, параметри симуляції збоїв). Gate2P виключено. Дані RETAIN — зберігаються між циклами CPU.

### DB_SimMechs.scl
Runtime-стани симуляторів. Секція `BEGIN` порожня — структури NON_RETAIN, ініціалізуються в нуль при старті CPU.

### generation_report.txt
Текстовий звіт у ZIP-архіві:
```
Generated: 2026-02-20 15:43:11
Source: graph.json
Project: Elevator_System v1.0.0

Devices:
  [OK]   id=1  noria  "Noria"    -> TYPE_NORIA,  SlotId=1, TypedIndex=0
  [OK]   id=2  noria  "Noria 2"  -> TYPE_NORIA,  SlotId=2, TypedIndex=1
  [OK]   id=3  redler "Redler"   -> TYPE_REDLER, SlotId=3, TypedIndex=0
  [SKIP] id=4  gate2P "Gate2P"   -> TYPE_GATE2P, SlotId=4, TypedIndex=0 (no simulator)
  [OK]   id=5  Fan    "Fan"      -> TYPE_FAN,    SlotId=5, TypedIndex=0

Constants:
  MECHS_COUNT        = 5
  REDLERS_COUNT      = 0
  NORIAS_COUNT       = 1
  GATES2P_COUNT      = 0
  FANS_COUNT         = 0

Warnings:
  [WARN] Порожні слоти у Mechs[]: 0

Files:
  DB_Mechs.scl     OK
  DB_SimConfig.scl OK
  DB_SimMechs.scl  OK
```

---

## Тестування

### Unit-тести (pytest)

```bash
cd codegen
py -3.12 -m pytest tests/ -v
```

23 тести покривають:
- Валідацію `id` (null, від'ємний, нечисловий, дублікат)
- Валідацію `type` (null, невідомий, не-механізм)
- Маппінг TypedIndex (сортування за id, різні типи)
- Підрахунок констант MECHS_COUNT / *_COUNT
- Визначення прогалин у слотах
- Тест-кейси T1–T10 з ТЗ

### Ручне тестування

```bash
# Запустити сервер
cd codegen
py -3.12 -m uvicorn main:app --reload --port 8080

# У другому терміналі
# 1. Успішна генерація
curl -s http://localhost:8080/generate \
  -X POST -F "file=@../graph.json" | python -m json.tool

# 2. Health
curl http://localhost:8080/health

# 3. Невалідний JSON
echo "not json" > /tmp/bad.json
curl -s -X POST http://localhost:8080/generate \
  -F "file=@/tmp/bad.json" | python -m json.tool
```

---

## Змінні середовища

| Змінна | За замовч. | Опис |
|---|---|---|
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8080` | HTTP порт |
| `LOG_LEVEL` | `info` | Рівень логування uvicorn |
| `MAX_UPLOAD_SIZE_MB` | `10` | Максимальний розмір graph.json |
| `DEFAULT_PROJECT_NAME` | `Elevator_System` | Назва проекту за замовч. |

---

## Структура проекту

```
codegen/
├── Dockerfile
├── requirements.txt
├── README.md
├── main.py                    # FastAPI: маршрути + обробка запитів
├── ui.html                    # Веб-інтерфейс (Vanilla JS, темна тема)
├── generator/
│   ├── defaults.py            # TYPE_MAPPING, NON_MECHANISM_TYPES, SIM_CONFIG_DEFAULTS
│   ├── parser.py              # Парсинг та валідація graph.json
│   ├── mapper.py              # SlotId / TypedIndex / константи
│   └── generators/
│       ├── db_mechs.py        # Генератор DB_Mechs.scl
│       ├── db_sim_config.py   # Генератор DB_SimConfig.scl
│       └── db_sim_mechs.py    # Генератор DB_SimMechs.scl
└── tests/
    ├── test_parser.py         # T1–T10 + додаткові кейси
    ├── test_mapper.py
    └── fixtures/
        ├── graph_full.json    # Всі типи (noria×2, redler, gate2p, fan, silo)
        ├── graph_empty.json   # Порожній devices
        └── graph_invalid.json # Невалідний JSON
```
