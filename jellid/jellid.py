#!/usr/bin/env python3

import argparse
import os

import utils
from session import NetworkSession
import download as download

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
    if not args.user and args.password:
        print(
            "Please set the username (JELLYFIN_USERNAME) and password (JELLYFIN_PASSWORD) using environment variables or pass as CLI arguments."
        )
        exit(1)

    # Check if URL is valid
    if not utils.valid_url(args.server):
        print("Bad URL format - correct is e.g. https://test.example.com")
        exit(1)

    with NetworkSession(args.server, args.user, args.password) as session:
        # Login with creds
        session.login()

        # Download movie(s)
        if args.movies and (len(args.movies[0]) > 0):
            download.get_movies(session, args.movies[0], args.yes, args.directory)

        # Download show(s)
        if args.shows and (len(args.shows[0]) > 0):
            # download.get_shows(session, args.shows[0], args.yes, args.directory)
            pass

        # Download album(s)
        if args.albums and (len(args.albums[0]) > 0):
            download.get_albums(session, args.albums[0], args.yes, args.directory)

        # Download all albums by artists
        if args.artists and (len(args.artists[0]) > 0):
            download.get_artists(session, args.artists[0], args.yes, args.directory)
