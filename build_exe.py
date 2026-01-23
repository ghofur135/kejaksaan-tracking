"""
Build script untuk membuat .exe dengan embedded credentials
Usage: python build_exe.py
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def load_env_file():
    """Load .env file dan parse credentials"""
    env_vars = {}
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ File .env tidak ditemukan!")
        print("   Pastikan file .env ada di folder project")
        sys.exit(1)
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def create_embedded_app():
    """Buat app_embedded.py dengan credentials yang sudah di-embed"""
    print("📝 Membuat app_embedded.py dengan credentials...")
    
    env_vars = load_env_file()
    database_url = env_vars.get('DATABASE_URL', '')
    secret_key = env_vars.get('SECRET_KEY', 'dev-secret-key')
    
    if not database_url:
        print("❌ DATABASE_URL tidak ditemukan di .env!")
        sys.exit(1)
    
    # Baca app.py original
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Replace embedded credentials
    app_content = app_content.replace(
        'EMBEDDED_DATABASE_URL = None  # Will be set by build_exe.py',
        f'EMBEDDED_DATABASE_URL = "{database_url}"  # Embedded by build_exe.py'
    )
    app_content = app_content.replace(
        'EMBEDDED_SECRET_KEY = None    # Will be set by build_exe.py',
        f'EMBEDDED_SECRET_KEY = "{secret_key}"    # Embedded by build_exe.py'
    )
    
    # Simpan ke app_embedded.py
    with open('app_embedded.py', 'w', encoding='utf-8') as f:
        f.write(app_content)
    
    print("✅ app_embedded.py berhasil dibuat")
    return True

def create_desktop_embedded():
    """Buat desktop_embedded.py yang import dari app_embedded"""
    print("📝 Membuat desktop_embedded.py...")
    
    desktop_content = """import webview
import sys
import threading
from app_embedded import app
import time

def start_server():
    app.run(port=5000, debug=False, use_reloader=False)

if __name__ == '__main__':
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server)
    t.daemon = True
    t.start()
    
    # Give server a second to start
    time.sleep(1)

    # Create a native window pointing to the Flask app
    webview.create_window(
        'E-Kejaksaan Tracking System', 
        'http://127.0.0.1:5000',
        width=1400,
        height=900,
        resizable=True,
        fullscreen=False
    )
    
    # Start the GUI loop
    webview.start()
    sys.exit()
"""
    
    with open('desktop_embedded.py', 'w', encoding='utf-8') as f:
        f.write(desktop_content)
    
    print("✅ desktop_embedded.py berhasil dibuat")

def create_spec_file():
    """Buat file .spec untuk PyInstaller"""
    print("📝 Membuat kejaksaan.spec...")
    
    spec_content = """# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['desktop_embedded.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('templates', 'templates'),
        ('static', 'static'),
    ],
    hiddenimports=[
        'engineio.async_drivers.threading',
        'sqlalchemy.sql.default_comparator',
        'werkzeug.security',
        'flask_login',
        'dateutil',
        'dateutil.parser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='E-Kejaksaan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Tidak tampilkan console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Bisa tambahkan icon.ico di sini
)
"""
    
    with open('kejaksaan.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ kejaksaan.spec berhasil dibuat")

def build_exe():
    """Build .exe menggunakan PyInstaller"""
    print("\n🔨 Memulai build dengan PyInstaller...")
    print("   Ini akan memakan waktu beberapa menit...\n")
    
    try:
        # Run PyInstaller
        result = subprocess.run(
            ['pyinstaller', '--clean', 'kejaksaan.spec'],
            check=True,
            capture_output=True,
            text=True
        )
        
        print("✅ Build berhasil!")
        print(f"\n📦 File .exe tersedia di: dist/E-Kejaksaan.exe")
        print(f"   Ukuran: ~{os.path.getsize('dist/E-Kejaksaan.exe') / (1024*1024):.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Build gagal!")
        print(f"Error: {e.stderr}")
        return False
    except FileNotFoundError:
        print("❌ PyInstaller tidak ditemukan!")
        print("   Install dengan: pip install pyinstaller")
        return False

def cleanup_temp_files():
    """Hapus file temporary"""
    print("\n🧹 Membersihkan file temporary...")
    
    temp_files = ['app_embedded.py', 'desktop_embedded.py']
    for file in temp_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"   Dihapus: {file}")
    
    # Hapus folder build
    if os.path.exists('build'):
        shutil.rmtree('build')
        print(f"   Dihapus: build/")
    
    print("✅ Cleanup selesai")

def main():
    print("=" * 60)
    print("  BUILD E-KEJAKSAAN DESKTOP APP (.EXE)")
    print("  Credentials akan di-embed ke dalam .exe")
    print("=" * 60)
    print()
    
    # Step 1: Create embedded files
    if not create_embedded_app():
        sys.exit(1)
    
    create_desktop_embedded()
    create_spec_file()
    
    # Step 2: Build
    success = build_exe()
    
    # Step 3: Cleanup
    cleanup_temp_files()
    
    if success:
        print("\n" + "=" * 60)
        print("  ✅ BUILD SELESAI!")
        print("=" * 60)
        print("\n📋 Cara menggunakan:")
        print("   1. Copy file 'dist/E-Kejaksaan.exe' ke komputer lain")
        print("   2. Double-click untuk menjalankan")
        print("   3. Pastikan ada koneksi internet (untuk akses Supabase)")
        print("\n⚠️  PENTING:")
        print("   - Credentials sudah embedded di dalam .exe")
        print("   - Jangan share .exe ke publik (ada database credentials)")
        print("   - Hanya untuk internal use")
        print("\n📖 Dokumentasi:")
        print("   - Quick Start: docs/BUILD_README.md")
        print("   - Lengkap: docs/CARA_BUILD_EXE.txt")
        print("   - Cheatsheet: docs/BUILD_CHEATSHEET.md")
        print()
    else:
        print("\n❌ Build gagal. Periksa error di atas.")
        sys.exit(1)

if __name__ == '__main__':
    main()
