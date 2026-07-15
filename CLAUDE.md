# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**PT AgriPulse Digital Nusantara** — Smart Greenhouse Management System (Agri-Tech Startup, Kelompok 2).

Tagline: *"Revolutionizing Agriculture with Precision Data"*

This is a **single-file Flask web application** (`KONTOL.py`) that simulates and (eventually) will manage real IoT greenhouse systems. It combines a company profile/e-commerce site with a real-time IoT dashboard.

---

## How to Run

```bash
pip install flask werkzeug
python KONTOL.py
# Open: http://localhost:5000
```

Default admin credentials (once auth is implemented): `admin` / `admin123`

---

## Architecture

### Single-File Pattern
Everything lives in `KONTOL.py` — constants, HTML templates (inline strings), Flask routes, helper functions, and business logic. There are **no separate template files, no static folder, no blueprints**. All HTML is rendered via `render_template_string()`.

The pattern used is:
1. **Constants** (top of file) — `KOMODITAS`, `BOM`, `TIM`, `CASHFLOW`, `PRODUK` dicts
2. **Helper functions** — `hitung_vpd()`, `analisis_otomatis()`, `baca_sensor_sim()`, etc.
3. **HTML page strings** — each page is a `make_page("""...""")` call stored in a `*_HTML` variable
4. **Flask routes** — at the bottom, each route renders its corresponding `*_HTML` variable

### `make_page()` / `BASE_HTML`
`BASE_HTML` is the shared layout string containing the full `<html>`, CSS, `<nav>`, and `<footer>`. It has a `%%CONTENT%%` placeholder. `make_page(content)` replaces that placeholder. All page HTML variables are built using this pattern at module load time.

### Sensor Simulation
`baca_sensor_sim()` generates random sensor values within realistic tropical ranges (Sumatera Utara climate). `analisis_otomatis(sensor, threshold)` compares readings against per-crop Gold Standard thresholds and returns `(aksi_list, alert_list)` driving the closed-loop control display.

### Domain Data
- **`KOMODITAS`** — 4 crops (selada/tomat/melon/paprika) with agronomic threshold ranges for suhu, kelembaban, CO₂, EC, pH
- **`PRODUK`** — 3 products: Smart-Kit (hardware), SaaS Dashboard, Hydro-Consult service
- **`CASHFLOW`** — Year 1 monthly projections (12 rows), cumulative sum pre-computed at module load
- **`BOM`** — Bill of Materials for 1 Smart-Kit unit

### Cart & Checkout
Session-based cart (`session["cart"]`). Checkout produces an in-memory invoice (no DB yet). `cart_count()` is passed to every render call for the navbar badge.

---

## Planned Additions (in progress — do NOT start fresh, extend existing file)

The goal is to **extend `KONTOL.py`** (not split into multiple files) with:

| Feature | Details |
|---|---|
| **SQLite DB** | `agripulse.db` — tables: `users`, `greenhouses`, `sensor_readings`, `alerts`, `orders` |
| **Auth** | Login/Register/Logout via `werkzeug.security`, session-based, `@login_required` / `@admin_required` decorators |
| **Multi-greenhouse** | Each user owns multiple greenhouses, each with its own komoditas, API key, CRUD |
| **Background simulator** | `threading.Thread(daemon=True)` — inserts sensor readings to DB every 30 seconds for all active greenhouses, saves alerts to DB |
| **Alert log** | `/alerts` page — view unresolved alerts from DB, resolve button, badge count in navbar |
| **CSV export** | `/export/csv/<gh_id>` — download sensor history as CSV |
| **Admin panel** | `/admin` — view all users, orders, greenhouse count, analytics; `@admin_required` |
| **API key auth** | Each greenhouse has a unique `api_key` for ESP32 POST authentication |

### DB Schema (target)
```sql
users          (id, username, email, password_hash, role, created_at)
greenhouses    (id, user_id, nama, komoditas, lokasi, luas, api_key, aktif, created_at)
sensor_readings(id, greenhouse_id, suhu, kelembaban, co2, ec, ph, vpd, timestamp)
alerts         (id, greenhouse_id, gh_nama, pesan, level, resolved, created_at)
orders         (id, user_id, nomor_invoice, nama, email, hp, perusahaan, alamat, items_json, total, pembayaran, status, created_at)
```

---

## Key Routes (current)

| Route | Function |
|---|---|
| `GET /` | Dashboard — sensor cards, VPD, chart, automated actions |
| `GET /tentang` | Company profile, vision/mission, core values |
| `GET /teknologi` | System architecture, BOM table, Gold Standard thresholds |
| `GET /tim` | Team cards, org structure, labor impact table |
| `GET /produk` | Product catalog with add-to-cart forms |
| `GET /finansial` | CAPEX, OPEX, HPP, cash flow table, depreciation |
| `GET /cart` | Shopping cart |
| `POST /checkout` | Creates invoice, clears cart |
| `GET /api/sensor` | JSON: simulated sensor + analysis (ESP32 compatible) |
| `POST /api/sensor/post` | Accepts real ESP32 JSON payload |
| `GET /api/history` | Last 20 sensor readings |

---

## ESP32 Integration (API)

**POST** `/api/sensor/post`
```json
{"suhu": 28.5, "kelembaban": 72, "co2": 650, "ec": 1.8, "ph": 6.1, "komoditas": "selada"}
```
Returns automated action commands and VPD. Once greenhouse API keys are implemented, include `api_key` in the payload.

---

## Business Context

- **Hardware**: AgriPulse Smart-Kit — ESP32 + SHT31 + MH-Z19C + EC/pH meter + 4-ch relay, priced at Rp 6.8M/unit, BOM Rp 3.5M
- **SaaS**: Dashboard subscription Rp 2M/year (free year 1 with kit purchase)
- **Consulting**: Hydro-Consult Rp 2.5M/visit
- Target market: horticultural greenhouses in Berastagi & Karo, Sumatera Utara
- Year 1 targets: 210 Smart-Kit units, cash flow positive from month 8, payback ±27 months
