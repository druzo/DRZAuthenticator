# DRZAuthenticator Installer - PowerShell version
# Supports Windows native PowerShell
# Usage: iwr -UseBasicParsing https://raw.githubusercontent.com/druzo/DRZAuthenticator/v0.3.0/install.ps1 | iex

param(
    [string]$Command = "install"
)

$VERSION = "0.3.0"
$REPO_URL = "https://github.com/druzo/DRZAuthenticator"
$INSTALL_DIR = "$env:LOCALAPPDATA\DRZAuthenticator"
$BIN_DIR = "$env:APPDATA\Python\Scripts"

# Function to log errors and exit
function Write-ErrorAndExit {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
    exit 1
}

# Function to log info
function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

# Function to log warnings
function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

# Check Python version requirement
function Check-Python {
    if (!(Get-Command python -ErrorAction SilentlyContinue) -and !(Get-Command py -ErrorAction SilentlyContinue)) {
        Write-ErrorAndExit "Python 3 not found. Install from https://python.org or with: winget install Python.Python.3"
    }

    # Test Python 3.8+
    $python_version = & python --version 2>&1
    if ($python_version -match "Python (\d+\.\d+)") {
        $major = [int]$matches[1].Split('.')[0]
        $minor = [int]$matches[1].Split('.')[1]
        if ($major -lt 3 -or $major -eq 3 -and $minor -lt 8) {
            Write-ErrorAndExit "Python 3.8 or higher required, found: $python_version"
        }
    } else {
        Write-ErrorAndExit "Unable to parse Python version: $python_version"
    }
}

# Check Git is available
function Check-Git {
    if (!(Get-Command git -ErrorAction SilentlyContinue)) {
        Write-ErrorAndExit "Git not found. Install with: winget install Git.Git"
    }
}

# Clone or update repo
function Setup-Repo {
    $branch = "v$VERSION"
    if (Test-Path "$INSTALL_DIR\.git") {
        Write-Info "Updating existing installation in $INSTALL_DIR"
        Set-Location $INSTALL_DIR
        git pull --ff-only origin "$branch" | Out-Null || Write-ErrorAndExit "Failed to update repository"
        Set-Location -Path $OLDPWD
    } else {
        Write-Info "Cloning DRZAuthenticator into $INSTALL_DIR"
        New-Item -ItemType Directory -Path $INSTALL_DIR -Force | Out-Null
        git clone --depth 1 --branch "$branch" "$REPO_URL" "$INSTALL_DIR" | Out-Null || Write-ErrorAndExit "Failed to clone repository"
    }
}

# Install dependencies via pip
function Install-Deps {
    $requirements = Join-Path $INSTALL_DIR "requirements.txt"
    if (!(Test-Path $requirements)) {
        Write-ErrorAndExit "Could not find requirements.txt in $INSTALL_DIR"
    }

    Write-Info "Installing Python dependencies..."
    try {
        pip install --user -r $requirements | Out-Null
    } catch {
        # Try with --break-system-packages flag for PEP 668 on some systems
        Write-Info "Trying installation with --break-system-packages flag"
        pip install --user -r $requirements --break-system-packages | Out-Null || Write-ErrorAndExit "Failed to install dependencies"
    }
}

# Create wrapper script in bin dir
function Create-Wrapper {
    $wrapper = Join-Path $BIN_DIR "drz-authenticator.cmd"
    if (!(Test-Path $BIN_DIR)) { New-Item -ItemType Directory -Path $BIN_DIR -Force | Out-Null }

    $wrapperContent = @"
@echo off
python "%LOCALAPPDATA%\DRZAuthenticator\src\main.py" %*
"@

    Set-Content -Path $wrapper -Value $wrapperContent
    Write-Info "Created wrapper script: $wrapper"
}

# Check if bin directory is in PATH
function Check-Path {
    $path = [Environment]::GetEnvironmentVariable("PATH", "User")
    if ($path -notlike "*$BIN_DIR*") {
        Write-Warn "Your \$PATH does not include $BIN_DIR"
        Write-Host "Add this line to your PowerShell profile or run in elevated prompt:"
        Write-Host "Set-ItemEnv -Name PATH -Value ""\$env:PATH;$BIN_DIR"""
        Write-Host ""
    }
}

# Uninstall function
function Uninstall {
    Write-Info "Uninstalling DRZAuthenticator..."
    
    if (Test-Path $INSTALL_DIR) {
        Remove-Item -Recurse -Force $INSTALL_DIR -ErrorAction Stop | Out-Null
        Write-Info "Removed installation directory: $INSTALL_DIR"
    }

    $wrapper = Join-Path $BIN_DIR "drz-authenticator.cmd"
    if (Test-Path $wrapper) {
        Remove-Item $wrapper -ErrorAction Stop | Out-Null
        Write-Info "Removed wrapper script: $wrapper"
    }
    
    Write-Info "Uninstallation complete."
}

# Update function
function Update {
    Write-Info "Updating DRZAuthenticator..."
    Setup-Repo
    Install-Deps
    Create-Wrapper
    Check-Path
    Write-Info "Update complete."
}

# Print version
function Version {
    Write-Host "DRZAuthenticator Installer v$VERSION"
}

# Print help
function Help {
    Write-Host "DRZAuthenticator Installer v$VERSION"
    Write-Host ""
    Write-Host "Usage: .\install.ps1 [COMMAND]"
    Write-Host ""
    Write-Host "Commands:"
    Write-Host "  install    Install DRZAuthenticator (default)"
    Write-Host "  update     Update existing installation"
    Write-Host "  uninstall  Remove installation"
    Write-Host "  version    Show installer version"
    Write-Host "  help       Show this help message"
    Write-Host ""
    Write-Host "Example:"
    Write-Host "  iwr -UseBasicParsing https://raw.githubusercontent.com/druzo/DRZAuthenticator/v0.3.0/install.ps1 | iex"
}

# Main logic
Check-Python
Check-Git

switch ($Command) {
    "install" {
        Setup-Repo
        Install-Deps
        Create-Wrapper
        Check-Path
        Write-Info "Installation complete."
        Write-Host "Run: drz-authenticator"
    }
    "update" {
        Update
    }
    "uninstall" {
        Uninstall
    }
    "version" {
        Version
    }
    "help" {
        Help
    }
    default {
        Write-ErrorAndExit "Unknown command: $Command. Use --help for usage."
    }
}