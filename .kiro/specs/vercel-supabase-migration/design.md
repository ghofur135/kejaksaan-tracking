# Design Document: Vercel & Supabase Migration

## Overview

Migrasi aplikasi Flask E-Kejaksaan dari SQLite lokal ke deployment serverless di Vercel dengan database PostgreSQL Supabase. Design ini mengadaptasi aplikasi yang awalnya dirancang untuk desktop/server tradisional menjadi serverless function yang stateless, dengan database cloud PostgreSQL.

Key changes:
- Database: SQLite → PostgreSQL (Supabase)
- Deployment: Local/Desktop → Vercel Serverless
- Configuration: Hardcoded → Environment Variables
- Session: Server-side → Cookie-based (Flask default sudah cookie-based)

## Architecture

### High-Level Architecture

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTPS
       ▼
┌─────────────────────────────────┐
│   Vercel Edge Network           │
│  ┌──────────────────────────┐   │
│  │  Serverless Function     │   │
│  │  (Flask WSGI App)        │   │
│  │  - Routes                │   │
│  │  - Authentication        │   │
│  │  - Business Logic        │   │
│  └──────────┬───────────────┘   │
└─────────────┼───────────────────┘
              │
              │ PostgreSQL Protocol
              ▼
┌─────────────────────────────────┐
│   Supabase PostgreSQL           │
│  - User table                   │
│  - Case table                   │
│  - Connection Pooling           │
└─────────────────────────────────┘
```

### Component Interaction

1. **User Request** → Vercel Edge Network
2. **Edge Network** → Cold start atau reuse existing serverless function
3. **Flask App** → Authenticate user via Flask-Login (cookie-based session)
4. **Flask App** → Query/Update PostgreSQL via SQLAlchemy
5. **Response** → Rendered HTML atau JSON response

## Components and Interfaces

### 1. Application Entry Point (app.py)

**Changes Required:**
- Remove desktop-specific code (`sys.frozen` checks)
- Remove SQLite-specific database configuration
- Add PostgreSQL connection string builder
- Remove manual `init_db()` call from `if __name__ == '__main__'`
- Keep WSGI app interface for Vercel

**New Configuration Logic:**
```python
# Environment variables
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-dev-key')

# Build PostgreSQL connection string
# Format: postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
def get_database_url():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")
    
    # Extract project ref from URL
    # https://wnqlufnhyjopsujokzrz.supabase.co → wnqlufnhyjopsujokzrz
    project_ref = SUPABASE_URL.replace('https://', '').replace('.supabase.co', '')
    
    # Supabase default password is the anon key for connection
    # Format: postgresql://postgres.[project-ref]:[anon-key]@aws-0-[region].pooler.supabase.com:6543/postgres
    # Simplified: postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres
    
    return f"postgresql://postgres:{SUPABASE_KEY}@db.{project_ref}.supabase.co:5432/postgres"

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
```

**Session Management:**
Flask-Login sudah menggunakan cookie-based session secara default, yang cocok untuk serverless. Tidak perlu perubahan pada authentication logic.

### 2. Database Models (models.py)

**Changes Required:**
- Minimal changes needed
- PostgreSQL compatible dengan semua tipe data yang digunakan
- `db.String()`, `db.Integer`, `db.Text`, `db.DateTime` semuanya compatible

**Potential Issues:**
- SQLite menggunakan `AUTOINCREMENT` untuk primary key, PostgreSQL menggunakan `SERIAL`
- SQLAlchemy akan handle ini secara otomatis
- Tidak perlu perubahan pada model definitions

### 3. Database Initialization

**Current Approach (SQLite):**
```python
def migrate_db():
    # ALTER TABLE untuk add columns
    conn.execute(db.text(f'ALTER TABLE "case" ADD COLUMN {col_name} {col_type}'))
```

**New Approach (PostgreSQL):**
```python
def init_db_tables():
    """Initialize database tables on first run"""
    try:
        with app.app_context():
            # Create all tables if not exist
            db.create_all()
            
            # Create admin user if not exists
            if not User.query.filter_by(username='admin').first():
                hashed_pw = generate_password_hash('12345', method='scrypt')
                admin = User(username='admin', password_hash=hashed_pw)
                db.session.add(admin)
                db.session.commit()
                print("Admin user created")
    except Exception as e:
        print(f"DB Init Error: {e}")
