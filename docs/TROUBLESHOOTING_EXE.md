# Troubleshooting .EXE Build

## Error: "127.0.0.1 refused to connect"

### Penyebab:
Flask server di dalam .exe tidak berhasil start.

### Solusi:

#### 1. Build dengan Debug Mode
```bash
# Build versi debug yang menampilkan console
pyinstaller --clean desktop_debug.spec
```

Jalankan `dist/E-Kejaksaan-Debug.exe` dan lihat error message di console.

#### 2. Gunakan Build Script Sederhana
```bash
# Windows
build_simple.bat

# Atau manual
pyinstaller --clean desktop_debug.spec
pyinstaller --clean desktop.spec
```

#### 3. Cek Dependencies
Pastikan semua dependencies terinstall:
```bash
pip install -r requirements.txt
pip install pyinstaller pywebview
```

#### 4. Test Desktop.py Sebelum Build
```bash
python desktop.py
```

Jika ini tidak jalan, fix dulu sebelum build .exe.

#### 5. Cek File .env
Pastikan `.env` ada dan berisi:
```
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
```

#### 6. Rebuild dari Awal
```bash
# Hapus cache
rmdir /s /q build dist
del *.spec

# Build ulang
python build_exe.py
```

## Error: Missing Module

### Gejala:
```
ModuleNotFoundError: No module named 'xxx'
```

### Solusi:
Tambahkan module ke `hiddenimports` di file `.spec`:

```python
hiddenimports=[
    'engineio.async_drivers.threading',
    'sqlalchemy.sql.default_comparator',
    'werkzeug.security',
    'flask_login',
    'dateutil',
    'dateutil.parser',
    'flask_sqlalchemy',
    'psycopg2',
    # Tambahkan module yang error di sini
],
```

## Error: Database Connection Failed

### Solusi:
1. Pastikan koneksi internet aktif
2. Test connection string di Python dulu:
```python
from sqlalchemy import create_engine
engine = create_engine("your-database-url")
conn = engine.connect()
print("Connected!")
```

3. Cek firewall tidak block aplikasi

## Tips Build Sukses

### 1. Gunakan Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Build Step by Step
```bash
# 1. Test app dulu
python app.py

# 2. Test desktop dulu
python desktop.py

# 3. Baru build
python build_exe.py
```

### 3. Cek Ukuran File
- Normal: 50-80 MB
- Terlalu kecil (<20 MB): Ada dependencies yang missing
- Terlalu besar (>200 MB): Ada file yang tidak perlu

### 4. Test di Komputer Lain
Setelah build, test di komputer yang:
- Tidak ada Python installed
- Tidak ada dependencies installed
- Fresh Windows install

## Build Commands Cheatsheet

```bash
# Debug build (with console)
pyinstaller --clean desktop_debug.spec

# Production build (no console)
pyinstaller --clean desktop.spec

# Build dengan embedded credentials
python build_exe.py

# Build simple (both debug & release)
build_simple.bat
```

## Logs & Debugging

### Lihat Console Output
Build dengan `console=True` di .spec file:
```python
exe = EXE(
    ...
    console=True,  # Show console
    ...
)
```

### Check PyInstaller Warnings
Saat build, perhatikan warning messages:
```
WARNING: Hidden import "xxx" not found
```

Tambahkan ke `hiddenimports`.

### Test Import
Sebelum build, test semua import:
```python
python -c "from app import app; print('OK')"
python -c "import flask_login; print('OK')"
python -c "import dateutil; print('OK')"
```

## Kontak Support

Jika masih error setelah semua solusi di atas:
1. Screenshot error message
2. Copy console output
3. Cek versi Python: `python --version`
4. Cek versi PyInstaller: `pyinstaller --version`
