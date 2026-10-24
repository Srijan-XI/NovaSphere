#!/bin/bash

# =============================================================================
# NovaSphere: NovaSphere - Linux Setup Script
# =============================================================================
# Author: Srijan-XI
# Date: October 1, 2025
# Version: 1.0
# Description: Automated setup script for Linux systems
# =============================================================================

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
INSTALL_DIR="$HOME/.local/share/novasphere"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
PYTHON_MIN_VERSION="3.8"
LOG_FILE="/tmp/novasphere-setup.log"

# =============================================================================
# Utility Functions
# =============================================================================

print_header() {
    echo -e "${CYAN}"
    echo "==================================================================================="
    echo "       NovaSphere: NovaSphere - Linux Setup Script"
    echo "===================================================================================="
    echo -e "${NC}"
}

print_section() {
    echo -e "\n${BLUE}==>${NC} ${WHITE}$1${NC}"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1" >&2
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${PURPLE}ℹ${NC} $1"
}

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root!"
        print_info "Please run as a regular user. Sudo privileges will be requested when needed."
        exit 1
    fi
}

# Check Linux distribution
detect_distro() {
    if command -v lsb_release >/dev/null 2>&1; then
        DISTRO=$(lsb_release -si)
        VERSION=$(lsb_release -sr)
    elif [[ -f /etc/os-release ]]; then
        . /etc/os-release
        DISTRO=$NAME
        VERSION=$VERSION_ID
    elif [[ -f /etc/redhat-release ]]; then
        DISTRO=$(cat /etc/redhat-release | awk '{print $1}')
        VERSION=$(cat /etc/redhat-release | awk '{print $3}')
    else
        DISTRO="Unknown"
        VERSION="Unknown"
    fi
    
    print_info "Detected: $DISTRO $VERSION"
    log "Detected distribution: $DISTRO $VERSION"
}

# Check Python version
check_python() {
    print_section "Checking Python Installation"
    
    if command -v python3 >/dev/null 2>&1; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_info "Found Python $PYTHON_VERSION"
        
        # Compare versions
        if python3 -c "import sys; exit(0 if sys.version_info >= (3, 7) else 1)" 2>/dev/null; then
            print_success "Python version is compatible (>= $PYTHON_MIN_VERSION)"
            PYTHON_CMD="python3"
        else
            print_error "Python version $PYTHON_VERSION is too old (minimum required: $PYTHON_MIN_VERSION)"
            exit 1
        fi
    else
        print_error "Python 3 is not installed!"
        print_info "Please install Python 3.8+ and try again"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 >/dev/null 2>&1; then
        print_success "pip3 is available"
        PIP_CMD="pip3"
    elif $PYTHON_CMD -m pip --version >/dev/null 2>&1; then
        print_success "pip is available via python -m pip"
        PIP_CMD="$PYTHON_CMD -m pip"
    else
        print_error "pip is not available!"
        print_info "Installing pip..."
        install_pip
    fi
}

# Install pip if missing
install_pip() {
    case $DISTRO in
        "Ubuntu"|"Debian"|"Kali"*)
            sudo apt-get update
            sudo apt-get install -y python3-pip python3-venv
            ;;
        "CentOS"|"Red Hat"*|"Fedora")
            if command -v dnf >/dev/null 2>&1; then
                sudo dnf install -y python3-pip python3-venv
            else
                sudo yum install -y python3-pip python3-venv
            fi
            ;;
        "Arch"|"Manjaro")
            sudo pacman -S --noconfirm python-pip
            ;;
        "openSUSE"*)
            sudo zypper install -y python3-pip python3-venv
            ;;
        *)
            print_warning "Unknown distribution. Please install pip manually."
            ;;
    esac
    PIP_CMD="pip3"
}

