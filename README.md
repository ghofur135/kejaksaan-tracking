# E-Kejaksaan Case Tracking System

Aplikasi web berbasis Python Flask untuk memantau dan melacak perkembangan perkara tindak pidana di lingkungan kejaksaan. Aplikasi ini dirancang untuk memudahkan administrasi data perkara mulai dari tahap SPDP hingga pelimpahan ke Pengadilan Negeri.

## 🚀 Fitur Utama

- **Manajemen Data Perkara**: Input data tersangka, pasal, dan nomor SPDP dengan mudah.
- **Pelacakan Tahapan (Tracking)**: Memantau progres perkara melalui berbagai tahapan:
  - SPDP
  - Berkas Tahap I
  - P-18 / P-19
  - P-21
  - Tahap II
  - Limpah PN
- **Sistem Peringatan Dini (Early Warning System)**: Indikator visual berwarna **merah** otomatis muncul jika tahapan perkara melebihi batas waktu yang ditentukan (SOP), membantu jaksa memprioritaskan penyelesaian berkas.
- **Edit Data Interaktif**: 
  - Edit tanggal tahapan langsung dari tabel menggunakan **Modal Date Picker**.
  - Edit keterangan secara langsung (inline editing).
  - Penyimpanan otomatis ke database.
- **Login Aman**: Sistem autentikasi pengguna (default admin).
- **Desain Modern**: Antarmuka responsif dengan mode gelap/terang (gradient), tabel sticky header, dan animasi halus.

## 🛠️ Teknologi yang Digunakan

- **Backend**: Python, Flask, Flask-SQLAlchemy, Flask-Login
- **Database**: SQLite
- **Frontend**: HTML5, CSS3 (Custom Modern UI), JavaScript (Vanilla)
- **Library Tambahan**: `python-dateutil` (parsing tanggal), `openpyxl` (opsional untuk data excel)

## 📦 Cara Install dan Menjalankan

1. **Clone Repository**
   ```bash
   git clone git@github.com:ghofur135/kejaksaan-tracking.git
   cd kejaksaan-tracking
   ```

2. **Buat Virtual Environment (Opsional tapi direkomendasikan)**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Jalankan Aplikasi**
   ```bash
   python app.py
   ```

5. **Akses di Browser**
   Buka `http://127.0.0.1:5000` di browser Anda.

## 🔑 Akun Default

Ketika aplikasi pertama kali dijalankan, akun admin akan dibuat otomatis:
- **Username**: `admin`
- **Password**: `12345`

## 📋 Batas Waktu (SOP) Alert

Sistem akan memberikan tanda merah (!) jika:
- **SPDP**: > 25 hari
- **Berkas Tahap I**: > 6 hari
- **P-18 / P-19**: > 10 hari
- **P-21**: > 12 hari
- **Tahap II**: > 7 hari

## 📝 Catatan Pengembang

- Pastikan format tanggal input konsisten (sistem mendukung format `YYYY-MM-DD` dan `DD-MM-YYYY`).
- Database menggunakan Supabase (PostgreSQL cloud) untuk sinkronisasi multi-device.
- File `.env` diperlukan untuk konfigurasi database (lihat `.env.example`).

## 💻 Desktop App (.exe)

Aplikasi ini bisa di-build menjadi **desktop app standalone** yang tidak perlu browser!

### Quick Start Build:
```bash
# 1. Install dependencies
pip install pyinstaller pywebview

# 2. Build .exe
python build_exe.py

# 3. Hasil ada di dist/E-Kejaksaan.exe
```

### Fitur Desktop App:
- ✅ Tidak perlu install Python
- ✅ Tidak perlu buka browser
- ✅ Tampilan seperti aplikasi native
- ✅ Credentials sudah embedded
- ✅ Tetap pakai Supabase (butuh internet)

### Dokumentasi Build:
- 📚 **Index Dokumentasi**: `docs/INDEX.md` (lihat semua dokumentasi)
- 📖 **Quick Start**: `docs/BUILD_README.md`
- 📖 **Lengkap**: `docs/build-exe.md`
- 📖 **Cheatsheet**: `docs/BUILD_CHEATSHEET.md`
- 📝 **Bahasa Indonesia**: `docs/CARA_BUILD_EXE.txt`
- 🏗️ **Arsitektur**: `docs/ARCHITECTURE.md`

### Test Setup:
```bash
python test_build_setup.py
```