```

**Migration Strategy:**
- Remove `migrate_db()` function (SQLite-specific ALTER TABLE)
- Use `db.create_all()` untuk initial table creation
- Untuk production migrations, gunakan Alembic atau manual SQL di Supabase dashboard

### 4. Vercel Configuration (vercel.json)

**Current Configuration:**
```json
{
    "version": 2,
    "builds": [{"src": "app.py", "use": "@vercel/python"}],
    "routes": [{"src": "/(.*)", "dest": "app.py"}]
}
```

**Enhanced Configuration:**
```json
{
    "version": 2,
    "builds": [
        {
            "src": "app.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/static/(.*)",
            "dest": "/static/$1"
        },
        {
            "src": "/(.*)",
            "dest": "app.py"
        }
    ],
    "env": {
        "SUPABASE_URL": "@supabase-url",
        "SUPABASE_KEY": "@supabase-key",
        "SECRET_KEY": "@secret-key"
    }
}
```

**Note:** Environment variables akan di-set di Vercel dashboard, bukan di vercel.json (untuk security).

### 5. WSGI Entry Point

**Create new file: `api/index.py`** (Vercel convention)
```python
from app import app

# Vercel will call this
def handler(request, context):
    return app(request, context)
```

**Alternative (simpler):** Vercel dapat langsung menggunakan `app.py` jika Flask app instance bernama `app`.

### 6. Dependencies Update (requirements.txt)

**Remove:**
- `gunicorn` (tidak diperlukan di Vercel)
- `psycopg2-binary` (Vercel prefer non-binary)

**Add/Keep:**
- `psycopg2` (PostgreSQL adapter)
- `Flask`, `Flask-Login`, `Flask-SQLAlchemy`
- `python-dateutil`
- `Werkzeug`
- `SQLAlchemy`
- `python-dotenv` (untuk local development)

**Updated requirements.txt:**
```
Flask==2.3.3
Flask-Login==0.6.3
Flask-SQLAlchemy==3.1.1
psycopg2==2.9.9
python-dateutil==2.8.2
Werkzeug==2.3.7
SQLAlchemy==2.0.21
python-dotenv==1.0.0
```

## Data Models

No changes to data models. PostgreSQL fully supports existing schema:

**User Model:**
- `id`: INTEGER PRIMARY KEY (PostgreSQL: SERIAL)
- `username`: VARCHAR(150) UNIQUE NOT NULL
- `password_hash`: VARCHAR(200) NOT NULL

**Case Model:**
- `id`: INTEGER PRIMARY KEY (PostgreSQL: SERIAL)
- `nama_tersangka`: VARCHAR(200)
- `umur_tersangka`: INTEGER
- `pasal`: VARCHAR(200)
- `jpu`: VARCHAR(200)
- `spdp`: VARCHAR(200)
- `spdp_tgl_terima`: VARCHAR(50)
- `spdp_ket_terima`: VARCHAR(200)
- `spdp_tgl_polisi`: VARCHAR(50)
- `spdp_ket_polisi`: VARCHAR(200)
- `berkas_tahap_1`: VARCHAR(200)
- `p18_p19`: VARCHAR(200)
- `p21`: VARCHAR(200)
- `tahap_2`: VARCHAR(200)
- `limpah_pn`: VARCHAR(200)
- `keterangan`: TEXT
- `created_at`: TIMESTAMP DEFAULT NOW()

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Database Connection String Construction and Validity

*For any* valid Supabase credentials (URL and anon key), the system should construct a valid PostgreSQL connection string and successfully establish a database connection.

**Validates: Requirements 1.1, 1.2, 3.5**

### Property 2: Environment Variable Reading

*For any* required environment variable (SUPABASE_URL, SUPABASE_KEY, SECRET_KEY), the system should correctly read and use the value when it is set.

**Validates: Requirements 3.1, 3.2, 3.3**

### Property 3: Missing Environment Variable Error Handling

*For any* missing required environment variable (SUPABASE_URL or SUPABASE_KEY), the system should fail with a clear, descriptive error message indicating which variable is missing.

**Validates: Requirements 3.4**

### Property 4: PostgreSQL Data Type Compatibility

*For any* valid data value (string, integer, text, datetime), when stored in PostgreSQL and retrieved, the value should be identical to the original value.

**Validates: Requirements 1.5**

### Property 5: Route Preservation

*For all* existing routes (`/`, `/login`, `/logout`, `/dashboard`, `/add_case`, `/update_cell`), they should remain functional after migration with identical HTTP status codes and response behavior.

**Validates: Requirements 8.1**

### Property 6: CRUD Operations Preservation

*For any* valid case data (with all required fields), create, read, and update operations should produce the same results as the pre-migration SQLite system.

**Validates: Requirements 8.3**

### Property 7: Overdue Calculation Consistency

*For any* date string and field name combination, the overdue checking logic should produce identical results (overdue or not overdue) before and after migration.

**Validates: Requirements 8.4**

## Error Handling

### Database Connection Errors

**Scenario:** Supabase credentials invalid atau database unreachable

**Handling:**
```python
try:
    db.create_all()
