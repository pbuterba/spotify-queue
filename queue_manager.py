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


def confirmation() -> bool:
    """
    @brief      Function which allows the user to select from binary options using the ENTER key as "Yes" and entering an "E"
                character as "No"
    @return:    (bool) The option selected
    """
    choice = input()
    if choice == '':
        return True
    elif choice.lower() == 'e':
        return False
    else:
        print('Invalid command. Valid commands are "E" followed by RETURN, and RETURN (with no other input)')
        return confirmation()


def list_artists(song: Dict) -> str:
    """
    @brief      Represents a songs artists as a comma-separated list
    @param      (Dict) song: A dictionary representing the song
    @return:    (str): The comma-separated list of artists
    """
    string = ''
    for artist in song['artists']:
        string = string + artist['name'] + ', '

    return string[:-2]


def str_to_ms(duration: str) -> int:
    """
    @brief      Converts a duration string into milliseconds
    @param      (str) duration: The duration represented as a string
    @return:    (int): The number of milliseconds represented by the duration, or -1 if an invalid duration string is entered
    """
    try:
        duration_hours = int(duration.split(':')[0])
        duration_minutes = int(duration.split(':')[1])
    except ValueError:
        return -1

    total_minutes = duration_minutes + (duration_hours * 60)
    return total_minutes * 60000


def ms_to_str(ms: int) -> str:
    """
    @brief      Converts a number of milliseconds into a duration string hh:mm:ss.ms
    @param      (int) ms: The total number of milliseconds to represent as a string
    @return:    (str): The duration represented as a string hh:mm:ss.ms
    """
    # Calculate individual values
    seconds = ms // 1000
    ms = ms - (seconds * 1000)

    minutes = seconds // 60
    seconds = seconds - (minutes * 60)

    hours = minutes // 60
    minutes = minutes - (hours * 60)

    # Add leading zeros
    if minutes < 10:
        minutes = f'0{minutes}'

    if seconds < 10:
        seconds = f'0{seconds}'

    if ms < 10:
        ms = f'00{ms}'
    elif ms < 100:
        ms = f'0{ms}'

    return f'{hours}:{minutes}:{seconds}.{ms}'


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
        refresh = confirmation()
        if not refresh:
            return None

        devices = spotify.devices()['devices']

    # Get the device selection
    if len(devices) == 1:
        device = devices[0]
        print(f'Selected your device "{device["name"]}" ({device["type"]}). To use a different device, please open Spotify on that device, and restart this program')
    else:
        print('You have active Spotify sessions on the following devices: ')
        for idx, device in enumerate(devices):
            print(f'{idx + 1}. {device["name"]} ({device["type"]})')

        # Get choice
        try:
            selection_index = int(input('Please select the device for which you would like to manage the queue, by entering the number with which it is listed: '))
        except ValueError:
            selection_index = -1

        # Validate index
        while selection_index < 1 or selection_index > len(devices):
            selection_index = int(input(f'Please select a device between 1 and {len(devices)}'))

        device = devices[selection_index - 1]
        print(f'Selected "{device["name"]} ({device["type"]})')

    return device


