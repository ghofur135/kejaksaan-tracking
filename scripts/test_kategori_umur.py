"""
Test script untuk memverifikasi logic notifikasi kategori umur
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, is_date_overdue

def test_overdue_logic():
    """Test overdue logic untuk Dewasa dan Anak"""
    
    print("=" * 60)
    print("TEST LOGIC NOTIFIKASI KATEGORI UMUR")
    print("=" * 60)
    
    # Test date: 10 hari yang lalu
    test_date = datetime.now() - timedelta(days=10)
    
    print(f"\nTanggal Test: {test_date.strftime('%Y-%m-%d')}")
    print(f"Hari Ini: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Selisih: 10 hari")
    
    # Test untuk Dewasa
    print("\n" + "=" * 60)
    print("KATEGORI: DEWASA")
    print("=" * 60)
    
    dewasa_limits = {
        'SPDP': 25,
        'Berkas Tahap I': 6,
        'P-18/P-19': 10,
        'P-21': 12,
        'Tahap II': 7
    }
    
    for field, limit in dewasa_limits.items():
        is_overdue = is_date_overdue(test_date, limit)
        status = "❌ OVERDUE" if is_overdue else "✓ OK"
        print(f"{field:20} | Limit: {limit:2} hari | {status}")
    
    # Test untuk Anak
    print("\n" + "=" * 60)
    print("KATEGORI: ANAK")
    print("=" * 60)
    
    anak_limits = {
        'SPDP': 25,
        'Berkas Tahap I': 3,
        'P-18/P-19': 7,
        'P-21': 10,
        'Tahap II': 5
    }
    
    for field, limit in anak_limits.items():
        is_overdue = is_date_overdue(test_date, limit)
        status = "❌ OVERDUE" if is_overdue else "✓ OK"
        print(f"{field:20} | Limit: {limit:2} hari | {status}")
    
    # Test edge cases
    print("\n" + "=" * 60)
    print("EDGE CASES")
    print("=" * 60)
    
    # Test: Tepat di deadline (6 hari untuk Berkas Tahap I Dewasa)
    edge_date = datetime.now() - timedelta(days=5)  # Hari ke-6 adalah deadline
    is_overdue = is_date_overdue(edge_date, 6)
    print(f"Tepat di deadline (6 hari): {'❌ OVERDUE' if is_overdue else '✓ OK (belum overdue)'}")
    
    # Test: 1 hari setelah deadline
    edge_date = datetime.now() - timedelta(days=6)  # Hari ke-7 sudah overdue
    is_overdue = is_date_overdue(edge_date, 6)
    print(f"1 hari setelah deadline: {'❌ OVERDUE' if is_overdue else '✓ OK'}")
    
    print("\n" + "=" * 60)
    print("TEST SELESAI")
    print("=" * 60)

if __name__ == '__main__':
    with app.app_context():
        test_overdue_logic()
