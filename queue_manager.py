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
    ms_elapsed = home['duration_ms']

    if ms_elapsed > total_ms:
        print('Not enough time in the drive')
        return 1
    elif ms_elapsed == total_ms:
        print('Insert "Almost Home" after "Home"')

    # Loop until end point
    print('Searching for insertion point...')
    while ms_elapsed < total_ms:
        queue = spotify.queue()
        current_song = queue['currently_playing']
        print(current_song["name"])
        ms_elapsed = ms_elapsed + current_song['duration_ms']
        spotify.next_track(device_id='DEVICE_ID_REDACTED')
        spotify.pause_playback(device_id='DEVICE_ID_REDACTED')
        songs_skipped = songs_skipped + 1

    print(f'Insert "Almost Home" after "{current_song["name"]}"')

    # Get insert location information
    seconds_elapsed = ms_elapsed // 1000
    ms_elapsed = ms_elapsed - (seconds_elapsed * 1000)

    minutes_elapsed = seconds_elapsed // 60
    seconds_elapsed = seconds_elapsed - (minutes_elapsed * 60)

    hours_elapsed = minutes_elapsed // 60
    minutes_elapsed = minutes_elapsed - (hours_elapsed * 60)

    print(f'Insert location is {hours_elapsed}:{minutes_elapsed}:{seconds_elapsed}.{ms_elapsed}')

    for i in range(songs_skipped):
        spotify.previous_track(device_id='DEVICE_ID_REDACTED')
    spotify.pause_playback(device_id='DEVICE_ID_REDACTED')

    # Add Home to queue
    spotify.add_to_queue(home_uri, device_id='DEVICE_ID_REDACTED')
    print('Added "Home" to queue')

    # Add current song to queue
    queue = spotify.queue()
    current_song = queue['currently_playing']
    current_uri = f'spotify:track:{current_song["id"]}'
    spotify.add_to_queue(current_uri, device_id='DEVICE_ID_REDACTED')
    print(f'Added {current_song["name"]} to queue')

    # Add Almost Home to queue
    spotify.add_to_queue(almost_home_uri, device_id='DEVICE_ID_REDACTED')
    print('Added "Almost Home" to queue')

    # Skip to start at "Home"
    spotify.next_track(device_id='DEVICE_ID_REDACTED')
    spotify.pause_playback(device_id='DEVICE_ID_REDACTED')

    return 0


if __name__ == "__main__":
    sys.exit(main())
