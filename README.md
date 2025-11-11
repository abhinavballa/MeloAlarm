# MeloAlarm 🎵

A macOS alarm clock that plays a random song from your Spotify playlist at your chosen time.

## Features

- Fetches tracks from your Spotify playlist using the Spotify Web API
- Randomly selects a song each day
- Automatically opens Spotify and plays the selected track
- Runs daily at your configured alarm time using macOS launchd
- Flexible playlist configuration: command-line argument, .env file, or interactive prompt
- Supports playlist URLs, URIs, or just the ID

## Quick Start

```bash
# 1. Run setup script
./setup.sh

# 2. Edit .env file with your Spotify credentials
# (See Setup Instructions below for details)

# 3. Test the script
python3 melo_alarm.py

# 4. Update alarm time in com.meloalarm.plist and install
./install_alarm.sh install
```

## Prerequisites

1. **Python 3.7+** - Usually pre-installed on macOS
2. **Spotify Account** - Free or Premium
3. **Spotify App** - Installed on your Mac
4. **Spotify Developer Account** - Free to create

## Setup Instructions

### 1. Create a Spotify App

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create an App"
4. Fill in the app details:
   - App name: "MeloAlarm" (or any name you like)
   - App description: "Alarm clock that plays Spotify playlists"
   - Redirect URI: `http://localhost:8888/callback`
   - Accept the terms and click "Create"
5. Copy your **Client ID** and **Client Secret**

### 2. Get Your Playlist ID

1. Open Spotify (web or app)
2. Navigate to your playlist
3. Copy the playlist URL (e.g., `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`)
4. The playlist ID is the part after `/playlist/` (e.g., `37i9dQZF1DXcBWIGoYBM5M`)

### 3. Install Dependencies

```bash
pip3 install -r requirements.txt
```

Or if you prefer to use a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` and fill in your credentials:
   ```env
   SPOTIFY_CLIENT_ID=your_actual_client_id
   SPOTIFY_CLIENT_SECRET=your_actual_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
   SPOTIFY_PLAYLIST_ID=your_playlist_id  # Optional: can also be provided via command-line
   SPOTIFY_USERNAME=your_spotify_username
   ```

   **Note:** `SPOTIFY_PLAYLIST_ID` is optional. You can provide it in three ways:
   - In the `.env` file (recommended for scheduled runs)
   - As a command-line argument: `python3 melo_alarm.py --playlist <ID>`
   - Interactively when running the script (prompts for input)

### 5. Initial Authentication

Run the script manually once to authenticate with Spotify:

```bash
# Option 1: With playlist ID in .env file
python3 melo_alarm.py

# Option 2: With playlist ID as command-line argument
python3 melo_alarm.py --playlist 37i9dQZF1DXcBWIGoYBM5M

# Option 3: With full playlist URL
python3 melo_alarm.py --playlist "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Option 4: Interactive mode (will prompt for playlist ID)
python3 melo_alarm.py
```

This will:
- Open a browser window for Spotify authorization
- Ask you to log in and authorize the app
- Save the authentication token to `.cache` file
- Test playing a random song from your playlist

**Playlist ID Formats Supported:**
- Full URL: `https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M`
- Playlist URI: `spotify:playlist:37i9dQZF1DXcBWIGoYBM5M`
- Just the ID: `37i9dQZF1DXcBWIGoYBM5M`

### 6. Set Up Daily Schedule with launchd

**Option A: Using the install script (Recommended)**

1. **Update the alarm time** in `com.meloalarm.plist`:
   - Edit `com.meloalarm.plist`
   - Change the `Hour` (0-23) and `Minute` (0-59) values in `StartCalendarInterval`
   - (Optional) To use a specific playlist, add `--playlist <ID>` as an argument in `ProgramArguments`

2. **Ensure playlist ID is set**:
   - Either set `SPOTIFY_PLAYLIST_ID` in your `.env` file (recommended)
   - Or add `--playlist <ID>` to the `ProgramArguments` array in the plist file
   - **Note:** For scheduled runs, you cannot use interactive prompts, so the playlist ID must be in `.env` or passed as an argument

3. **Run the install script**:
   ```bash
   ./install_alarm.sh install
   ```
   
   The script will automatically:
   - Update paths in the plist file
   - Detect and use virtual environment if present
   - Copy the plist to the correct location
   - Load the launchd agent

4. **Verify installation**:
   ```bash
   ./install_alarm.sh status
   ```

**Option B: Manual installation**

1. **Update the plist file** with your alarm time:
   - Edit `com.meloalarm.plist`
   - Change the `Hour` and `Minute` values in `StartCalendarInterval`
   - Update the Python path if using a virtual environment
   - Update the script path to match your installation location

2. **Load the launch agent**:
   ```bash
   # Copy plist to LaunchAgents directory
   cp com.meloalarm.plist ~/Library/LaunchAgents/
   
   # Load the agent
   launchctl load ~/Library/LaunchAgents/com.meloalarm.plist
   ```

3. **Verify it's loaded**:
   ```bash
   launchctl list | grep meloalarm
   ```

### 7. Test the Alarm

Test if everything works:

```bash
# Test run immediately (uses playlist from .env or plist arguments)
launchctl start com.meloalarm

