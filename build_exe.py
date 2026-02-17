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
    print("📝 Membuat app_embedded.py untuk SQLite...")
    
    env_vars = load_env_file()
    secret_key = env_vars.get('SECRET_KEY', 'dev-secret-key')
    
    # SQLite tidak perlu DATABASE_URL di-embed karena menggunakan file lokal
    # Database path akan di-handle otomatis oleh app.py dengan basedir
    
    # Baca app.py original
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # Replace embedded credentials
    # Untuk SQLite, kita biarkan EMBEDDED_DATABASE_URL = None agar menggunakan default SQLite path
    app_content = app_content.replace(
        'EMBEDDED_SECRET_KEY = None    # Will be set by build_exe.py',
        f'EMBEDDED_SECRET_KEY = "{secret_key}"    # Embedded by build_exe.py'
    )
    
    # Simpan ke app_embedded.py
    with open('app_embedded.py', 'w', encoding='utf-8') as f:
        f.write(app_content)
    
    print("✅ app_embedded.py berhasil dibuat (SQLite mode)")
    return True

def create_desktop_embedded():
    """Buat desktop_embedded.py yang import dari app_embedded"""
    print("📝 Membuat desktop_embedded.py...")
    
    desktop_content = """import webview
import sys
import threading
from app_embedded import app
import time
import socket

def find_free_port():
    \"\"\"Find a free port to use\"\"\"
    ports_to_try = [5000, 5001, 5002, 5003, 8000, 8080, 8888]
    
    for port in ports_to_try:
        try:
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            return port
        except OSError:
            continue
    
    # If all ports are taken, use a random free port
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port

def start_server(port):
    \"\"\"Start Flask server without reloader (required for PyInstaller)\"\"\"
    try:
        print(f"Starting Flask server on port {port}...")
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False, threaded=True)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    # Find a free port
    port = find_free_port()
    print(f"Using port: {port}")
    
    # Start Flask in a separate thread
    t = threading.Thread(target=start_server, args=(port,))
    t.daemon = True
    t.start()
    
    # Give server more time to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Test if server is running
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result != 0:
            print(f"ERROR: Server failed to start on port {port}")
            print("Please check:")
            print("1. Firewall/Antivirus settings")
            print("2. Port is not blocked")
            print("3. Database connection is working")
            input("Press Enter to exit...")
            sys.exit(1)
        else:
            print(f"Server is running on http://127.0.0.1:{port}")
    except Exception as e:
        print(f"Error checking server: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

    # Create a native window pointing to the Flask app
    try:
        webview.create_window(
            'E-Kejaksaan Tracking System', 
            f'http://127.0.0.1:{port}',
            width=1400,
            height=900,
            resizable=True,
            fullscreen=False
        )
        
        # Start the GUI loop
        webview.start()
    except Exception as e:
        print(f"Error creating window: {e}")
        input("Press Enter to exit...")
    
    sys.exit()
"""
    
    with open('desktop_embedded.py', 'w', encoding='utf-8') as f:
        f.write(desktop_content)
    
    print("✅ desktop_embedded.py berhasil dibuat")

def create_spec_file():
    """Buat file .spec untuk PyInstaller"""
    print("📝 Membuat kejaksaan.spec...")
    
    # Detect OS for proper file separator
    import platform
    is_windows = platform.system() == 'Windows'
    separator = ';' if is_windows else ':'
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

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
    hooksconfig={{}},
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
    import platform
    os_name = platform.system()
    
    print("\n🔨 Memulai build dengan PyInstaller...")
    print(f"   Platform: {os_name}")
    
    if os_name == "Linux":
        print("   ⚠️  PERHATIAN: Build di Linux akan menghasilkan executable Linux (bukan .exe)")
        print("   Untuk build .exe Windows, jalankan script ini di Windows")
    
    print("   Ini akan memakan waktu beberapa menit...\n")
    
    try:
        # Run PyInstaller with real-time output (no capture)
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--clean', 'kejaksaan.spec'],
            check=True
        )
        
        print("\n✅ Build berhasil!")
        
        # Determine output file based on OS
        if os_name == "Windows":
            exe_path = 'dist/E-Kejaksaan.exe'
            print(f"\n📦 File .exe tersedia di: {exe_path}")
        else:
            exe_path = 'dist/E-Kejaksaan'
            print(f"\n📦 File executable tersedia di: {exe_path}")
        
        # Check if file exists before getting size
        if os.path.exists(exe_path):
            print(f"   Ukuran: ~{os.path.getsize(exe_path) / (1024*1024):.1f} MB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("\n❌ Build gagal!")
        print(f"Error: {str(e)}")
        return False
    except Exception as e:
        print("\n❌ PyInstaller error!")
        print(f"   Error: {str(e)}")
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
    print("  Database: SQLite Local (Portable)")
    print("=" * 60)
    
    import platform
    if platform.system() != "Windows":
        print(f"\n⚠️  PERHATIAN: Anda menjalankan di {platform.system()}")
        print("   Build akan menghasilkan executable untuk Linux, bukan .exe")
        print("   Untuk build .exe Windows, jalankan script ini di Windows\n")
        response = input("Lanjutkan build untuk Linux? (y/n): ")
        if response.lower() != 'y':
            print("Build dibatalkan.")
            sys.exit(0)
    
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
        print("   3. Database SQLite akan otomatis terbuat di: instance/kejaksaan.db")
        print("\n⚠️  PENTING:")
        print("   - Database menggunakan SQLite lokal (tidak perlu internet)")
        print("   - Data disimpan di folder instance/ di-samping .exe")
        print("   - Untuk backup, copy folder instance/kejaksaan.db")
        print("\n💡 TIPS:")
        print("   - Database SQLite portable, bisa copy kemana saja")
        print("   - Pastikan tidak hapus folder instance/")
        print("   - Login default: admin / 12345 (ubah setelah login)")
        print("\n📖 Dokumentasi:")
        print("   - Quick Start: docs/build-exe.md")
        print()
    else:
        print("\n❌ Build gagal. Periksa error di atas.")
        sys.exit(1)

if __name__ == '__main__':
    main()
