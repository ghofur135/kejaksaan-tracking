from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from extensions import db, login_manager
from models import User, Case
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from dateutil import parser
import re

import os
import sys

# Define base path for resources (templates/static)
if getattr(sys, 'frozen', False):
    # Running as compiled .exe
    # PyInstaller extracts data to sys._MEIPASS
    base_dir = sys._MEIPASS
    template_dir = os.path.join(base_dir, 'templates')
    static_dir = os.path.join(base_dir, 'static')
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
else:
    # Running normal python script
    app = Flask(__name__, template_folder='templates', static_folder='static')

app.config['SECRET_KEY'] = 'kejaksaan-secret-key-123'

# Database Configuration Logic
if getattr(sys, 'frozen', False):
    # Mode: Desktop App (.exe)
    # Store database next to the executable file
    exe_dir = os.path.dirname(sys.executable)
    db_path = os.path.join(exe_dir, 'kejaksaan.db')
    # Use forward slashes for SQLite URI to avoid Windows backslash issues
    db_path = db_path.replace('\\', '/')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
else:
    # Mode: Web Server / Development
    # Use DATABASE_URL if provided (Railway/Heroku), else fall back to local instance
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)  # Fix for some platforms
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///kejaksaan.db'

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
    delta = datetime.now() - date_obj
    return delta.days > days_limit

@app.template_filter('check_overdue')
def check_overdue(value, field_name):
    """
    Filter to check if a field is overdue.
    Usage: {{ case.spdp | check_overdue('spdp') }}
    Returns: 'overdue-cell' if true, else ''
    """
    date_obj = parse_date(value)
    if not date_obj:
        return ""
    
    limits = {
        'spdp': 25, # Overdue jika: Hari Ini > (Tgl SPDP + 25 hari)
        'berkas_tahap_1': 6,
        'p18_p19': 10,
        'p21': 12,
        'tahap_2': 7
    }
    
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
    cases = Case.query.order_by(Case.created_at.desc()).all()
    return render_template('dashboard.html', cases=cases)

@app.route('/add_case', methods=['POST'])
@login_required
def add_case():
    nama = request.form.get('nama_tersangka')
    umur = request.form.get('umur_tersangka')
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
        'nama_tersangka', 'umur_tersangka', 'pasal', 'jpu' # Allow editing text fields
    ]
    if field not in allowed_fields:
        return jsonify({'success': False, 'error': 'Field not editable'}), 403
        
    setattr(case, field, value)
    db.session.commit()
    return jsonify({'success': True})

def create_admin():
    # Helper to create default admin
    if not User.query.filter_by(username='admin').first():
        hashed_pw = generate_password_hash('12345', method='scrypt')
        admin = User(username='admin', password_hash=hashed_pw)
        db.session.add(admin)
        db.session.commit()
        print("Admin user created (admin/12345)")

def migrate_db():
    """Check for missing columns and add them (SQLite Migration)"""
    inspector = db.inspect(db.engine)
    columns = [col['name'] for col in inspector.get_columns('case')]
    
    new_cols = {
        'spdp_tgl_terima': 'VARCHAR(50)',
        'spdp_ket_terima': 'VARCHAR(200)',
        'spdp_tgl_polisi': 'VARCHAR(50)',
        'spdp_ket_polisi': 'VARCHAR(200)',
        'umur_tersangka': 'INTEGER',
        'jpu': 'VARCHAR(200)'
    }
    
    with db.engine.connect() as conn:
        for col_name, col_type in new_cols.items():
            if col_name not in columns:
                print(f"Migrating: Adding {col_name} to case table...")
                # Use double quotes for table name "case" because it is a reserved keyword in SQL
                conn.execute(db.text(f'ALTER TABLE "case" ADD COLUMN {col_name} {col_type}'))
                conn.commit()

def init_db():
    try:
        with app.app_context():
            db.create_all()
            create_admin()
            migrate_db() # Run migration check
    except Exception as e:
        print(f"DB Init Error: {e}")

# Auto-initialize DB if running as frozen app (desktop) to ensure tables exist
if getattr(sys, 'frozen', False):
    init_db()

if __name__ == '__main__':
    # Initialize DB (Create tables + Migrate calls)
    init_db()
    app.run(debug=True)
