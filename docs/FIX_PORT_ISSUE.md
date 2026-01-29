# Fix: Port Access Forbidden Error

## Error Message
```
An attempt was made to access a socket in a way forbidden by its access permissions
```

## Penyebab
1. **Port 5000 sudah digunakan** oleh aplikasi lain
2. **Windows Firewall** memblokir akses port
3. **Antivirus** memblokir aplikasi
4. **Hyper-V** atau **Docker** reserve port range tertentu

## Solusi yang Sudah Diterapkan

### 1. Auto Port Detection
Aplikasi sekarang otomatis mencari port yang tersedia:
- Coba port: 5000, 5001, 5002, 5003, 8000, 8080, 8888
- Jika semua terpakai, gunakan random free port

### 2. Error Handling
- Tampilkan pesan error yang jelas
- Test koneksi sebelum buka window
- Berikan instruksi troubleshooting

## Cara Test

### Test Desktop.py
```bash
python desktop.py
```

Lihat output:
```
Using port: 5000
Starting Flask server on port 5000...
Waiting for server to start...
Server is running on http://127.0.0.1:5000
```

### Test Port Availability
```bash
# Windows - Cek port yang digunakan
netstat -ano | findstr :5000

# Jika ada, kill process
taskkill /PID <PID> /F
```

## Troubleshooting Manual

### 1. Cek Port yang Digunakan
```powershell
# PowerShell
Get-NetTCPConnection -LocalPort 5000

# CMD
netstat -ano | findstr :5000
```

### 2. Matikan Aplikasi yang Menggunakan Port
Aplikasi yang sering pakai port 5000:
- AirPlay Receiver (macOS/Windows)
- Flask development server lain
- Docker containers
- Node.js servers

### 3. Disable Hyper-V Port Reservation (Windows 10/11)
```powershell
# Run as Administrator
netsh int ipv4 show excludedportrange protocol=tcp

# Jika port 5000 di-reserve, restart Windows
```

### 4. Allow di Windows Firewall
1. Windows Security → Firewall & network protection
2. Allow an app through firewall
3. Tambahkan `E-Kejaksaan.exe`
4. Centang Private dan Public networks

### 5. Disable Antivirus Sementara
Beberapa antivirus memblokir aplikasi .exe yang baru:
- Windows Defender
- Avast
- AVG
- Kaspersky

Tambahkan `E-Kejaksaan.exe` ke whitelist/exclusions.

## Build Ulang

Setelah update kode, rebuild:

```bash
# Cara 1: Simple
build_simple.bat

# Cara 2: Manual
pyinstaller --clean desktop_debug.spec

# Cara 3: Dengan embedded credentials
python build_exe.py
```

## Test Setelah Build

1. Jalankan `E-Kejaksaan-Debug.exe`
2. Lihat console output
3. Pastikan muncul:
   ```
   Using port: 5000
   Server is running on http://127.0.0.1:5000
   ```
4. Jika OK, gunakan `E-Kejaksaan.exe` (tanpa console)

## Alternatif: Gunakan Port Lain

Edit `desktop.py` untuk force port tertentu:

```python
# Ganti
port = find_free_port()

# Dengan
port = 8080  # atau port lain yang free
```

## Kontak Support

Jika masih error:
1. Screenshot console output
2. Jalankan: `netstat -ano | findstr :5000`
3. Cek Windows Event Viewer untuk error details