except Exception as e:
    print(f"Database connection failed: {e}")
    # Vercel will show 500 error
    raise
```

### Missing Environment Variables

**Scenario:** SUPABASE_URL atau SUPABASE_KEY tidak di-set

**Handling:**
```python
def get_database_url():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "Missing required environment variables: SUPABASE_URL and SUPABASE_KEY. "
            "Please set them in Vercel dashboard."
        )
    return build_connection_string()
```

### Cold Start Performance

**Issue:** Serverless functions have cold start latency

**Mitigation:**
- Keep database connections lightweight
- Use Supabase connection pooling
- Minimize imports in app.py
- Consider Vercel's connection pooling features

### Session Persistence

**Issue:** Serverless functions are stateless

**Solution:** Flask-Login already uses cookie-based sessions (client-side storage), which is perfect for serverless. No changes needed.

## Testing Strategy

### Unit Tests

**Test Categories:**
1. **Configuration Tests**
   - Test `get_database_url()` with valid credentials
   - Test error handling for missing environment variables
   - Test SECRET_KEY fallback for development

2. **Database Connection Tests**
   - Test successful connection to Supabase
   - Test table creation
   - Test admin user creation

3. **Route Tests**
   - Test all existing routes return expected status codes
   - Test login flow
   - Test CRUD operations

4. **Utility Function Tests**
   - Test `parse_date()` with various formats
   - Test `is_date_overdue()` with different scenarios
   - Test `check_overdue()` template filter

### Property-Based Tests

**Property Test Framework:** Use `hypothesis` for Python property-based testing

**Configuration:**
- Minimum 100 iterations per property test
- Tag format: `# Feature: vercel-supabase-migration, Property {N}: {description}`

**Property Tests to Implement:**

1. **Property 1: Database Connection String Construction and Validity**
   ```python
   @given(st.text(min_size=10), st.text(min_size=20))
   def test_database_connection_string_construction(project_ref, anon_key):
       # Feature: vercel-supabase-migration, Property 1: Database Connection String Construction and Validity
       url = f"https://{project_ref}.supabase.co"
       conn_string = build_connection_string(url, anon_key)
       assert conn_string.startswith("postgresql://")
       assert project_ref in conn_string
   ```

2. **Property 3: Missing Environment Variable Error Handling**
   ```python
   @given(st.sampled_from(['SUPABASE_URL', 'SUPABASE_KEY']))
   def test_missing_env_var_error_message(missing_var):
       # Feature: vercel-supabase-migration, Property 3: Missing Environment Variable Error Handling
       with pytest.raises(ValueError) as exc_info:
           get_database_url_with_missing_var(missing_var)
       assert missing_var in str(exc_info.value)
   ```

