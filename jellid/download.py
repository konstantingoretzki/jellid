import os

import api
import utils


def get_movies(session, movies, yes, path=""):
    for movie in movies:
        # get info about movie
        movie_info = api.get_item_info(session, movie)

        # TODO: subs_path for movie name aswell?
        movie_name = movie_info["Name"]
        movie_container = movie_info["Container"].split(",")[0]
        movie_filename = utils.subs_path(movie_name) + "." + movie_container

        print(f"\n🎥 Movie: {movie_name}")

        # ask before download
        if not yes:
            user_input = input(f"Download the movie ? (y/n): ")
            if user_input != "y":
                continue

        session.download_item(movie, os.path.join(path, movie_filename))


def get_shows(session, series, yes, path=""):
    # TODO
    pass


def get_albums(session, albums, yes, path=""):
    for album in albums:
        # get list of songs
        songs = api.get_songs(session, album)

        # TODO: handle albums with multiple disks

        # directory name
        album_name = songs["Items"][0]["Album"]
        directory = os.path.join(path, utils.subs_path(album_name))

        print(f"\n🎶 Album: {album_name}")
        number_songs = songs["TotalRecordCount"]

        # ask before download
        if not yes:
            user_input = input(
                f"Found {number_songs} song(s) - do you want to download it / them? (y/n): "
            )
            if user_input != "y":
                continue

        utils.save_mkdir(directory)

        # Is it possible to now have an index number?
        for song in songs["Items"]:
            print(
                "Downloading song "
                + str(song["IndexNumber"])
                + "/"
                + str(number_songs)
                + " ..."
            )
            # Add leading '0' if the track number < 10
            song_name = (
                f"{int(song['IndexNumber']) if int(song['IndexNumber']) >= 10 else '0'+str(song['IndexNumber'])} - "
                + utils.subs_path(song["Name"])
            )

            song_filename = song_name + "." + song["MediaSources"][0]["Container"]
            session.download_item(song["Id"], os.path.join(directory, song_filename))
            print("\033[2A")


def get_artists(session, artists, yes, path=""):
    for artist in artists:
        # get list of albums
        albums = api.get_albums(session, artist)

        # get the artist name through the first album
        artist_name = albums["Items"][0]["AlbumArtist"]
        directory = os.path.join(path, utils.subs_path(artist_name))

        print(f"\n🎨 Artist: {artist_name}")

        # ask before download
        if not yes:
            user_input = input(f"Download all the albums ? (y/n): ")
            if user_input != "y":
                continue

        # create artist directory
        utils.save_mkdir(directory)

        # list of albums for get_albums()
        albums_ids = [album["Id"] for album in albums["Items"]]

        get_albums(session, albums_ids, yes=True, path=directory)
        print("")
