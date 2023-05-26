import sys

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def main() -> int:
    scope = 'user-library-read user-read-playback-state user-modify-playback-state'

    # Log into Spotify
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

    # Get duration information
    duration = input('Enter the duration to insert "Almost Home" at in hh:mm format: ')
    duration_hours = int(duration.split(':')[0])
    duration_minutes = int(duration.split(':')[1])
    total_minutes = duration_minutes + (duration_hours * 60)
    total_ms = total_minutes * 60 * 1000
    songs_skipped = 0

    # URIs for fixed tracks
    home_uri = 'spotify:track:2aMb1asq5acm7cDYlFsYhY'
    almost_home_uri = 'spotify:track:4c4Y0MvScCAI98Eum1dwOz'

    # Add Home to queue
    home = spotify.track(home_uri)
    spotify.add_to_queue(home_uri, device_id='DEVICE_ID_REDACTED')
    print('Added "Home" to queue')
    ms_elapsed = home['duration_ms']

    # Add current song to queue
    queue = spotify.queue()
    current_song = queue['currently_playing']
    current_uri = f'spotify:track:{current_song["id"]}'
    spotify.add_to_queue(current_uri, device_id='DEVICE_ID_REDACTED')
    print(f'Added {current_song["name"]} to queue')
    ms_elapsed = ms_elapsed + current_song['duration_ms']

    # Add Almost Home to queue
    spotify.add_to_queue(almost_home_uri, device_id='DEVICE_ID_REDACTED')
    print('Added "Almost Home" to queue')

    # Skip to first song after the initial 3
    for i in range(4):
        spotify.next_track(device_id='DEVICE_ID_REDACTED')
    spotify.pause_playback(device_id='DEVICE_ID_REDACTED')

    if ms_elapsed > total_ms:
        print('Not enough time in the drive')
        return 1

    # Loop until end point
    while ms_elapsed < total_ms:
        queue = spotify.queue()
        current_song = queue['currently_playing']
        print(f'Current song: {current_song["name"]}')
        spotify.next_track(device_id='DEVICE_ID_REDACTED')
        spotify.pause_playback(device_id='DEVICE_ID_REDACTED')
        queue = spotify.queue()
        current_song = queue['currently_playing']
        print(f'Current song: {current_song["name"]}')
        spotify.previous_track(device_id='DEVICE_ID_REDACTED')
        spotify.pause_playback(device_id='DEVICE_ID_REDACTED')

    return 0


if __name__ == "__main__":
    sys.exit(main())