# Install system dependencies
install_system_deps() {
    print_section "Installing System Dependencies"
    
    case $DISTRO in
        "Ubuntu"|"Debian"|"Kali"*)
            print_info "Installing dependencies for Debian/Ubuntu systems..."
            sudo apt-get update
            sudo apt-get install -y \
                python3-dev \
                python3-venv \
                build-essential \
                portaudio19-dev \
                libasound2-dev \
                libsdl2-dev \
                libsdl2-mixer-dev \
                libopencv-dev \
                python3-opencv \
                bluetooth \
                libbluetooth-dev \
                bluez \
                bluez-tools \
                curl \
                wget \
                git
            ;;
        "CentOS"|"Red Hat"*|"Fedora")
            print_info "Installing dependencies for Red Hat/Fedora systems..."
            if command -v dnf >/dev/null 2>&1; then
                PKG_MGR="dnf"
            else
                PKG_MGR="yum"
            fi
            
            sudo $PKG_MGR install -y \
                python3-devel \
                gcc \
                gcc-c++ \
                make \
                portaudio-devel \
                alsa-lib-devel \
                SDL2-devel \
                SDL2_mixer-devel \
                opencv-devel \
                python3-opencv \
                bluez \
                bluez-libs-devel \
                curl \
                wget \
                git
            ;;
        "Arch"|"Manjaro")
            print_info "Installing dependencies for Arch systems..."
            sudo pacman -S --noconfirm \
                python \
                python-pip \
                base-devel \
                portaudio \
                alsa-lib \
                sdl2 \
                sdl2_mixer \
                opencv \
                python-opencv \
                bluez \
                bluez-utils \
                curl \
                wget \
                git
            ;;
        "openSUSE"*)
            print_info "Installing dependencies for openSUSE systems..."
            sudo zypper install -y \
                python3-devel \
                gcc \
                gcc-c++ \
                make \
                portaudio-devel \
                alsa-devel \
                libSDL2-devel \
                libSDL2_mixer-devel \
                opencv-devel \
                python3-opencv \
                bluez \
                bluez-devel \
                curl \
                wget \
                git
            ;;
        *)
            print_warning "Unknown distribution. You may need to install dependencies manually:"
            print_info "  - Python 3.8+ development headers"
            print_info "  - Build tools (gcc, make)"
            print_info "  - PortAudio development libraries"
            print_info "  - ALSA development libraries"
            print_info "  - SDL2 development libraries"
            print_info "  - OpenCV development libraries"
            print_info "  - Bluetooth development libraries"
            ;;
    esac
    
    print_success "System dependencies installed"
}

# Create directories
create_directories() {
    print_section "Creating Installation Directories"
    
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BIN_DIR"
    mkdir -p "$DESKTOP_DIR"
    mkdir -p "$HOME/.config/novasphere"
    
    print_success "Directories created"
    log "Created directories: $INSTALL_DIR, $BIN_DIR, $DESKTOP_DIR"
}

# Copy application files
copy_files() {
    print_section "Copying Application Files"
    
    if [[ -d "$PROJECT_DIR" && -f "$PROJECT_DIR/main.py" ]]; then
        cp -r "$PROJECT_DIR"/. "$INSTALL_DIR/"
        print_success "Application files copied to $INSTALL_DIR"
    else
        print_error "Application files not found in $PROJECT_DIR"
        print_info "Please ensure the setup script is inside the NovaSphere project directory"
        exit 1
    fi
    
    # Make main.py executable
    chmod +x "$INSTALL_DIR/main.py"
    log "Copied application files to $INSTALL_DIR"
}

# Create virtual environment and install Python dependencies
setup_python_env() {
    print_section "Setting Up Python Environment"
    
    # Create virtual environment
    print_info "Creating virtual environment..."
    $PYTHON_CMD -m venv "$INSTALL_DIR/venv"
    
    # Activate virtual environment
    source "$INSTALL_DIR/venv/bin/activate"
    
    # Upgrade pip
    print_info "Upgrading pip..."
    pip install --upgrade pip
    
    # Install Python dependencies
    print_info "Installing Python dependencies..."
    if [[ -f "$INSTALL_DIR/requirements.txt" ]]; then
        pip install -r "$INSTALL_DIR/requirements.txt"
        print_success "Python dependencies installed"
    else
        print_warning "requirements.txt not found, installing basic dependencies..."
        pip install psutil colorama packaging
    fi
    
    deactivate
    log "Python environment set up successfully"
}

