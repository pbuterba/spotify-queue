import spotipy
from spotipy.oauth2 import SpotifyOAuth

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
spotify.add_to_queue(home_uri, device_id='121affd97f452422d170f9cbe1f41191fcece3ec')
ms_elapsed = home['duration_ms']

while ms_elapsed < total_ms:
    queue = spotify.queue()
    current_song = queue['currently_playing']
    print(f'Current song: {current_song["name"]}')
    spotify.next_track(device_id='121affd97f452422d170f9cbe1f41191fcece3ec')
    spotify.pause_playback(device_id='121affd97f452422d170f9cbe1f41191fcece3ec')
    queue = spotify.queue()
    current_song = queue['currently_playing']
    print(f'Current song: {current_song["name"]}')
    spotify.previous_track(device_id='121affd97f452422d170f9cbe1f41191fcece3ec')
    spotify.pause_playback(device_id='121affd97f452422d170f9cbe1f41191fcece3ec')
