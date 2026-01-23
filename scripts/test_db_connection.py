"""
Test script to verify database connection and initialization.
This script tests:
1. Database connection to Supabase
2. Tables are created
3. Admin user exists
"""
from app import app, db
from models import User, Case
from sqlalchemy import inspect

def test_database_connection():
    """Test database connection and initialization"""
    print("=" * 60)
    print("Testing Database Connection to Supabase")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Test 1: Database connection
            print("\n1. Testing database connection...")
            db.engine.connect()
            print("   ✓ Database connection successful!")
            
            # Test 2: Check if tables exist
            print("\n2. Checking if tables are created...")
            inspector = inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"   Found tables: {tables}")
            
            if 'user' in tables:
                print("   ✓ 'user' table exists")
            else:
                print("   ✗ 'user' table NOT found")
                
            if 'case' in tables:
                print("   ✓ 'case' table exists")
            else:
                print("   ✗ 'case' table NOT found")
            
            # Test 3: Check admin user
            print("\n3. Checking admin user...")
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"   ✓ Admin user exists (ID: {admin.id}, Username: {admin.username})")
            else:
                print("   ✗ Admin user NOT found")
            
            # Test 4: Count existing cases
            print("\n4. Checking existing cases...")
            case_count = Case.query.count()
            print(f"   Found {case_count} case(s) in database")
            
            # Test 5: Verify table structure
            print("\n5. Verifying table structures...")
            
            # User table columns
            user_columns = [col['name'] for col in inspector.get_columns('user')]
            print(f"   User table columns: {user_columns}")
            expected_user_cols = ['id', 'username', 'password_hash']
            if all(col in user_columns for col in expected_user_cols):
                print("   ✓ User table structure is correct")
            else:
                print("   ✗ User table structure is incomplete")
            
            # Case table columns
            case_columns = [col['name'] for col in inspector.get_columns('case')]
            print(f"   Case table columns: {case_columns}")
            expected_case_cols = ['id', 'nama_tersangka', 'umur_tersangka', 'pasal', 'jpu']
            if all(col in case_columns for col in expected_case_cols):
                print("   ✓ Case table structure is correct")
            else:
                print("   ✗ Case table structure is incomplete")
            
            print("\n" + "=" * 60)
            print("All database tests completed successfully!")
            print("=" * 60)
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("\n" + "=" * 60)
            print("Database test FAILED!")
            print("=" * 60)
            raise

if __name__ == '__main__':
    test_database_connection()