# Create launcher script
create_launcher() {
    print_section "Creating Launcher Script"
    
    cat > "$BIN_DIR/nova" << 'EOF'
#!/bin/bash
# NovaSphere Launcher

INSTALL_DIR="$HOME/.local/share/novasphere"

# Activate virtual environment and run the application
source "$INSTALL_DIR/venv/bin/activate"
cd "$INSTALL_DIR"
python main.py "$@"
deactivate
EOF
    
    chmod +x "$BIN_DIR/nova"
    print_success "Launcher script created at $BIN_DIR/nova"
    log "Created launcher script"
}

# Create desktop entry
create_desktop_entry() {
    print_section "Creating Desktop Entry"
    
    cat > "$DESKTOP_DIR/novasphere.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NovaSphere
Comment=Comprehensive system diagnostic and monitoring tool suite
Exec=$BIN_DIR/nova --gui
Icon=utilities-system-monitor
Terminal=false
Categories=System;Monitor;Utility;
Keywords=system;monitor;diagnostic;battery;hardware;
StartupNotify=true
EOF
    
    chmod +x "$DESKTOP_DIR/novasphere.desktop"
    print_success "Desktop entry created"
    log "Created desktop entry"
}

# Update PATH
update_path() {
    print_section "Updating PATH"
    
    # Check if ~/.local/bin is already in PATH
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        # Add to .bashrc
        if [[ -f "$HOME/.bashrc" ]]; then
            echo "" >> "$HOME/.bashrc"
            echo "# Added by NovaSphere installer" >> "$HOME/.bashrc"
            echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.bashrc"
            print_success "Added $BIN_DIR to PATH in ~/.bashrc"
        fi
        
        # Add to .zshrc if it exists
        if [[ -f "$HOME/.zshrc" ]]; then
            echo "" >> "$HOME/.zshrc"
            echo "# Added by NovaSphere installer" >> "$HOME/.zshrc"
            echo "export PATH=\"\$PATH:$BIN_DIR\"" >> "$HOME/.zshrc"
            print_success "Added $BIN_DIR to PATH in ~/.zshrc"
        fi
        
        # Add to current session
        export PATH="$PATH:$BIN_DIR"
        print_info "PATH updated for current session"
    else
        print_info "$BIN_DIR is already in PATH"
    fi
    
    log "Updated PATH configuration"
}

# Set up permissions
setup_permissions() {
    print_section "Setting Up Permissions"
    
    # Add user to required groups for hardware access
    print_info "Adding user to required groups..."
    
    # Audio group for microphone/speaker tests
    sudo usermod -a -G audio "$USER" 2>/dev/null || true
    
    # Video group for camera tests
    sudo usermod -a -G video "$USER" 2>/dev/null || true
    
    # Dialout group for some hardware access
    sudo usermod -a -G dialout "$USER" 2>/dev/null || true
    
    print_success "User added to hardware access groups"
    print_warning "You may need to log out and back in for group changes to take effect"
    log "Set up user permissions"
}

# Test installation
test_installation() {
    print_section "Testing Installation"
    
    # Test if the application can be launched
    if source "$INSTALL_DIR/venv/bin/activate" && cd "$INSTALL_DIR" && python main.py --help >/dev/null 2>&1; then
        print_success "Installation test passed"
        deactivate 2>/dev/null || true
    else
        print_error "Installation test failed"
        print_info "Check the log file: $LOG_FILE"
        deactivate 2>/dev/null || true
        exit 1
    fi
    
    log "Installation test completed successfully"
}

# Create uninstaller
create_uninstaller() {
    print_section "Creating Uninstaller"
    
    cat > "$INSTALL_DIR/uninstall.sh" << 'EOF'
#!/bin/bash
# NovaSphere Uninstaller

echo "Uninstalling NovaSphere..."

# Remove installation directory
rm -rf "$HOME/.local/share/novasphere"

# Remove launcher
rm -f "$HOME/.local/bin/nova"

# Remove desktop entry
rm -f "$HOME/.local/share/applications/novasphere.desktop"

# Remove config directory
rm -rf "$HOME/.config/novasphere"

echo "NovaSphere has been uninstalled."
echo "Note: PATH entries in shell configuration files were not removed."
EOF
    
    chmod +x "$INSTALL_DIR/uninstall.sh"
    print_success "Uninstaller created at $INSTALL_DIR/uninstall.sh"
    log "Created uninstaller"
}

