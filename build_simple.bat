@echo off
echo ========================================
echo BUILD E-KEJAKSAAN DESKTOP (SIMPLE)
echo ========================================
echo.

echo [1/2] Building DEBUG version (with console)...
pyinstaller --clean desktop_debug.spec
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo [2/2] Building RELEASE version (no console)...
pyinstaller --clean desktop.spec
if %errorlevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo BUILD SELESAI!
echo ========================================
echo.
echo File tersedia di:
echo   - dist\E-Kejaksaan-Debug.exe (untuk debugging)
echo   - dist\E-Kejaksaan.exe (untuk production)
echo.
echo Cara test:
echo   1. Jalankan E-Kejaksaan-Debug.exe dulu
echo   2. Lihat console untuk error messages
echo   3. Jika OK, gunakan E-Kejaksaan.exe
echo.
pause
