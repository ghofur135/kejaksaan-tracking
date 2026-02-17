# Build Desktop App (.exe)

## Cara Build ke .exe

### 1. Install Dependencies
```bash
pip install pyinstaller pywebview
```

### 2. Pastikan .env sudah terisi
File `.env` harus berisi:
- `SECRET_KEY` - Flask secret key

> **Note:** DATABASE_URL tidak perlu diset karena SQLite menggunakan file lokal.

### 3. Jalankan Build Script
```bash
python build_exe.py
```

Script akan otomatis:
- ✅ Embed SECRET_KEY dari .env ke dalam .exe
- ✅ Build dengan PyInstaller dan pywebview
- ✅ Cleanup file temporary
- ✅ Menghasilkan `dist/E-Kejaksaan.exe`

### 4. Distribusi
File `.exe` ada di folder `dist/`:
- **File**: `E-Kejaksaan.exe`
- **Ukuran**: ~50-80 MB
- **Standalone**: Tidak perlu install Python
- **Database**: SQLite lokal (folder `instance/`)
- **Koneksi**: Tidak perlu internet

## Cara Menggunakan .exe

1. Copy `E-Kejaksaan.exe` ke komputer lain
2. Double-click untuk menjalankan
3. Database SQLite akan otomatis terbuat di `instance/kejaksaan.db`
4. Login dengan username: `admin`, password: `12345`

## Catatan Penting

⚠️ **DATABASE**:
- Database menggunakan SQLite lokal (file di `instance/kejaksaan.db`)
- Portable - bisa copy kemana saja bersama .exe
- Untuk backup: copy folder `instance/`
- Untuk restore: paste folder `instance/` di-samping .exe

💡 **TIPS**:
- Ganti password default admin setelah pertama kali login
- Jangan hapus folder `instance/` karena berisi semua data
- Untuk migrasi ke komputer lain, copy .exe + folder instance/

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

### Database tidak terbuat otomatis
- Pastikan folder `instance/` ada di-samping .exe
- Folder akan otomatis dibuat saat pertama kali jalan
- Jika masih error, coba jalankan sebagai Administrator

### Data hilang setelah restart
- Pastikan folder `instance/` tidak dihapus
- Check antivirus tidak block folder tersebut
- Copy backup dari `instance/kejaksaan.db`

## Build Manual (Advanced)

Jika ingin build manual tanpa script:

```bash
# 1. Buat app_embedded.py (copy app.py, edit SECRET_KEY)
# 2. Buat desktop_embedded.py (import app_embedded)
# 3. Build
pyinstaller --clean --onefile --windowed \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --hidden-import engineio.async_drivers.threading \
  --name E-Kejaksaan \
  desktop_embedded.py
```
