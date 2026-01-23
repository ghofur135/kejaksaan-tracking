# Build Desktop App (.exe)

## Cara Build ke .exe

### 1. Install Dependencies
```bash
pip install pyinstaller pywebview
```

### 2. Pastikan .env sudah terisi
File `.env` harus berisi:
- `DATABASE_URL` - Connection string Supabase
- `SECRET_KEY` - Flask secret key

### 3. Jalankan Build Script
```bash
python build_exe.py
```

Script akan otomatis:
- ✅ Embed credentials dari .env ke dalam .exe
- ✅ Build dengan PyInstaller
- ✅ Cleanup file temporary
- ✅ Menghasilkan `dist/E-Kejaksaan.exe`

### 4. Distribusi
File `.exe` ada di folder `dist/`:
- **File**: `E-Kejaksaan.exe`
- **Ukuran**: ~50-80 MB
- **Standalone**: Tidak perlu install Python
- **Koneksi**: Butuh internet untuk akses Supabase

## Cara Menggunakan .exe

1. Copy `E-Kejaksaan.exe` ke komputer lain
2. Double-click untuk menjalankan
3. Aplikasi akan terbuka seperti desktop app native
4. Login dengan username/password yang sama

## Catatan Penting

⚠️ **KEAMANAN**:
- Credentials sudah embedded di dalam .exe
- **JANGAN** share .exe ke publik
- Hanya untuk internal use (tim kejaksaan)
- Siapapun yang punya .exe bisa akses database

💡 **TIPS**:
- Buat user dengan password kuat di database
- Gunakan role-based access di Supabase jika perlu
- Monitor akses database dari Supabase dashboard

## Troubleshooting

### Build gagal - PyInstaller not found
```bash
pip install pyinstaller
```

### Build gagal - pywebview not found
```bash
pip install pywebview
```

### .exe tidak jalan - Missing DLL
Install Visual C++ Redistributable:
https://aka.ms/vs/17/release/vc_redist.x64.exe

### .exe tidak bisa connect database
- Pastikan komputer ada koneksi internet
- Cek firewall tidak block aplikasi
- Test connection string di .env dulu sebelum build

## Build Manual (Advanced)

Jika ingin build manual tanpa script:

```bash
# 1. Buat app_embedded.py (copy app.py, edit credentials)
# 2. Buat desktop_embedded.py (import app_embedded)
# 3. Build
pyinstaller --clean --onefile --windowed \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --hidden-import engineio.async_drivers.threading \
  --name E-Kejaksaan \
  desktop_embedded.py
```
