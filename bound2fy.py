# bound2fy 0.1
# author: @soxasora

import spotipy
import glob
import yaml
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from termcolor import colored
from spotipy.oauth2 import SpotifyOAuth


with open("config.yaml") as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

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
print("Profile: "+sp.user(sp.current_user()['id'])['display_name']
      + colored("Authenticated successfully to Spotify.", 'green'))


# Directory input
folder = input(colored("Drag here your folder...", 'yellow'))
if folder.endswith(" "):
    folder = folder[:-1]

# Retrieving only flacs and mp3s
filelist = glob.glob(folder + "/*.flac") + glob.glob(folder + "/*.mp3")

# Track IDs list initialization
track_ids = []

# Search the correspondant Spotify track for every file found
for song in filelist:
    if song.endswith(".mp3"): file = MP3(song)
    else: file = FLAC(song)

    # Metadata analyzed
    titolo = file["TITLE"]
    artista = file["ARTIST"]
    album = file["ALBUM"]

    # Searching for the track on Spotify using Artist, Album, Title
    query = f"artist:{artista} album:{album} track:{titolo}"
    results = sp.search(q=query, type='track')
    id_traccia = results['tracks']['items'][0]['id']
    # Append the first result's track id to the list
    track_ids.append(id_traccia)

# Completed list overview
print("These tracks have been found:")
counter = 0
for i in track_ids:
    print(filelist[counter] + " >> " + sp.track('spotify:track:'+i)["name"])
    counter =+ 1

# Playlist creation process
print("You're about to create a playlist on your Spotify account.")
playlist_name = input("Playlist name: ")
playlist_desc = input("Playlist description: ")
user_id = sp.current_user()['id']
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, description=playlist_desc)

# Add tracks to the playlist
sp.user_playlist_add_tracks(user=user_id, playlist_id=playlist['id'], tracks=track_ids)
