# 🏗️ Architecture - E-Kejaksaan Desktop App

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    USER COMPUTER                             │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         E-Kejaksaan.exe (Desktop App)              │    │
│  │                                                     │    │
│  │  ┌──────────────┐         ┌──────────────┐        │    │
│  │  │   PyWebView  │◄────────┤ Flask Server │        │    │
│  │  │  (GUI Window)│         │ (Port 5000)  │        │    │
│  │  └──────────────┘         └──────┬───────┘        │    │
│  │                                   │                │    │
│  │                          ┌────────▼────────┐       │    │
│  │                          │  SQLAlchemy ORM │       │    │
│  │                          └────────┬────────┘       │    │
│  └───────────────────────────────────┼────────────────┘    │
│                                      │                     │
└──────────────────────────────────────┼─────────────────────┘
                                       │
                                       │ Internet
                                       │ (PostgreSQL Protocol)
                                       │
                         ┌─────────────▼──────────────┐
                         │    SUPABASE CLOUD          │
                         │                            │
                         │  ┌──────────────────────┐  │
                         │  │  PostgreSQL Database │  │
                         │  │  - users table       │  │
                         │  │  - case table        │  │
                         │  └──────────────────────┘  │
                         │                            │
                         └────────────────────────────┘
```

---

## Component Details

### 1. Desktop App (.exe)

**Components:**
- **PyWebView**: Native window wrapper (GUI)
- **Flask Server**: Web server running on localhost:5000
- **Embedded Credentials**: DATABASE_URL & SECRET_KEY

**Flow:**
1. User double-click `E-Kejaksaan.exe`
2. Flask server starts in background thread
3. PyWebView opens native window pointing to `http://127.0.0.1:5000`
4. User interacts with web interface in native window

### 2. Flask Application

**Modules:**
- `app.py`: Main application logic
- `models.py`: Database models (User, Case)
- `extensions.py`: Flask extensions (SQLAlchemy, LoginManager)
- `templates/`: HTML templates (Jinja2)
- `static/`: CSS, JavaScript, images

**Features:**
- Authentication (Flask-Login)
- CRUD operations
- Date validation & overdue checking
- Real-time inline editing

### 3. Database (Supabase)

**Type:** PostgreSQL (Cloud)

**Tables:**
- `user`: Authentication
  - id, username, password_hash
- `case`: Case tracking
  - id, nama_tersangka, umur_tersangka, kategori_umur
  - pasal, jpu, spdp fields
  - berkas_tahap_1, p18_p19, p21, tahap_2, limpah_pn
  - keterangan, created_at

**Connection:**
- Protocol: PostgreSQL (port 6543 - Transaction Mode)
- Pooling: NullPool (serverless-friendly)
- SSL: Enabled

---

## Build Process

```
┌─────────────────────────────────────────────────────────────┐
│                    BUILD MACHINE                             │
│                                                              │
│  1. Source Files                                            │
│     ├── app.py                                              │
│     ├── desktop.py                                          │
│     ├── models.py                                           │
│     ├── templates/                                          │
│     ├── static/                                             │
│     └── .env (credentials)                                  │
│                                                              │
│  2. build_exe.py (Build Script)                             │
│     ├── Read .env                                           │
│     ├── Create app_embedded.py (with credentials)           │
│     ├── Create desktop_embedded.py                          │
│     └── Create kejaksaan.spec                               │
│                                                              │
│  3. PyInstaller                                             │
│     ├── Analyze dependencies                                │
│     ├── Bundle Python interpreter                           │
│     ├── Bundle all modules                                  │
│     ├── Bundle templates & static files                     │
│     └── Create single .exe                                  │
│                                                              │
│  4. Output                                                  │
│     └── dist/E-Kejaksaan.exe (~50-80 MB)                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### User Login
```
User Input (username/password)
    ↓
Flask Route (/login)
    ↓
Query Supabase (User table)
    ↓
Password Verification (werkzeug.security)
    ↓
Flask-Login Session
    ↓
Redirect to Dashboard
```

### Add Case
```
User Input (form data)
    ↓
Flask Route (/add_case)
    ↓
