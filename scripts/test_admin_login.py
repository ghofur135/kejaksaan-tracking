"""
Test admin user login functionality
"""
from app import app
from models import User
from werkzeug.security import check_password_hash

def test_admin_login():
    """Test that admin user can login with correct password"""
    print("=" * 60)
    print("Testing Admin User Login")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Get admin user
            print("\n1. Fetching admin user from database...")
            admin = User.query.filter_by(username='admin').first()
            
            if not admin:
                print("   ✗ Admin user not found!")
                return False
            
            print(f"   ✓ Admin user found (ID: {admin.id})")
            
            # Test correct password
            print("\n2. Testing correct password (12345)...")
            if check_password_hash(admin.password_hash, '12345'):
                print("   ✓ Password verification successful!")
            else:
                print("   ✗ Password verification failed!")
                return False
            
            # Test incorrect password
            print("\n3. Testing incorrect password (wrong)...")
            if not check_password_hash(admin.password_hash, 'wrong'):
                print("   ✓ Incorrect password correctly rejected!")
            else:
                print("   ✗ Incorrect password was accepted (security issue)!")
                return False
            
            print("\n" + "=" * 60)
            print("Admin login test completed successfully!")
            print("You can login with: admin / 12345")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
            print("\n" + "=" * 60)
            print("Admin login test FAILED!")
            print("=" * 60)
            return False

if __name__ == '__main__':
    test_admin_login()
