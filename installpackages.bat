@echo off
title InstallPackages
cls
echo Installing packages...

python -c "import discord" 2>nul
if %errorlevel%==0 (
    set DISCORD_INSTALLED=1
) else (
    set DISCORD_INSTALLED=0
)

python -c "import dotenv" 2>nul
if %errorlevel%==0 (
    set DOTENV_INSTALLED=1
) else (
    set DOTENV_INSTALLED=0
)

set PACKAGES_TO_INSTALL=

if %DISCORD_INSTALLED%==0 set PACKAGES_TO_INSTALL=%PACKAGES_TO_INSTALL% discord.py
if %DOTENV_INSTALLED%==0 set PACKAGES_TO_INSTALL=%PACKAGES_TO_INSTALL% python-dotenv

if "%PACKAGES_TO_INSTALL%"=="" (
    echo All packages are already installed.
    timeout /t 4 /nobreak >nul
    exit
)

python -m pip install --upgrade pip --quiet
python -m pip install%PACKAGES_TO_INSTALL% --quiet

if %DISCORD_INSTALLED%==0 if %DOTENV_INSTALLED%==0 (
    echo Installed all packages.
) else (
    echo Installed remaining packages.
)

timeout /t 4 /nobreak >nul
exit

