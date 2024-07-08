#!/usr/bin/env python3

import argparse
import os

import utils
from session import NetworkSession
from download import Downloader

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Download items from a Jellyfin instance"
    )
    parser.add_argument(
        "-s", "--server", type=str, help="URL of the Jellyfin instance", required=True
    )

    # Env variables
    # Set env vars via e.g. `export JELLYFIN_USERNAME=my_user_name`
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

    # Assume yes: automatic "yes" to prompts, run non-interactively
    parser.add_argument(
        "-yes",
        "--yes",
        default=False,
        action="store_true",
        help="Automatic 'yes' to prompts",
    )

    # Overwrite existing items
    parser.add_argument(
        "-over",
        "--overwrite",
        default=False,
        action="store_true",
        help="Overwrite existing items",
    )

    # Directory for downloaded items
    parser.add_argument(
        "-dir",
        "--directory",
        default=os.getcwd(),
        type=str,
        help="Directory where the items should be saved",
    )

    # Download movie(s)
    parser.add_argument(
        "-m", "--movies", nargs="+", action="append", help="Ids of movies to download"
    )

    # Download show(s)
    parser.add_argument(
        "--seasons",
        nargs="+",
        action="append",
        help="Ids of seasons to download",
    )

    # Download show(s)
    parser.add_argument(
        "--shows",
        nargs="+",
        action="append",
        help="Ids of shows to download",
    )

    # Download album(s)
    parser.add_argument(
        "-a", "--albums", nargs="+", action="append", help="Ids of albums to download"
    )

    # Download all albums from artists
    parser.add_argument(
        "-art",
        "--artists",
        nargs="+",
        action="append",
        help="Ids of artists to download their albums",
    )

    args = parser.parse_args()

    print(f"\033[1mjellid.py - unoffical jellyfin item downloader\033[0m")

    # Check if username and password are set
    if (args.user is None) or (args.password is None):
        print(
            "Please set the username (JELLYFIN_USERNAME) and password (JELLYFIN_PASSWORD) using environment variables or pass as CLI arguments."
        )
        exit(1)

    # Check if URL is valid
    if not utils.valid_url(args.server):
        print("Bad URL format - correct is e.g. https://test.example.com")
        exit(1)

    with NetworkSession(args.server, args.user, args.password, args.overwrite) as session:
        # Login with creds
        session.login()

        downloader = Downloader(session)

        # Download movie(s)
        if args.movies and (len(args.movies[0]) > 0):
            downloader.get_movies(args.movies[0], args.directory, args.yes)

        # Download season(s)
        if args.seasons and (len(args.seasons[0]) > 0):
            downloader.get_seasons(args.seasons[0], args.directory, args.yes)

        # Download show(s)
        if args.shows and (len(args.shows[0]) > 0):
            downloader.get_shows(args.shows[0], args.directory, args.yes)

        # Download album(s)
        if args.albums and (len(args.albums[0]) > 0):
            downloader.get_albums(args.albums[0], args.directory, args.yes)

        # Download artist(s)
        if args.artists and (len(args.artists[0]) > 0):
            downloader.get_artists(args.artists[0], args.directory, args.yes)
