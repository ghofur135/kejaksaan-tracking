# Implementation Plan: Vercel & Supabase Migration

## Overview

Migrasi aplikasi Flask dari SQLite lokal ke Vercel serverless dengan database PostgreSQL Supabase. Implementasi akan dilakukan secara incremental, dimulai dari konfigurasi database, kemudian update dependencies, lalu deployment configuration, dan terakhir testing.

## Tasks

- [x] 1. Setup environment configuration dan database connection
  - Create `.env.example` file dengan template environment variables
  - Update `app.py` untuk read environment variables (SUPABASE_URL, SUPABASE_KEY, SECRET_KEY)
  - Implement `get_database_url()` function untuk build PostgreSQL connection string dari Supabase credentials
  - Remove desktop-specific code (`sys.frozen` checks) dari `app.py`
  - Update database configuration untuk use PostgreSQL connection string
  - _Requirements: 1.1, 1.2, 2.2, 3.1, 3.2, 3.3, 3.5_

- [ ]* 1.1 Write property test for database connection string construction
  - **Property 1: Database Connection String Construction and Validity**
  - Test that valid Supabase credentials produce valid PostgreSQL connection string
  - _Requirements: 1.1, 1.2, 3.5_

- [ ]* 1.2 Write property test for environment variable reading
  - **Property 2: Environment Variable Reading**
  - Test that all required environment variables are correctly read when set
  - _Requirements: 3.1, 3.2, 3.3_

- [ ]* 1.3 Write property test for missing environment variable error handling
  - **Property 3: Missing Environment Variable Error Handling**
  - Test that missing required env vars produce clear error messages
  - _Requirements: 3.4_

- [x] 2. Update dependencies dan requirements
  - Update `requirements.txt`: remove `gunicorn` dan `psycopg2-binary`
  - Add `psycopg2` (without binary) to requirements.txt
  - Ensure `python-dotenv` is in requirements.txt untuk local development
  - Verify all Flask dependencies (Flask, Flask-Login, Flask-SQLAlchemy) are present
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ]* 2.1 Write unit tests for requirements.txt validation
  - Test that psycopg2 (not psycopg2-binary) is in requirements
  - Test that gunicorn is NOT in requirements
  - Test that all required Flask packages are present
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 3. Update database initialization logic
  - Remove `migrate_db()` function (SQLite-specific ALTER TABLE logic)
  - Update `init_db()` function untuk use `db.create_all()` only
  - Ensure `create_admin()` function remains idempotent
  - Remove desktop-specific `init_db()` call from `if getattr(sys, 'frozen', False)` block
  - Keep `init_db()` call in `if __name__ == '__main__'` for local development
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 3.1 Write unit tests for database initialization
  - Test that `db.create_all()` creates tables successfully
  - Test that admin user is created when not exists
  - Test that admin user is not duplicated on multiple runs
  - _Requirements: 4.1, 4.2_

- [x] 4. Checkpoint - Test database connection locally
  - Create `.env` file dengan Supabase credentials untuk local testing
  - Run application locally dan verify database connection
  - Verify tables are created in Supabase
  - Verify admin user is created
  - Ensure all tests pass, ask the user if questions arise

- [x] 5. Update Vercel configuration
  - Update `vercel.json` dengan static file routing
  - Add route untuk `/static/(.*)` to serve static files
  - Ensure main route `/(.*)`  points to `app.py`
  - Remove desktop-specific template/static folder logic dari `app.py`
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 7.1, 7.2_

- [ ]* 5.1 Write unit tests for static file routing
  - Test that CSS files are accessible via `/static/css/style.css`
  - Test that JS files are accessible via `/static/js/script.js`
  - _Requirements: 5.1, 5.2_

- [x] 6. Create deployment documentation
  - Create `DEPLOYMENT.md` dengan step-by-step deployment guide
  - Document environment variables yang perlu di-set di Vercel dashboard
  - Document Supabase table creation SQL (optional, karena `db.create_all()` will handle it)
  - Add troubleshooting section untuk common issues
  - _Requirements: 7.3_

- [x] 7. Implement backward compatibility tests
  - Test all existing routes (`/`, `/login`, `/logout`, `/dashboard`, `/add_case`, `/update_cell`)
  - Test login functionality dengan admin credentials
  - Test case CRUD operations (create, read, update)
  - Test overdue checking logic dengan sample dates
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 7.1 Write property test for route preservation
  - **Property 5: Route Preservation**
  - Test that all existing routes return expected status codes
  - _Requirements: 8.1_

- [ ]* 7.2 Write property test for CRUD operations preservation
  - **Property 6: CRUD Operations Preservation**
  - Test that case create, read, update operations work correctly
  - _Requirements: 8.3_

- [ ]* 7.3 Write property test for overdue calculation consistency
  - **Property 7: Overdue Calculation Consistency**
  - Test that overdue logic produces correct results for various dates
  - _Requirements: 8.4_

- [ ]* 7.4 Write property test for PostgreSQL data type compatibility
  - **Property 4: PostgreSQL Data Type Compatibility**
  - Test that all data types (string, integer, text, datetime) round-trip correctly
  - _Requirements: 1.5_

- [x] 8. Checkpoint - Run all tests
  - Run all unit tests dan ensure they pass
  - Run all property-based tests dengan minimum 100 iterations
  - Fix any failing tests
  - Ensure all tests pass, ask the user if questions arise

- [ ] 9. Deploy to Vercel
  - Push code to GitHub repository
  - Import project to Vercel dashboard
  - Set environment variables di Vercel (SUPABASE_URL, SUPABASE_KEY, SECRET_KEY)
  - Trigger deployment
  - Monitor deployment logs untuk errors
  - _Requirements: 7.3_

- [ ] 10. Post-deployment verification
  - Visit deployed URL dan verify application loads
  - Test login dengan admin/12345
  - Test creating a new case
  - Test editing an existing case
  - Test overdue indicators display correctly
  - Verify static files (CSS, JS) load correctly
  - Check browser console untuk errors
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 11. Update README.md
  - Update deployment section dengan Vercel instructions
  - Update database section dengan Supabase information
  - Add environment variables documentation
  - Remove desktop app references
  - Add link to DEPLOYMENT.md
  - _Requirements: 7.3_

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties
- Unit tests validate specific examples and edge cases
- Environment variables MUST be set di Vercel dashboard sebelum deployment
- Local testing requires `.env` file dengan Supabase credentials
