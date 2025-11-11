#!/bin/bash
# Install/uninstall MeloAlarm launchd agent

PLIST_NAME="com.meloalarm.plist"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/$PLIST_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

function install_alarm() {
    echo "🎵 Installing MeloAlarm..."
    
    # Check if plist exists in current directory
    if [ ! -f "$SCRIPT_DIR/$PLIST_NAME" ]; then
        echo "❌ Error: $PLIST_NAME not found in current directory"
        exit 1
    fi
    
    # Create LaunchAgents directory if it doesn't exist
    mkdir -p "$LAUNCH_AGENTS_DIR"
    
    # Create a temporary copy of the plist to modify
    TEMP_PLIST="/tmp/${PLIST_NAME}.$$"
    cp "$SCRIPT_DIR/$PLIST_NAME" "$TEMP_PLIST"
    
    # Update Python path in plist if using virtual environment
    if [ -d "$SCRIPT_DIR/venv" ]; then
        echo "⚠️  Virtual environment detected. Updating Python path in plist..."
        PYTHON_PATH="$SCRIPT_DIR/venv/bin/python3"
        # Use sed to update the Python path (macOS compatible)
        sed -i '' "s|/usr/bin/python3|$PYTHON_PATH|g" "$TEMP_PLIST"
    fi
    
    # Update script path in plist (escape slashes for sed)
    ESCAPED_SCRIPT_DIR=$(echo "$SCRIPT_DIR" | sed 's|/|\\/|g')
    ESCAPED_ORIGINAL_DIR=$(echo "/Users/abhi/Documents/GitHub/MeloAlarm" | sed 's|/|\\/|g')
    sed -i '' "s|${ESCAPED_ORIGINAL_DIR}|${ESCAPED_SCRIPT_DIR}|g" "$TEMP_PLIST"
    
    # Update log file paths
    sed -i '' "s|${ESCAPED_ORIGINAL_DIR}|${ESCAPED_SCRIPT_DIR}|g" "$TEMP_PLIST"
    
    # Copy modified plist to LaunchAgents
    cp "$TEMP_PLIST" "$PLIST_PATH"
    rm "$TEMP_PLIST"
    echo "✅ Copied plist to $PLIST_PATH"
    
    # Unload if already loaded
    if launchctl list | grep -q "com.meloalarm"; then
        echo "Unloading existing agent..."
        launchctl unload "$PLIST_PATH" 2>/dev/null || true
    fi
    
    # Load the agent
    launchctl load "$PLIST_PATH"
    echo "✅ MeloAlarm agent loaded"
    
    # Verify it's loaded
    if launchctl list | grep -q "com.meloalarm"; then
        echo "✅ MeloAlarm is scheduled and ready!"
        echo ""
        echo "To check status: launchctl list | grep meloalarm"
        echo "To test run: launchctl start com.meloalarm"
        echo "To uninstall: ./install_alarm.sh uninstall"
    else
        echo "⚠️  Warning: Could not verify agent was loaded"
    fi
}

function uninstall_alarm() {
    echo "🎵 Uninstalling MeloAlarm..."
    
    # Unload the agent
    if [ -f "$PLIST_PATH" ]; then
        launchctl unload "$PLIST_PATH" 2>/dev/null || true
        echo "✅ Agent unloaded"
    fi
    
    # Remove plist file
    if [ -f "$PLIST_PATH" ]; then
        rm "$PLIST_PATH"
        echo "✅ Removed $PLIST_PATH"
    fi
    
    echo "✅ MeloAlarm uninstalled"
}

function status_alarm() {
    echo "🎵 MeloAlarm Status"
    echo "=================="
    
    if launchctl list | grep -q "com.meloalarm"; then
        echo "✅ MeloAlarm is installed and loaded"
        echo ""
        launchctl list | grep meloalarm
    else
        echo "❌ MeloAlarm is not installed or loaded"
    fi
}

# Main script logic
case "${1:-install}" in
    install)
        install_alarm
        ;;
    uninstall)
        uninstall_alarm
        ;;
    status)
        status_alarm
        ;;
    *)
        echo "Usage: $0 [install|uninstall|status]"
        echo ""
        echo "  install   - Install and load the MeloAlarm agent (default)"
        echo "  uninstall - Uninstall the MeloAlarm agent"
        echo "  status    - Check if MeloAlarm is installed and loaded"
        exit 1
        ;;
esac

