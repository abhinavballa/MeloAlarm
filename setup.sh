#!/bin/bash
# Setup script for MeloAlarm

echo "🎵 MeloAlarm Setup"
echo "=================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Create virtual environment (optional but recommended)
read -p "Create a virtual environment? (recommended) [y/N]: " create_venv
if [[ $create_venv =~ ^[Yy]$ ]]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
    echo ""
fi

# Install dependencies
echo "Installing dependencies..."
pip3 install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  Please edit .env and add your Spotify credentials:"
    echo "   - SPOTIFY_CLIENT_ID"
    echo "   - SPOTIFY_CLIENT_SECRET"
    echo "   - SPOTIFY_PLAYLIST_ID"
    echo ""
else
    echo "✅ .env file already exists"
    echo ""
fi

# Make script executable
chmod +x melo_alarm.py
echo "✅ Script is executable"
echo ""

echo "📝 Next steps:"
echo "1. Edit .env file and add your Spotify credentials"
echo "2. Run 'python3 melo_alarm.py' to test and authenticate"
echo "3. Update com.meloalarm.plist with your alarm time"
echo "4. Load the launchd agent:"
echo "   cp com.meloalarm.plist ~/Library/LaunchAgents/"
echo "   launchctl load ~/Library/LaunchAgents/com.meloalarm.plist"
echo ""
echo "For detailed instructions, see README.md"

