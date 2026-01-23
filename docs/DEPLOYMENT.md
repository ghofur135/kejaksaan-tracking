# Deployment Guide: Vercel & Supabase

## Overview

Aplikasi Flask E-Kejaksaan telah berhasil dikonfigurasi untuk deployment ke Vercel dengan database PostgreSQL Supabase.

## 📑 Quick Navigation

- [Local Development Setup](#-local-development-setup) - Setup aplikasi di local machine
- [Vercel Deployment](#-vercel-deployment) - Deploy ke production
- [Database Schema](#-database-schema) - SQL table definitions
- [Troubleshooting](#-troubleshooting) - Common issues dan solutions
- [Configuration Files](#-configuration-files) - vercel.json dan requirements.txt
- [Deployment Checklist](#-deployment-checklist) - Pre-deployment verification

## ✅ Yang Sudah Dikonfigurasi

### 1. Environment Configuration
- ✓ File `.env.example` dengan template environment variables
- ✓ `python-dotenv` untuk load environment variables
- ✓ Support untuk `DATABASE_URL` dari Supabase

### 2. Database Connection
- ✓ PostgreSQL connection menggunakan Supabase Transaction Mode Pooler
- ✓ NullPool configuration untuk serverless compatibility
- ✓ Automatic table creation dengan `db.create_all()`
- ✓ Admin user creation (username: admin, password: 12345)

### 3. Code Changes
- ✓ Removed desktop-specific code (`sys.frozen` checks)
- ✓ Removed SQLite-specific migration code
- ✓ Updated database configuration untuk PostgreSQL
- ✓ URL encoding untuk password dengan karakter khusus

## 📋 Local Development Setup

### Prerequisites
- Python 3.8+
- Supabase account dengan project aktif

### Steps

1. **Clone repository**
   ```bash
   git clone <repository-url>
   cd kejaksaan-app2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   
   Copy `.env.example` ke `.env`:
   ```bash
   copy .env.example .env
   ```
   
   Update `.env` dengan credentials Supabase Anda:
   ```env
   DATABASE_URL=postgresql://postgres.your-project-ref:your-password@aws-1-region.pooler.supabase.com:6543/postgres
   SECRET_KEY=your-secret-key-here
   ```
   
   **Cara mendapatkan DATABASE_URL:**
   - Buka https://supabase.com/dashboard
   - Pilih project Anda
   - Settings > Database > Connection string > **Transaction** tab
   - Copy connection string lengkap

4. **Initialize database**
   ```bash
   python app.py
   ```
   
   Ini akan:
   - Create tables (`user` dan `case`)
   - Create admin user (admin/12345)

5. **Run application**
   ```bash
   python app.py
   ```
   
   Open browser: http://localhost:5000

## 🚀 Vercel Deployment

### Prerequisites
- Vercel account
- GitHub repository dengan code ini
- Supabase project dengan database aktif

### Steps

1. **Push code ke GitHub**
   ```bash
   git add .
   git commit -m "Configure for Vercel deployment"
   git push origin main
   ```

2. **Import project ke Vercel**
   - Go to https://vercel.com/dashboard
   - Click "Add New" > "Project"
   - Import your GitHub repository
   - Framework Preset: **Other**

3. **Configure Environment Variables**
   
   Di Vercel project settings, tambahkan environment variables:
   
   | Name | Value | Description |
   |------|-------|-------------|
   | `DATABASE_URL` | `postgresql://postgres.your-project-ref:your-password@aws-1-region.pooler.supabase.com:6543/postgres` | Supabase PostgreSQL connection string (Transaction mode) |
   | `SECRET_KEY` | `your-secret-key-here` | Flask secret key untuk session encryption (generate random string) |
   
   **Cara set environment variables di Vercel:**
   - Project Settings > Environment Variables
   - Add each variable dengan Name dan Value
   - Select environment: Production, Preview, Development (pilih semua)
   - Click "Save"
   
   **PENTING:** 
   - Gunakan connection string dari Supabase dashboard (Transaction mode)
   - Jika password mengandung karakter khusus (#, !, @, $, %), encode dengan URL encoding:
     - `#` → `%23`
     - `!` → `%21`
     - `@` → `%40`
     - `$` → `%24`
     - `%` → `%25`
   - Generate secure SECRET_KEY: `python -c "import secrets; print(secrets.token_hex(32))"`

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Vercel akan automatically run `db.create_all()` on first request

5. **Verify Deployment**
   - Visit deployed URL
   - Login dengan admin/12345
   - Test creating a case
   - Verify data persists di Supabase

## 🔧 Configuration Files

### vercel.json
```json
{
    "version": 2,
    "builds": [{"src": "app.py", "use": "@vercel/python"}],
    "routes": [{"src": "/(.*)", "dest": "app.py"}]
}
```

### requirements.txt
Key dependencies:
- Flask==2.3.3
- Flask-SQLAlchemy==3.1.1
- psycopg2-binary==2.9.9 (untuk Vercel)
- python-dotenv==1.0.0

## 📊 Database Schema

Tables akan dibuat otomatis oleh `db.create_all()` saat aplikasi pertama kali dijalankan. Jika ingin manually create tables di Supabase SQL Editor, gunakan SQL berikut:

### Table: user
```sql
CREATE TABLE IF NOT EXISTS "user" (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(200) NOT NULL
);
```

### Table: case
```sql
CREATE TABLE IF NOT EXISTS "case" (
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

**Note:** Manual table creation adalah optional. Aplikasi akan automatically create tables menggunakan SQLAlchemy's `db.create_all()` method.

## 🐛 Troubleshooting

### Error: "Tenant or user not found"
**Cause:** Connection string format salah atau credentials tidak valid

**Solution:**
1. Verify connection string dari Supabase dashboard
2. Pastikan menggunakan **Transaction mode** (port 6543)
3. Verify database password benar
4. Check project reference ID matches your Supabase project

### Error: "password authentication failed"
**Cause:** Database password salah atau tidak di-encode dengan benar

**Solution:**
1. Reset database password di Supabase dashboard
2. Jika password mengandung karakter khusus, encode dengan URL encoding:
   - `#` → `%23`
   - `!` → `%21`
   - `@` → `%40`
   - `$` → `%24`
   - `%` → `%25`
3. Update `DATABASE_URL` dengan password yang sudah di-encode
4. Redeploy ke Vercel

### Error: "no pg_hba.conf entry"
**Cause:** IP address tidak diizinkan

**Solution:**
1. Supabase dashboard > Settings > Database
2. Enable "Allow all IP addresses" (untuk production, configure specific IPs)
3. Atau tambahkan Vercel IP ranges ke allowlist

### Tables tidak dibuat otomatis
**Cause:** `init_db()` tidak dipanggil atau error saat table creation

**Solution:**
1. Jalankan aplikasi sekali: `python app.py`
2. Atau manually run:
   ```python
   from app import app, db
   with app.app_context():
       db.create_all()
   ```
3. Check Vercel logs untuk error messages
4. Verify DATABASE_URL environment variable is set correctly

### Error: "500 Internal Server Error" di Vercel
**Cause:** Environment variables tidak di-set atau database connection gagal

**Solution:**
1. Check Vercel logs: Project > Deployments > Click deployment > View Function Logs
2. Verify environment variables di Vercel dashboard
3. Test DATABASE_URL locally dengan connection string yang sama
4. Check Supabase database status (Settings > Database)

### Static files (CSS/JS) tidak load
**Cause:** Routing configuration salah atau file path tidak benar

**Solution:**
1. Verify `vercel.json` contains static file routing
2. Check browser console untuk 404 errors
3. Verify file paths di templates menggunakan `url_for('static', filename='...')`
4. Clear browser cache dan reload

### Session tidak persist / Login tidak bertahan
**Cause:** SECRET_KEY tidak di-set atau berubah setiap deployment

**Solution:**
1. Set SECRET_KEY environment variable di Vercel
2. Gunakan SECRET_KEY yang sama untuk semua deployments
3. Verify cookies are enabled di browser
4. Check HTTPS is enabled (required untuk secure cookies)

### Database connection pool exhausted
**Cause:** Too many concurrent connections

**Solution:**
1. Aplikasi sudah menggunakan NullPool untuk serverless
2. Verify Supabase connection limits (Settings > Database > Connection pooling)
3. Consider upgrading Supabase plan jika traffic tinggi
4. Monitor connection usage di Supabase dashboard

## 📝 Notes

### Supabase Connection Modes
- **Transaction Mode (port 6543)**: Recommended untuk serverless (Vercel)
- **Session Mode (port 5432)**: Untuk long-running servers
- **Direct Connection**: Untuk local development

### SQLAlchemy Pool Configuration
Aplikasi menggunakan `NullPool` untuk serverless compatibility:
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'poolclass': NullPool,
}
```

### Security
- ⚠️ Change default admin password (admin/12345) setelah deployment
- ⚠️ Generate secure `SECRET_KEY` untuk production
- ⚠️ Jangan commit `.env` file ke repository

## 🔗 References

- [Supabase SQLAlchemy Guide](https://supabase.com/docs/guides/troubleshooting/using-sqlalchemy-with-supabase)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [Flask-SQLAlchemy Documentation](https://flask-sqlalchemy.palletsprojects.com/)

## ✅ Deployment Checklist

- [ ] Code pushed ke GitHub
- [ ] Vercel project created
- [ ] Environment variables configured di Vercel
- [ ] Deployment successful
- [ ] Database tables created
- [ ] Admin user dapat login
- [ ] CRUD operations berfungsi
- [ ] Static files (CSS/JS) load correctly
- [ ] Change default admin password
- [ ] Configure production SECRET_KEY
