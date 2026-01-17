"""
Test basic CRUD operations on Case model
"""
from app import app, db
from models import Case
from datetime import datetime

def test_crud_operations():
    """Test Create, Read, Update, Delete operations"""
    print("=" * 60)
    print("Testing CRUD Operations")
    print("=" * 60)
    
    with app.app_context():
        try:
            # CREATE
            print("\n1. Testing CREATE operation...")
            test_case = Case(
                nama_tersangka="Test Tersangka",
                umur_tersangka=30,
                pasal="Pasal 123",
                jpu="JPU Test",
                spdp_tgl_terima="2024-01-15",
                spdp_ket_terima="Diterima",
                spdp_tgl_polisi="2024-01-10",
                spdp_ket_polisi="Dari Polisi"
            )
            db.session.add(test_case)
            db.session.commit()
            print(f"   ✓ Case created with ID: {test_case.id}")
            test_id = test_case.id
            
            # READ
            print("\n2. Testing READ operation...")
            retrieved_case = Case.query.get(test_id)
            if retrieved_case:
                print(f"   ✓ Case retrieved: {retrieved_case.nama_tersangka}")
                print(f"      - Umur: {retrieved_case.umur_tersangka}")
                print(f"      - Pasal: {retrieved_case.pasal}")
                print(f"      - JPU: {retrieved_case.jpu}")
            else:
                print("   ✗ Case not found!")
                return False
            
            # UPDATE
            print("\n3. Testing UPDATE operation...")
            retrieved_case.nama_tersangka = "Updated Tersangka"
            retrieved_case.berkas_tahap_1 = "2024-01-20"
            db.session.commit()
            
            updated_case = Case.query.get(test_id)
            if updated_case.nama_tersangka == "Updated Tersangka":
                print(f"   ✓ Case updated successfully")
                print(f"      - New name: {updated_case.nama_tersangka}")
                print(f"      - Berkas Tahap 1: {updated_case.berkas_tahap_1}")
            else:
                print("   ✗ Update failed!")
                return False
            
            # DELETE
            print("\n4. Testing DELETE operation...")
            db.session.delete(updated_case)
            db.session.commit()
            
            deleted_case = Case.query.get(test_id)
            if deleted_case is None:
                print("   ✓ Case deleted successfully")
            else:
                print("   ✗ Delete failed!")
                return False
            
            # Verify count
            print("\n5. Verifying final state...")
            final_count = Case.query.count()
            print(f"   Total cases in database: {final_count}")
            
            print("\n" + "=" * 60)
            print("All CRUD operations completed successfully!")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("\n" + "=" * 60)
            print("CRUD operations test FAILED!")
            print("=" * 60)
            # Rollback in case of error
            db.session.rollback()
            return False

if __name__ == '__main__':
    test_crud_operations()
