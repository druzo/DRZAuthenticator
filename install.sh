#!/bin/bash

# DRZAuthenticator Installer - POSIX version
# Supports Linux, macOS, WSL, Git Bash
# Usage: curl -fsSL https://raw.githubusercontent.com/druzo/DRZAuthenticator/v0.3.0/install.sh | bash

set -euo pipefail

readonly VERSION="0.3.0"
readonly REPO_URL="https://github.com/druzo/DRZAuthenticator"
readonly INSTALL_DIR="$HOME/.local/share/DRZAuthenticator"
readonly BIN_DIR="$HOME/.local/bin"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly NC='\033[0m' # No Color

# Command line args
COMMAND="${1:-install}"

# Print error and exit
err() {
    echo -e "${RED}[ERROR]${NC} $*" >&2
    exit 1
}

# Print info
info() {
    echo -e "${GREEN}[INFO]${NC} $*"
}

# Print warning
warn() {
    echo -e "${YELLOW}[WARN]${NC} $*"
}

# Detect OS type
detect_os() {
    local os_name
    os_name="$(uname -s)"
    case "$os_name" in
        Linux*)     echo "linux" ;;
        Darwin*)    echo "darwin" ;;
        MINGW*|MSYS*|CYGWIN*)
            if grep -q "Microsoft" /proc/version 2>/dev/null; then
                echo "wsl"
            else
                echo "mingw"  # Git Bash
            fi ;;
        *)          err "Unsupported OS: $os_name" ;;
    esac
}

# Check python version requirement
check_python() {
    if ! command -v python3 &> /dev/null; then
        case "$(detect_os)" in
            linux)
                err "Python 3 not found. Install with: sudo apt install python3 python3-pip"
                ;;
            darwin)
                err "Python 3 not found. Install from https://python.org or with: brew install python@3"
                ;;
            wsl|mingw)
                err "Python 3 not found. Install with: winget install Python.Python.3 or use Git Bash with Ubuntu"
                ;;
        esac
    fi

    local version
    version="$(python3 --version 2>&1 | cut -d' ' -f2)"
    # Simple version comparison (not robust, but works for now)
    if [[ "${version%%.*}" -lt 3 ]] || [[ "${version%%.*}" -eq 3 && "$(echo "$version" | cut -d. -f2)" -lt 8 ]]; then
        err "Python 3.8 or higher required, found: $version"
    fi
}

# Check git is available and version
check_git() {
    if ! command -v git &> /dev/null; then
        case "$(detect_os)" in
            linux)
                err "Git not found. Install with: sudo apt install git"
                ;;
            darwin)
                err "Git not found. Install from https://git-scm.com or with: brew install git"
                ;;
            wsl|mingw)
                err "Git not found. Install with: winget install Git.Git"
                ;;
        esac
    fi
}

# Clone or update repo
setup_repo() {
    local branch="v$VERSION"
    if [ -d "$INSTALL_DIR" ] && [ -d "$INSTALL_DIR/.git" ]; then
        info "Updating existing installation in $INSTALL_DIR"
        cd "$INSTALL_DIR"
        git pull --ff-only origin "$branch" || err "Failed to update repository"
        cd - > /dev/null
    else
        info "Cloning DRZAuthenticator into $INSTALL_DIR"
        mkdir -p "$INSTALL_DIR"
        git clone --depth 1 --branch "$branch" "$REPO_URL" "$INSTALL_DIR" || err "Failed to clone repository"
    fi
}

# Install dependencies via pip
install_deps() {
    local requirements="$INSTALL_DIR/requirements.txt"
    if [ ! -f "$requirements" ]; then
        err "Could not find requirements.txt in $INSTALL_DIR"
    fi

    info "Installing Python dependencies..."
    if pip3 install --user -r "$requirements" 2>&1 | grep -q "break-system-packages"; then
        # Try with --break-system-packages flag for PEP 668 on Debian/Ubuntu
        info "Trying installation with break-system-packages flag"
        pip3 install --user -r "$requirements" --break-system-packages || err "Failed to install dependencies"
    fi
}

# Create wrapper script in bin dir
create_wrapper() {
    local wrapper="$BIN_DIR/drz-authenticator"
    mkdir -p "$BIN_DIR"

    cat > "$wrapper" << EOF
#!/bin/bash
exec python3 "$INSTALL_DIR/src/main.py" "\$@"
EOF

    chmod +x "$wrapper"
    info "Created wrapper script: $wrapper"
}

# Check if bin directory is in PATH
check_path() {
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        warn "Your \$PATH does not include $BIN_DIR"
        echo -e "Add this line to your shell rc file (~/.bashrc, ~/.zshrc, etc.):"
        echo -e "export PATH=\"\$PATH:$BIN_DIR\""
        echo ""
    fi
}

# Uninstall function
uninstall() {
    info "Uninstalling DRZAuthenticator..."
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf "$INSTALL_DIR" || err "Failed to remove installation directory"
        info "Removed installation directory: $INSTALL_DIR"
    fi

    local wrapper="$BIN_DIR/drz-authenticator"
    if [ -f "$wrapper" ]; then
        rm -f "$wrapper" || err "Failed to remove wrapper script"
        info "Removed wrapper script: $wrapper"
    fi

    info "Uninstallation complete."
}

# Update function
update() {
    info "Updating DRZAuthenticator..."
    setup_repo
    install_deps
    create_wrapper
    check_path
    info "Update complete."
}

# Print version
version() {
    echo "DRZAuthenticator Installer v$VERSION"
}

# Print help
help() {
    echo "DRZAuthenticator Installer v$VERSION"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  install    Install DRZAuthenticator (default)"
    echo "  update     Update existing installation"
    echo "  uninstall  Remove installation"
    echo "  version    Show installer version"
    echo "  help       Show this help message"
    echo ""
    echo "Example:"
    echo "  curl -fsSL https://raw.githubusercontent.com/druzo/DRZAuthenticator/v0.3.0/install.sh | bash"
}

# Main logic
main() {
    check_python
    check_git

    case "$COMMAND" in
        install)
            setup_repo
            install_deps
            create_wrapper
            check_path
            info "Installation complete."
            echo "Run: drz-authenticator"
            ;;
        update)
            update
            ;;
        uninstall)
            uninstall
            ;;
        version)
            version
            ;;
        help|--help|-h)
            help
            ;;
        *)
            err "Unknown command: $COMMAND. Use --help for usage."
            ;;
    esac
}

# Run main function with all args
main "$@"