3. **Property 4: PostgreSQL Data Type Compatibility**
   ```python
   @given(st.text(), st.integers(), st.datetimes())
   def test_postgresql_data_type_roundtrip(text_val, int_val, datetime_val):
       # Feature: vercel-supabase-migration, Property 4: PostgreSQL Data Type Compatibility
       case = Case(nama_tersangka=text_val, umur_tersangka=int_val, created_at=datetime_val)
       db.session.add(case)
       db.session.commit()
       
       retrieved = Case.query.get(case.id)
       assert retrieved.nama_tersangka == text_val
       assert retrieved.umur_tersangka == int_val
       assert retrieved.created_at == datetime_val
   ```

4. **Property 7: Overdue Calculation Consistency**
   ```python
   @given(st.dates(), st.sampled_from(['spdp', 'berkas_tahap_1', 'p18_p19', 'p21', 'tahap_2']))
   def test_overdue_calculation_consistency(date, field_name):
       # Feature: vercel-supabase-migration, Property 7: Overdue Calculation Consistency
       date_str = date.strftime('%Y-%m-%d')
       result = check_overdue(date_str, field_name)
       # Result should be either "overdue-cell" or ""
       assert result in ["overdue-cell", ""]
   ```

### Integration Tests

1. **End-to-End Login Flow**
   - Create test user in Supabase
   - Test login via POST /login
   - Verify session cookie
   - Test protected route access

2. **Case CRUD Operations**
   - Test add_case creates record in PostgreSQL
   - Test dashboard displays cases
   - Test update_cell modifies database
   - Verify data persistence

3. **Deployment Test**
   - Deploy to Vercel preview environment
   - Test all routes in deployed environment
   - Verify static files load correctly
   - Test database operations in production

### Manual Testing Checklist

- [ ] Deploy to Vercel successfully
- [ ] Environment variables set correctly
- [ ] Database tables created automatically
- [ ] Admin user can login
- [ ] Dashboard displays correctly
- [ ] CSS and JS files load
- [ ] Add new case works
- [ ] Edit case works
- [ ] Overdue indicators show correctly
- [ ] Logout works
- [ ] Session persists across page refreshes

## Deployment Steps

### 1. Prepare Supabase

1. Login to Supabase dashboard
2. Create tables manually (or let app create them):
   ```sql
   CREATE TABLE "user" (
       id SERIAL PRIMARY KEY,
       username VARCHAR(150) UNIQUE NOT NULL,
       password_hash VARCHAR(200) NOT NULL
   );
   
   CREATE TABLE "case" (
       id SERIAL PRIMARY KEY,
       nama_tersangka VARCHAR(200),
       umur_tersangka INTEGER,
       pasal VARCHAR(200),
       jpu VARCHAR(200),
       spdp VARCHAR(200),
       spdp_tgl_terima VARCHAR(50),
       spdp_ket_terima VARCHAR(200),
       spdp_tgl_polisi VARCHAR(50),
       spdp_ket_polisi VARCHAR(200),
       berkas_tahap_1 VARCHAR(200),
       p18_p19 VARCHAR(200),
       p21 VARCHAR(200),
       tahap_2 VARCHAR(200),
       limpah_pn VARCHAR(200),
       keterangan TEXT,
       created_at TIMESTAMP DEFAULT NOW()
   );
   ```

### 2. Update Code

1. Modify `app.py` - remove desktop code, add PostgreSQL config
2. Update `requirements.txt` - change psycopg2-binary to psycopg2
3. Update `vercel.json` - ensure correct routing
4. Create `.env` for local testing:
   ```
   SUPABASE_URL=https://wnqlufnhyjopsujokzrz.supabase.co
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   SECRET_KEY=your-secret-key-here
   ```

### 3. Deploy to Vercel

1. Push code to GitHub
2. Import project to Vercel
3. Set environment variables in Vercel dashboard:
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SECRET_KEY`
4. Deploy

### 4. Verify Deployment

1. Visit deployed URL
2. Check logs for database connection
3. Test login with admin/12345
4. Test creating a case
5. Test editing a case

## References

- [Vercel Python Deployment Guide](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Supabase SQLAlchemy Integration](https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase)
- [Flask-Login Documentation](https://flask-login.readthedocs.io/)
- [Vercel Application Authentication](https://vercel.com/guides/application-authentication-on-vercel)

*Content was rephrased for compliance with licensing restrictions*
