# 🚀 Quick Start - Build Desktop App

## Build ke .exe (1 Command)

```bash
python build_exe.py
```

Selesai! File `.exe` ada di `dist/E-Kejaksaan.exe`

---

## Persyaratan

1. **Install dependencies** (sekali saja):
```bash
pip install pyinstaller pywebview
```

2. **File .env harus ada** dengan isi:
```env
DATABASE_URL=postgresql://postgres.xxx:password@aws-xxx.pooler.supabase.com:6543/postgres
SECRET_KEY=your-secret-key
```

---

## Hasil Build

✅ **File**: `dist/E-Kejaksaan.exe` (~50-80 MB)  
✅ **Standalone**: Tidak perlu install Python  
✅ **Credentials**: Sudah embedded di dalam .exe  
✅ **Database**: Tetap pakai Supabase (butuh internet)

---

## Cara Pakai

1. Copy `E-Kejaksaan.exe` ke komputer lain
2. Double-click untuk jalankan
3. Login seperti biasa

---

## ⚠️ Penting

- **JANGAN share .exe ke publik** (ada database credentials)
- Hanya untuk internal use
- Komputer harus ada koneksi internet

---

## Troubleshooting

**Build gagal?**
```bash
pip install --upgrade pyinstaller pywebview
```

**Dokumentasi lengkap**: Lihat `docs/build-exe.md`
