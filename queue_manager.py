"""
@package    queue-manager
@brief      This program allows for custom insertion of songs into existing Spotify queues

@author     Preston Buterbaugh
@date       5/25/2023
@updated    7/8/2023
"""
# Imports
import sys
from typing import Dict

import spotipy
from spotipy.oauth2 import SpotifyOAuth


def get_device(spotify: spotipy.client) -> Dict | None:
    """
    @brief      Function that takes the user through a process of selecting which device to manage
    @param      (Spotipy Client) spotify: An authenticated Spotipy client object
    @return
                - (Dict): A dictionary representing the device selected
                - (None): The user cancelled the program
    """
    # Get device list
    devices = spotify.devices()['devices']
    while len(devices) == 0:
        print('You have no active Spotify sessions. Please open and sign into Spotify on a device. Press RETURN to refresh. Enter "E" to exit')
        choice = input()

        if choice.lower() == 'e':
            return None

        while choice != '':
            print(f'Invalid command {choice}. Valid commands are "E" or RETURN (no input)')

        devices = spotify.devices()['devices']

    # Get the device selection
    if len(devices) == 1:
        device = devices[0]
        print(f'Selected your device "{device["name"]}" ({device["type"]}). To use a different device, please open Spotify on that device, and restart this program')
    else:
        print('You have active Spotify sessions on the following devices: ')
        for idx, device in enumerate(devices):
            print(f'{idx + 1}. {device["name"]} ({device["type"]})')

        selection_index = int(input('Please select the device for which you would like to manage the queue, by entering the number with which it is listed: '))
        while selection_index < 1 or selection_index > len(devices):
            selection_index = int(input(f'Please select a device between 1 and {len(devices)}'))

        device = devices[selection_index - 1]
        print(f'Selected "{device["name"]} ({device["type"]})')

    return device


def main() -> int:
    """
    @brief      Main program entrypoint. Allows a user to determine the optimal point to insert songs into their Spotify queue
    @return:    (int)
                - 0 if finished with no errors
                - 1 if errors occurred
    """
    # Set API scopes
    scope = 'user-library-read user-read-playback-state user-modify-playback-state'

    # Log into Spotify
    spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))
    print(f'Welcome, {spotify.current_user()["display_name"]}!')
    print(f'Fetching your devices...')

    # Get user device selection
    device = get_device(spotify)

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
        while queue['currently_playing'] is None:
            print('Could not fetch current song. Try briefly playing and pausing music on your phone so that it is recognized as an active queue')
            print('Press ENTER to try again. Press "E" followed by ENTER to cancel.')
            keyboard = input()
            if keyboard.lower() == 'e':
                print('Aborting program')
                return 0
            elif keyboard.lower() == '':
                queue = spotify.queue()
            else:
                print('Unrecognized command. Press ENTER to fetch queue again, press "E" followed by ENTER to end program')

        current_song = queue['currently_playing']
        print(current_song["name"])
        ms_elapsed = ms_elapsed + current_song['duration_ms']
        spotify.next_track(device_id=device['id'])
        spotify.pause_playback(device_id=device['id'])
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
        spotify.previous_track(device_id=device['id'])
    spotify.pause_playback(device_id=device['id'])

    # Add Home to queue
    spotify.add_to_queue(home_uri, device_id=device['id'])
    print('Added "Home" to queue')

    # Add current song to queue
    queue = spotify.queue()
    current_song = queue['currently_playing']
    current_uri = f'spotify:track:{current_song["id"]}'
    spotify.add_to_queue(current_uri, device_id=device['id'])
    print(f'Added "{current_song["name"]}" to queue')

    # Add Almost Home to queue
    spotify.add_to_queue(almost_home_uri, device_id=device['id'])
    print('Added "Almost Home" to queue')

    # Skip to start at "Home"
    spotify.next_track(device_id=device['id'])
    spotify.pause_playback(device_id=device['id'])

    return 0


if __name__ == "__main__":
    sys.exit(main())