# Print usage information
print_usage() {
    print_section "Installation Complete!"
    
    echo -e "\n${GREEN}✓ NovaSphere has been successfully installed!${NC}\n"
    
    echo -e "${WHITE}Usage:${NC}"
    echo -e "  ${CYAN}nova${NC}                  # Launch CLI interface (default)"
    echo -e "  ${CYAN}nova --cli${NC}            # Launch CLI interface"
    echo -e "  ${CYAN}nova --gui${NC}            # Launch GUI interface"
    echo -e "  ${CYAN}nova --web${NC}            # Launch web interface"
    echo -e "  ${CYAN}nova --help${NC}           # Show help"
    
    echo -e "\n${WHITE}Available Tools:${NC}"
    echo -e "  🔋 ${YELLOW}Battery Monitor${NC}       - Real-time battery monitoring"
    echo -e "  🔧 ${YELLOW}Hardware Diagnostics${NC}  - Test cameras, microphones, speakers, etc."
    echo -e "  📊 ${YELLOW}System Monitor${NC}        - CPU, memory, disk, network monitoring"
    
    echo -e "\n${WHITE}Files:${NC}"
    echo -e "  Installation: ${CYAN}$INSTALL_DIR${NC}"
    echo -e "  Configuration: ${CYAN}$HOME/.config/novasphere${NC}"
    echo -e "  Launcher: ${CYAN}$BIN_DIR/nova${NC}"
    echo -e "  Uninstaller: ${CYAN}$INSTALL_DIR/uninstall.sh${NC}"
    echo -e "  Log file: ${CYAN}$LOG_FILE${NC}"
    
    echo -e "\n${WHITE}Note:${NC}"
    echo -e "  • ${YELLOW}Restart your terminal${NC} or run ${CYAN}source ~/.bashrc${NC} to update PATH"
    echo -e "  • Some hardware tests may require ${YELLOW}group membership changes${NC} - log out/in if needed"
    echo -e "  • Desktop entry is available in applications menu"
    
    echo -e "\n${WHITE}Support:${NC}"
    echo -e "  • Repository: ${CYAN}https://github.com/Srijan-XI/NovaSphere${NC}"
    echo -e "  • Issues: ${CYAN}https://github.com/Srijan-XI/NovaSphere/issues${NC}"
    
    echo ""
}

# =============================================================================
# Main Installation Process
# =============================================================================

main() {
    print_header
    
    # Start logging
    log "Starting NovaSphere installation"
    log "Script directory: $SCRIPT_DIR"
    
    # Pre-installation checks
    check_root
    detect_distro
    check_python
    
    # Installation steps
    install_system_deps
    create_directories
    copy_files
    setup_python_env
    create_launcher
    create_desktop_entry
    update_path
    setup_permissions
    test_installation
    create_uninstaller
    
    # Complete
    print_usage
    log "Installation completed successfully"
}

# =============================================================================
# Script Entry Point
# =============================================================================

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        echo "NovaSphere: NovaSphere - Linux Setup Script"
        echo ""
        echo "Usage: $0 [OPTIONS]"
        echo ""
        echo "Options:"
        echo "  --help, -h    Show this help message"
        echo "  --uninstall   Uninstall NovaSphere"
        echo ""
        echo "This script will:"
        echo "  • Install system dependencies"
        echo "  • Set up Python virtual environment"
        echo "  • Install Python packages"
        echo "  • Create launcher scripts"
        echo "  • Set up desktop integration"
        echo "  • Configure user permissions"
        exit 0
        ;;
    --uninstall)
        if [[ -f "$HOME/.local/share/novasphere/uninstall.sh" ]]; then
            bash "$HOME/.local/share/novasphere/uninstall.sh"
        else
            print_error "Uninstaller not found. NovaSphere may not be installed."
        fi
        exit 0
        ;;
    "")
        # No arguments, proceed with installation
        main
        ;;
    *)
        print_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
