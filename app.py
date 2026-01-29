from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from extensions import db, login_manager
from models import User, Case
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from dateutil import parser
from sqlalchemy.pool import NullPool
from urllib.parse import quote_plus
import re
import os

# Load environment variables from .env file for local development
from dotenv import load_dotenv
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Embedded credentials for .exe build (will be replaced by build script)
EMBEDDED_DATABASE_URL = None  # Will be set by build_exe.py
EMBEDDED_SECRET_KEY = None    # Will be set by build_exe.py

# Read environment variables (prioritize embedded for .exe, fallback to .env for dev)
DATABASE_URL = EMBEDDED_DATABASE_URL or os.environ.get('DATABASE_URL')
SUPABASE_DB_PASSWORD = os.environ.get('SUPABASE_DB_PASSWORD')
SUPABASE_PROJECT_REF = os.environ.get('SUPABASE_PROJECT_REF')
SECRET_KEY = EMBEDDED_SECRET_KEY or os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

app.config['SECRET_KEY'] = SECRET_KEY

def get_database_url():
    """
    Build PostgreSQL connection string for Supabase.
    
    Based on Supabase best practices:
    https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase
    
    For serverless/Vercel: Use Transaction Mode Pooler (port 6543) with NullPool
    
    Returns:
        str: PostgreSQL connection string
        
    Raises:
        ValueError: If required environment variables are missing
    """
    # Method 1: Use DATABASE_URL directly (recommended)
    if DATABASE_URL:
        # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
        if DATABASE_URL.startswith("postgres://"):
            return DATABASE_URL.replace("postgres://", "postgresql://", 1)
        return DATABASE_URL
    
    # Method 2: Build from components
    if SUPABASE_DB_PASSWORD and SUPABASE_PROJECT_REF:
        # URL encode password to handle special characters
        encoded_password = quote_plus(SUPABASE_DB_PASSWORD)
        
        # Use Transaction Mode Pooler (port 6543) for serverless
        # Format: postgresql://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:6543/postgres
        return f"postgresql://postgres.{SUPABASE_PROJECT_REF}:{encoded_password}@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
    
    raise ValueError(
        "Missing required environment variables for database connection.\n"
        "Please set one of the following:\n"
        "  1. DATABASE_URL - full connection string from Supabase dashboard (Settings > Database > Connection string > Transaction)\n"
        "  2. SUPABASE_DB_PASSWORD and SUPABASE_PROJECT_REF\n"
    )

