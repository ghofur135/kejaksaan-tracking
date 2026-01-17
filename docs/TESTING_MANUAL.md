# 🧪 Manual Testing Guide - Overdue Logic

## 📋 Skenario Testing Manual

### Skenario User:
1. **Tanggal komputer**: 13 Januari 2026
2. **Input SPDP**: 20 Januari 2026
3. **Ubah tanggal komputer**: 14 Februari 2026
4. **Hasil**: SPDP harus jadi **🔴 MERAH**

### Perhitungan:
- **Input SPDP**: 20 Januari 2026
- **Batas waktu**: 25 hari kalender
- **Deadline**: 20 Jan + 24 hari = **13 Februari 2026**
- **Mulai MERAH**: 14 Februari 2026
- **Status pada 14 Feb 2026**: 🔴 **MERAH** (terlambat 1 hari)

## 🔧 Cara Testing Manual

### Step 1: Setup Awal
```bash
# Set tanggal komputer ke 13 Jan 2026
# Windows: Settings > Time & Language > Date & Time
# Linux: sudo date -s "2026-01-13"
```

### Step 2: Input Data
1. Jalankan aplikasi: `python app.py`
2. Login dengan admin/12345
3. Input data perkara baru:
   - Nama Tersangka: Test User
   - Pasal: Test Pasal
   - **Tgl Terima (Kejaksaan)**: 20 Januari 2026

### Step 3: Verifikasi Normal
- Refresh dashboard
- SPDP harus berwarna **✅ Normal** (tidak merah)

### Step 4: Ubah Tanggal Sistem
```bash
# Set tanggal komputer ke 14 Feb 2026
# Windows: Settings > Time & Language > Date & Time  
# Linux: sudo date -s "2026-02-14"
```

### Step 5: Verifikasi Overdue
1. Refresh halaman dashboard
2. SPDP harus berubah jadi **🔴 MERAH**
3. Background cell akan memiliki class `overdue-cell`

## 💡 Mengapa TIDAK Perlu Cron/Worker?

### ✅ Real-Time Processing
- Setiap page load, template memanggil `{{ case.spdp_tgl_terima | check_overdue('spdp') }}`
- Filter `check_overdue()` menggunakan `datetime.now()` 
- Membandingkan dengan deadline secara real-time
- Return `'overdue-cell'` jika overdue, `''` jika normal

### ✅ Keuntungan Pendekatan Ini:
1. **Sederhana**: Tidak perlu background job
2. **Real-time**: Langsung update saat page refresh
3. **Akurat**: Selalu menggunakan tanggal sistem terkini
4. **Ringan**: Tidak ada overhead cron job

### ✅ Kapan Warna Berubah:
- **Otomatis** saat user refresh halaman
- **Otomatis** saat user buka dashboard
- **Otomatis** saat tanggal sistem berubah (misal lewat tengah malam)

## 🎯 Testing Scenarios Lainnya

### Test 1: Berbagai Kolom
```
Input Berkas Tahap I: 1 Feb 2026 (6 hari)
Deadline: 6 Feb 2026
Test tanggal: 7 Feb 2026 → 🔴 MERAH
```

### Test 2: Edge Case
```
Input P-21: 10 Feb 2026 (12 hari)  
Deadline: 21 Feb 2026
Test tanggal: 21 Feb 2026 → ✅ Normal
Test tanggal: 22 Feb 2026 → 🔴 MERAH
```

### Test 3: Multiple Cases
- Input beberapa perkara dengan tanggal berbeda
- Ubah tanggal sistem
- Verifikasi masing-masing case sesuai deadline-nya

## 🚀 Kesimpulan

**TIDAK PERLU** cron job atau background worker karena:
- Logic overdue berjalan **real-time** setiap page load
- Menggunakan `datetime.now()` untuk akurasi terkini  
- Performa tetap baik karena perhitungan sederhana
- User experience lebih responsif

**Testing manual sangat mudah** dengan mengubah tanggal sistem komputer!