Create Case Object
    ↓
SQLAlchemy ORM
    ↓
INSERT to Supabase
    ↓
Commit Transaction
    ↓
Redirect to Dashboard (with flash message)
```

### Edit Cell (Inline)
```
User Click Cell
    ↓
JavaScript (show modal/contenteditable)
    ↓
User Edit Value
    ↓
JavaScript AJAX (POST /update_cell)
    ↓
Flask Route (/update_cell)
    ↓
SQLAlchemy ORM
    ↓
UPDATE Supabase
    ↓
JSON Response (success/error)
    ↓
JavaScript Update UI
```

---

## Security Model

### Authentication
- **Method**: Session-based (Flask-Login)
- **Password**: Hashed with scrypt
- **Session**: Stored in Flask session (encrypted cookie)

### Database
- **Connection**: SSL/TLS encrypted
- **Credentials**: Embedded in .exe (not in plain text in memory)
- **Access**: Username/password authentication

### Desktop App
- **Isolation**: Runs on localhost only (127.0.0.1)
- **Port**: 5000 (not exposed to network)
- **Window**: Native (not browser, no address bar)

---

## Deployment Models

### Model 1: Web App (Current)
```
User Browser → Vercel/Server → Supabase
```
**Pros:** Multi-device, no installation
**Cons:** Need browser, internet required

### Model 2: Desktop App (.exe)
```
User PC → E-Kejaksaan.exe → Supabase
```
**Pros:** Native feel, no browser, standalone
**Cons:** Internet required, per-device installation

### Model 3: Hybrid (Recommended)
```
Office: Desktop App (.exe)
Remote: Web App (browser)
Both → Same Supabase Database
```
**Pros:** Best of both worlds, data synced
**Cons:** Need to maintain both

---

## Performance Considerations

### Desktop App
- **Startup Time**: ~2-3 seconds (Flask + PyWebView)
- **Memory Usage**: ~100-150 MB
- **CPU Usage**: Low (idle), Medium (during operations)

### Database
- **Latency**: ~50-200ms (depends on internet)
- **Throughput**: Limited by Supabase free tier
- **Pooling**: NullPool (no connection pooling)

### Optimization Tips
- Use indexes on frequently queried columns
- Implement caching for static data
- Batch operations when possible
- Monitor Supabase dashboard for slow queries

---

## Scalability

### Current Limits (Supabase Free Tier)
- Database: 500 MB
- Bandwidth: 2 GB/month
- API Requests: Unlimited (with rate limiting)

### Scaling Options
1. **Upgrade Supabase Plan**: More storage, bandwidth
2. **Optimize Queries**: Reduce database calls
3. **Add Caching**: Redis/Memcached
4. **Load Balancing**: Multiple app instances

---

## Maintenance

### Regular Tasks
- [ ] Monitor Supabase usage (dashboard)
- [ ] Backup database (Supabase auto-backup)
- [ ] Update dependencies (pip)
- [ ] Test .exe on clean Windows machine
- [ ] Review user feedback

### Update Process
1. Update source code
2. Test locally (`python app.py`)
3. Test desktop (`python desktop.py`)
4. Rebuild .exe (`python build_exe.py`)
5. Distribute new .exe to users

---

## Troubleshooting Guide

| Issue | Possible Cause | Solution |
|-------|---------------|----------|
| .exe won't start | Missing DLL | Install VC++ Redistributable |
| Can't connect DB | No internet | Check connection |
| Slow performance | High latency | Check internet speed |
| Login fails | Wrong credentials | Reset password in Supabase |
| Data not syncing | Database error | Check Supabase logs |

---

## Future Enhancements

### Planned Features
- [ ] Offline mode (local SQLite cache)
- [ ] Auto-update mechanism
- [ ] Multi-user roles (admin, user, viewer)
- [ ] Export to Excel/PDF
- [ ] Email notifications for overdue cases
- [ ] Dashboard analytics & charts

### Technical Improvements
- [ ] Add unit tests
- [ ] Implement CI/CD pipeline
- [ ] Add logging & monitoring
- [ ] Optimize database queries
- [ ] Add API documentation