# Or run the script directly with various options
python3 melo_alarm.py                                    # Uses .env or prompts
python3 melo_alarm.py --playlist 37i9dQZF1DXcBWIGoYBM5M  # Specific playlist
python3 melo_alarm.py -p "https://open.spotify.com/playlist/..."  # Full URL
```

## Usage

### Running Manually

```bash
# With playlist ID from .env file
python3 melo_alarm.py

# With playlist ID as command-line argument
python3 melo_alarm.py --playlist 37i9dQZF1DXcBWIGoYBM5M

# With full playlist URL
python3 melo_alarm.py --playlist "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"

# Interactive mode (will prompt for playlist ID)
python3 melo_alarm.py

# Show help
python3 melo_alarm.py --help
```

### Using Playlist ID in launchd (Optional)

If you want to specify a playlist ID directly in the plist file instead of using `.env`, you can modify the `ProgramArguments` array:

```xml
<key>ProgramArguments</key>
<array>
    <string>/usr/bin/python3</string>
    <string>/Users/abhi/Documents/GitHub/MeloAlarm/melo_alarm.py</string>
    <string>--playlist</string>
    <string>37i9dQZF1DXcBWIGoYBM5M</string>
</array>
```

**Note:** Using `.env` file is recommended as it's easier to change without modifying the plist file.

## Managing the Alarm

### Change Alarm Time

1. Edit `com.meloalarm.plist`:
   ```xml
   <key>Hour</key>
   <integer>7</integer>  <!-- Change to your desired hour (0-23) -->
   <key>Minute</key>
   <integer>0</integer>  <!-- Change to your desired minute (0-59) -->
   ```

2. Reload the agent:
   ```bash
   ./install_alarm.sh install
   ```
   
   Or manually:
   ```bash
   launchctl unload ~/Library/LaunchAgents/com.meloalarm.plist
   launchctl load ~/Library/LaunchAgents/com.meloalarm.plist
   ```

### Disable the Alarm

```bash
launchctl unload ~/Library/LaunchAgents/com.meloalarm.plist
```

### Enable the Alarm

```bash
launchctl load ~/Library/LaunchAgents/com.meloalarm.plist
```

### Uninstall the Alarm

```bash
./install_alarm.sh uninstall
```

Or manually:
```bash
launchctl unload ~/Library/LaunchAgents/com.meloalarm.plist
rm ~/Library/LaunchAgents/com.meloalarm.plist
```

### Check Status

```bash
./install_alarm.sh status
```

### View Logs

Check the log files for any issues:
```bash
tail -f melo_alarm.log
tail -f melo_alarm.error.log
```

## Troubleshooting

### Script doesn't run at scheduled time

1. Check if launchd has loaded the job:
   ```bash
   launchctl list | grep meloalarm
   ```

2. Check the log files for errors:
   ```bash
   cat melo_alarm.error.log
   ```

3. Make sure Python path is correct in the plist file

### Authentication errors

- Delete the `.cache` file and run the script again to re-authenticate
- Make sure your Spotify app credentials are correct in `.env`
- Check that the redirect URI matches what you set in the Spotify Developer Dashboard

### Spotify doesn't open or play

- Make sure Spotify is installed on your Mac
- Try running the script manually to test
- Check that you have an active Spotify device (the script will try to use your active device)
- Make sure your Mac's volume is not muted

### Permission issues

- Make sure the script has execute permissions:
  ```bash
  chmod +x melo_alarm.py
  ```

## Notes

- The script requires Spotify to be installed on your Mac
- For best results, keep your Mac awake (disable sleep) or use a Mac that stays on
- The script will try to play on your active Spotify device, but you may need to manually select a device in some cases
- Authentication tokens are cached in `.cache` file - delete this file if you need to re-authenticate

## License

MIT

