# 🚀 Build Cheatsheet - E-Kejaksaan Desktop App

## Quick Commands

```bash
# 1. Test setup (optional)
python test_build_setup.py

# 2. Build .exe
python build_exe.py

# 3. Test .exe
cd dist
./E-Kejaksaan.exe
```

---

## File Structure

```
project/
├── app.py                    # Main Flask app
├── desktop.py                # Desktop wrapper
├── build_exe.py             # 🔥 Build script (jalankan ini!)
├── test_build_setup.py      # Test setup
├── .env                     # Credentials (akan di-embed)
├── templates/               # HTML templates
├── static/                  # CSS, JS, images
└── dist/
    └── E-Kejaksaan.exe     # 🎯 Hasil build
```

---

## Build Process Flow

```
.env (credentials)
    ↓
build_exe.py (embed)
    ↓
app_embedded.py (temporary)
    ↓
PyInstaller
    ↓
E-Kejaksaan.exe (final)
```

---

## Dependencies

### Runtime (untuk development)
```bash
pip install flask flask-login flask-sqlalchemy psycopg2-binary python-dateutil python-dotenv
```

### Build (untuk build .exe)
```bash
pip install pyinstaller pywebview
```

### All-in-one
```bash
pip install -r requirements.txt
```

---

## Common Issues

| Problem | Solution |
|---------|----------|
| `pyinstaller: command not found` | `pip install pyinstaller` |
| `No module named 'webview'` | `pip install pywebview` |
| `.env not found` | Buat file `.env` dengan `DATABASE_URL` dan `SECRET_KEY` |
| `Missing DLL` | Install [VC++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) |
| `.exe can't connect DB` | Cek koneksi internet & firewall |

---

## Build Options

### Standard Build (recommended)
```bash
python build_exe.py
```

### Manual Build (advanced)
```bash
pyinstaller --clean --onefile --windowed \
  --add-data "templates:templates" \
  --add-data "static:static" \
  --hidden-import engineio.async_drivers.threading \
  --name E-Kejaksaan \
  desktop_embedded.py
```

---

## Security Checklist

- [ ] `.env` file ada dan terisi
- [ ] `DATABASE_URL` valid
- [ ] `SECRET_KEY` strong (minimal 32 karakter)
- [ ] `.exe` hanya untuk internal use
- [ ] Tidak share `.exe` ke publik
- [ ] Monitor database access di Supabase

---

## Distribution

### What to share:
✅ `E-Kejaksaan.exe` (file tunggal)

### What NOT to share:
❌ `.env` file  
❌ Source code (jika tidak perlu)  
❌ Build scripts  

---

## Testing

### Before build:
```bash
# Test Flask app
python app.py

# Test desktop wrapper
python desktop.py

# Test build setup
python test_build_setup.py
```

### After build:
```bash
# Run .exe
cd dist
./E-Kejaksaan.exe
```

---

## Rebuild

Jika perlu rebuild (misal ganti credentials):

```bash
# 1. Edit .env
nano .env

# 2. Rebuild
python build_exe.py

# 3. Test
cd dist
./E-Kejaksaan.exe
```

---

## File Sizes

| File | Size |
|------|------|
| Source code | ~100 KB |
| Templates + Static | ~50 KB |
| **E-Kejaksaan.exe** | **~50-80 MB** |

---

## System Requirements

### Development Machine (untuk build):
- Python 3.8+
- pip
- Internet connection

### Target Machine (untuk run .exe):
- Windows 10/11
- Internet connection (untuk Supabase)
- Visual C++ Redistributable (biasanya sudah ada)

---

## Support

📖 **Dokumentasi lengkap**: `build-exe.md`  
📋 **Quick start**: `BUILD_README.md`  
📝 **Cara lengkap**: `CARA_BUILD_EXE.txt`  
🏗️ **Arsitektur**: `ARCHITECTURE.md`  
🧪 **Test setup**: `python test_build_setup.py` (di root folder)
