# AgriPulse

**PT AgriPulse Digital Nusantara** — Smart Greenhouse Management System.

Tagline: *"Revolutionizing Agriculture with Precision Data"*

AgriPulse adalah aplikasi web **Flask single-file** yang menggabungkan situs profil perusahaan/e-commerce dengan dashboard monitoring IoT greenhouse secara real-time (simulasi). Proyek ini dibuat untuk tugas kelompok (Kelompok 2) bertema agri-tech startup yang menjual paket hardware IoT ("Smart-Kit") + layanan SaaS dashboard untuk memantau dan mengendalikan kondisi greenhouse hortikultura secara otomatis.

## Fitur Utama

- **Dashboard monitoring real-time** (`/`) — kartu sensor (suhu, kelembaban, CO₂, EC, pH), perhitungan VPD (Vapor Pressure Deficit), grafik, dan rekomendasi aksi otomatis berdasarkan threshold agronomi per komoditas.
- **Multi-komoditas** — threshold "Gold Standard" untuk 4 jenis tanaman: selada, tomat, melon, dan paprika (suhu, kelembaban, CO₂, EC, pH masing-masing).
- **Autentikasi pengguna** — register, login, logout dengan `werkzeug.security` (password hashing), session-based, beserta decorator `@login_required` dan `@admin_required`.
- **Manajemen multi-greenhouse** — setiap user dapat menambah, melihat, dan menghapus greenhouse miliknya, masing-masing dengan API key unik untuk integrasi perangkat.
- **Simulasi & integrasi sensor IoT (ESP32)**:
  - `GET /api/sensor` — data sensor simulasi + hasil analisis otomatis (kompatibel ESP32).
  - `POST /api/sensor/post` — endpoint untuk menerima payload JSON dari perangkat ESP32 sungguhan.
  - `GET /api/history` — riwayat 20 pembacaan sensor terakhir.
- **Sistem alert** — pencatatan alert otomatis ke database ketika kondisi keluar dari threshold, halaman `/alerts` untuk melihat & resolve alert, badge jumlah alert di navbar.
- **Export CSV** — unduh riwayat data sensor per greenhouse (`/export/csv/<gh_id>`).
- **Admin panel** (`/admin`) — khusus role admin.
- **Company profile & e-commerce**:
  - `/tentang` — profil perusahaan, visi & misi, core values.
  - `/teknologi` — arsitektur sistem, Bill of Materials (BOM), spesifikasi teknis.
  - `/tim` — struktur tim & organisasi.
  - `/produk` — katalog produk (Smart-Kit, SaaS Dashboard, Hydro-Consult) dengan form tambah ke keranjang.
  - `/finansial` — proyeksi keuangan: CAPEX, OPEX, HPP, cash flow tahun pertama, depresiasi.
- **Keranjang belanja & checkout** — cart berbasis session, checkout menghasilkan invoice.
- **Database SQLite** (`agripulse.db`, dibuat otomatis saat aplikasi pertama kali dijalankan) dengan tabel: `users`, `greenhouses`, `sensor_readings`, `alerts`, `orders`.

## Tech Stack

- **Backend**: Python 3, Flask
- **Database**: SQLite3 (bawaan Python, tanpa server DB terpisah)
- **Autentikasi**: Werkzeug Security (`generate_password_hash` / `check_password_hash`)
- **Frontend**: HTML/CSS inline (di-render dengan `render_template_string`, tanpa folder `templates/` atau `static/` terpisah — semua ada dalam satu file Python)
- **Pola arsitektur**: single-file application (`KONTOL.py`) — konstanta data domain, helper functions, string HTML per halaman, lalu route Flask di bagian bawah file

## Instalasi & Menjalankan

1. Pastikan Python 3 sudah terpasang.
2. Install dependency:
   ```bash
   pip install flask werkzeug
   ```
3. Jalankan aplikasi:
   ```bash
   python KONTOL.py
   ```
4. Buka browser ke:
   ```
   http://localhost:5000
   ```

Database SQLite (`agripulse.db`) beserta akun admin default akan dibuat otomatis saat aplikasi pertama kali dijalankan (tabel dan seed admin dibuat lewat fungsi `init_db()`).

## Konfigurasi

Aplikasi ini saat ini tidak memerlukan environment variable eksternal (tidak ada pemanggilan API pihak ketiga). Beberapa hal yang perlu diperhatikan bila akan di-deploy:

- `app.secret_key` — Flask session secret key, saat ini di-hardcode di source code untuk keperluan development/simulasi. Untuk deployment produksi, sebaiknya dipindahkan ke environment variable, misalnya `SECRET_KEY=YOUR_SECRET_KEY_HERE`.
- `DB_PATH` — lokasi file SQLite (default: `agripulse.db`, relatif terhadap direktori kerja).
- Akun admin default dibuat otomatis (`admin` / `admin123`) — sebaiknya diganti setelah instalasi pertama.

File `.gitignore` pada repo ini sudah menyiapkan pengecualian untuk file sensitif seperti `.env`, `*.key`, `*.pem`, `credentials.json`, serta file database lokal (`*.db`, `*.sqlite`).

## Struktur Folder

```
agripulse/
├── KONTOL.py           # Aplikasi utama (Flask, semua route, HTML, logika bisnis)
├── KONTOL - Copy.py     # Versi cadangan/lama dari KONTOL.py (belum ada fitur auth, DB, dsb.)
├── LICENSE              # Lisensi MIT
├── .gitignore
└── CLAUDE.md            # Catatan panduan arsitektur untuk pengembangan lanjutan
```

## Integrasi ESP32 (contoh payload)

```
POST /api/sensor/post
Content-Type: application/json

{"suhu": 28.5, "kelembaban": 72, "co2": 650, "ec": 1.8, "ph": 6.1, "komoditas": "selada"}
```

Endpoint akan mengembalikan hasil analisis otomatis (aksi & alert) berdasarkan threshold komoditas yang dipilih.

## Lisensi

MIT License — lihat file [LICENSE](LICENSE).
