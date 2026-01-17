# Changelog - Fitur Kategori Umur

## Tanggal: 17 Januari 2026

### Perubahan Utama

#### 1. Label Field SPDP
- ✅ "Tanggal Pemberitahuan Penyidikan" → "Tanggal SPDP"
- ✅ "Nomor" → "Nomor SPDP"

#### 2. Dropdown Kategori Umur
- ✅ Tambah dropdown "Kategori Umur" di form input dengan pilihan:
  - Dewasa (default)
  - Anak
- ✅ Tambah kolom "KATEGORI" di tabel data perkara
- ✅ Field kategori_umur dapat diedit langsung di tabel

#### 3. Logic Notifikasi Berbeda

**Kategori Dewasa:**
- SPDP: 25 hari kalender
- Berkas Tahap I: 6 hari kalender
- P-18/P-19: 10 hari kalender
- P-21: 12 hari kalender
- Tahap II: 7 hari kalender

**Kategori Anak:**
- SPDP: 25 hari kalender (sama dengan Dewasa)
- Berkas Tahap I: 3 hari kalender ⚡
- P-18/P-19: 7 hari kalender ⚡
- P-21: 10 hari kalender ⚡
- Tahap II: 5 hari kalender ⚡

### File yang Dimodifikasi

1. **models.py**
   - Tambah field `kategori_umur` (VARCHAR(20), default: 'Dewasa')
   - Update method `to_dict()`

2. **app.py**
   - Update filter `check_overdue()` dengan parameter `kategori_umur`
   - Implementasi logic limits untuk Dewasa dan Anak
   - Update route `add_case()` untuk handle kategori_umur
   - Update `allowed_fields` di route `update_cell()`

3. **templates/dashboard.html**
   - Tambah dropdown kategori umur di form
   - Tambah kolom KATEGORI di tabel header
   - Update semua pemanggilan filter `check_overdue()` dengan parameter kategori_umur
   - Tampilkan kategori_umur di tabel (editable)

### Script Migrasi

**File:** `scripts/add_kategori_umur.py`

Jalankan untuk menambahkan kolom kategori_umur ke database:
```bash
python scripts/add_kategori_umur.py
```

Output yang diharapkan:
```
✓ Successfully added 'kategori_umur' column
✓ Updated X existing records with default value 'Dewasa'
```

### Testing

**File:** `scripts/test_kategori_umur.py`

Jalankan untuk memverifikasi logic notifikasi:
```bash
python scripts/test_kategori_umur.py
```

Test mencakup:
- Logic overdue untuk kategori Dewasa
- Logic overdue untuk kategori Anak
- Edge cases (tepat di deadline, 1 hari setelah deadline)

### Backward Compatibility

✅ Data existing otomatis di-set sebagai "Dewasa"
✅ Tidak ada breaking changes
✅ Semua fitur existing tetap berfungsi normal

### Cara Deploy

1. Pull perubahan code
2. Jalankan script migrasi:
   ```bash
   python scripts/add_kategori_umur.py
   ```
3. Restart aplikasi
4. Verifikasi dengan test script (opsional):
   ```bash
   python scripts/test_kategori_umur.py
   ```

### Catatan Penting

- Kategori umur wajib dipilih saat input data baru
- Data lama akan otomatis menggunakan kategori "Dewasa"
- Kategori dapat diubah dengan klik langsung di tabel
- Notifikasi overdue akan otomatis menyesuaikan dengan kategori yang dipilih
