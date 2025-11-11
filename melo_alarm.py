#!/usr/bin/env python3
"""
MeloAlarm - Spotify Playlist Alarm Clock
Fetches a random track from a Spotify playlist and plays it at alarm time.
"""

import os
import sys
import random
import subprocess
import time
import argparse
import re
from pathlib import Path
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Load environment variables
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI', 'http://localhost:8888/callback')
SPOTIFY_PLAYLIST_ID = os.getenv('SPOTIFY_PLAYLIST_ID')
SPOTIFY_USERNAME = os.getenv('SPOTIFY_USERNAME')

# Scope required for playing music
SCOPE = "user-read-playback-state,user-modify-playback-state,playlist-read-private"


def extract_playlist_id(playlist_input):
    """
    Extract playlist ID from various input formats:
    - Full URL: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M
    - Playlist URI: spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
    - Just the ID: 37i9dQZF1DXcBWIGoYBM5M
    """
    if not playlist_input:
        return None
    
    # Remove whitespace
    playlist_input = playlist_input.strip()
    
    # Try to extract ID from URL
    url_match = re.search(r'playlist/([a-zA-Z0-9]+)', playlist_input)
    if url_match:
        return url_match.group(1)
    
    # Try to extract ID from URI
    uri_match = re.search(r'spotify:playlist:([a-zA-Z0-9]+)', playlist_input)
    if uri_match:
        return uri_match.group(1)
    
    # If it's already just an ID (alphanumeric, typically 22 characters)
    if re.match(r'^[a-zA-Z0-9]{22}$', playlist_input):
        return playlist_input
    
    # Return as-is if no pattern matches (might still be valid)
    return playlist_input


def authenticate_spotify():
    """Authenticate with Spotify using OAuth."""
    if not all([SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET]):
        print("Error: Spotify credentials not found in environment variables.")
        print("Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env file")
        sys.exit(1)
    
    try:
        auth_manager = SpotifyOAuth(
            client_id=SPOTIFY_CLIENT_ID,
            client_secret=SPOTIFY_CLIENT_SECRET,
            redirect_uri=SPOTIFY_REDIRECT_URI,
            scope=SCOPE,
            cache_path=str(Path(__file__).parent / '.cache')
        )
        sp = spotipy.Spotify(auth_manager=auth_manager)
        return sp
    except Exception as e:
        print(f"Error authenticating with Spotify: {e}")
        sys.exit(1)


def get_playlist_tracks(sp, playlist_id):
    """Fetch all tracks from a Spotify playlist."""
    try:
        tracks = []
        results = sp.playlist_tracks(playlist_id)
        
        while results:
            for item in results['items']:
                if item['track'] and item['track']['id']:
                    tracks.append(item['track'])
            
            if results['next']:
                results = sp.next(results)
            else:
                break
        
        return tracks
    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
        return []


def open_spotify_app():
    """Open Spotify application on macOS."""
    try:
        subprocess.run(['open', '-a', 'Spotify'], check=True)
        # Wait a bit for Spotify to open
        time.sleep(3)
    except subprocess.CalledProcessError as e:
        print(f"Error opening Spotify app: {e}")
        print("Please make sure Spotify is installed on your Mac")


def play_track(sp, track_uri, device_id=None):
    """Play a track on Spotify."""
    try:
        # Get available devices
        devices = sp.devices()
        active_devices = [d for d in devices['devices'] if d['is_active']]
        
        if not active_devices and not device_id:
            print("No active Spotify devices found.")
            print("Please open Spotify and make sure it's playing on a device.")
            return False
        
        # Use the first active device or the specified device
        target_device = device_id or active_devices[0]['id']
        
        # Start playback
        sp.start_playback(device_id=target_device, uris=[track_uri])
        print(f"Playing: {track_uri}")
        return True
    except Exception as e:
        print(f"Error playing track: {e}")
        # If playback fails, try to transfer playback to this computer
        try:
            devices = sp.devices()
            if devices['devices']:
                computer_device = devices['devices'][0]
                sp.transfer_playback(computer_device['id'], force_play=True)
                sp.start_playback(device_id=computer_device['id'], uris=[track_uri])
                print(f"Playing on {computer_device['name']}: {track_uri}")
                return True
        except Exception as transfer_error:
            print(f"Error transferring playback: {transfer_error}")
        return False


