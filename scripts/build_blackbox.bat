@echo off
:: Build blackbox_decode from source on Windows using MSYS2
:: Run this from the MSYS2 UCRT64/MinGW64 shell, NOT from CMD.
::
:: Prerequisites (install once):
::   pacman -S mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-make
::
:: Then run:
::   scripts/build_blackbox.bat   (from MSYS2 shell, inside Qt-PID-Analyzer/)

setlocal enabledelayedexpansion

set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%..
set BLACKBOX_SRC=%PROJECT_ROOT%\vendor\blackbox-tools
set BIN_DIR=%PROJECT_ROOT%\bin

echo [build_blackbox] Source: %BLACKBOX_SRC%
echo [build_blackbox] Output: %BIN_DIR%

if not exist "%BLACKBOX_SRC%\Makefile" (
    echo ERROR: vendor\blackbox-tools not found.
    echo Run:  git submodule update --init --recursive
    exit /b 1
)

where gcc >nul 2>&1
if errorlevel 1 (
    echo ERROR: gcc not found on PATH.
    echo Install via MSYS2: pacman -S mingw-w64-ucrt-x86_64-gcc mingw-w64-ucrt-x86_64-make
    exit /b 1
)

:: Prefer mingw32-make, fall back to make
set MAKE_CMD=
where mingw32-make >nul 2>&1 && set MAKE_CMD=mingw32-make
if "%MAKE_CMD%"=="" where make >nul 2>&1 && set MAKE_CMD=make
if "%MAKE_CMD%"=="" (
    echo ERROR: make / mingw32-make not found on PATH.
    echo Install via MSYS2: pacman -S mingw-w64-ucrt-x86_64-make
    exit /b 1
)

pushd "%BLACKBOX_SRC%"
%MAKE_CMD% obj/blackbox_decode
popd

if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"
copy /Y "%BLACKBOX_SRC%\obj\blackbox_decode.exe" "%BIN_DIR%\blackbox_decode.exe"

echo [build_blackbox] Done: %BIN_DIR%\blackbox_decode.exe
