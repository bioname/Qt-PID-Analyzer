@echo off
:: Build blackbox_decode from source on Windows using MinGW (MSYS2/MinGW64)
:: Requires: MinGW make + gcc on PATH (e.g. from MSYS2: pacman -S mingw-w64-x86_64-gcc make)

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
    echo Install MSYS2 and run: pacman -S mingw-w64-x86_64-gcc make
    exit /b 1
)

pushd "%BLACKBOX_SRC%"
make obj/blackbox_decode
popd

if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"
copy /Y "%BLACKBOX_SRC%\obj\blackbox_decode.exe" "%BIN_DIR%\blackbox_decode.exe"

echo [build_blackbox] Done: %BIN_DIR%\blackbox_decode.exe
