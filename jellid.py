#!/usr/bin/env python3

import argparse
import errno
import re
from urllib.parse import urlparse, urljoin
import os  # environ, mkdir, path, listdir, name
import requests
import time


def valid_url(url):
    # regex to check for a valid URL
    # https://mathiasbynens.be/demo/url-regex
    # fails on TLD check
    regex = "^(https?)://[^\s/$.?#].[^\s]*$"

    # string is empty or regex hasn't matched
    if (url == None) or (not bool(re.search(regex, url))):
        return False
    else:
        return True


def subsPath(path):
    bad_chars = []

    # Windows bad dir / file chars
    # WSL will be detected as Linux so OS check can be skipped
    bad_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]

    # should be fast
    # https://stackoverflow.com/a/27086669
    for c in bad_chars:
        if c in path:
            path = path.replace(c, " -")

    return path


def download_albums(albums, yes, path=""):
    for album in albums:
        # get list of songs
        items = connector.get_items(album)

        # directory name
        any_song_id = list(items["songs"].keys())[0]
        album_name = items["songs"][any_song_id]["album"]["name"]
        directory = os.path.join(path, subsPath(album_name))

        print(f"\n🎶 Album: {album_name}")
        number_songs = len(items["songs"])

        # ask before download
        if not yes:
            user_input = input(
                f"Found {number_songs} song(s) - do you want to download it / them? (y/n): "
            )
            if user_input != "y":
                continue

        try:
            os.mkdir(directory)

        except OSError as e:

            # directory already exists
            if e.errno == errno.EEXIST:
                print(f"Album already found - skipping.")
                continue

            else:
                raise

        except Exception as err:
            print(f"\n{err}")
            exit(1)

        ctr = 1
        for song in items["songs"]:
            print("Downloading song " + str(ctr) + "/" + str(number_songs) + " ...")
            # add song number if it's available --> 01 - SongXYZ
            if "index" in items["songs"][song]:
                song_id = items["songs"][song]["index"]
                song_name = (
                    f"{int(song_id) if int(song_id) >= 10 else '0'+str(song_id)} - "
                    + subsPath(items["songs"][song]["name"])
                )
            else:
                song_name = subsPath(items["songs"][song]["name"])
            connector.download_item(song, os.path.join(directory, song_name + ".flac"))
            print("\033[2A")
            ctr += 1


def download_artists(artists, yes, path=""):
    for artist in artists:
        artist_info = connector.get_items(
            artist, search_filter={"IncludeItemTypes": "MusicAlbum"}
        )

        artist_name = artist_info["albums"][list(artist_info["albums"].items())[0][0]][
            "artist"
        ]
        directory = os.path.join(path, subsPath(artist_name))
        albums = [album for album in artist_info["albums"]]

        print(f"\n🎨 Artist: {artist_name}")

        # ask before download
        if not yes:
            user_input = input(f"Download all the albums ? (y/n): ")
            if user_input != "y":
                continue

        # create artist directory
        try:
            os.mkdir(directory)

        except OSError as e:

            # directory already exists
            if e.errno == errno.EEXIST:
                pass

            else:
                raise

        except Exception as err:
            print(f"\n{err}")
            exit(1)

        download_albums(albums, yes=True, path=directory)
        print("")


def download_movies(movies, yes, path=""):
    for movie in movies:
        # get info about movie
        movie_info = connector.get_item_info(movie)

        movie_name = movie_info["Name"]
        movie_container = movie_info["Container"].split(",")[0]
        movie_filename = movie_name + "." + movie_container

        print(f"\n🎥 Movie: {movie_name}")

        # ask before download
        if not yes:
            user_input = input(f"Download the movie ? (y/n): ")
            if user_input != "y":
                continue

        connector.download_item(movie, os.path.join(path, movie_filename))


