#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "============================================"
echo "Voice Assistant Installer (Linux)"
echo "============================================"
echo ""

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo -e "${RED}Cannot detect Linux distribution${NC}"
    DISTRO="unknown"
fi

echo -e "${BLUE}Detected distribution: $DISTRO${NC}"
echo ""

# Check if Python is installed
echo "Checking for Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo -e "${GREEN}Python is already installed: $PYTHON_VERSION${NC}"
    PYTHON_CMD="python3"
else
    echo -e "${YELLOW}Python 3 is not installed${NC}"
    echo ""
    echo "Would you like to install Python 3? (y/n)"
    read -r install_python
    
    if [[ $install_python == "y" || $install_python == "Y" ]]; then
        install_python_func
    else
        echo -e "${RED}Python 3 is required to run Voice Assistant${NC}"
        echo "Please install Python 3 and run this script again"
        exit 1
    fi
fi

# Check Python version (need 3.8+)
PYTHON_VERSION_NUM=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION_NUM" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}Python 3.8 or higher is required (found $PYTHON_VERSION_NUM)${NC}"
    exit 1
fi

echo ""
echo "============================================"
echo "Installing System Dependencies..."
echo "============================================"
echo ""

install_system_deps() {
    case $DISTRO in
        ubuntu|debian|linuxmint|pop)
            echo "Installing dependencies for Debian/Ubuntu-based system..."
            sudo apt-get update
            sudo apt-get install -y python3-pip python3-dev portaudio19-dev \
                python3-pyaudio ffmpeg espeak
            ;;
        fedora|rhel|centos)
            echo "Installing dependencies for Fedora/RHEL-based system..."
            sudo dnf install -y python3-pip python3-devel portaudio-devel \
                ffmpeg espeak
            ;;
        arch|manjaro)
            echo "Installing dependencies for Arch-based system..."
            sudo pacman -S --noconfirm python-pip portaudio ffmpeg espeak
            ;;
        opensuse*)
            echo "Installing dependencies for openSUSE..."
            sudo zypper install -y python3-pip portaudio-devel ffmpeg espeak
            ;;
        *)
            echo -e "${YELLOW}Unknown distribution. You may need to install dependencies manually:${NC}"
            echo "  - portaudio development libraries"
            echo "  - ffmpeg"
            echo "  - espeak or espeak-ng"
            echo ""
            echo "Continue anyway? (y/n)"
            read -r continue_anyway
            if [[ $continue_anyway != "y" && $continue_anyway != "Y" ]]; then
                exit 1
            fi
            ;;
    esac
}

install_system_deps

echo ""
echo "============================================"
echo "Installing Python Dependencies..."
echo "============================================"
echo ""

# Upgrade pip
echo "Upgrading pip..."
python3 -m pip install --upgrade pip --user

# Install core dependencies
echo ""
echo "Installing core packages..."
python3 -m pip install --user SpeechRecognition pyttsx3 requests

# Install PyAudio
echo ""
echo "Installing PyAudio..."
python3 -m pip install --user pyaudio
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}PyAudio installation failed. This is common.${NC}"
    echo "Trying to install python3-pyaudio from system package manager..."
    
    case $DISTRO in
        ubuntu|debian|linuxmint|pop)
            sudo apt-get install -y python3-pyaudio
            ;;
        fedora|rhel|centos)
            sudo dnf install -y python3-pyaudio
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm python-pyaudio
            ;;
    esac
fi

# Install optional dependencies
echo ""
echo "Installing optional packages for better audio support..."
python3 -m pip install --user pydub
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}pydub installation failed - continuing without it${NC}"
fi

echo ""
echo "============================================"
echo "Creating Launcher..."
echo "============================================"
echo ""

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Create launcher script
cat > "$SCRIPT_DIR/launch.sh" << 'EOF'
#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

cd "$SCRIPT_DIR"
python3 voice-assistant.py

if [ $? -ne 0 ]; then
    echo ""
    echo "Error running Voice Assistant!"
    echo "Press any key to exit..."
    read -n 1
fi
EOF

chmod +x "$SCRIPT_DIR/launch.sh"
echo -e "${GREEN}Launcher created: launch.sh${NC}"

# Create desktop entry
echo ""
echo "Would you like to create a desktop shortcut? (y/n)"
read -r create_shortcut

if [[ $create_shortcut == "y" || $create_shortcut == "Y" ]]; then
    create_desktop_shortcut
fi

echo ""
echo "============================================"
echo -e "${GREEN}Installation Complete!${NC}"
echo "============================================"
echo ""
echo "You can now run the Voice Assistant by:"
echo "  - Running: ./launch.sh"
echo "  - Or: python3 voice-assistant.py"
echo ""

if [[ $create_shortcut == "y" || $create_shortcut == "Y" ]]; then
    echo "A desktop shortcut has also been created."
    echo ""
fi

echo -e "${YELLOW}Note: You may need to configure your microphone permissions${NC}"
echo "and ensure your user is in the 'audio' group:"
echo "  sudo usermod -a -G audio \$USER"
echo ""

exit 0

# Function to install Python
install_python_func() {
    echo "Installing Python 3..."
    
    case $DISTRO in
        ubuntu|debian|linuxmint|pop)
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-dev
            ;;
        fedora|rhel|centos)
            sudo dnf install -y python3 python3-pip python3-devel
            ;;
        arch|manjaro)
            sudo pacman -S --noconfirm python python-pip
            ;;
        opensuse*)
            sudo zypper install -y python3 python3-pip python3-devel
            ;;
        *)
            echo -e "${RED}Cannot automatically install Python on this distribution${NC}"
            echo "Please install Python 3.8+ manually"
            exit 1
            ;;
    esac
    
    if command -v python3 &> /dev/null; then
        echo -e "${GREEN}Python installed successfully!${NC}"
        PYTHON_CMD="python3"
    else
        echo -e "${RED}Python installation failed${NC}"
        exit 1
    fi
}

# Function to create desktop shortcut
create_desktop_shortcut() {
    echo "Creating desktop shortcut..."
    
    DESKTOP_DIR="$HOME/Desktop"
    if [ ! -d "$DESKTOP_DIR" ]; then
        DESKTOP_DIR="$HOME/.local/share/applications"
        mkdir -p "$DESKTOP_DIR"
    fi
    
    DESKTOP_FILE="$DESKTOP_DIR/voice-assistant.desktop"
    
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Voice Assistant
Comment=Self-hosted voice assistant
Exec=$SCRIPT_DIR/launch.sh
Icon=audio-input-microphone
Terminal=false
Categories=Audio;Utility;
EOF
    
    chmod +x "$DESKTOP_FILE"
    
    # Try to trust the desktop file (for some desktop environments)
    if command -v gio &> /dev/null; then
        gio set "$DESKTOP_FILE" metadata::trusted true 2>/dev/null
    fi
    
    echo -e "${GREEN}Desktop shortcut created!${NC}"
}
