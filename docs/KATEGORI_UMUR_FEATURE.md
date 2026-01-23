# Fitur Kategori Umur (Dewasa/Anak)

## Deskripsi
Fitur ini menambahkan dropdown kategori umur pada form input SPDP dengan pilihan "Dewasa" atau "Anak". Logic notifikasi overdue akan berbeda berdasarkan kategori yang dipilih.

## Perubahan Database

### Kolom Baru
- `kategori_umur` (VARCHAR(20), default: 'Dewasa')

### Migrasi
Jalankan script migrasi untuk menambahkan kolom:
```bash
python scripts/add_kategori_umur.py
```

## Logic Notifikasi

### Dewasa (Default)
- SPDP: 25 hari kalender
- Berkas Tahap I: 6 hari kalender
- P-18/P-19: 10 hari kalender
- P-21: 12 hari kalender
- Tahap II: 7 hari kalender

### Anak
- SPDP: 25 hari kalender (sama)
- Berkas Tahap I: 3 hari kalender
- P-18/P-19: 7 hari kalender
- P-21: 10 hari kalender
- Tahap II: 5 hari kalender

## Perubahan File

### 1. models.py
- Tambah field `kategori_umur` di model Case
- Update method `to_dict()` untuk include kategori_umur

### 2. app.py
- Update filter `check_overdue()` untuk menerima parameter `kategori_umur`
- Tambah logic limits untuk Dewasa dan Anak
- Update route `add_case()` untuk menyimpan kategori_umur
- Update `allowed_fields` di route `update_cell()` untuk allow edit kategori_umur

### 3. templates/dashboard.html
- Tambah dropdown "Kategori Umur" di form input
- Tambah kolom "KATEGORI" di tabel
- Update semua pemanggilan filter `check_overdue()` dengan parameter kategori_umur
- Tampilkan kategori_umur di tabel (editable)

## Cara Penggunaan

1. Saat input data tersangka baru, pilih kategori umur dari dropdown:
   - Dewasa (default)
   - Anak

2. System akan otomatis menerapkan logic notifikasi yang sesuai

3. Kategori umur dapat diedit langsung di tabel dengan klik pada cell

## Backward Compatibility

- Data lama yang belum memiliki kategori_umur akan otomatis di-set sebagai "Dewasa"
- Script migrasi akan update semua record existing dengan default value "Dewasa"
