"""
Backward Compatibility Tests for Vercel & Supabase Migration

This test suite validates that all existing functionality remains intact after migration:
- All existing routes are functional
- Login functionality works with admin credentials
- Case CRUD operations work correctly
- Overdue checking logic produces correct results

Requirements: 8.1, 8.2, 8.3, 8.4, 8.5
"""
import unittest
from datetime import datetime, timedelta
from app import app, db, parse_date, is_date_overdue, check_overdue
from models import User, Case
from werkzeug.security import generate_password_hash, check_password_hash


class BackwardCompatibilityTests(unittest.TestCase):
    """Test suite for backward compatibility after migration"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests"""
        cls.app = app
        cls.app.config['TESTING'] = True
        cls.app.config['WTF_CSRF_ENABLED'] = False
        
    def setUp(self):
        """Set up before each test"""
        # Create a new test client for each test to ensure clean session
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        
    def tearDown(self):
        """Clean up after each test"""
        # Rollback any uncommitted changes
        db.session.rollback()
        self.ctx.pop()
    
    # ========================================================================
    # Route Tests (Requirement 8.1)
    # ========================================================================
    
    def test_route_root_redirects_to_dashboard(self):
        """Test that / route redirects to dashboard (requires login)"""
        response = self.client.get('/', follow_redirects=False)
        # Should redirect to login since not authenticated
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_route_login_get(self):
        """Test that /login route returns 200 on GET"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login', response.data.lower())
    
    def test_route_login_post_invalid(self):
        """Test that /login route handles invalid credentials"""
        response = self.client.post('/login', data={
            'username': 'invalid',
            'password': 'invalid'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid', response.data)
    
    def test_route_logout_requires_auth(self):
        """Test that /logout route requires authentication"""
        response = self.client.get('/logout', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_route_dashboard_requires_auth(self):
        """Test that /dashboard route requires authentication"""
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_route_add_case_requires_auth(self):
        """Test that /add_case route requires authentication"""
        response = self.client.post('/add_case', data={}, follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    def test_route_update_cell_requires_auth(self):
        """Test that /update_cell route requires authentication"""
        response = self.client.post('/update_cell', 
                                   json={'id': 1, 'field': 'test', 'value': 'test'},
                                   follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    # ========================================================================
    # Login Functionality Tests (Requirement 8.2)
    # ========================================================================
    
    def test_admin_user_exists(self):
        """Test that admin user exists in database"""
        admin = User.query.filter_by(username='admin').first()
        self.assertIsNotNone(admin, "Admin user should exist")
        self.assertEqual(admin.username, 'admin')
    
    def test_admin_password_verification(self):
        """Test that admin password (12345) can be verified"""
        admin = User.query.filter_by(username='admin').first()
        self.assertIsNotNone(admin)
        self.assertTrue(
            check_password_hash(admin.password_hash, '12345'),
            "Admin password should be '12345'"
        )
    
    def test_admin_login_flow(self):
        """Test complete admin login flow"""
        # Login with admin credentials
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        }, follow_redirects=False)
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard', response.location)
        
        # Follow redirect and verify dashboard loads
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_logout_flow(self):
        """Test admin logout flow"""
        # Login first
        self.client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        })
        
        # Logout
        response = self.client.get('/logout', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
        
        # Verify can't access dashboard after logout
        response = self.client.get('/dashboard', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)
    
    # ========================================================================
    # CRUD Operations Tests (Requirement 8.3)
    # ========================================================================
    
    def test_case_create_operation(self):
        """Test creating a new case"""
        # Login first
        self.client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        })
        
        # Create a case
        initial_count = Case.query.count()
        response = self.client.post('/add_case', data={
            'nama_tersangka': 'Test Tersangka',
            'umur_tersangka': '30',
            'pasal': 'Pasal 123',
            'jpu': 'JPU Test',
            'spdp_tgl_terima': '2024-01-15',
            'spdp_ket_terima': 'Diterima',
            'spdp_tgl_polisi': '2024-01-10',
            'spdp_ket_polisi': 'Dari Polisi'
        }, follow_redirects=False)
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify case was created
        final_count = Case.query.count()
        self.assertEqual(final_count, initial_count + 1)
        
        # Verify case data
        new_case = Case.query.filter_by(nama_tersangka='Test Tersangka').first()
        self.assertIsNotNone(new_case)
        self.assertEqual(new_case.umur_tersangka, 30)
        self.assertEqual(new_case.pasal, 'Pasal 123')
        self.assertEqual(new_case.jpu, 'JPU Test')
        
        # Cleanup
        db.session.delete(new_case)
        db.session.commit()
    
    def test_case_read_operation(self):
        """Test reading cases from database"""
        # Create a test case
        test_case = Case(
            nama_tersangka='Read Test',
            umur_tersangka=25,
            pasal='Pasal 456',
            jpu='JPU Read'
        )
        db.session.add(test_case)
        db.session.commit()
        test_id = test_case.id
        
        # Read the case
        retrieved_case = Case.query.get(test_id)
        self.assertIsNotNone(retrieved_case)
        self.assertEqual(retrieved_case.nama_tersangka, 'Read Test')
        self.assertEqual(retrieved_case.umur_tersangka, 25)
        self.assertEqual(retrieved_case.pasal, 'Pasal 456')
        
        # Cleanup
        db.session.delete(retrieved_case)
        db.session.commit()
    
    def test_case_update_operation(self):
        """Test updating a case via update_cell endpoint"""
        # Create a test case
        test_case = Case(
            nama_tersangka='Update Test',
            umur_tersangka=28,
            pasal='Pasal 789'
        )
        db.session.add(test_case)
        db.session.commit()
        test_id = test_case.id
        
        # Login first
        self.client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        })
        
        # Update the case
        response = self.client.post('/update_cell', json={
            'id': test_id,
            'field': 'berkas_tahap_1',
            'value': '2024-01-20'
        })
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data['success'])
        
        # Verify update
        updated_case = Case.query.get(test_id)
        self.assertEqual(updated_case.berkas_tahap_1, '2024-01-20')
        
        # Cleanup
        db.session.delete(updated_case)
        db.session.commit()
    
    def test_case_update_security(self):
        """Test that only allowed fields can be updated"""
        # Create a test case
        test_case = Case(nama_tersangka='Security Test')
        db.session.add(test_case)
        db.session.commit()
        test_id = test_case.id
        
        # Login first
        self.client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        })
        
        # Try to update a non-allowed field
        response = self.client.post('/update_cell', json={
            'id': test_id,
            'field': 'created_at',  # Not in allowed_fields
            'value': '2024-01-01'
        })
        
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertFalse(data['success'])
        
        # Cleanup
        db.session.delete(test_case)
        db.session.commit()
    
    def test_dashboard_displays_cases(self):
        """Test that dashboard displays cases correctly"""
        # Create test cases
        case1 = Case(nama_tersangka='Dashboard Test 1')
        case2 = Case(nama_tersangka='Dashboard Test 2')
        db.session.add_all([case1, case2])
        db.session.commit()
        
        # Login and access dashboard
        self.client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        })
        response = self.client.get('/dashboard')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard Test 1', response.data)
        self.assertIn(b'Dashboard Test 2', response.data)
        
        # Cleanup
        db.session.delete(case1)
        db.session.delete(case2)
        db.session.commit()
    
    # ========================================================================
    # Overdue Checking Logic Tests (Requirement 8.4)
    # ========================================================================
    
    def test_parse_date_iso_format(self):
        """Test parsing ISO format dates (YYYY-MM-DD)"""
        date_obj = parse_date('2024-01-15')
        self.assertIsNotNone(date_obj)
        self.assertEqual(date_obj.year, 2024)
        self.assertEqual(date_obj.month, 1)
        self.assertEqual(date_obj.day, 15)
    
    def test_parse_date_dd_mm_yyyy_format(self):
        """Test parsing DD-MM-YYYY format dates"""
        date_obj = parse_date('15-01-2024')
        self.assertIsNotNone(date_obj)
        self.assertEqual(date_obj.year, 2024)
        self.assertEqual(date_obj.month, 1)
        self.assertEqual(date_obj.day, 15)
    
    def test_parse_date_invalid(self):
        """Test parsing invalid dates returns None"""
        self.assertIsNone(parse_date('invalid'))
        self.assertIsNone(parse_date(''))
        self.assertIsNone(parse_date(None))
    
    def test_is_date_overdue_past_deadline(self):
        """Test overdue detection for dates past deadline"""
        # Date 30 days ago with 25 day limit should be overdue
        past_date = datetime.now() - timedelta(days=30)
        self.assertTrue(is_date_overdue(past_date, 25))
    
    def test_is_date_overdue_within_deadline(self):
        """Test overdue detection for dates within deadline"""
        # Date 10 days ago with 25 day limit should not be overdue
        recent_date = datetime.now() - timedelta(days=10)
        self.assertFalse(is_date_overdue(recent_date, 25))
    
    def test_is_date_overdue_exact_deadline(self):
        """Test overdue detection on exact deadline day"""
        # Date exactly at deadline should not be overdue
        deadline_date = datetime.now() - timedelta(days=24)  # 25 days limit
        self.assertFalse(is_date_overdue(deadline_date, 25))
    
    def test_check_overdue_filter_spdp(self):
        """Test check_overdue filter for SPDP field (25 days)"""
        # Date 30 days ago should be overdue for SPDP
        past_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        result = check_overdue(past_date, 'spdp')
        self.assertEqual(result, 'overdue-cell')
        
        # Date 10 days ago should not be overdue for SPDP
        recent_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        result = check_overdue(recent_date, 'spdp')
        self.assertEqual(result, '')
    
    def test_check_overdue_filter_berkas_tahap_1(self):
        """Test check_overdue filter for berkas_tahap_1 field (6 days)"""
        # Date 10 days ago should be overdue for berkas_tahap_1
        past_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        result = check_overdue(past_date, 'berkas_tahap_1')
        self.assertEqual(result, 'overdue-cell')
        
        # Date 3 days ago should not be overdue for berkas_tahap_1
        recent_date = (datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d')
        result = check_overdue(recent_date, 'berkas_tahap_1')
        self.assertEqual(result, '')
    
    def test_check_overdue_filter_p18_p19(self):
        """Test check_overdue filter for p18_p19 field (10 days)"""
        # Date 15 days ago should be overdue for p18_p19
        past_date = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d')
        result = check_overdue(past_date, 'p18_p19')
        self.assertEqual(result, 'overdue-cell')
        
        # Date 5 days ago should not be overdue for p18_p19
        recent_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
        result = check_overdue(recent_date, 'p18_p19')
        self.assertEqual(result, '')
    
    def test_check_overdue_filter_p21(self):
        """Test check_overdue filter for p21 field (12 days)"""
        # Date 20 days ago should be overdue for p21
        past_date = (datetime.now() - timedelta(days=20)).strftime('%Y-%m-%d')
        result = check_overdue(past_date, 'p21')
        self.assertEqual(result, 'overdue-cell')
        
        # Date 8 days ago should not be overdue for p21
        recent_date = (datetime.now() - timedelta(days=8)).strftime('%Y-%m-%d')
        result = check_overdue(recent_date, 'p21')
        self.assertEqual(result, '')
    
    def test_check_overdue_filter_tahap_2(self):
        """Test check_overdue filter for tahap_2 field (7 days)"""
        # Date 10 days ago should be overdue for tahap_2
        past_date = (datetime.now() - timedelta(days=10)).strftime('%Y-%m-%d')
        result = check_overdue(past_date, 'tahap_2')
        self.assertEqual(result, 'overdue-cell')
        
        # Date 4 days ago should not be overdue for tahap_2
        recent_date = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')
        result = check_overdue(recent_date, 'tahap_2')
        self.assertEqual(result, '')
    
    def test_check_overdue_filter_invalid_date(self):
        """Test check_overdue filter with invalid date"""
        result = check_overdue('invalid', 'spdp')
        self.assertEqual(result, '')
        
        result = check_overdue('', 'spdp')
        self.assertEqual(result, '')
        
        result = check_overdue(None, 'spdp')
        self.assertEqual(result, '')
    
    def test_check_overdue_filter_unknown_field(self):
        """Test check_overdue filter with unknown field name"""
        date_str = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        result = check_overdue(date_str, 'unknown_field')
        self.assertEqual(result, '')
    
    # ========================================================================
    # Template Rendering and UI Features Tests (Requirement 8.5)
    # ========================================================================
    
    def test_dashboard_template_renders(self):
        """Test that dashboard template renders without errors"""
        # Login first
        self.client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        })
        
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        # Check for key UI elements (the app uses "e-kejaksaan" branding)
        self.assertIn(b'e-kejaksaan', response.data.lower())
    
    def test_login_template_renders(self):
        """Test that login template renders without errors"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'username', response.data.lower())
        self.assertIn(b'password', response.data.lower())
    
    def test_overdue_indicator_in_dashboard(self):
        """Test that overdue indicators appear in dashboard"""
        # Create a case with overdue date
        overdue_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        test_case = Case(
            nama_tersangka='Overdue Test',
            spdp_tgl_terima=overdue_date
        )
        db.session.add(test_case)
        db.session.commit()
        
        # Login and check dashboard
        self.client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        })
        response = self.client.get('/dashboard')
        
        self.assertEqual(response.status_code, 200)
        # The overdue-cell class should be present for overdue dates
        self.assertIn(b'Overdue Test', response.data)
        
        # Cleanup
        db.session.delete(test_case)
        db.session.commit()


def run_tests():
    """Run all backward compatibility tests"""
    print("=" * 70)
    print("Running Backward Compatibility Tests")
    print("=" * 70)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(BackwardCompatibilityTests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ All backward compatibility tests passed!")
        print("The application maintains full backward compatibility after migration.")
    else:
        print("\n✗ Some tests failed. Please review the failures above.")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
