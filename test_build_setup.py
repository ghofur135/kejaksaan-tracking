"""
Script untuk test apakah setup build sudah siap
Usage: python test_build_setup.py
"""
import sys
import os
from pathlib import Path

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"🐍 Python Version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("   ❌ Python 3.8+ required")
        return False
    else:
        print("   ✅ Python version OK")
        return True

def check_dependencies():
    """Check required packages"""
    print("\n📦 Checking Dependencies:")
    
    required = {
        'flask': 'Flask',
        'flask_login': 'Flask-Login',
        'flask_sqlalchemy': 'Flask-SQLAlchemy',
        'psycopg2': 'psycopg2-binary',
        'dateutil': 'python-dateutil',
        'dotenv': 'python-dotenv',
        'pyinstaller': 'PyInstaller',
        'webview': 'pywebview',
    }
    
    all_ok = True
    for module, package in required.items():
        try:
            __import__(module)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - Install: pip install {package}")
            all_ok = False
    
    return all_ok

def check_env_file():
    """Check .env file"""
    print("\n📄 Checking .env file:")
    
    env_path = Path('.env')
    if not env_path.exists():
        print("   ❌ File .env tidak ditemukan")
        print("      Buat file .env dengan isi:")
        print("      DATABASE_URL=postgresql://...")
        print("      SECRET_KEY=your-secret-key")
        return False
    
    print("   ✅ File .env ditemukan")
    
    # Check content
    with open(env_path, 'r') as f:
        content = f.read()
        
    has_db = 'DATABASE_URL=' in content
    has_key = 'SECRET_KEY=' in content
    
    if has_db:
        print("   ✅ DATABASE_URL ada")
    else:
        print("   ❌ DATABASE_URL tidak ada")
    
    if has_key:
        print("   ✅ SECRET_KEY ada")
    else:
        print("   ⚠️  SECRET_KEY tidak ada (akan pakai default)")
    
    return has_db

def check_project_files():
    """Check required project files"""
    print("\n📁 Checking Project Files:")
    
    required_files = [
        'app.py',
        'desktop.py',
        'models.py',
        'extensions.py',
        'build_exe.py',
        'templates/dashboard.html',
        'templates/login.html',
        'static/css/style.css',
    ]
    
    all_ok = True
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - File tidak ditemukan")
            all_ok = False
    
    return all_ok

def main():
    print("=" * 70)
    print("  TEST BUILD SETUP - E-KEJAKSAAN DESKTOP APP")
    print("=" * 70)
    print()
    
    results = []
    
    # Run checks
    results.append(("Python Version", check_python_version()))
    results.append(("Dependencies", check_dependencies()))
    results.append((".env File", check_env_file()))
    results.append(("Project Files", check_project_files()))
    
    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print()
    
    if all_passed:
        print("🎉 Setup lengkap! Siap untuk build.")
        print("\nJalankan: python build_exe.py")
    else:
        print("⚠️  Ada yang kurang. Perbaiki error di atas dulu.")
        print("\nSetelah diperbaiki, jalankan lagi: python test_build_setup.py")
    
    print()
    return 0 if all_passed else 1

if __name__ == '__main__':
    sys.exit(main())
