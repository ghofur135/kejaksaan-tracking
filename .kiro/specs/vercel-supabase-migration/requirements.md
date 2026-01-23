# Requirements Document: Vercel & Supabase Migration

## Introduction

Migrasi aplikasi Flask E-Kejaksaan Case Tracking System dari SQLite lokal ke deployment Vercel dengan database PostgreSQL Supabase. Aplikasi saat ini menggunakan SQLite dan dirancang untuk berjalan sebagai desktop app atau web server lokal. Migrasi ini akan mengubah aplikasi menjadi serverless function di Vercel dengan database cloud PostgreSQL.

## Glossary

- **System**: Aplikasi Flask E-Kejaksaan Case Tracking
- **Vercel**: Platform serverless deployment untuk aplikasi web
- **Supabase**: Platform database PostgreSQL cloud dengan API built-in
- **SQLAlchemy**: ORM Python untuk database operations
- **WSGI**: Web Server Gateway Interface untuk aplikasi Python
- **Serverless_Function**: Function yang berjalan on-demand tanpa server persistent
- **Environment_Variables**: Variabel konfigurasi yang disimpan di platform deployment

## Requirements

### Requirement 1: Database Migration to PostgreSQL

**User Story:** Sebagai developer, saya ingin mengubah database dari SQLite ke PostgreSQL Supabase, sehingga aplikasi dapat berjalan di environment serverless dengan database cloud.

#### Acceptance Criteria

1. THE System SHALL connect to Supabase PostgreSQL database using provided credentials
2. WHEN the application starts, THE System SHALL use connection string format compatible with PostgreSQL
3. THE System SHALL remove SQLite-specific code and configurations
4. THE System SHALL maintain all existing table structures (User, Case) in PostgreSQL
5. THE System SHALL handle PostgreSQL-specific data types correctly

### Requirement 2: Vercel Serverless Compatibility

**User Story:** Sebagai developer, saya ingin aplikasi dapat berjalan sebagai serverless function di Vercel, sehingga aplikasi dapat di-deploy tanpa mengelola server.

#### Acceptance Criteria

1. THE System SHALL expose WSGI application interface for Vercel Python runtime
2. THE System SHALL remove desktop app specific code (sys.frozen checks)
3. WHEN deployed to Vercel, THE System SHALL initialize database connections properly
4. THE System SHALL handle serverless cold starts efficiently
5. THE System SHALL use environment variables for sensitive configuration

### Requirement 3: Environment Configuration

**User Story:** Sebagai developer, saya ingin konfigurasi sensitif disimpan sebagai environment variables, sehingga credentials tidak ter-commit ke repository.

#### Acceptance Criteria

1. THE System SHALL read Supabase URL from environment variable
2. THE System SHALL read Supabase anon key from environment variable
3. THE System SHALL read secret key from environment variable
4. WHEN environment variables are missing, THE System SHALL provide clear error messages
5. THE System SHALL construct PostgreSQL connection string from Supabase credentials

### Requirement 4: Database Initialization

**User Story:** Sebagai developer, saya ingin database tables dibuat otomatis saat pertama kali deploy, sehingga tidak perlu manual migration.

#### Acceptance Criteria

1. WHEN the application first runs, THE System SHALL create all required tables
2. THE System SHALL create default admin user if not exists
3. THE System SHALL handle database initialization errors gracefully
4. THE System SHALL not run desktop-specific migration code in serverless environment
5. THE System SHALL use PostgreSQL-compatible ALTER TABLE syntax

### Requirement 5: Static Files Handling

**User Story:** Sebagai developer, saya ingin static files (CSS, JS) dapat diakses dengan benar di Vercel, sehingga UI aplikasi tampil dengan baik.

#### Acceptance Criteria

1. THE System SHALL serve static files through Vercel routing configuration
2. THE System SHALL maintain correct paths for CSS and JavaScript files
3. WHEN templates are rendered, THE System SHALL use correct static file URLs
4. THE System SHALL remove desktop-specific template/static path logic

### Requirement 6: Dependencies Management

**User Story:** Sebagai developer, saya ingin dependencies yang tidak diperlukan dihapus, sehingga deployment lebih cepat dan efisien.

#### Acceptance Criteria

1. THE System SHALL remove psycopg2-binary from requirements
2. THE System SHALL add psycopg2 (without binary) for Vercel compatibility
3. THE System SHALL remove gunicorn (tidak diperlukan di Vercel)
4. THE System SHALL maintain all Flask dependencies yang diperlukan
5. THE System SHALL add python-dotenv untuk local development

### Requirement 7: Vercel Configuration

**User Story:** Sebagai developer, saya ingin konfigurasi Vercel yang tepat, sehingga routing dan build process berjalan dengan benar.

#### Acceptance Criteria

1. THE System SHALL have vercel.json with correct Python runtime configuration
2. THE System SHALL route all requests to WSGI application
3. THE System SHALL configure environment variables di Vercel dashboard
4. THE System SHALL exclude unnecessary files from deployment

### Requirement 8: Backward Compatibility

**User Story:** Sebagai user, saya ingin semua fitur existing tetap berfungsi setelah migrasi, sehingga tidak ada disruption pada workflow.

#### Acceptance Criteria

1. THE System SHALL maintain all existing routes and endpoints
2. THE System SHALL preserve login functionality
3. THE System SHALL keep all CRUD operations for cases
4. THE System SHALL maintain overdue checking logic
5. THE System SHALL preserve all template rendering and UI features
