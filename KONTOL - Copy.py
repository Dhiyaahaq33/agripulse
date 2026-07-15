"""
╔══════════════════════════════════════════════════════════════════╗
║         PT AgriPulse Digital Nusantara — Simulasi Sistem         ║
║         "Revolutionizing Agriculture with Precision Data"        ║
╚══════════════════════════════════════════════════════════════════╝

Cara Jalankan:
  1. pip install flask
  2. python KONTOL.py
  3. Buka browser: http://localhost:5000

Halaman:
  /           → Dashboard monitoring real-time (auto-refresh 30s, chart, VPD)
  /tentang    → Tentang Kami, Visi & Misi, Core Values
  /teknologi  → Arsitektur Sistem, BOM Komponen, Spesifikasi Teknis
  /tim        → Struktur Bisnis & Meet Our Team
  /produk     → Katalog Produk & Pemesanan
  /finansial  → Proyeksi Keuangan, Cash Flow, HPP, CAPEX/OPEX
  /cart       → Keranjang Belanja & Checkout
  /api/sensor → API JSON (siap integrasi ESP32/MQTT)
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
import random, math, json
from datetime import datetime
from collections import deque

app = Flask(__name__)
app.secret_key = "agripulse-2025-k2"

# ─── RIWAYAT SENSOR (max 20 data terakhir, simulasi buffer lokal) ─
sensor_history = deque(maxlen=20)

# ─── THRESHOLD PER KOMODITAS (Gold Standard Agronomi) ─────────────
KOMODITAS = {
    "selada": {
        "nama": "Selada (Butterhead & Romaine)", "emoji": "🥬", "sistem": "NFT",
        "suhu":       {"min": 18, "max": 25,   "unit": "°C"},
        "kelembaban": {"min": 60, "max": 80,   "unit": "%"},
        "co2":        {"min": 400, "max": 800,  "unit": "ppm"},
        "ec":         {"min": 1.2, "max": 2.0, "unit": "mS/cm"},
        "ph":         {"min": 5.5, "max": 6.5, "unit": ""},
    },
    "tomat": {
        "nama": "Tomat (Beef & Cherry)", "emoji": "🍅", "sistem": "Drip System",
        "suhu":       {"min": 20, "max": 28,   "unit": "°C"},
        "kelembaban": {"min": 65, "max": 80,   "unit": "%"},
        "co2":        {"min": 600, "max": 1000, "unit": "ppm"},
        "ec":         {"min": 2.0, "max": 3.5, "unit": "mS/cm"},
        "ph":         {"min": 5.8, "max": 6.8, "unit": ""},
    },
    "melon": {
        "nama": "Melon Premium", "emoji": "🍈", "sistem": "Drip System",
        "suhu":       {"min": 25, "max": 32,   "unit": "°C"},
        "kelembaban": {"min": 60, "max": 75,   "unit": "%"},
        "co2":        {"min": 600, "max": 1000, "unit": "ppm"},
        "ec":         {"min": 2.0, "max": 3.5, "unit": "mS/cm"},
        "ph":         {"min": 6.0, "max": 6.8, "unit": ""},
    },
    "paprika": {
        "nama": "Paprika", "emoji": "🫑", "sistem": "Drip System",
        "suhu":       {"min": 20, "max": 28,   "unit": "°C"},
        "kelembaban": {"min": 65, "max": 75,   "unit": "%"},
        "co2":        {"min": 600, "max": 1000, "unit": "ppm"},
        "ec":         {"min": 2.5, "max": 4.0, "unit": "mS/cm"},
        "ph":         {"min": 5.8, "max": 6.5, "unit": ""},
    },
}

# ─── BOM KOMPONEN SMART-KIT (sumber: PDF slide 12) ────────────────
BOM = [
    {"komponen": "Microcontroller",  "spesifikasi": "ESP32 DevKit V1 + Expansion Board",           "harga": 150_000},
    {"komponen": "Sensor Iklim",     "spesifikasi": "Sensirion SHT31 Industrial Grade",             "harga": 250_000},
    {"komponen": "Sensor Nutrisi",   "spesifikasi": "Industrial EC & pH Meter Kit (BNC Interface)", "harga": 1_200_000},
    {"komponen": "Sensor Gas",       "spesifikasi": "MH-Z19C NDIR CO₂ Sensor (self-calibrating)",  "harga": 450_000},
    {"komponen": "Aktuator",         "spesifikasi": "4-Channel Relay Module + Solenoid Valve 12V",  "harga": 400_000},
    {"komponen": "Power System",     "spesifikasi": "Adaptor 12V 10A + Step-down Buck Converter",   "harga": 350_000},
    {"komponen": "Housing",          "spesifikasi": "Panel Box ABS IP65 (Tahan Air & Panas)",       "harga": 250_000},
    {"komponen": "Kabel & Konektor", "spesifikasi": "Kabel AWG22 + Gland Cable + Terminal Block",   "harga": 450_000},
]

# ─── TIM (sumber: PDF slide 10) ───────────────────────────────────
TIM = [
    {"nama": "Zacky Mubarok",       "jabatan": "CEO", "desc": "Strategi & representasi perusahaan",   "emoji": "👨‍💼"},
    {"nama": "Rizzi Amalia",        "jabatan": "COO", "desc": "Operasional, produksi & logistik",     "emoji": "👩‍💼"},
    {"nama": "Rinjanie Ardelya L.", "jabatan": "CPO", "desc": "Product development & roadmap",        "emoji": "👩‍🔬"},
    {"nama": "M. Yahya D. H.",      "jabatan": "CTO", "desc": "Firmware, IoT & inovasi teknologi",    "emoji": "👨‍💻"},
    {"nama": "Amr. Ibrahimovich A.","jabatan": "CBO", "desc": "Business development & kemitraan B2B", "emoji": "🤝"},
]

# ─── CASH FLOW PROYEKSI TAHUN 1 (sumber: PDF slide 21) ───────────
CASHFLOW = [
    {"bulan":1,  "unit":0,  "kit":0,           "saas":0,          "consult":0,          "total_in":0,           "opex":129_260_000},
    {"bulan":2,  "unit":0,  "kit":0,           "saas":0,          "consult":0,          "total_in":0,           "opex":129_260_000},
    {"bulan":3,  "unit":5,  "kit":34_000_000,  "saas":0,          "consult":5_000_000,  "total_in":39_000_000,  "opex":129_260_000},
    {"bulan":4,  "unit":5,  "kit":34_000_000,  "saas":4_000_000,  "consult":5_000_000,  "total_in":43_000_000,  "opex":129_260_000},
    {"bulan":5,  "unit":15, "kit":102_000_000, "saas":8_000_000,  "consult":7_500_000,  "total_in":117_500_000, "opex":129_260_000},
    {"bulan":6,  "unit":15, "kit":102_000_000, "saas":12_000_000, "consult":7_500_000,  "total_in":121_500_000, "opex":129_260_000},
    {"bulan":7,  "unit":15, "kit":102_000_000, "saas":16_000_000, "consult":7_500_000,  "total_in":125_500_000, "opex":129_260_000},
    {"bulan":8,  "unit":15, "kit":102_000_000, "saas":20_000_000, "consult":7_500_000,  "total_in":129_500_000, "opex":129_260_000},
    {"bulan":9,  "unit":25, "kit":170_000_000, "saas":26_000_000, "consult":10_000_000, "total_in":206_000_000, "opex":150_260_000},
    {"bulan":10, "unit":25, "kit":170_000_000, "saas":32_000_000, "consult":10_000_000, "total_in":212_000_000, "opex":150_260_000},
    {"bulan":11, "unit":25, "kit":170_000_000, "saas":38_000_000, "consult":10_000_000, "total_in":218_000_000, "opex":150_260_000},
    {"bulan":12, "unit":25, "kit":170_000_000, "saas":44_000_000, "consult":10_000_000, "total_in":224_000_000, "opex":150_260_000},
]
_kum = 0
for _cf in CASHFLOW:
    _cf["net"] = _cf["total_in"] - _cf["opex"]
    _kum += _cf["net"]
    _cf["kumulatif"] = _kum

# ─── PRODUK & HARGA (sumber: PDF slide 7 & 19) ────────────────────
PRODUK = {
    "smartkit": {
        "id": "smartkit", "emoji": "📦", "badge": "Best Seller",
        "nama": "AgriPulse Smart-Kit",
        "harga": 6_800_000, "hpp": 4_963_000, "satuan": "/unit",
        "deskripsi": "Paket IoT plug-and-play untuk greenhouse kecil menengah. Tidak perlu keahlian teknis khusus.",
        "isi": [
            "ESP32 DevKit V1 + Expansion Board",
            "Sensor SHT31 Industrial Grade (Suhu & RH)",
            "Sensor CO₂ MH-Z19C NDIR (self-calibrating)",
            "Industrial EC & pH Meter (BNC Interface)",
            "Relay 4-Channel + Solenoid Valve 12V",
            "Power Supply 12V 10A + Buck Converter",
            "Panel Box ABS IP65 (Tahan Air & Panas)",
            "Kabel AWG22 + Gland Cable Lengkap",
            "✅ Akses Dashboard Cloud 1 Tahun GRATIS",
        ],
    },
    "saas": {
        "id": "saas", "emoji": "☁️", "badge": "Gratis Tahun 1*",
        "nama": "Enterprise Dashboard (SaaS)",
        "harga": 2_000_000, "hpp": 200_000, "satuan": "/tahun",
        "deskripsi": "Platform cloud monitoring real-time. GRATIS tahun pertama untuk pembeli Smart-Kit!",
        "isi": [
            "Monitoring real-time 24/7",
            "Data historis & grafik tren",
            "Notifikasi otomatis (WhatsApp/Email)",
            "Laporan analitik bulanan (PDF)",
            "Multi-greenhouse dalam 1 akun",
            "VPD Calculator & Gold Standard tanaman",
            "Export data CSV/Excel",
        ],
    },
    "hydroconsult": {
        "id": "hydroconsult", "emoji": "🔧", "badge": "Premium",
        "nama": "Hydro-Consult",
        "harga": 2_500_000, "hpp": 500_000, "satuan": "/kunjungan",
        "deskripsi": "Jasa desain, instalasi, kalibrasi & pelatihan sistem hidroponik terintegrasi on-site.",
        "isi": [
            "Survei & desain layout greenhouse",
            "Instalasi sistem IoT on-site",
            "Kalibrasi sensor & aktuator",
            "Pemilihan sistem budidaya (NFT / DFT / Drip)",
            "Pelatihan operator (4 jam)",
            "Support teknis 30 hari",
            "Dokumentasi SOP operasional",
        ],
    },
}

# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def hitung_vpd(suhu, rh):
    """Vapor Pressure Deficit (kPa) — Gold Standard mikroklimat tanaman."""
    svp = 0.6108 * math.exp(17.27 * suhu / (suhu + 237.3))
    vpd = svp * (1 - rh / 100)
    return round(vpd, 2)

def vpd_status(vpd):
    if vpd < 0.4:   return "Terlalu Lembab", "waspada"
    if vpd <= 0.8:  return "Optimal — Vegetatif", "optimal"
    if vpd <= 1.2:  return "Optimal — Generatif", "optimal"
    if vpd <= 1.6:  return "Tinggi — Waspada", "waspada"
    return "Sangat Tinggi — Kritis", "kritis"

def get_threshold(komoditas_key):
    k = KOMODITAS.get(komoditas_key, KOMODITAS["selada"])
    return {kk: vv for kk, vv in k.items() if kk not in ("nama", "emoji", "sistem")}

def baca_sensor():
    """Simulasi pembacaan sensor tiap 30 detik (rentang realistis iklim tropis Sumatera Utara)."""
    s = {
        "suhu":       round(random.uniform(19, 35), 1),
        "kelembaban": round(random.uniform(52, 93), 1),
        "co2":        int(round(random.uniform(320, 1150))),
        "ec":         round(random.uniform(0.9, 4.1), 2),
        "ph":         round(random.uniform(4.8, 7.4), 2),
        "timestamp":  datetime.now().strftime("%H:%M:%S"),
    }
    sensor_history.append(s)
    return s

def analisis_otomatis(sensor, threshold):
    """Closed-loop control — respons otomatis aktuator berdasarkan threshold komoditas."""
    aksi, alert = [], []

    if sensor["suhu"] > threshold["suhu"]["max"]:
        aksi.append("🌫️ Mist Fogger AKTIF — menurunkan suhu ruangan")
        aksi.append("💨 Exhaust Fan AKTIF — sirkulasi udara panas keluar")
    elif sensor["suhu"] < threshold["suhu"]["min"]:
        alert.append("🌡️ Suhu terlalu rendah — periksa pemanas / heater")

    if sensor["kelembaban"] > threshold["kelembaban"]["max"]:
        aksi.append("💨 Exhaust Fan AKTIF — mengurangi kelembaban berlebih")
    elif sensor["kelembaban"] < threshold["kelembaban"]["min"]:
        aksi.append("🌫️ Mist Fogger AKTIF — menaikkan kelembaban udara")

    if sensor["co2"] < threshold["co2"]["min"]:
        aksi.append("🔄 Sirkulasi Udara AKTIF — meningkatkan kadar CO₂")
    elif sensor["co2"] > threshold["co2"]["max"]:
        aksi.append("💨 Exhaust Fan AKTIF — menurunkan CO₂ berlebih")

    if sensor["ec"] < threshold["ec"]["min"]:
        aksi.append("💧 Pompa Nutrisi AKTIF — menaikkan EC larutan")
    elif sensor["ec"] > threshold["ec"]["max"]:
        alert.append("⚠️ EC terlalu tinggi — encerkan konsentrasi larutan nutrisi")

    if sensor["ph"] < threshold["ph"]["min"]:
        alert.append("🔴 pH terlalu asam — tambahkan larutan pH Up")
    elif sensor["ph"] > threshold["ph"]["max"]:
        alert.append("🔴 pH terlalu basa — tambahkan larutan pH Down")

    if not aksi and not alert:
        aksi.append("✅ Semua parameter dalam rentang optimal — sistem standby")

    return aksi, alert

def status_sensor(nilai, key, threshold):
    mn, mx = threshold[key]["min"], threshold[key]["max"]
    if mn <= nilai <= mx:   return "optimal"
    if nilai < mn * 0.92 or nilai > mx * 1.08: return "kritis"
    return "waspada"

def get_cart():  return session.get("cart", {})
def save_cart(c): session["cart"] = c

def cart_count():
    return sum(v["qty"] for v in get_cart().values())

def rp(n):
    return "Rp {:,}".format(int(n)).replace(",", ".")

def make_page(content):
    return BASE_HTML.replace("%%CONTENT%%", content)

# ─────────────────────────────────────────────
# BASE HTML — CSS + NAVBAR + FOOTER
# ─────────────────────────────────────────────

BASE_HTML = """<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AgriPulse Tech — {{ title }}</title>
<style>
:root{--gd:#2d5a27;--gm:#4a7c40;--gl:#7ab648;--gp:#e8f5e1;--or:#f5a623;--rd:#e74c3c;--bl:#3498db;--bg:#f0f4ed;--tx:#2c3e50;--wh:#ffffff;}
*{box-sizing:border-box;margin:0;padding:0;}
body{font-family:'Segoe UI',sans-serif;background:var(--bg);color:var(--tx);}

/* NAV */
nav{background:var(--gd);padding:0 20px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:100;box-shadow:0 2px 10px rgba(0,0,0,.35);min-height:54px;}
.nav-brand{color:#fff;font-size:1.2rem;font-weight:700;text-decoration:none;}
.nav-brand span{color:var(--gl);}
.nav-links{display:flex;align-items:center;gap:3px;flex-wrap:wrap;}
.nav-links a{color:#cde8c0;text-decoration:none;padding:7px 11px;border-radius:6px;font-size:.83rem;transition:all .2s;white-space:nowrap;}
.nav-links a:hover{background:rgba(255,255,255,.12);color:#fff;}
.nav-links a.active{background:var(--gl);color:#fff;font-weight:600;}
.cart-badge{background:var(--or);color:#fff;border-radius:10px;padding:1px 6px;font-size:.72rem;font-weight:700;margin-left:2px;}

/* HERO */
.hero{background:linear-gradient(135deg,var(--gd) 0%,var(--gm) 60%,var(--gl) 100%);color:#fff;text-align:center;padding:48px 24px 38px;}
.hero h1{font-size:2rem;margin-bottom:8px;}
.hero p{opacity:.85;font-size:1rem;}

/* CONTAINER */
.container{max-width:1150px;margin:0 auto;padding:26px 16px;}

/* CARD */
.card{background:var(--wh);border-radius:12px;padding:22px;box-shadow:0 2px 12px rgba(0,0,0,.07);margin-bottom:20px;}
.card h2{color:var(--gd);margin-bottom:14px;font-size:1.1rem;}

/* SENSOR GRID */
.sensor-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(162px,1fr));gap:13px;margin-bottom:20px;}
.sensor-card{border-radius:10px;padding:14px;text-align:center;border:2px solid transparent;transition:transform .2s;}
.sensor-card:hover{transform:translateY(-2px);}
.sensor-card.optimal{background:#e8f5e1;border-color:var(--gl);}
.sensor-card.waspada{background:#fff8e1;border-color:var(--or);}
.sensor-card.kritis{background:#fdecea;border-color:var(--rd);}
.sensor-label{font-size:.74rem;color:#666;text-transform:uppercase;letter-spacing:1px;}
.sensor-value{font-size:1.85rem;font-weight:700;margin:5px 0;}
.optimal .sensor-value{color:var(--gd);}
.waspada .sensor-value{color:#e67e22;}
.kritis .sensor-value{color:var(--rd);}
.sensor-unit{font-size:.8rem;color:#888;}
.sensor-range{font-size:.7rem;color:#aaa;margin-top:3px;}
.sensor-status{display:inline-block;margin-top:5px;padding:2px 9px;border-radius:20px;font-size:.7rem;font-weight:600;}
.optimal .sensor-status{background:var(--gl);color:#fff;}
.waspada .sensor-status{background:var(--or);color:#fff;}
.kritis .sensor-status{background:var(--rd);color:#fff;}

/* ACTION LIST */
.aksi-list{list-style:none;}
.aksi-list li{padding:7px 12px;margin-bottom:5px;background:var(--gp);border-radius:6px;border-left:4px solid var(--gl);font-size:.88rem;}
.alert-item{background:#fff3cd!important;border-left-color:var(--or)!important;}

/* PRODUK GRID */
.produk-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(296px,1fr));gap:20px;}
.produk-card{background:var(--wh);border-radius:14px;padding:22px;box-shadow:0 2px 16px rgba(0,0,0,.09);border-top:4px solid var(--gl);display:flex;flex-direction:column;position:relative;}
.produk-badge{position:absolute;top:14px;right:14px;background:var(--or);color:#fff;padding:3px 10px;border-radius:20px;font-size:.72rem;font-weight:700;}
.produk-emoji{font-size:2.3rem;margin-bottom:8px;}
.produk-nama{font-size:1.1rem;font-weight:700;color:var(--gd);}
.produk-harga{font-size:1.4rem;font-weight:700;color:var(--gm);margin:8px 0;}
.produk-desc{color:#666;font-size:.86rem;margin-bottom:10px;}
.produk-isi{list-style:none;margin-bottom:14px;flex:1;}
.produk-isi li{padding:3px 0;font-size:.84rem;color:#555;}
.produk-isi li::before{content:"✓ ";color:var(--gl);font-weight:700;}
.hpp-info{font-size:.76rem;color:#999;margin-bottom:10px;}

/* BUTTONS */
.btn{display:inline-block;padding:10px 20px;border-radius:8px;font-size:.9rem;font-weight:600;cursor:pointer;border:none;text-decoration:none;text-align:center;transition:opacity .2s,transform .1s;}
.btn:hover{opacity:.88;transform:translateY(-1px);}
.btn-green{background:var(--gm);color:#fff;}
.btn-dark{background:var(--gd);color:#fff;}
.btn-orange{background:var(--or);color:#fff;}
.btn-red{background:var(--rd);color:#fff;}
.btn-outline{background:transparent;color:var(--gd);border:2px solid var(--gd);}
.w100{width:100%;}

/* TABLE */
.tbl{width:100%;border-collapse:collapse;font-size:.87rem;}
.tbl th{background:var(--gd);color:#fff;padding:9px 13px;text-align:left;}
.tbl td{padding:9px 13px;border-bottom:1px solid #eee;}
.tbl tr:last-child td{border-bottom:none;}
.tbl tr:hover td{background:var(--gp);}
.tbl .total-row td{font-weight:700;background:var(--gp);color:var(--gd);}
.tbl .highlight{background:#fff8e1;}

/* CART */
.qty-ctrl{display:flex;align-items:center;gap:7px;}
.qty-ctrl a{display:inline-flex;align-items:center;justify-content:center;width:26px;height:26px;border-radius:50%;background:var(--gp);color:var(--gd);text-decoration:none;font-weight:700;font-size:1rem;}
.qty-ctrl a:hover{background:var(--gl);color:#fff;}

/* INVOICE */
.invoice-box{border:2px solid var(--gd);border-radius:12px;padding:30px;max-width:680px;margin:0 auto;background:var(--wh);}
.invoice-title{font-size:1.7rem;font-weight:700;color:var(--gd);}
.badge-lunas{background:var(--gl);color:#fff;padding:3px 14px;border-radius:20px;font-size:.82rem;font-weight:700;}

/* FORM */
.form-group{margin-bottom:14px;}
.form-group label{display:block;margin-bottom:5px;font-weight:600;color:var(--gd);font-size:.88rem;}
.form-group input,.form-group select,.form-group textarea{width:100%;padding:9px 12px;border:2px solid #ddd;border-radius:8px;font-size:.95rem;transition:border-color .2s;}
.form-group input:focus,.form-group select:focus,.form-group textarea:focus{border-color:var(--gl);outline:none;}

/* MISC */
.section-title{font-size:1.35rem;font-weight:700;color:var(--gd);margin-bottom:16px;}
.alert-box{padding:11px 16px;border-radius:8px;margin-bottom:14px;background:#d4edda;color:#155724;border:1px solid #c3e6cb;}
.info-box{background:#d1ecf1;color:#0c5460;border:1px solid #bee5eb;padding:11px 16px;border-radius:8px;margin-bottom:14px;font-size:.88rem;}
.warn-box{background:#fff3cd;color:#856404;border:1px solid #ffc107;padding:11px 16px;border-radius:8px;margin-bottom:14px;font-size:.88rem;}

/* STAT CARDS */
.stat-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:20px;}
.stat-card{background:var(--gd);color:#fff;border-radius:12px;padding:18px 20px;}
.stat-card.g2{background:var(--gm);}
.stat-card.or{background:#e67e22;}
.stat-card.rd{background:var(--rd);}
.stat-card.bl{background:var(--bl);}
.stat-label{font-size:.78rem;opacity:.8;margin-bottom:3px;}
.stat-value{font-size:1.5rem;font-weight:700;}
.stat-sub{font-size:.74rem;opacity:.75;margin-top:2px;}

/* VPD */
.vpd-bar{display:flex;align-items:center;gap:14px;background:var(--gp);border:2px solid var(--gl);border-radius:10px;padding:10px 18px;margin-bottom:16px;flex-wrap:wrap;}
.vpd-val{font-size:1.6rem;font-weight:700;color:var(--gd);}
.vpd-info{font-size:.85rem;}

/* KOMODITAS PILLS */
.pills{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px;}
.pills a{padding:7px 16px;border-radius:20px;font-size:.85rem;font-weight:600;text-decoration:none;border:2px solid var(--gl);color:var(--gd);transition:all .2s;}
.pills a.active,.pills a:hover{background:var(--gl);color:#fff;}

/* FLOW STEPS */
.flow-steps{display:flex;flex-wrap:wrap;border-radius:10px;overflow:hidden;margin-bottom:6px;}
.flow-step{flex:1;min-width:128px;text-align:center;padding:14px 8px;color:#fff;}
.flow-step:nth-child(odd){background:var(--gd);}
.flow-step:nth-child(even){background:var(--gm);}
.flow-num{font-size:1.5rem;font-weight:700;opacity:.3;}
.flow-name{font-weight:700;font-size:.88rem;margin:2px 0;}
.flow-desc{font-size:.74rem;opacity:.82;}

/* ARCH GRID */
.arch-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:16px;margin-bottom:20px;}
.arch-card{background:var(--wh);border-radius:12px;padding:18px;border-top:4px solid var(--gl);box-shadow:0 2px 8px rgba(0,0,0,.07);}
.arch-icon{font-size:2rem;margin-bottom:8px;}
.arch-title{font-weight:700;color:var(--gd);margin-bottom:8px;}
.arch-list{list-style:none;}
.arch-list li{font-size:.83rem;color:#555;padding:2px 0;}
.arch-list li::before{content:"→ ";color:var(--gl);}

/* TEAM GRID */
.team-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(178px,1fr));gap:16px;}
.team-card{background:var(--wh);border-radius:12px;padding:20px;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,.08);border-top:4px solid var(--gl);}
.team-emoji{font-size:2.8rem;margin-bottom:8px;}
.team-nama{font-weight:700;color:var(--gd);font-size:.98rem;}
.team-jabatan{background:var(--gd);color:#fff;display:inline-block;padding:2px 12px;border-radius:20px;font-size:.75rem;font-weight:700;margin:5px 0;}
.team-desc{color:#666;font-size:.8rem;margin-top:4px;}

/* CORE VALUES */
.cv-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;}
.cv-card{background:var(--gp);border-radius:10px;padding:16px;border-left:4px solid var(--gl);}
.cv-title{font-weight:700;color:var(--gd);font-size:.95rem;margin-bottom:5px;}
.cv-desc{color:#555;font-size:.83rem;}

/* REFRESH BAR */
.refresh-bar{background:var(--gp);border:1px solid var(--gl);border-radius:8px;padding:9px 16px;margin-bottom:18px;display:flex;align-items:center;justify-content:space-between;font-size:.86rem;flex-wrap:wrap;gap:8px;}

/* CHART */
.chart-container{position:relative;height:220px;}

/* CF TABLE */
.cf-pos{color:#27ae60;font-weight:700;}
.cf-neg{color:var(--rd);font-weight:700;}
.cf-hl{background:#e8f5e1!important;}

/* TIMELINE */
.tl-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin-bottom:20px;}
.tl-item{background:var(--wh);border-radius:10px;padding:14px;border-left:4px solid var(--gl);}
.tl-fase{font-weight:700;color:var(--gd);font-size:.93rem;}
.tl-period{color:var(--gm);font-size:.8rem;margin:2px 0;}
.tl-unit{font-weight:700;font-size:1.1rem;color:var(--gd);}
.tl-desc{color:#666;font-size:.8rem;}

footer{background:var(--gd);color:#aad08a;text-align:center;padding:18px;font-size:.82rem;margin-top:40px;}
@media(max-width:640px){.nav-links a{padding:5px 7px;font-size:.76rem;}.hero h1{font-size:1.5rem;}.sensor-value{font-size:1.5rem;}}
</style>
</head>
<body>
<nav>
  <a class="nav-brand" href="/">🌿 <span>AgriPulse</span> Tech</a>
  <div class="nav-links">
    <a href="/"          class="{{ 'active' if active=='dashboard' }}">📊 Dashboard</a>
    <a href="/tentang"   class="{{ 'active' if active=='tentang'   }}">🌿 Tentang</a>
    <a href="/teknologi" class="{{ 'active' if active=='teknologi' }}">⚙️ Teknologi</a>
    <a href="/tim"       class="{{ 'active' if active=='tim'       }}">👥 Tim</a>
    <a href="/produk"    class="{{ 'active' if active=='produk'    }}">🛒 Produk</a>
    <a href="/finansial" class="{{ 'active' if active=='finansial' }}">💰 Finansial</a>
    <a href="/cart"      class="{{ 'active' if active=='cart'      }}">
      🛍️ Keranjang{% if cart_count > 0 %}<span class="cart-badge">{{ cart_count }}</span>{% endif %}
    </a>
  </div>
</nav>
%%CONTENT%%
<footer>
  &copy; 2025 PT AgriPulse Digital Nusantara &nbsp;|&nbsp;
  "Revolutionizing Agriculture with Precision Data" &nbsp;|&nbsp;
  Kelompok 2 — CEO: Zacky M. | COO: Rizzi A. | CPO: Rinjanie A. | CTO: M.Yahya D.H. | CBO: Amr. Ibrahimovich A.
</footer>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</body>
</html>"""

# ─────────────────────────────────────────────
# DASHBOARD PAGE
# ─────────────────────────────────────────────

DASHBOARD_HTML = make_page("""
<div class="hero">
  <h1>📡 Greenhouse Monitoring Dashboard</h1>
  <p>Real-time sensor data · Closed-loop control aktif · Auto-refresh setiap 30 detik</p>
</div>
<div class="container">

  <!-- KOMODITAS SELECTOR -->
  <div class="section-title">🌱 Pilih Komoditas</div>
  <div class="pills">
    {% for k, v in komoditas_list.items() %}
    <a href="/?komoditas={{ k }}" class="{{ 'active' if k == komoditas_key }}">{{ v.emoji }} {{ v.nama }}</a>
    {% endfor %}
  </div>

  <!-- REFRESH BAR -->
  <div class="refresh-bar">
    <span>🕐 Pembacaan terakhir: <strong id="last-update">{{ sensor.timestamp }}</strong>
      &nbsp;·&nbsp; Komoditas: <strong>{{ komoditas_info.emoji }} {{ komoditas_info.nama }}</strong>
      &nbsp;·&nbsp; Sistem: <strong>{{ komoditas_info.sistem }}</strong>
    </span>
    <span>🔄 Auto-refresh dalam <strong id="countdown">30s</strong></span>
  </div>

  <!-- VPD BAR -->
  <div class="vpd-bar" id="vpd-bar">
    <div>
      <div style="font-size:.78rem;color:#666;text-transform:uppercase;letter-spacing:1px;">VPD (Vapor Pressure Deficit)</div>
      <div class="vpd-val" id="vpd-value">{{ vpd }} kPa</div>
    </div>
    <div class="vpd-info" id="vpd-info">
      <strong>{{ vpd_label }}</strong><br>
      <span style="font-size:.78rem;color:#777;">Rentang optimal: 0.4 – 1.2 kPa &nbsp;|&nbsp; Mengukur tekanan evaporasi tanaman</span>
    </div>
  </div>

  <!-- SENSOR CARDS -->
  <div class="section-title">📡 Data Sensor Greenhouse</div>
  <div class="sensor-grid">
    {% for key, label, icon in [('suhu','Suhu Udara','🌡️'),('kelembaban','Kelembaban','💧'),('co2','CO₂','🌫️'),('ec','EC Nutrisi','⚗️'),('ph','pH Larutan','🔬')] %}
    {% set val = sensor[key] %}
    {% set st  = statuses[key] %}
    <div class="sensor-card {{ st }}" id="card-{{ key }}">
      <div class="sensor-label">{{ icon }} {{ label }}</div>
      <div class="sensor-value" id="val-{{ key }}">{{ val }}</div>
      <div class="sensor-unit">{{ threshold[key].unit }}</div>
      <span class="sensor-status" id="sta-{{ key }}">
        {% if st=='optimal' %}✓ Optimal{% elif st=='waspada' %}⚠ Waspada{% else %}🔴 Kritis{% endif %}
      </span>
      <div class="sensor-range">Range: {{ threshold[key].min }}–{{ threshold[key].max }} {{ threshold[key].unit }}</div>
    </div>
    {% endfor %}
  </div>

  <!-- AUTOMATED ACTION -->
  <div class="card">
    <h2>⚙️ Automated Action (Closed-Loop Control)</h2>
    <p style="font-size:.82rem;color:#777;margin-bottom:10px;">ESP32 merespons otomatis berdasarkan data sensor & Gold Standard komoditas — bukan timer.</p>
    <ul class="aksi-list" id="aksi-list">
      {% for a in aksi %}<li>{{ a }}</li>{% endfor %}
      {% for a in alerts %}<li class="alert-item">{{ a }}</li>{% endfor %}
    </ul>
  </div>

  <!-- HISTORIS CHART -->
  <div class="card">
    <h2>📈 Grafik Historis Sensor ({{ history|length }} pembacaan terakhir)</h2>
    <div class="chart-container">
      <canvas id="sensorChart"></canvas>
    </div>
  </div>

  <!-- ALUR SISTEM -->
  <div class="card">
    <h2>🔄 Konsep Kinerja Alat — 5 Tahap</h2>
    <div class="flow-steps">
      <div class="flow-step"><div class="flow-num">1</div><div class="flow-name">Data Acquisition</div><div class="flow-desc">Sensor baca tiap 30 detik</div></div>
      <div class="flow-step"><div class="flow-num">2</div><div class="flow-name">Data Transmission</div><div class="flow-desc">ESP32 → Cloud via MQTT</div></div>
      <div class="flow-step"><div class="flow-num">3</div><div class="flow-name">Data Processing</div><div class="flow-desc">Bandingkan Gold Standard</div></div>
      <div class="flow-step"><div class="flow-num">4</div><div class="flow-name">Automated Action</div><div class="flow-desc">Aktuator respons otomatis</div></div>
      <div class="flow-step"><div class="flow-num">5</div><div class="flow-name">Monitoring & Report</div><div class="flow-desc">Dashboard & notifikasi</div></div>
    </div>
  </div>

  <div class="info-box">
    💡 <strong>Simulasi</strong>: Pada sistem nyata, ESP32 DevKit V1 mengirim data via MQTT ke cloud server setiap 30 detik.
    Dashboard memperbarui otomatis. Threshold disesuaikan komoditas yang dipilih (Gold Standard agronomi).
    <a href="/produk" style="color:var(--gd);font-weight:600;">Lihat produk →</a>
  </div>
</div>

<script>
// ── Chart.js Historis ──────────────────────────────────────────────
const histData = {{ history_json | safe }};
const ctx = document.getElementById('sensorChart');
let chart = null;
if (ctx && histData.length > 0) {
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: histData.map(h => h.timestamp),
      datasets: [
        { label: 'Suhu (°C)',      data: histData.map(h => h.suhu),       borderColor:'#e74c3c', backgroundColor:'rgba(231,76,60,.08)',  tension:.4, pointRadius:3 },
        { label: 'Kelembaban (%)', data: histData.map(h => h.kelembaban), borderColor:'#3498db', backgroundColor:'rgba(52,152,219,.08)', tension:.4, pointRadius:3 },
        { label: 'CO₂ ÷10',       data: histData.map(h => h.co2/10),     borderColor:'#9b59b6', backgroundColor:'rgba(155,89,182,.08)', tension:.4, pointRadius:3 },
        { label: 'EC (mS/cm)',     data: histData.map(h => h.ec),         borderColor:'#27ae60', backgroundColor:'rgba(39,174,96,.08)',  tension:.4, pointRadius:3 },
      ]
    },
    options: {
      responsive:true, maintainAspectRatio:false,
      plugins:{ legend:{ position:'top', labels:{ font:{ size:11 } } } },
      scales:{ y:{ beginAtZero:false, grid:{ color:'rgba(0,0,0,.04)' } } }
    }
  });
}

// ── Auto-refresh + countdown ───────────────────────────────────────
let countdown = 30;
const komoditas = '{{ komoditas_key }}';

function updateDom(data) {
  const s = data.sensor, st = data.statuses;
  document.getElementById('last-update').textContent = s.timestamp;
  document.getElementById('vpd-value').textContent = data.vpd + ' kPa';
  document.getElementById('vpd-info').innerHTML = '<strong>' + data.vpd_label + '</strong><br><span style="font-size:.78rem;color:#777;">Rentang optimal: 0.4 – 1.2 kPa &nbsp;|&nbsp; Mengukur tekanan evaporasi tanaman</span>';
  ['suhu','kelembaban','co2','ec','ph'].forEach(key => {
    const card = document.getElementById('card-' + key);
    if (!card) return;
    card.className = 'sensor-card ' + st[key];
    document.getElementById('val-' + key).textContent = s[key];
    const el = document.getElementById('sta-' + key);
    el.textContent = st[key]==='optimal' ? '✓ Optimal' : st[key]==='waspada' ? '⚠ Waspada' : '🔴 Kritis';
  });
  const aksiEl = document.getElementById('aksi-list');
  if (aksiEl) {
    let h = '';
    data.aksi.forEach(a => h += '<li>' + a + '</li>');
    data.alerts.forEach(a => h += '<li class="alert-item">' + a + '</li>');
    aksiEl.innerHTML = h;
  }
  if (chart) {
    chart.data.labels.push(s.timestamp);
    chart.data.datasets[0].data.push(s.suhu);
    chart.data.datasets[1].data.push(s.kelembaban);
    chart.data.datasets[2].data.push(s.co2 / 10);
    chart.data.datasets[3].data.push(s.ec);
    if (chart.data.labels.length > 20) {
      chart.data.labels.shift();
      chart.data.datasets.forEach(d => d.data.shift());
    }
    chart.update('none');
  }
}

function tick() {
  document.getElementById('countdown').textContent = countdown + 's';
  countdown--;
  if (countdown < 0) {
    countdown = 30;
    fetch('/api/sensor?komoditas=' + komoditas)
      .then(r => r.json())
      .then(updateDom)
      .catch(console.error);
  }
}
setInterval(tick, 1000);
</script>
""")

# ─────────────────────────────────────────────
# TENTANG PAGE
# ─────────────────────────────────────────────

TENTANG_HTML = make_page("""
<div class="hero">
  <h1>🌿 Tentang PT AgriPulse Digital Nusantara</h1>
  <p>"Revolutionizing Agriculture with Precision Data"</p>
</div>
<div class="container">

  <!-- STAT CARDS -->
  <div class="stat-grid">
    <div class="stat-card"><div class="stat-label">Penurunan Risiko Gagal Panen</div><div class="stat-value">↓ 40%</div><div class="stat-sub">vs. metode konvensional</div></div>
    <div class="stat-card g2"><div class="stat-label">Efisiensi Biaya Tenaga Kerja</div><div class="stat-value">↓ 50%</div><div class="stat-sub">lewat otomasi berbasis sensor</div></div>
    <div class="stat-card or"><div class="stat-label">Komoditas Unggulan</div><div class="stat-value">4</div><div class="stat-sub">Selada · Melon · Tomat · Paprika</div></div>
    <div class="stat-card bl"><div class="stat-label">Pilar Bisnis Utama</div><div class="stat-value">3</div><div class="stat-sub">Hardware + SaaS + Konsultasi</div></div>
  </div>

  <!-- ABOUT -->
  <div class="card">
    <h2>🏢 Gambaran Umum Perusahaan</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;flex-wrap:wrap;">
      <div>
        <p style="line-height:1.7;margin-bottom:12px;">
          <strong>PT AgriPulse Digital Nusantara (AgriPulse Tech)</strong> adalah startup Agri-Tech yang
          fokus pada IoT Smart-Kit untuk manajemen greenhouse cerdas.
        </p>
        <p style="line-height:1.7;margin-bottom:12px;">
          Kami hadir karena petani hortikultura masih bergantung pada intuisi dan kontrol manual
          di tengah iklim tropis yang tidak stabil. Kami menyediakan ekosistem lengkap: sensor industri,
          kontrol otomatis berbasis mikrokontroler, dan dashboard cloud yang bisa diakses dari mana saja.
        </p>
        <p style="line-height:1.7;">
          Didirikan oleh tim lintas disiplin (IoT, agronomi, software), kami percaya masa depan
          ketahanan pangan ada pada kombinasi pengalaman bertani dan teknologi data.
        </p>
      </div>
      <div>
        <table class="tbl">
          <tr><th colspan="2">Profil Perusahaan</th></tr>
          <tr><td><strong>Nama</strong></td><td>PT AgriPulse Digital Nusantara</td></tr>
          <tr><td><strong>Tagline</strong></td><td>"Revolutionizing Agriculture with Precision Data"</td></tr>
          <tr><td><strong>Sektor</strong></td><td>Agri-Tech</td></tr>
          <tr><td><strong>Model Bisnis</strong></td><td>IoT Hardware + SaaS + Konsultasi</td></tr>
          <tr><td><strong>Lokasi Target</strong></td><td>Berastagi & Karo, Sumatera Utara</td></tr>
          <tr><td><strong>CAPEX Awal</strong></td><td>Rp 323.000.000</td></tr>
          <tr><td><strong>Target Tahun 1</strong></td><td>210 unit Smart-Kit</td></tr>
          <tr><td><strong>Payback Period</strong></td><td>±26–28 bulan</td></tr>
        </table>
      </div>
    </div>
  </div>

  <!-- TARGET PASAR -->
  <div class="card">
    <h2>🎯 Target Pasar</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;">
      <div style="background:var(--gp);border-radius:8px;padding:14px;border-left:4px solid var(--gl);">
        <div style="font-weight:700;color:var(--gd);">🌾 Pengusaha Hortikultura Premium</div>
        <div style="font-size:.82rem;color:#666;margin-top:4px;">Greenhouse skala menengah–besar yang butuh efisiensi operasional</div>
      </div>
      <div style="background:var(--gp);border-radius:8px;padding:14px;border-left:4px solid var(--gl);">
        <div style="font-weight:700;color:var(--gd);">🏭 Perusahaan Benih & Agribisnis</div>
        <div style="font-size:.82rem;color:#666;margin-top:4px;">Skala menengah–besar yang butuh sistem data presisi</div>
      </div>
      <div style="background:var(--gp);border-radius:8px;padding:14px;border-left:4px solid var(--gl);">
        <div style="font-weight:700;color:var(--gd);">🎓 Lembaga Riset & Universitas</div>
        <div style="font-size:.82rem;color:#666;margin-top:4px;">Kebutuhan data sensor presisi untuk penelitian agronomi</div>
      </div>
      <div style="background:var(--gp);border-radius:8px;padding:14px;border-left:4px solid var(--gl);">
        <div style="font-weight:700;color:var(--gd);">👨‍🌾 Petani Pertanian Presisi</div>
        <div style="font-size:.82rem;color:#666;margin-top:4px;">Petani yang beralih dari konvensional ke smart farming</div>
      </div>
    </div>
  </div>

  <!-- VISI & MISI -->
  <div class="card">
    <h2>🔭 Visi & Misi</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
      <div>
        <div style="background:var(--gd);color:#fff;border-radius:10px;padding:16px;text-align:center;margin-bottom:14px;">
          <div style="font-size:.8rem;opacity:.8;margin-bottom:4px;">VISI</div>
          <div style="font-size:1rem;font-weight:700;line-height:1.5;">Kedaulatan pangan nasional berbasis data presisi.</div>
        </div>
      </div>
      <div>
        <div style="background:var(--gp);border-radius:10px;padding:16px;">
          <div style="font-weight:700;color:var(--gd);margin-bottom:10px;">MISI AgriPulse Tech</div>
          <ol style="padding-left:16px;font-size:.85rem;line-height:1.9;">
            <li><strong>Inovasi berkelanjutan</strong> — IoT greenhouse canggih, andal, terjangkau</li>
            <li><strong>Efisiensi operasional</strong> — Menekan biaya TK hingga 50% via otomasi</li>
            <li><strong>Ekosistem data</strong> — Data presisi untuk prediksi panen & kebutuhan input</li>
            <li><strong>Aksesibilitas teknologi</strong> — Smart farming dari agribisnis besar ke petani menengah</li>
            <li><strong>Transparansi rantai pasok</strong> — Traceability dari benih hingga panen</li>
          </ol>
        </div>
      </div>
    </div>
  </div>

  <!-- CORE VALUES -->
  <div class="card">
    <h2>💎 Core Values</h2>
    <div class="cv-grid">
      <div class="cv-card"><div class="cv-title">📊 Data-Driven Precision</div><div class="cv-desc">Setiap keputusan budidaya diambil berdasarkan data sensor, bukan intuisi.</div></div>
      <div class="cv-card"><div class="cv-title">💧 Efisiensi Sumber Daya</div><div class="cv-desc">Penghematan air dan pupuk melalui sistem irigasi presisi berbasis EC/pH.</div></div>
      <div class="cv-card"><div class="cv-title">🧑‍💻 User-Centric Innovation</div><div class="cv-desc">Teknologi yang mudah dioperasikan oleh petani lokal tanpa keahlian teknis.</div></div>
      <div class="cv-card"><div class="cv-title">🔍 Radical Transparency</div><div class="cv-desc">Memberikan akses data yang transparan dan real-time bagi semua konsumen.</div></div>
      <div class="cv-card"><div class="cv-title">🛡️ Adaptive Resilience</div><div class="cv-desc">Sistem tangguh dan adaptif terhadap perubahan iklim mikro ekstrem tropis.</div></div>
    </div>
  </div>

</div>
""")

# ─────────────────────────────────────────────
# TEKNOLOGI PAGE
# ─────────────────────────────────────────────

TEKNOLOGI_HTML = make_page("""
<div class="hero">
  <h1>⚙️ Bidang Usaha & Detail Teknologi</h1>
  <p>Smart Greenhouse Management & Precision Horticulture · Arsitektur Sistem AgriPulse</p>
</div>
<div class="container">

  <!-- ARSITEKTUR SISTEM -->
  <div class="section-title">🏗️ Arsitektur Sistem AgriPulse</div>
  <div class="arch-grid">
    <div class="arch-card">
      <div class="arch-icon">🖥️</div>
      <div class="arch-title">Hardware (IoT Node)</div>
      <ul class="arch-list">
        <li><strong>ESP32 DevKit V1</strong> — otak sistem</li>
        <li>Dual-core, WiFi & Bluetooth</li>
        <li>Hemat daya & mudah dikembangkan</li>
        <li>Expansion board untuk sensor industrial</li>
        <li>Standar IoT pertanian Asia Tenggara</li>
      </ul>
    </div>
    <div class="arch-card">
      <div class="arch-icon">🌡️</div>
      <div class="arch-title">Sensor Suite</div>
      <ul class="arch-list">
        <li><strong>SHT31</strong> — Suhu & Kelembaban (akurasi tinggi, IP-rated)</li>
        <li><strong>MH-Z19C</strong> — CO₂ NDIR (presisi, self-calibrating)</li>
        <li><strong>EC & pH Meter</strong> — Nutrisi & keasaman larutan (BNC Industrial)</li>
        <li>Tahan lingkungan lembab (RH 70–90%)</li>
      </ul>
    </div>
    <div class="arch-card">
      <div class="arch-icon">⚙️</div>
      <div class="arch-title">Automation Actuator</div>
      <ul class="arch-list">
        <li><strong>Mist Fogger</strong> — kontrol suhu & kelembaban</li>
        <li><strong>Exhaust Fan</strong> — sirkulasi & ventilasi</li>
        <li><strong>Pompa Nutrisi</strong> — kontrol EC larutan</li>
        <li><strong>Solenoid Valve</strong> — irigasi otomatis</li>
        <li>Relay 4-channel, berbasis threshold sensor</li>
      </ul>
    </div>
    <div class="arch-card">
      <div class="arch-icon">☁️</div>
      <div class="arch-title">Software (Cloud System)</div>
      <ul class="arch-list">
        <li>Data via <strong>MQTT</strong> — ringan, stabil koneksi lemah</li>
        <li>Buffer lokal ESP32 saat internet putus</li>
        <li>Analisis dengan Gold Standard agronomi</li>
        <li>Dashboard real-time dari mana saja</li>
        <li>Notifikasi WhatsApp / Email otomatis</li>
      </ul>
    </div>
  </div>

  <!-- KONSEP KINERJA -->
  <div class="card">
    <h2>🔄 Konsep Kinerja Alat — Berbasis Kebutuhan Tanaman, Bukan Timer</h2>
    <div class="flow-steps" style="margin-bottom:14px;">
      <div class="flow-step"><div class="flow-num">1</div><div class="flow-name">Data Acquisition</div><div class="flow-desc">Sensor baca tiap 30 detik</div></div>
      <div class="flow-step"><div class="flow-num">2</div><div class="flow-name">Data Transmission</div><div class="flow-desc">ESP32 → Cloud via MQTT</div></div>
      <div class="flow-step"><div class="flow-num">3</div><div class="flow-name">Data Processing</div><div class="flow-desc">Bandingkan Gold Standard</div></div>
      <div class="flow-step"><div class="flow-num">4</div><div class="flow-name">Automated Action</div><div class="flow-desc">Relay → aktuator aktif</div></div>
      <div class="flow-step"><div class="flow-num">5</div><div class="flow-name">Monitoring & Report</div><div class="flow-desc">Dashboard & notifikasi</div></div>
    </div>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;font-size:.84rem;">
      <div style="background:var(--gp);padding:10px;border-radius:7px;"><strong>Suhu tinggi →</strong> Mist Fogger + Exhaust Fan</div>
      <div style="background:var(--gp);padding:10px;border-radius:7px;"><strong>CO₂ rendah →</strong> Sirkulasi udara aktif</div>
      <div style="background:var(--gp);padding:10px;border-radius:7px;"><strong>EC rendah →</strong> Pompa nutrisi aktif</div>
      <div style="background:#fff3cd;padding:10px;border-radius:7px;"><strong>pH abnormal →</strong> Alert ke dashboard</div>
    </div>
  </div>

  <!-- BOM TABLE -->
  <div class="card">
    <h2>🛠️ Bill of Materials (BOM) — 1 Unit Smart-Kit</h2>
    <table class="tbl">
      <thead>
        <tr><th>Komponen</th><th>Spesifikasi</th><th style="text-align:right;">Harga Satuan</th></tr>
      </thead>
      <tbody>
        {% for item in bom %}
        <tr>
          <td><strong>{{ item.komponen }}</strong></td>
          <td>{{ item.spesifikasi }}</td>
          <td style="text-align:right;">{{ item.harga | int | format_rp }}</td>
        </tr>
        {% endfor %}
        <tr class="total-row">
          <td colspan="2"><strong>Total BOM / Unit</strong></td>
          <td style="text-align:right;"><strong>Rp 3.500.000</strong></td>
        </tr>
      </tbody>
    </table>
    <div class="info-box" style="margin-top:14px;margin-bottom:0;">
      💡 HPP per unit (termasuk TK + overhead): <strong>Rp 4.963.000</strong> &nbsp;·&nbsp;
      Harga jual: <strong>Rp 6.800.000</strong> &nbsp;·&nbsp; Gross margin: <strong>~37%</strong>
    </div>
  </div>

  <!-- GOLD STANDARD THRESHOLD -->
  <div class="card">
    <h2>📏 Gold Standard Threshold per Komoditas</h2>
    <table class="tbl">
      <thead>
        <tr><th>Komoditas</th><th>Suhu (°C)</th><th>Kelembaban (%)</th><th>CO₂ (ppm)</th><th>EC (mS/cm)</th><th>pH</th><th>Sistem</th></tr>
      </thead>
      <tbody>
        {% for k, v in komoditas_list.items() %}
        <tr>
          <td>{{ v.emoji }} <strong>{{ v.nama }}</strong></td>
          <td>{{ v.suhu.min }}–{{ v.suhu.max }}</td>
          <td>{{ v.kelembaban.min }}–{{ v.kelembaban.max }}</td>
          <td>{{ v.co2.min }}–{{ v.co2.max }}</td>
          <td>{{ v.ec.min }}–{{ v.ec.max }}</td>
          <td>{{ v.ph.min }}–{{ v.ph.max }}</td>
          <td>{{ v.sistem }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>

  <!-- ANALISIS KELAYAKAN -->
  <div class="card">
    <h2>📍 Analisis Kelayakan Teknis — Berastagi & Karo, Sumatera Utara</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
      <div>
        <div style="font-weight:700;color:var(--gd);margin-bottom:8px;">Kesesuaian Lokasi & Lingkungan</div>
        <p style="font-size:.85rem;line-height:1.7;margin-bottom:10px;">
          Sumatera beriklim tropis lembab (24–34°C, RH 70–90%) sehingga kontrol mikroklimat
          greenhouse menjadi kebutuhan utama, bukan tambahan.
        </p>
        <ul style="font-size:.83rem;padding-left:16px;line-height:1.8;">
          <li>Cuaca ekstrem → kontrol otomatis berbasis sensor</li>
          <li>Internet tidak stabil → buffer lokal + MQTT ringan</li>
          <li>Listrik fluktuatif → UPS + proteksi daya</li>
          <li>Kelembaban tinggi → perangkat IP65</li>
        </ul>
      </div>
      <div>
        <div style="font-weight:700;color:var(--gd);margin-bottom:8px;">Sarana & Prasarana</div>
        <ul style="font-size:.83rem;padding-left:16px;line-height:1.9;">
          <li>Internet: tersedia di sentra agribisnis</li>
          <li>Listrik PLN: tersedia di area pertanian utama</li>
          <li>Akses logistik: baik di Berastagi, Solok, Lampung</li>
          <li>Komponen elektronik: tersedia di kota besar Sumatera</li>
          <li>Tenaga teknisi: via SMK Teknik Elektronika lokal</li>
        </ul>
        <div class="info-box" style="margin-top:10px;margin-bottom:0;font-size:.8rem;">
          📍 Koordinat: 3.10–3.30 LU, 98.30–98.70 BT (Karo Dataran Tinggi)
        </div>
      </div>
    </div>
  </div>

</div>
""")

# ─────────────────────────────────────────────
# TIM PAGE
# ─────────────────────────────────────────────

TIM_HTML = make_page("""
<div class="hero">
  <h1>👥 Struktur Bisnis AgriPulse Tech</h1>
  <p>Meet Our Team — Kelompok 2</p>
</div>
<div class="container">

  <!-- TEAM CARDS -->
  <div class="section-title">🏆 Meet Our Team</div>
  <div class="team-grid">
    {% for p in tim %}
    <div class="team-card">
      <div class="team-emoji">{{ p.emoji }}</div>
      <div class="team-nama">{{ p.nama }}</div>
      <div class="team-jabatan">{{ p.jabatan }}</div>
      <div class="team-desc">{{ p.desc }}</div>
    </div>
    {% endfor %}
  </div>

  <!-- SDM INTERNAL -->
  <div class="card" style="margin-top:10px;">
    <h2>🏢 SDM Internal AgriPulse Tech</h2>
    <table class="tbl">
      <thead><tr><th>Jabatan</th><th>Jumlah</th><th>Gaji/Orang</th><th>Total</th><th>Tanggung Jawab</th></tr></thead>
      <tbody>
        <tr><td>CEO</td><td>1</td><td>Rp 8.000.000</td><td>Rp 8.000.000</td><td>Strategi & representasi perusahaan</td></tr>
        <tr><td>COO</td><td>1</td><td>Rp 6.000.000</td><td>Rp 6.000.000</td><td>Produksi, logistik, QC</td></tr>
        <tr><td>CPO</td><td>1</td><td>Rp 6.000.000</td><td>Rp 6.000.000</td><td>Product development & roadmap</td></tr>
        <tr><td>CTO</td><td>1</td><td>Rp 5.000.000</td><td>Rp 5.000.000</td><td>Firmware & inovasi teknologi</td></tr>
        <tr><td>CBO</td><td>1</td><td>Rp 5.000.000</td><td>Rp 5.000.000</td><td>Akuisisi & kemitraan B2B</td></tr>
        <tr class="total-row"><td colspan="3"><strong>Total SDM / Bulan</strong></td><td><strong>Rp 30.000.000</strong></td><td></td></tr>
      </tbody>
    </table>
  </div>

  <!-- DAMPAK TK KLIEN -->
  <div class="card">
    <h2>👷 Dampak ke Tenaga Kerja Klien (Greenhouse 6×12 m)</h2>
    <table class="tbl">
      <thead><tr><th>Tahap Kegiatan</th><th>Jumlah Pekerja</th><th>Lama Kerja (Hari)</th><th>Total HOK</th></tr></thead>
      <tbody>
        <tr><td>Persiapan & Instalasi</td><td>2</td><td>3</td><td>6</td></tr>
        <tr><td>Penanaman</td><td>1</td><td>1</td><td>1</td></tr>
        <tr><td>Pemeliharaan (Rutinitas)</td><td>1</td><td>30</td><td>30</td></tr>
        <tr><td>Panen & Pascapanen</td><td>2</td><td>2</td><td>4</td></tr>
        <tr class="total-row"><td colspan="3">Total Estimasi</td><td>41 HOK</td></tr>
        <tr class="total-row"><td colspan="3">Total Upah (Rp 100.000/HOK)</td><td>Rp 4.100.000</td></tr>
      </tbody>
    </table>
    <div class="warn-box" style="margin-top:14px;margin-bottom:0;">
      * Mengurangi kebutuhan tenaga kerja hingga <strong>±50%</strong> vs konvensional (±82+ HOK).
      Investasi Smart-Kit dapat kembali dalam <strong>1–2 musim tanam</strong>.
    </div>
  </div>

  <!-- KAPABILITAS -->
  <div class="card">
    <h2>🎓 Kapabilitas Tim R&D</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;">
      <div style="background:var(--gp);border-radius:8px;padding:12px;">
        <div style="font-weight:700;color:var(--gd);">💻 R&D & Engineering</div>
        <div style="font-size:.82rem;color:#555;margin-top:4px;">IoT, PCB design, firmware ESP32, sensor calibration</div>
      </div>
      <div style="background:var(--gp);border-radius:8px;padding:12px;">
        <div style="font-weight:700;color:var(--gd);">☁️ Software</div>
        <div style="font-size:.82rem;color:#555;margin-top:4px;">Cloud platform, MQTT broker, mobile/web dashboard</div>
      </div>
      <div style="background:var(--gp);border-radius:8px;padding:12px;">
        <div style="font-weight:700;color:var(--gd);">🌱 Agronomi</div>
        <div style="font-size:.82rem;color:#555;margin-top:4px;">VPD, hidroponik NFT/DFT/Drip, fisiologi tanaman</div>
      </div>
      <div style="background:var(--gp);border-radius:8px;padding:12px;">
        <div style="font-weight:700;color:var(--gd);">📈 Business Development</div>
        <div style="font-size:.82rem;color:#555;margin-top:4px;">B2B agribisnis, partnership SMK Teknik lokal</div>
      </div>
    </div>
  </div>

</div>
""")

# ─────────────────────────────────────────────
# FINANSIAL PAGE
# ─────────────────────────────────────────────

FINANSIAL_HTML = make_page("""
<div class="hero">
  <h1>💰 Proyeksi Keuangan Tahun 1</h1>
  <p>Perencanaan Anggaran · Cash Flow · HPP · CAPEX/OPEX — PT AgriPulse Digital Nusantara</p>
</div>
<div class="container">

  <!-- SUMMARY STATS -->
  <div class="section-title">📊 Ringkasan Keuangan Tahun 1</div>
  <div class="stat-grid">
    <div class="stat-card"><div class="stat-label">Total Pendapatan</div><div class="stat-value" style="font-size:1.2rem;">Rp 1,545 M</div><div class="stat-sub">210 unit · 84 SaaS · 20 Consult</div></div>
    <div class="stat-card rd"><div class="stat-label">Total COGS</div><div class="stat-value" style="font-size:1.2rem;">Rp 819 M</div><div class="stat-sub">Bahan baku + TK produksi</div></div>
    <div class="stat-card g2"><div class="stat-label">Laba Kotor</div><div class="stat-value" style="font-size:1.2rem;">Rp 726 M</div><div class="stat-sub">Gross Margin: 47%</div></div>
    <div class="stat-card or"><div class="stat-label">Laba Bersih</div><div class="stat-value" style="font-size:1.2rem;">Rp 44,3 M</div><div class="stat-sub">NPM ~2.9% · Payback ±27 bln</div></div>
  </div>

  <!-- HPP -->
  <div class="card">
    <h2>🏭 Harga Pokok Produksi (HPP) — per Unit Smart-Kit</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;">
      <div>
        <table class="tbl">
          <thead><tr><th>Elemen</th><th>Perhitungan</th><th style="text-align:right;">Nilai</th></tr></thead>
          <tbody>
            <tr><td>Bahan Baku Langsung</td><td>Per unit</td><td style="text-align:right;">Rp 3.500.000</td></tr>
            <tr><td>Tenaga Kerja Langsung</td><td>Rp 7.000.000 ÷ 20 unit</td><td style="text-align:right;">Rp 350.000</td></tr>
            <tr><td>Overhead Pabrik</td><td>Rp 22.260.000 ÷ 20 unit</td><td style="text-align:right;">Rp 1.113.000</td></tr>
            <tr class="total-row"><td colspan="2"><strong>HPP per Unit</strong></td><td style="text-align:right;"><strong>Rp 4.963.000</strong></td></tr>
          </tbody>
        </table>
      </div>
      <div>
        <table class="tbl">
          <thead><tr><th>Produk</th><th>HPP</th><th>Harga Jual</th><th>Margin</th></tr></thead>
          <tbody>
            <tr><td>AgriPulse Smart-Kit</td><td>Rp 4.963.000</td><td>Rp 6.800.000</td><td><strong>~37%</strong></td></tr>
            <tr><td>Langganan Dashboard</td><td>Rp 200.000/klien</td><td>Rp 2.000.000/thn</td><td><strong>90%</strong></td></tr>
            <tr><td>Jasa Hydro-Consult</td><td>Rp 500.000/sesi</td><td>Rp 2.500.000/sesi</td><td><strong>80%</strong></td></tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- CAPEX -->
  <div class="card">
    <h2>🏗️ Investasi Awal (CAPEX) — Total: Rp 323.000.000</h2>
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;">
      <div>
        <div style="font-weight:700;color:var(--gd);margin-bottom:8px;">Peralatan Produksi & Workshop</div>
        <table class="tbl">
          <tr><td>Workbench & Soldering Station</td><td style="text-align:right;">Rp 8.000.000</td></tr>
          <tr><td>Oscilloscope & Multimeter Digital</td><td style="text-align:right;">Rp 6.000.000</td></tr>
          <tr><td>3D Printer (housing prototype)</td><td style="text-align:right;">Rp 7.000.000</td></tr>
          <tr><td>PCB Assembly Tools</td><td style="text-align:right;">Rp 4.000.000</td></tr>
          <tr><td>Rak Penyimpanan + Laptop/PC (2 unit)</td><td style="text-align:right;">Rp 23.000.000</td></tr>
          <tr class="total-row"><td><strong>Subtotal</strong></td><td style="text-align:right;"><strong>Rp 48.000.000</strong></td></tr>
        </table>
      </div>
      <div>
        <div style="font-weight:700;color:var(--gd);margin-bottom:8px;">Infrastruktur Digital</div>
        <table class="tbl">
          <tr><td>Cloud Server Setup (AWS/GCP)</td><td style="text-align:right;">Rp 5.000.000</td></tr>
          <tr><td>Pengembangan App Android/iOS (MVP)</td><td style="text-align:right;">Rp 90.000.000</td></tr>
          <tr><td>Domain, SSL, Backend Infrastructure</td><td style="text-align:right;">Rp 2.000.000</td></tr>
          <tr class="total-row"><td><strong>Subtotal</strong></td><td style="text-align:right;"><strong>Rp 97.000.000</strong></td></tr>
        </table>
      </div>
      <div>
        <div style="font-weight:700;color:var(--gd);margin-bottom:8px;">Modal Kerja Awal (Buffer 3 Bulan)</div>
        <table class="tbl">
          <tr><td>Stok komponen awal (10 unit × 3 bln)</td><td style="text-align:right;">Rp 105.000.000</td></tr>
          <tr><td>Biaya operasional bulan 1–3</td><td style="text-align:right;">Rp 60.000.000</td></tr>
          <tr class="total-row"><td><strong>Subtotal</strong></td><td style="text-align:right;"><strong>Rp 165.000.000</strong></td></tr>
        </table>
        <div style="margin-top:10px;">
          <div style="font-weight:700;color:var(--gd);margin-bottom:8px;">Legalitas & Setup</div>
          <table class="tbl">
            <tr><td>Pendirian PT + Sertifikasi produk</td><td style="text-align:right;">Rp 13.000.000</td></tr>
          </table>
        </div>
      </div>
    </div>
  </div>

  <!-- OPEX -->
  <div class="card">
    <h2>📅 OPEX per Bulan — Total: Rp 129.260.000/bulan</h2>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
      <div>
        <table class="tbl">
          <thead><tr><th>Overhead</th><th style="text-align:right;">Biaya/Bulan</th></tr></thead>
          <tbody>
            <tr><td>Gaji SDM (5 orang)</td><td style="text-align:right;">Rp 30.000.000</td></tr>
            <tr><td>Sewa Workshop & Kantor</td><td style="text-align:right;">Rp 7.000.000</td></tr>
            <tr><td>Listrik & Internet</td><td style="text-align:right;">Rp 2.500.000</td></tr>
            <tr><td>Cloud Server & App Maintenance</td><td style="text-align:right;">Rp 1.700.000</td></tr>
            <tr><td>Transportasi & Logistik</td><td style="text-align:right;">Rp 2.000.000</td></tr>
            <tr><td>Marketing & Promosi Digital</td><td style="text-align:right;">Rp 8.000.000</td></tr>
            <tr><td>Biaya Tak Terduga (5%)</td><td style="text-align:right;">Rp 1.060.000</td></tr>
            <tr class="total-row"><td><strong>Total Overhead</strong></td><td style="text-align:right;"><strong>Rp 22.260.000</strong></td></tr>
          </tbody>
        </table>
      </div>
      <div>
        <table class="tbl">
          <thead><tr><th>Bahan Baku & Produksi</th><th style="text-align:right;">Nilai</th></tr></thead>
          <tbody>
            <tr><td>Bahan baku 20 unit/bulan × Rp 3.500.000</td><td style="text-align:right;">Rp 70.000.000</td></tr>
            <tr><td>TK Produksi Langsung</td><td style="text-align:right;">Rp 7.000.000</td></tr>
            <tr class="total-row"><td><strong>Total Produksi</strong></td><td style="text-align:right;"><strong>Rp 77.000.000</strong></td></tr>
          </tbody>
        </table>
        <div class="info-box" style="margin-top:12px;margin-bottom:0;">
          💡 OPEX/Tahun: <strong>Rp 1.551.120.000</strong><br>
          Bulan 9–12 OPEX naik menjadi Rp 150.260.000 (tambah 1 teknisi + produksi 25 unit/bln)
        </div>
      </div>
    </div>
  </div>

  <!-- PERIODE PRODUKSI -->
  <div class="card">
    <h2>📆 Periode Produksi — Target Total 210 Unit Tahun 1</h2>
    <div class="tl-grid">
      <div class="tl-item"><div class="tl-fase">Setup & Trial</div><div class="tl-period">Bulan 1–2</div><div class="tl-unit">0 unit</div><div class="tl-desc">Assembly tools, QC awal, soft launch</div></div>
      <div class="tl-item"><div class="tl-fase">Pilot & Akuisisi</div><div class="tl-period">Bulan 3–4</div><div class="tl-unit">5 unit/bulan</div><div class="tl-desc">Demo ke klien perdana, perbaikan produk</div></div>
      <div class="tl-item"><div class="tl-fase">Produksi Awal</div><div class="tl-period">Bulan 5–8</div><div class="tl-unit">15 unit/bulan</div><div class="tl-desc">Klien aktif bertambah, SaaS mulai berjalan</div></div>
      <div class="tl-item"><div class="tl-fase">Scaling</div><div class="tl-period">Bulan 9–12</div><div class="tl-unit">25 unit/bulan</div><div class="tl-desc">Ekspansi ke kota target ke-2</div></div>
    </div>
  </div>

  <!-- CASH FLOW TABLE -->
  <div class="card">
    <h2>📈 Cash Flow Proyeksi Tahun 1</h2>
    <div style="overflow-x:auto;">
      <table class="tbl">
        <thead>
          <tr>
            <th>Bln</th><th>Unit</th>
            <th style="text-align:right;">Pendapatan Kit</th>
            <th style="text-align:right;">SaaS</th>
            <th style="text-align:right;">Hydro-Consult</th>
            <th style="text-align:right;">Total In</th>
            <th style="text-align:right;">OPEX</th>
            <th style="text-align:right;">Net Cash Flow</th>
            <th style="text-align:right;">Kumulatif</th>
          </tr>
        </thead>
        <tbody>
          {% for cf in cashflow %}
          <tr class="{{ 'cf-hl' if cf.net >= 0 }}">
            <td><strong>{{ cf.bulan }}</strong></td>
            <td>{{ cf.unit }}</td>
            <td style="text-align:right;">{{ cf.kit | int | format_rp if cf.kit > 0 else '—' }}</td>
            <td style="text-align:right;">{{ cf.saas | int | format_rp if cf.saas > 0 else '—' }}</td>
            <td style="text-align:right;">{{ cf.consult | int | format_rp if cf.consult > 0 else '—' }}</td>
            <td style="text-align:right;">{{ cf.total_in | int | format_rp if cf.total_in > 0 else '—' }}</td>
            <td style="text-align:right;">{{ cf.opex | int | format_rp }}</td>
            <td style="text-align:right;" class="{{ 'cf-pos' if cf.net >= 0 else 'cf-neg' }}">
              {{ ('+' if cf.net >= 0 else '') }}{{ cf.net | int | format_rp }}
            </td>
            <td style="text-align:right;" class="{{ 'cf-pos' if cf.kumulatif >= 0 else 'cf-neg' }}">
              {{ cf.kumulatif | int | format_rp }}
            </td>
          </tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
    <div class="alert-box" style="margin-top:14px;margin-bottom:0;">
      ✅ <strong>Cash flow positif mulai bulan ke-8.</strong>
      Perusahaan sudah mampu membiayai dirinya sendiri tanpa suntikan modal tambahan.
      Saldo kumulatif masih negatif karena CAPEX Rp 323 juta belum diperhitungkan di tabel ini.
    </div>
  </div>

  <!-- PENYUSUTAN -->
  <div class="card">
    <h2>📉 Penyusutan Aset Tetap (Metode Garis Lurus)</h2>
    <table class="tbl">
      <thead><tr><th>Aset</th><th style="text-align:right;">Nilai</th><th>Umur Ekonomis</th><th style="text-align:right;">Penyusutan/Tahun</th><th style="text-align:right;">Penyusutan/Bulan</th></tr></thead>
      <tbody>
        <tr><td>Peralatan Produksi</td><td style="text-align:right;">Rp 48.000.000</td><td>5 tahun</td><td style="text-align:right;">Rp 9.600.000</td><td style="text-align:right;">Rp 800.000</td></tr>
        <tr><td>Laptop/PC</td><td style="text-align:right;">Rp 20.000.000</td><td>4 tahun</td><td style="text-align:right;">Rp 5.000.000</td><td style="text-align:right;">Rp 416.667</td></tr>
        <tr><td>Infrastruktur Digital</td><td style="text-align:right;">Rp 97.000.000</td><td>3 tahun</td><td style="text-align:right;">Rp 32.333.333</td><td style="text-align:right;">Rp 2.694.444</td></tr>
        <tr class="total-row"><td colspan="3"><strong>Total</strong></td><td style="text-align:right;"><strong>Rp 46.933.333/thn</strong></td><td style="text-align:right;"><strong>Rp 3.911.111/bln</strong></td></tr>
      </tbody>
    </table>
  </div>

</div>
""")

# ─────────────────────────────────────────────
# PRODUK PAGE
# ─────────────────────────────────────────────

PRODUK_HTML = make_page("""
<div class="hero">
  <h1>🛒 Produk & Layanan AgriPulse Tech</h1>
  <p>Tiga pilar bisnis: IoT Hardware · SaaS · Konsultasi</p>
</div>
<div class="container">
  {% if pesan %}
  <div class="alert-box">✅ {{ pesan }}</div>
  {% endif %}

  <div class="produk-grid">
    {% for pid, p in produk.items() %}
    <div class="produk-card">
      {% if p.badge %}<div class="produk-badge">{{ p.badge }}</div>{% endif %}
      <div class="produk-emoji">{{ p.emoji }}</div>
      <div class="produk-nama">{{ p.nama }}</div>
      <div class="produk-harga">
        Rp {{ "{:,}".format(p.harga).replace(",",".") }}
        <small style="font-size:.8rem;color:#999;font-weight:400;">{{ p.satuan }}</small>
      </div>
      <div class="produk-desc">{{ p.deskripsi }}</div>
      <ul class="produk-isi">
        {% for item in p.isi %}
        <li>{{ item }}</li>
        {% endfor %}
      </ul>
      <div class="hpp-info">HPP: Rp {{ "{:,}".format(p.hpp).replace(",",".") }} &nbsp;|&nbsp; BOM Kit: Rp 3.500.000</div>
      <form method="POST" action="/add-to-cart">
        <input type="hidden" name="produk_id" value="{{ pid }}">
        <div style="display:flex;gap:8px;align-items:center;margin-bottom:8px;">
          <label style="font-size:.85rem;">Qty:</label>
          <input type="number" name="qty" value="1" min="1" max="10"
                 style="width:60px;padding:6px;border:2px solid #ddd;border-radius:6px;">
        </div>
        <button type="submit" class="btn btn-green w100">🛒 Tambah ke Keranjang</button>
      </form>
    </div>
    {% endfor %}
  </div>

  <div class="info-box">
    * SaaS Dashboard <strong>GRATIS tahun pertama</strong> untuk setiap pembelian AgriPulse Smart-Kit.
    Mulai tahun ke-2: Rp 2.000.000/tahun.
    &nbsp;·&nbsp; Harga Hydro-Consult per kunjungan on-site.
  </div>
</div>
""")

# ─────────────────────────────────────────────
# CART PAGE
# ─────────────────────────────────────────────

CART_HTML = make_page("""
<div class="hero">
  <h1>🛍️ Keranjang Belanja</h1>
  <p>Review pesanan Anda sebelum checkout</p>
</div>
<div class="container">
  {% if not cart %}
  <div class="card" style="text-align:center;padding:48px;">
    <div style="font-size:3rem;">🛒</div>
    <p style="color:#888;margin:16px 0;">Keranjang masih kosong</p>
    <a href="/produk" class="btn btn-green" style="display:inline-block;width:auto;">Lihat Produk</a>
  </div>
  {% else %}
  <div class="card">
    <h2>📋 Rincian Pesanan</h2>
    <div style="overflow-x:auto;">
      <table class="tbl">
        <thead>
          <tr><th>Produk</th><th style="text-align:right;">Harga Satuan</th><th>Qty</th><th style="text-align:right;">Subtotal</th><th>Aksi</th></tr>
        </thead>
        <tbody>
          {% for pid, item in cart.items() %}
          <tr>
            <td><strong>{{ item.emoji }} {{ item.nama }}</strong></td>
            <td style="text-align:right;">Rp {{ "{:,}".format(item.harga).replace(",",".") }}</td>
            <td>
              <div class="qty-ctrl">
                <a href="/cart-qty/{{ pid }}/kurang">−</a>
                <strong>{{ item.qty }}</strong>
                <a href="/cart-qty/{{ pid }}/tambah">+</a>
              </div>
            </td>
            <td style="text-align:right;"><strong>Rp {{ "{:,}".format(item.harga * item.qty).replace(",",".") }}</strong></td>
            <td><a href="/remove-from-cart/{{ pid }}" class="btn btn-red" style="padding:4px 10px;font-size:.8rem;">Hapus</a></td>
          </tr>
          {% endfor %}
          <tr class="total-row">
            <td colspan="3" style="text-align:right;">TOTAL PEMBAYARAN</td>
            <td style="text-align:right;">Rp {{ "{:,}".format(total).replace(",",".") }}</td>
            <td></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>

  <div class="card">
    <h2>📝 Data Pemesan</h2>
    <form method="POST" action="/checkout">
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;">
        <div class="form-group">
          <label>Nama Lengkap *</label>
          <input type="text" name="nama" required placeholder="Budi Santoso">
        </div>
        <div class="form-group">
          <label>No. HP / WhatsApp *</label>
          <input type="text" name="hp" required placeholder="08xxxxxxxxxx">
        </div>
        <div class="form-group">
          <label>Email *</label>
          <input type="email" name="email" required placeholder="budi@email.com">
        </div>
        <div class="form-group">
          <label>Nama Perusahaan / Kebun</label>
          <input type="text" name="perusahaan" placeholder="Opsional">
        </div>
      </div>
      <div class="form-group">
        <label>Alamat Pengiriman *</label>
        <textarea name="alamat" rows="2" required placeholder="Jl. Raya Berastagi No. 12, Karo, Sumatera Utara"></textarea>
      </div>
      <div class="form-group">
        <label>Metode Pembayaran</label>
        <select name="pembayaran">
          <option value="transfer">Transfer Bank (BCA / BRI / Mandiri)</option>
          <option value="dp">DP 50% — Pelunasan saat pengiriman</option>
          <option value="qris">QRIS</option>
        </select>
      </div>
      <button type="submit" class="btn btn-dark w100" style="padding:14px;font-size:1rem;">
        ✅ Konfirmasi Pesanan & Buat Invoice
      </button>
    </form>
  </div>
  {% endif %}
</div>
""")

# ─────────────────────────────────────────────
# INVOICE PAGE
# ─────────────────────────────────────────────

INVOICE_HTML = make_page("""
<div class="container" style="padding-top:36px;">
  <div class="invoice-box">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:22px;flex-wrap:wrap;gap:12px;">
      <div>
        <div class="invoice-title">🌿 INVOICE</div>
        <div style="color:var(--gm);font-weight:600;margin-top:2px;">PT AgriPulse Digital Nusantara</div>
        <div style="font-size:.83rem;color:#888;">Kawasan Agribisnis Berastagi, Karo, Sumatera Utara</div>
        <div style="font-size:.83rem;color:#888;">agripulse@tech.id · WA: 0812-AGRI-PULSE</div>
      </div>
      <div style="text-align:right;font-size:.88rem;color:#666;">
        <div><strong>No. Invoice:</strong> {{ invoice.nomor }}</div>
        <div><strong>Tanggal:</strong> {{ invoice.tanggal }}</div>
        <div style="margin-top:6px;"><span class="badge-lunas">✓ DITERIMA</span></div>
      </div>
    </div>

    <div style="background:var(--gp);border-radius:8px;padding:13px;margin-bottom:18px;font-size:.88rem;">
      <strong>Kepada Yth:</strong><br>
      {{ invoice.nama }}<br>
      {% if invoice.perusahaan %}<em>{{ invoice.perusahaan }}</em><br>{% endif %}
      {{ invoice.hp }} &nbsp;|&nbsp; {{ invoice.email }}<br>
      {{ invoice.alamat }}
    </div>

    <table style="width:100%;border-collapse:collapse;margin-bottom:16px;font-size:.87rem;">
      <thead>
        <tr style="background:var(--gp);">
          <th style="padding:8px 12px;color:var(--gd);text-align:left;">Produk / Layanan</th>
          <th style="padding:8px 12px;color:var(--gd);text-align:right;">Harga Satuan</th>
          <th style="padding:8px 12px;color:var(--gd);text-align:center;">Qty</th>
          <th style="padding:8px 12px;color:var(--gd);text-align:right;">Subtotal</th>
        </tr>
      </thead>
      <tbody>
        {% for item in invoice.items %}
        <tr style="border-bottom:1px solid #f0f0f0;">
          <td style="padding:9px 12px;">{{ item.nama }}</td>
          <td style="padding:9px 12px;text-align:right;">Rp {{ "{:,}".format(item.harga).replace(",",".") }}</td>
          <td style="padding:9px 12px;text-align:center;">{{ item.qty }}</td>
          <td style="padding:9px 12px;text-align:right;">Rp {{ "{:,}".format(item.subtotal).replace(",",".") }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <div style="text-align:right;font-size:1.15rem;font-weight:700;color:var(--gd);margin-bottom:14px;">
      Total: Rp {{ "{:,}".format(invoice.total).replace(",",".") }}
    </div>

    <div style="background:#fff8e1;border-radius:8px;padding:12px;font-size:.87rem;margin-bottom:16px;">
      <strong>Metode Pembayaran:</strong> {{ invoice.pembayaran_label }}<br>
      {% if invoice.dp > 0 %}
      💳 DP yang harus dibayar sekarang: <strong>Rp {{ "{:,}".format(invoice.dp).replace(",",".") }}</strong><br>
      💳 Pelunasan saat pengiriman: <strong>Rp {{ "{:,}".format(invoice.pelunasan).replace(",",".") }}</strong>
      {% endif %}
    </div>

    <div style="margin-top:16px;padding-top:14px;border-top:1px dashed #ccc;font-size:.82rem;color:#888;text-align:center;">
      Pesanan diproses dalam 1–2 hari kerja. Pengiriman ke Berastagi, Karo & seluruh Sumatera Utara.<br>
      <em>Terima kasih telah mempercayakan greenhouse Anda kepada AgriPulse Tech!</em><br>
      <strong style="color:var(--gd);">"Revolutionizing Agriculture with Precision Data"</strong>
    </div>
  </div>

  <div style="text-align:center;margin-top:22px;">
    <a href="/" class="btn btn-green" style="display:inline-block;width:auto;margin-right:8px;">📊 Kembali ke Dashboard</a>
    <a href="/produk" class="btn btn-outline" style="display:inline-block;width:auto;">🛒 Pesan Lagi</a>
  </div>
</div>
""")

# ─────────────────────────────────────────────
# TEMPLATE FILTER
# ─────────────────────────────────────────────

@app.template_filter("format_rp")
def format_rp_filter(value):
    return "Rp {:,}".format(int(value)).replace(",", ".")

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@app.route("/")
def dashboard():
    komoditas_key = request.args.get("komoditas", "selada")
    if komoditas_key not in KOMODITAS:
        komoditas_key = "selada"
    threshold = get_threshold(komoditas_key)
    sensor = baca_sensor()
    aksi, alerts = analisis_otomatis(sensor, threshold)
    statuses = {k: status_sensor(sensor[k], k, threshold) for k in threshold}
    vpd = hitung_vpd(sensor["suhu"], sensor["kelembaban"])
    vpd_label, _ = vpd_status(vpd)
    history = list(sensor_history)
    return render_template_string(DASHBOARD_HTML,
        title="Dashboard",
        active="dashboard",
        sensor=sensor,
        aksi=aksi,
        alerts=alerts,
        statuses=statuses,
        threshold=threshold,
        komoditas_key=komoditas_key,
        komoditas_list=KOMODITAS,
        komoditas_info=KOMODITAS[komoditas_key],
        vpd=vpd,
        vpd_label=vpd_label,
        history=history,
        history_json=json.dumps(history),
        cart_count=cart_count(),
    )

@app.route("/tentang")
def tentang():
    return render_template_string(TENTANG_HTML,
        title="Tentang Kami", active="tentang", cart_count=cart_count())

@app.route("/teknologi")
def teknologi():
    return render_template_string(TEKNOLOGI_HTML,
        title="Teknologi", active="teknologi",
        bom=BOM,
        komoditas_list=KOMODITAS,
        cart_count=cart_count())

@app.route("/tim")
def tim():
    return render_template_string(TIM_HTML,
        title="Tim Kami", active="tim", tim=TIM, cart_count=cart_count())

@app.route("/finansial")
def finansial():
    return render_template_string(FINANSIAL_HTML,
        title="Finansial", active="finansial",
        cashflow=CASHFLOW,
        cart_count=cart_count())

@app.route("/produk")
def produk():
    pesan = request.args.get("pesan", "")
    return render_template_string(PRODUK_HTML,
        title="Produk", active="produk",
        produk=PRODUK, pesan=pesan, cart_count=cart_count())

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    pid = request.form.get("produk_id")
    qty = int(request.form.get("qty", 1))
    if pid not in PRODUK:
        return redirect(url_for("produk"))
    cart = get_cart()
    if pid in cart:
        cart[pid]["qty"] += qty
    else:
        p = PRODUK[pid]
        cart[pid] = {"nama": p["nama"], "harga": p["harga"], "qty": qty, "emoji": p["emoji"]}
    save_cart(cart)
    return redirect(url_for("produk", pesan=f"{PRODUK[pid]['nama']} ditambahkan ke keranjang!"))

@app.route("/remove-from-cart/<pid>")
def remove_from_cart(pid):
    cart = get_cart()
    cart.pop(pid, None)
    save_cart(cart)
    return redirect(url_for("cart"))

@app.route("/cart-qty/<pid>/<aksi>")
def cart_qty(pid, aksi):
    cart = get_cart()
    if pid in cart:
        if aksi == "tambah":
            cart[pid]["qty"] += 1
        elif aksi == "kurang":
            cart[pid]["qty"] = max(1, cart[pid]["qty"] - 1)
    save_cart(cart)
    return redirect(url_for("cart"))

@app.route("/cart")
def cart():
    c = get_cart()
    total = sum(v["harga"] * v["qty"] for v in c.values())
    return render_template_string(CART_HTML,
        title="Keranjang", active="cart",
        cart=c, total=total, cart_count=cart_count())

@app.route("/checkout", methods=["POST"])
def checkout():
    cart = get_cart()
    if not cart:
        return redirect(url_for("cart"))
    total = sum(v["harga"] * v["qty"] for v in cart.values())
    pembayaran = request.form.get("pembayaran", "transfer")
    label_map = {
        "transfer": "Transfer Bank (BCA / BRI / Mandiri)",
        "dp": "DP 50% + Pelunasan saat pengiriman",
        "qris": "QRIS",
    }
    dp = total // 2 if pembayaran == "dp" else 0
    invoice = {
        "nomor": f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "tanggal": datetime.now().strftime("%d %B %Y, %H:%M"),
        "nama": request.form.get("nama"),
        "hp": request.form.get("hp"),
        "email": request.form.get("email"),
        "perusahaan": request.form.get("perusahaan"),
        "alamat": request.form.get("alamat"),
        "items": [
            {"nama": v["nama"], "harga": v["harga"], "qty": v["qty"], "subtotal": v["harga"] * v["qty"]}
            for v in cart.values()
        ],
        "total": total,
        "pembayaran_label": label_map.get(pembayaran, pembayaran),
        "dp": dp,
        "pelunasan": total - dp,
    }
    save_cart({})
    return render_template_string(INVOICE_HTML,
        title="Invoice", active="", invoice=invoice, cart_count=0)

# ─── API ENDPOINTS (ESP32 / MQTT integration) ─────────────────────

@app.route("/api/sensor")
def api_sensor():
    """GET endpoint: simulasi data sensor + analisis threshold per komoditas."""
    komoditas_key = request.args.get("komoditas", "selada")
    if komoditas_key not in KOMODITAS:
        komoditas_key = "selada"
    threshold = get_threshold(komoditas_key)
    sensor = baca_sensor()
    aksi, alerts = analisis_otomatis(sensor, threshold)
    statuses = {k: status_sensor(sensor[k], k, threshold) for k in threshold}
    vpd = hitung_vpd(sensor["suhu"], sensor["kelembaban"])
    vpd_label, _ = vpd_status(vpd)
    return jsonify({
        "status": "ok",
        "komoditas": komoditas_key,
        "komoditas_nama": KOMODITAS[komoditas_key]["nama"],
        "sensor": sensor,
        "statuses": statuses,
        "aksi": aksi,
        "alerts": alerts,
        "threshold": threshold,
        "vpd": vpd,
        "vpd_label": vpd_label,
        "history_count": len(sensor_history),
    })

@app.route("/api/sensor/post", methods=["POST"])
def api_sensor_post():
    """
    POST endpoint: terima data real dari ESP32 DevKit V1.
    ESP32 kirim JSON: {"suhu":28.5,"kelembaban":72,"co2":650,"ec":1.8,"ph":6.1,"komoditas":"selada"}
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No JSON data"}), 400
    komoditas_key = data.get("komoditas", "selada")
    threshold = get_threshold(komoditas_key)
    aksi, alerts = analisis_otomatis(data, threshold)
    data["timestamp"] = datetime.now().strftime("%H:%M:%S")
    sensor_history.append(data)
    vpd = hitung_vpd(data.get("suhu", 25), data.get("kelembaban", 70))
    return jsonify({
        "status": "ok",
        "aksi": aksi,
        "alerts": alerts,
        "vpd": vpd,
        "vpd_label": vpd_status(vpd)[0],
    })

@app.route("/api/history")
def api_history():
    """GET endpoint: riwayat sensor 20 data terakhir."""
    return jsonify({"status": "ok", "count": len(sensor_history), "data": list(sensor_history)})

# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 65)
    print("  🌿 PT AgriPulse Digital Nusantara")
    print("  'Revolutionizing Agriculture with Precision Data'")
    print("  Kelompok 2 — Agri-Tech IoT Greenhouse System")
    print("=" * 65)
    print()
    print("  ✅ Server berjalan di: http://localhost:5000")
    print()
    print("  Halaman:")
    print("    /           → Dashboard monitoring real-time")
    print("    /tentang    → Tentang Kami, Visi & Misi, Core Values")
    print("    /teknologi  → Arsitektur sistem, BOM, spesifikasi")
    print("    /tim        → Struktur bisnis & Meet Our Team")
    print("    /produk     → Katalog produk & pemesanan")
    print("    /finansial  → Proyeksi keuangan & cash flow")
    print("    /cart       → Keranjang belanja")
    print()
    print("  API:")
    print("    GET  /api/sensor?komoditas=selada  → data sensor + analisis")
    print("    POST /api/sensor/post              → terima data dari ESP32")
    print("    GET  /api/history                  → riwayat 20 pembacaan")
    print("=" * 65)
    app.run(debug=True, port=5000)