# Database Configuration
# Use NullPool for serverless/transaction mode as per Supabase best practices
app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': NullPool,  # Required for Supabase Transaction Mode Pooler
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def parse_date(date_str):
    """
    Robust date parser using dateutil.
    Handles YYYY-MM-DD (ISO) and DD-MM-YYYY formats.
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    try:
        # Check for ISO format YYYY-MM-DD via regex to avoid ambiguity
        if isinstance(date_str, str) and re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            return parser.parse(date_str, yearfirst=True, dayfirst=False)
            
        # Fallback: parser is smart enough to handle most formats
        # dayfirst=True ensures 01/02/2023 is treated as 1st Feb
        return parser.parse(date_str, dayfirst=True)
    except (ValueError, TypeError):
        return None

def is_date_overdue(date_obj, days_limit):
    if not date_obj:
        return False
    # Hitung tanggal deadline: tanggal input + (days_limit - 1) hari
    # Karena hari input sudah dihitung sebagai hari ke-1
    deadline = date_obj + timedelta(days=days_limit - 1)
    # Cek apakah hari ini sudah melewati deadline
    return datetime.now().date() > deadline.date()

@app.template_filter('check_overdue')
def check_overdue(value, field_name, kategori_umur='Dewasa'):
    """
    Filter to check if a field is overdue.
    Usage: {{ case.spdp | check_overdue('spdp', case.kategori_umur) }}
    Returns: 'overdue-cell' if true, else ''
    """
    date_obj = parse_date(value)
    if not date_obj:
        return ""
    
    # Logic untuk Dewasa (default)
    limits_dewasa = {
        'spdp': 25,             # Overdue jika: Hari Ini > (Tgl Input + 24 hari) - SPDP 25 hari kalender
        'berkas_tahap_1': 6,    # Overdue jika: Hari Ini > (Tgl Input + 5 hari) - Berkas Tahap I 6 hari kalender  
        'p18_p19': 10,          # Overdue jika: Hari Ini > (Tgl Input + 9 hari) - P-18/P-19 10 hari kalender
        'p21': 12,              # Overdue jika: Hari Ini > (Tgl Input + 11 hari) - P-21 12 hari kalender
        'tahap_2': 7            # Overdue jika: Hari Ini > (Tgl Input + 6 hari) - Tahap II 7 hari kalender
    }
    
    # Logic untuk Anak
    limits_anak = {
        'spdp': 25,             # SPDP tetap 25 hari
        'berkas_tahap_1': 3,    # Berkas Tahap I 3 hari kalender
        'p18_p19': 7,           # P-18/P-19 7 hari kalender
        'p21': 10,              # P-21 10 hari kalender
        'tahap_2': 5            # Tahap II 5 hari kalender
    }
    
    # Pilih limits berdasarkan kategori umur
    limits = limits_anak if kategori_umur == 'Anak' else limits_dewasa
    
    limit = limits.get(field_name)
    if limit and is_date_overdue(date_obj, limit):
        return "overdue-cell"
    return ""

@app.route('/')
@login_required
def index():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Validate per_page values
        if per_page not in [10, 30, 50, 100]:
            per_page = 10
        
        # Validate page number
        if page < 1:
            page = 1
        
        # Query with pagination
        pagination = Case.query.order_by(Case.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return render_template('dashboard.html', 
                             cases=pagination.items,
                             pagination=pagination,
                             per_page=per_page)
    except Exception as e:
        # Log error for debugging
        print(f"Dashboard error: {str(e)}")
        # Fallback to simple query without pagination
        cases = Case.query.order_by(Case.created_at.desc()).limit(10).all()
        # Create a simple pagination object
        class SimplePagination:
            def __init__(self, items):
                self.items = items
                self.page = 1
                self.per_page = 10
                self.total = len(items)
                self.pages = 1
                self.has_prev = False
                self.has_next = False
                self.prev_num = None
                self.next_num = None
        
        pagination = SimplePagination(cases)
        return render_template('dashboard.html', 
                             cases=cases,
                             pagination=pagination,
                             per_page=10)

@app.route('/add_case', methods=['POST'])
@login_required
def add_case():
    nama = request.form.get('nama_tersangka')
    umur = request.form.get('umur_tersangka')
    kategori_umur = request.form.get('kategori_umur', 'Dewasa')
    pasal = request.form.get('pasal')
    jpu = request.form.get('jpu')
    
    # New SPDP Inputs
    tgl_terima = request.form.get('spdp_tgl_terima')
    ket_terima = request.form.get('spdp_ket_terima')
    tgl_polisi = request.form.get('spdp_tgl_polisi')
    ket_polisi = request.form.get('spdp_ket_polisi')
    
    new_case = Case(
        nama_tersangka=nama,
        umur_tersangka=umur,
        kategori_umur=kategori_umur,
        pasal=pasal,
        jpu=jpu,
        spdp_tgl_terima=tgl_terima,
        spdp_ket_terima=ket_terima,
        spdp_tgl_polisi=tgl_polisi,
        spdp_ket_polisi=ket_polisi,
        # Construct legacy string for backward compat display if needed, or leave empty
        spdp=f"{ket_terima} ({tgl_terima})" if ket_terima else tgl_terima
    )
    db.session.add(new_case)
    db.session.commit()
    flash('Data berhasil ditambahkan!')
    return redirect(url_for('dashboard'))

@app.route('/update_cell', methods=['POST'])
@login_required
def update_cell():
    data = request.json
    case_id = data.get('id')
    field = data.get('field')
    value = data.get('value')
    
    if not case_id or not field:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
        
    case = Case.query.get(case_id)
    if not case:
        return jsonify({'success': False, 'error': 'Case not found'}), 404
        
    # Security: Ensure field is allowed
    # Allowed: Existing stages + New SPDP fields
    allowed_fields = [
        'berkas_tahap_1', 'p18_p19', 'p21', 'tahap_2', 'limpah_pn', 'keterangan',
        'spdp_tgl_terima', 'spdp_tgl_polisi', # Allow editing dates via modal
        'nama_tersangka', 'umur_tersangka', 'kategori_umur', 'pasal', 'jpu' # Allow editing text fields
    ]
    if field not in allowed_fields:
        return jsonify({'success': False, 'error': 'Field not editable'}), 403
        
    setattr(case, field, value)
    db.session.commit()
    return jsonify({'success': True})

@app.route('/delete_case/<int:case_id>', methods=['DELETE'])
@login_required
def delete_case(case_id):
    case = Case.query.get(case_id)
    if not case:
        return jsonify({'success': False, 'error': 'Case not found'}), 404
    
    try:
        db.session.delete(case)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Data berhasil dihapus'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

def create_admin():
    """Create default admin user if not exists"""
    if not User.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('12345', method='scrypt')
        admin = User(username='admin', password_hash=hashed_pw)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created (admin/12345)")

def init_db():
    """Initialize database tables on first run"""
    try:
        with app.app_context():
            db.create_all()
            create_admin()
    except Exception as e:
        print(f"DB Init Error: {e}")

if __name__ == '__main__':
    # Initialize DB (Create tables + admin user)
    init_db()
    app.run(debug=True)