def find_song(spotify: spotipy.client, title: str, artist: str) -> Dict | None:
    """
    @brief      Allows the user to find a specific song by name and artist, with album as a tie-breaking criterion
    @param      (Spotipy Client) spotify: An authenticated Spotipy Client object
    @param      (str) title: The title of the song being searched for
    @param      (str) artist: The artist of the song being searched for
    @return:
                (Dict): A dictionary representing the song selected
                (None): If the song could not be found, or the search was cancelled
    """
    query_title = title.replace(' ', '%20')
    query_artist = artist.replace(' ', '%20')
    results = spotify.search(q=f'{query_title}%20artist:{query_artist}')
    songs = []
    end_of_results = False
    while not end_of_results:
        # Check if this is the last page of results
        if results['tracks']['next'] is None:
            end_of_results = True

        # Loop over current page of results
        for result in results['tracks']['items']:
            for result_artist in result['artists']:
                if result_artist['name'] == artist:
                    songs.append(result)

        # Fetch next page of results
        if not end_of_results:
            results = spotify.search(q=f'{query_title}%20artist:{query_artist}', offset=results['tracks']['offset'] + results['tracks']['limit'])

    # Case where no song with that artist is found
    if not songs:
        print(f'Couldn\'t find a song called "{title}" by "{artist}" on Spotify')
        return None

    # Case where only one track was found
    if len(songs) == 1:
        song = songs[0]
        print(f'Found "{song["name"]}" by "{list_artists(song)}" - Album: {song["album"]["name"]}')
        print('Add song to queue? Press RETURN to add, enter "E" to skip')
        add = confirmation()
        if add:
            return song
        else:
            return None

    # Case where multiple tracks were found
    # List songs
    print(f'The following songs match your search criteria: ')
    for idx, song in enumerate(songs):
        print(f'{idx + 1}. {song["name"]} - {list_artists(song)} ({song["album"]["name"]})')

    # Get choice
    try:
        selected_index = int(input('Please select which song you would like to add, by typing the number with which it is listed. Enter 0 to find a new song'))
    except ValueError:
        selected_index = -1

    # Validate index
    while selected_index < 0 or selected_index > len(songs):
        selected_index = int(input(f'Selection must be between 0 and {len(songs)}'))

    # Return selected song
    if selected_index == 0:
        return None
    else:
        return songs[selected_index - 1]


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

    # Set up variables to track what songs will be added to the queue
    insert_after_list = {}
    starting_song = None
    starting_ms = 0

    # Continue adding songs until user enters empty song title
    title = input('Enter the title of a song to add to the queue: ')
    while title != '':
        # Get artist
        artist = input(f'Enter the artist for "{title}": ')

        # Search for the song
        song = find_song(spotify, title, artist)

        if song is not None:
            # Get duration information
            total_ms = str_to_ms(input(f'Enter the duration in the queue at which to insert "{song["name"]}", in hh:mm format: '))

            # Check for improperly formatted duration
            while total_ms == -1:
                print('Improperly formatted duration. Please try again')
                total_ms = str_to_ms(input())

            # Check for duration of zero if a starting song has already been set
            while total_ms == 0 and starting_song is not None:
                print(f'"{starting_song["name"]} is already set as the starting song. Please enter a new duration:')
                total_ms = str_to_ms(input())

                # Check for improperly formatted duration
                while total_ms == -1:
                    print('Improperly formatted duration. Please try again')
                    total_ms = str_to_ms(input())

            # Check if song is inserted at the beginning or in the middle of the queue
            if total_ms > 0:
                # Set tracking variables
                ms_elapsed = starting_ms
                songs_skipped = 0

                # Loop until end point
                print('Searching for insertion point...')
                while ms_elapsed < total_ms:
                    # Get queue
                    queue = spotify.queue()
                    while queue['currently_playing'] is None:
                        print('Could not fetch current song. Try briefly playing and pausing music on your phone so that it is recognized as an active queue')
                        print('Press RETURN to try again. Enter the value "E" to exit the program.')
                        check = confirmation()
                        if not check:
                            return 0

                    # Get current song
                    current_song = queue['currently_playing']
                    print(current_song["name"])
                    ms_elapsed = ms_elapsed + current_song['duration_ms']

                    # Check if song is meant to have another song inserted after it
                    if current_song['name'] in insert_after_list.keys():
                        ms_elapsed = ms_elapsed + insert_after_list[current_song['name']]

                    # Skip to next song
                    spotify.next_track(device_id=device['id'])
                    spotify.pause_playback(device_id=device['id'])
                    songs_skipped = songs_skipped + 1

                # Get insert location information
                duration_string = ms_to_str(ms_elapsed)

                # Output insertion location
                print(f'Insert "{song["name"]}" after "{current_song["name"]}" ({duration_string})')
                insert_after_list[current_song['name']] = song

                for i in range(songs_skipped):
                    spotify.previous_track(device_id=device['id'])
                spotify.pause_playback(device_id=device['id'])
            else:
                # Song is inserted at the beginning of the queue
                print(f'"{song["name"]}" will be inserted at the beginning of the queue')
                starting_song = song
                starting_ms = song['duration_ms']

        # Get next song title
        print('Enter the title of another song, or press RETURN to exit')
        title = input()

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
