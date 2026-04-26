@echo off
set PYTHON=C:\Users\dell\anaconda3\python.exe
echo ============================================
echo   TEST CONNEXION BACKEND ^<-^> ML
echo ============================================

echo.
echo [1/2] Verification Python Anaconda...
%PYTHON% --version
if errorlevel 1 (
    echo ERREUR: Python Anaconda introuvable!
    pause
    exit /b 1
)

echo.
echo [2/2] Lancement du script d'integration ML...
%PYTHON% integration_backend.py

echo.
echo ============================================
echo   TERMINE
echo ============================================
pause
