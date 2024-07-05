import os

import api
import utils


def get_movies(session, movies, yes, path=""):
    for movie in movies:
        # Get info about movie
        movie_info = api.get_item_info(session, movie)
        movie_name = movie_info["Name"]

        print(f"\n🎥 Movie: {movie_name}")

        # Ask before download
        if not yes:
            user_confirm = input(f"Download the movie ? (y/n): ")
            if user_confirm != "y":
                continue

        # Multiple quality versions exists
        if ( (len(movie_info["MediaSources"]) > 1) and (not yes)):
            print(f"\nMultiple formats exists:")
            index_ctr = 0
            for source in movie_info["MediaSources"]:
                print(f"{index_ctr}) - {source['Name']}")
                index_ctr += 1

            valid_indizes = list(range(0, len(movie_info["MediaSources"])))
            user_index = input(f"Which version to download? (index, e.g. '0'): ")

            # Validate user selection
            try:
                # Index out of range
                if not int(user_index) in valid_indizes:
                    raise ()
                # Different sources can have different containers
                movie_container = movie_info["MediaSources"][int(user_index)][
                    "Container"
                ]
                # Override the ID to the selected item
                movie = movie_info["MediaSources"][int(user_index)]["Id"]
            except Exception:
                # Invalid user input like out of range or float input
                print(f"Invalid selection - exiting ...\n")
                exit(1)

        # Only one version exists or auto-yes flag was set
        else:
            movie_container = movie_info["MediaSources"][0]["Container"]

        movie_filename = utils.subs_path(movie_name) + "." + movie_container
        session.download_item(movie, os.path.join(path, movie_filename))


def get_shows(session, shows, yes, path=""):
    for show in shows:
        # Get list of episodes
        episodes = api.get_episodes(session, show)

        # Directory name
        show_name = episodes["Items"][0]["SeriesName"]
        directory = os.path.join(path, utils.subs_path(show_name))

        print(f"\n📺 Show: {show_name}")
        number_episodes = episodes["TotalRecordCount"]

        # Ask before download
        if not yes:
            user_confirm = input(
                f"Found {number_episodes} episode(s) - do you want to download it / them? (y/n): "
            )
            if user_confirm != "y":
                continue

        # For every unique season
        seasons = [episode["SeasonName"] for episode in episodes["Items"]]
        print(sorted(list(set(seasons))))
        for season in sorted(list(set(seasons))):
            # Create season dir
            directory = os.path.join(path, utils.subs_path(show_name), utils.subs_path(season))
            utils.save_mkdirs(directory)

            # Get episodes per season
            # Costs a few cycles, but now it's sure that the episode is part of the season
            season_episodes = [episode["Id"] for episode in episodes["Items"] if season == episode["SeasonName"]]
            get_movies(session, season_episodes, yes=True, path=directory)
        print("")


def get_albums(session, albums, yes, path=""):
    for album in albums:
        # Get list of songs
        songs = api.get_songs(session, album)

        # Directory name
        album_name = songs["Items"][0]["Album"]
        directory = os.path.join(path, utils.subs_path(album_name))

        print(f"\n🎶 Album: {album_name}")
        number_songs = songs["TotalRecordCount"]

        # Ask before download
        if not yes:
            user_confirm = input(
                f"Found {number_songs} song(s) - do you want to download it / them? (y/n): "
            )
            if user_confirm != "y":
                continue

        utils.save_mkdirs(directory)

        # Check if multiple discs are present
        parent_indizes = [song["ParentIndexNumber"] for song in songs["Items"]]
        multiple_disks = any(index != 1 for index in parent_indizes)
        # Manual tracking needed because the index would reset for multiple dics
        index_counter = 1

        # Is it possible to not have an index number?
        for song in songs["Items"]:
            print(
                "Downloading song "
                + str(index_counter)
                + "/"
                + str(number_songs)
                + " ..."
            )
            # Add leading '0' if the track number < 10
            song_name = (
                f"{int(song['IndexNumber']) if int(song['IndexNumber']) >= 10 else '0'+str(song['IndexNumber'])} - "
                + utils.subs_path(song["Name"])
            )

            # Add leading number if multiple discs are present
            if multiple_disks:
                song_name = str(song["ParentIndexNumber"]) + song_name

            song_filename = song_name + "." + song["MediaSources"][0]["Container"]
            session.download_item(song["Id"], os.path.join(directory, song_filename))
            index_counter += 1
            print("\033[2A")


def get_artists(session, artists, yes, path=""):
    for artist in artists:
        # Get list of albums
        albums = api.get_albums(session, artist)

        # Get the artist name through the first album
        artist_name = albums["Items"][0]["AlbumArtist"]
        directory = os.path.join(path, utils.subs_path(artist_name))

        print(f"\n🎨 Artist: {artist_name}")

        # Ask before download
        if not yes:
            user_confirm = input(f"Download all the albums ? (y/n): ")
            if user_confirm != "y":
                continue

        # Create artist directory
        utils.save_mkdirs(directory)

        # List of albums for get_albums()
        albums_ids = [album["Id"] for album in albums["Items"]]

        get_albums(session, albums_ids, yes=True, path=directory)
        print("")