def is_interactive():
    """Check if running in an interactive environment (has stdin)."""
    return sys.stdin.isatty()


def get_playlist_id_from_user():
    """Prompt user for playlist ID if not provided."""
    # Check if we're in an interactive environment
    if not is_interactive():
        return None
    
    print("\n📋 Playlist ID not provided.")
    print("You can provide it in one of these formats:")
    print("  - Full URL: https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M")
    print("  - Playlist URI: spotify:playlist:37i9dQZF1DXcBWIGoYBM5M")
    print("  - Just the ID: 37i9dQZF1DXcBWIGoYBM5M")
    print()
    
    while True:
        try:
            playlist_input = input("Enter playlist ID or URL: ").strip()
            if playlist_input:
                playlist_id = extract_playlist_id(playlist_input)
                if playlist_id:
                    return playlist_id
                else:
                    print("❌ Could not extract playlist ID. Please try again.")
            else:
                print("❌ Playlist ID cannot be empty. Please try again.")
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Input cancelled.")
            return None


def main():
    """Main function to select and play a random track."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='MeloAlarm - Play a random song from a Spotify playlist',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 melo_alarm.py
  python3 melo_alarm.py --playlist 37i9dQZF1DXcBWIGoYBM5M
  python3 melo_alarm.py --playlist "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"
  python3 melo_alarm.py -p spotify:playlist:37i9dQZF1DXcBWIGoYBM5M
        """
    )
    parser.add_argument(
        '-p', '--playlist',
        type=str,
        help='Spotify playlist ID, URL, or URI. If not provided, will prompt interactively or use .env file.'
    )
    
    args = parser.parse_args()
    
    print("🎵 MeloAlarm - Starting...")
    
    # Determine playlist ID: command-line argument > .env file > interactive prompt
    playlist_id = None
    
    if args.playlist:
        # Extract ID from command-line argument
        playlist_id = extract_playlist_id(args.playlist)
        if not playlist_id:
            print(f"❌ Error: Could not extract playlist ID from: {args.playlist}")
            sys.exit(1)
        print(f"✅ Using playlist ID from command-line: {playlist_id}")
    elif SPOTIFY_PLAYLIST_ID:
        # Use from .env file
        playlist_id = extract_playlist_id(SPOTIFY_PLAYLIST_ID)
        print(f"✅ Using playlist ID from .env file: {playlist_id}")
    else:
        # Try to prompt user interactively (only works if stdin is available)
        playlist_id = get_playlist_id_from_user()
        if playlist_id:
            print(f"✅ Using playlist ID: {playlist_id}")
    
    if not playlist_id:
        print("❌ Error: No playlist ID provided")
        print("\nPlease provide playlist ID in one of these ways:")
        print("  1. Command-line argument: python3 melo_alarm.py --playlist <ID>")
        print("  2. .env file: Set SPOTIFY_PLAYLIST_ID in .env file")
        print("  3. Interactive prompt: Run the script interactively")
        print("\nFor scheduled runs (launchd), use option 1 or 2.")
        sys.exit(1)
    
    # Authenticate with Spotify
    print("\nAuthenticating with Spotify...")
    sp = authenticate_spotify()
    
    # Get playlist tracks
    print(f"\nFetching tracks from playlist: {playlist_id}")
    tracks = get_playlist_tracks(sp, playlist_id)
    
    if not tracks:
        print("No tracks found in playlist or error occurred")
        sys.exit(1)
    
    print(f"Found {len(tracks)} tracks in playlist")
    
    # Select a random track
    random_track = random.choice(tracks)
    track_name = random_track['name']
    track_artists = ', '.join([artist['name'] for artist in random_track['artists']])
    track_uri = random_track['uri']
    
    print(f"\n🎶 Selected track: {track_name} by {track_artists}")
    print(f"URI: {track_uri}")
    
    # Open Spotify app
    print("\nOpening Spotify app...")
    open_spotify_app()
    
    # Wait a bit for Spotify to fully initialize
    time.sleep(2)
    
    # Play the track
    print(f"\nPlaying track...")
    if play_track(sp, track_uri):
        print(f"✅ Successfully started playing: {track_name} by {track_artists}")
    else:
        print("❌ Failed to play track automatically.")
        print("Please manually play the track in Spotify:")
        print(f"   {track_name} by {track_artists}")


if __name__ == "__main__":
    main()

