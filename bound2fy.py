# bound2fy 0.1.3
# author: @soxasora

import os
import spotipy
import glob
import yaml
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from termcolor import colored
from spotipy.oauth2 import SpotifyOAuth

file_config = 'config.yaml'
default_config = {
    'client_id': 'YOUR CLIENT ID',
    'client_secret': 'YOUR CLIENT SECRET',
    'redirect_uri': 'https://localhost:8888/callback'
}

def read_file(file_config):
    with open(file_config, 'r') as f:
        return yaml.safe_load(f)


if not os.path.exists(file_config):
    print(colored("Generating configuration file...", color='yellow'))
    with open(file_config, 'w') as f:
        yaml.dump(default_config, f)
    print(colored("Configuration file has been generated, please check the config file", color='green'))
    quit()
else:
    config = read_file(file_config)
    print(colored("Configuration file has been loaded", color='green'))

# Authentication stage
print(colored("Authenticating to Spotify...", 'yellow'), end='\r', flush=True)
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-public",  # Can create/modify public playlists
        redirect_uri=config["redirect_uri"],
        client_id=config["client_id"],
        client_secret=config["client_secret"],
        cache_path="token.txt"
    )
)
print("Profile: " + sp.user(sp.current_user()['id'])['display_name']
      + colored(" Authenticated successfully to Spotify.", 'green'))

# Directory input
folder = input(colored("Drag here your folder...", 'yellow'))
if folder.endswith(" "):
    folder = folder[:-1]

# Retrieving only flacs and mp3s
filelist = glob.glob(folder + "/*.flac") + glob.glob(folder + "/*.mp3")

# Sort list alphabetically
filelist.sort()

# Track IDs list initialization
track_ids = []

# Search the correspondant Spotify track for every file found
for index, song in enumerate(filelist):
    if song.endswith(".mp3"):
        file = MP3(song)
    else:
        file = FLAC(song)

    # Metadata analyzed
    title = file["TITLE"]
    artist = file["ARTIST"]
    album = file["ALBUM"]

    # Searching for the track on Spotify using Artist, Album, Title
    query = f"artist:{artist} album:{album} track:{title}"
    results = sp.search(q=query, type='track')
    if not results['tracks']['items']:
        found = False
        print(colored("Track: " + filelist[index] + " has not been found.", color='red'))
        c = input("Want to search for it manually? Y/N [Y]: ").lower()
        match c:
            case '_':
                while not found:
                    # TODO Verifica perché un exit dalla ricerca manuale non funziona
                    # TODO Risolta gestione apici nell'url; Risolto case-sensitive
                    title = input("Enter the title of the track you would like to search for: ")
                    title = title.replace("'", " ").lower()
                    artist = input("Enter the name of the artist of the track: ")
                    artist = artist.replace("'", " ").lower()
                    album = input("Enter the title of the album of the track: ")
                    album = album.replace("'", " ").lower()

                    query = f"artist:{artist} album:{album} track:{title}"
                    results = sp.search(q=query, limit=10, type='track')
                    if not results['tracks']['items']:
                        print(colored("Track: " + title + " by " + artist + "has not been found on Spotify.", color='red'))
                        c_2 = input("Want to try again? Y/N [Y]: ").lower()
                        match c_2:
                            case 'n':
                                found = True
                            case '_':
                                found = False
                    else:
                        found = True
                        print("These tracks have been found: ")
                        for index2, track in enumerate(results['tracks']['items']):
                            print(index2.__str__() + ": " + colored(track['name'], color='yellow'))
                        pick = int(input("Pick a track by its ID [0-99]: "))
                        ids = results['tracks']['items'][pick]['id']
                        # Append the track id to the list
                        track_ids.append(ids)

            case 'n':
                print(colored("File " + filelist[index] + " skipped.", color='yellow'))
    else:
        ids = results['tracks']['items'][0]['id']
        # Append the first result's track id to the list
        track_ids.append(ids)


# Completed list overview
print("These tracks have been found:")
for index, i in enumerate(track_ids):
    print(filelist[index] + " >> " + colored(sp.track('spotify:track:' + i)["name"], color='green'))

# Playlist creation process
c = input("You're about to create a playlist on your Spotify account. Proceed Y/N [N]: ").lower()
match c:
    case 'Y':
        playlist_name = input("Enter the playlist name: ")
        playlist_desc = input("Enter the playlist description: ")
        user_id = sp.current_user()['id']
        playlist = sp.user_playlist_create(user=user_id, name=playlist_name, description=playlist_desc)

        # Add tracks to the playlist
        sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=track_ids)
    case '_':
        print("No playlist will be created.")
