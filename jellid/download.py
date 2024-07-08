import os

import api
import utils


class Downloader:
    def __init__(self, session):
        self.session = session

    def get_movies(self, movies, path="", yes=True):
        for movie in movies:
            # Get info about movie
            movie_info = api.get_item_info(self.session, movie)
            movie_name = movie_info["Name"]

            print(f"\n🎥 Movie: {movie_name}")

            # Ask before download
            if not yes:
                user_confirm = input(f"Download the movie ? (y/n): ")
                if user_confirm != "y":
                    continue

            # Multiple quality versions exists
            if (len(movie_info["MediaSources"]) > 1) and (not yes):
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
            self.session.download_item(movie, os.path.join(path, movie_filename))
        print("")

    def get_seasons(self, seasons, path="", yes=True):
        for season in seasons:
            # Get list of episodes for the selected season
            episodes = api.get_episodes(self.session, season)

            # Directory name
            show_name = episodes["Items"][0]["SeriesName"]
            season_name = episodes["Items"][0]["SeasonName"]
            directory = os.path.join(path, utils.subs_path(season_name))

            print(f"\n📺 {show_name}: {season_name}")
            number_episodes = episodes["TotalRecordCount"]

            # Ask before download
            if not yes:
                user_confirm = input(
                    f"Found {number_episodes} episode(s) - do you want to download it / them? (y/n): "
                )
                if user_confirm != "y":
                    continue

            utils.save_mkdirs(directory)

            episode_ids = [episode["Id"] for episode in episodes["Items"]]
            self.get_movies(episode_ids, path=directory)
        print("")

    def get_shows(self, shows, path="", yes=True):
        for show in shows:
            # Get list of seasons
            seasons = api.get_seasons(self.session, show)

            # Directory name
            show_name = seasons["Items"][0]["SeriesName"]
            directory = os.path.join(path, utils.subs_path(show_name))

            print(f"\n📺 Show: {show_name}")

            # Ask before download
            if not yes:
                user_confirm = input(f"Download all the seasons ? (y/n): ")
                if user_confirm != "y":
                    continue

            season_ids = [season["Id"] for season in seasons["Items"]]
            self.get_seasons(season_ids, path=directory)
        print("")

    def get_albums(self, albums, path="", yes=True):
        for album in albums:
            # Get list of songs
            songs = api.get_songs(self.session, album)

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
                    "\nDownloading song "
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
                self.session.download_item(
                    song["Id"], os.path.join(directory, song_filename)
                )
                index_counter += 1
            print("")
        print("")

    def get_artists(self, artists, path="", yes=True):
        for artist in artists:
            # Get list of albums
            albums = api.get_albums(self.session, artist)

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

            self.get_albums(albums_ids, path=directory)
        print("")