class Jellyfin:
    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        # use hacky private attribut self.__password instead?
        self.password = password

        self.user_id = ""
        self.token = ""

        self.headers = {
            "Host": self.url.hostname,
            "Accept": "application/json",
        }

        self.queue = []

    def set_headers(self):
        self.headers["X-Emby-Authorization"] = (
            'MediaBrowser Client="Jellyfin Downloader", Token=' + self.token
        )

    def login(self):
        # DeviceID is just User-Agent | Unix-timestamp + sth else?
        # Device is mandatory, can be set arbitary
        headers_auth = {
            "Host": self.url.hostname,
            "Content-Type": "application/json",
            "X-Emby-Authorization": 'MediaBrowser Client="Jellyfin Downloader", Device='
            + self.username
            + ', DeviceId="TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzk1LjAuNDYzOC42OSBTYWZhcmkvNTM3LjM2fDE2MzkwNjYyNDcyNzM1", Version="0.1.0"',
        }

        data_auth = {"Username": self.username, "Pw": self.password}

        # e.g. https://test.example.com/Users/authenticatebyname
        response = requests.post(
            urljoin(self.url.geturl(), "Users/authenticatebyname"),
            headers=headers_auth,
            json=data_auth,
        )
        response_json = response.json()

        self.user_id = response_json["SessionInfo"]["UserId"]
        self.token = response_json["AccessToken"]
        self.set_headers()

    def get_items(self, directory=None, search_filter=None):
        parameters = {
            "SortBy": "SortName",
            "SortOrder": "Ascending",
            "Recursive": "true",
        }

        # directory to search for items
        if directory:
            parameters["ParentId"] = directory

        # overwrite parameters with user provided
        if search_filter:
            parameters.update(search_filter)

        # URL structure
        # https://test.example.com/Users/<user-id>/Items?SortBy=SortName&SortOrder=Ascending&ParentId=<directory>&....
        response = requests.get(
            urljoin(self.url.geturl(), "Users/" + str(self.user_id) + "/Items"),
            params=parameters,
            headers=self.headers,
        )
        # print("DEBUG: " + response.request.url)
        response_json = response.json()

        # add date?
        # are there songs that do not have an artist or album?
        """
        items = {
            "songs" : {
                "1dofewejf" : {
                    "name" : "abc", 
                    "album" : {"id" : "abc", "name" : "abc", "index": 1}
                },
            },
            "albums" : {
                "1dofewejf" : {
                    "name" : "abc", 
                    "album" : {"id" : "abc", "name" : "abc", "artist" : "abc" }
                },
            },
        }
        """

        items = {
            "songs": {},
            "albums": {},
            # "collections" : {},
        }

        for item in response_json["Items"]:

            # album
            if item["Type"] == "MusicAlbum":
                items["albums"][item["Id"]] = {
                    "name": item["Name"],
                    "id": item["Id"],
                    "artist": item["AlbumArtist"],
                }

            # songs
            elif item["Type"] == "Audio":
                items["songs"][item["Id"]] = {"name": item["Name"]}

                # add album info
                if "Album" in item:
                    items["songs"][item["Id"]]["album"] = {
                        "id": item["AlbumId"],
                        "name": item["Album"],
                    }

                # TODO: fix me
                # add artist info (use Artists or AlbumArtists instead?)
                # will fail for more than one AlbumArtists ...
                if "ArtistItems" in item:
                    items["songs"][item["Id"]]["artists"] = {
                        "id": item["AlbumArtists"][0]["Id"],
                        "name": item["AlbumArtists"][0]["Name"],
                    }

                if "IndexNumber" in item:
                    items["songs"][item["Id"]]["index"] = item["IndexNumber"]

            # collection
            # else if item["Type"] == "CollectionFolder":
            #    items["collections"].append({"name" : item["Name"], "id" : item["Id"]})

        return items

    def get_item_info(self, item_id):
        # URL structure
        # https://test.example.com/Users/<user-id>/Items/<item-id>
        response = requests.get(
            urljoin(
                self.url.geturl(),
                "Users/" + str(self.user_id) + "/Items/" + str(item_id),
            ),
            headers=self.headers,
        )
        # print("DEBUG: " + response.request.url)
        response_json = response.json()
        return response_json

    def download_part(self, url, filename, byte_position):
        headers = self.headers
        headers["Range"] = f"bytes={byte_position}-"
        # print(f"DEBUG: {headers}")

        with open(filename, "ab") as f:
            try:
                start = time.perf_counter()
                r = requests.get(url, stream=True, headers=headers, timeout=10)
                content_range = r.headers.get("Content-Range")
                # print(content_range)

                # download will fail for servers that do not support partial download
                if (r.status_code != 206) or (content_range is None):
                    raise Exception("Server does not support partial download.")

                total = int(content_range.split("/")[1])
                # use only downloaded bytes instead of written bytes?
                written = 0
                bytes_dl = 0

                for chunk in r.iter_content(1024):
                    bytes_dl += len(chunk)
                    written += f.write(chunk)
                    done = int(30 * (int(written) + int(byte_position)) / int(total))
                    # [=============                 ] 12.34 MB/s
                    dl_speed = bytes_dl / (time.perf_counter() - start) / (1024 * 1024)
                    print(
                        f"[{'=' * done}{' ' * (30-done)}] {dl_speed:.2f} MB/s", end="\r"
                    )

            except requests.exceptions.Timeout:
                print(
                    f"Download timeout on {time.strftime('%H:%M:%S', time.localtime())}"
                )

            except Exception as e:
                print(e)

            finally:
                return [written, total]

    def download_item(self, item_id, item_path):
        max_tries = 5
        current_try = 1

        total_written = 0
        file_size = 0

        while current_try <= max_tries:

            written, file_size = self.download_part(
                urljoin(
                    self.url.geturl(),
                    "Items/" + str(item_id) + "/Download?api_key=" + str(self.token),
                ),
                item_path,
                f"{total_written}",
            )
            total_written += written
            # print(f"\nWrote {total_written}/{file_size}")

            # download is done
            if total_written == file_size:
                # print("\nDownload of the complete file is done.")
                break

            # only a part could be downloaded
            else:
                print("Download interrupted - resuming session ...\n")
                current_try += 1
        
        print("\n")


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Download items from a Jellyfin instance"
    )
    parser.add_argument(
        "-s", "--server", type=str, help="URL of the Jellyfin instance", required=True
    )

    # env variables
    # set env vars via e.g. `export JELLYFIN_USERNAME=my_user_name`
    parser.add_argument(
        "-u",
        "--user",
        default=os.environ.get("JELLYFIN_USERNAME"),
        type=str,
        help="Username of the Jellyfin account",
    )
    parser.add_argument(
        "-p",
        "--password",
        default=os.environ.get("JELLYFIN_PASSWORD"),
        type=str,
        help="Password of the Jellyfin account",
    )

    # assume yes: automatic "yes" to prompts, run non-interactively
    parser.add_argument(
        "-yes",
        "--yes",
        default=False,
        action="store_true",
        help="Automatic 'yes' to prompts",
    )

    # directory for downloaded items
    parser.add_argument(
        "-dir",
        "--directory",
        default=os.getcwd(),
        type=str,
        help="Directory where the items should be saved",
    )

    # download album(s)
    parser.add_argument(
        "-a", "--albums", nargs="+", action="append", help="Ids of albums to download"
    )

    # download all albums from artists
    parser.add_argument(
        "-art",
        "--artists",
        nargs="+",
        action="append",
        help="Ids of artists to download their albums",
    )

    # download movie(s)
    parser.add_argument(
        "-m", "--movies", nargs="+", action="append", help="Ids of movies to download"
    )

    args = parser.parse_args()

    print(f"\033[1mjellid.py - unoffical jellyfin item downloader\033[0m")

    # check username and apssword
    if args.user and args.password:

        # check if URL is valid
        if valid_url(args.server):
            connector = Jellyfin(urlparse(args.server), args.user, args.password)
        else:
            print("Bad URL format - correct is e.g. https://test.example.com")
            exit(1)

    else:
        print(
            "Please set the username (JELLYFIN_USERNAME) and password (JELLYFIN_PASSWORD) using environment variables or pass as CLI arguments."
        )
        exit(1)

    # login with creds
    connector.login()

    # download album(s)
    if args.albums and (len(args.albums[0]) > 0):
        download_albums(args.albums[0], args.yes, args.directory)

    # download all albums by artists
    if args.artists and (len(args.artists[0]) > 0):
        download_artists(args.artists[0], args.yes, args.directory)

    # download movie(s)
    if args.movies and (len(args.movies[0]) > 0):
        download_movies(args.movies[0], args.yes, args.directory)
