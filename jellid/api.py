# URL structure
# /Users/<user-id>/ is not needed


def get_item_info(session, item_id):
    # https://test.example.com/Items/<item_id>
    return session.get_json("/Items/" + str(item_id))


def get_songs(session, album_id):
    # https://test.example.com/Items/?ParentId=<album_id>&Fields=MediaSources&SortBy=ParentIndexNumber,IndexNumber
    # MediaSources provides access to the Container
    # Sorting by ParentIndexNumber is needed if the Album contains multiple disks
    # IndexNumber gives the position of the title in the album
    return session.get_json(
        "/Items?ParentId="
        + str(album_id)
        + "&Fields=MediaSources&SortBy=ParentIndexNumber,IndexNumber"
    )


def get_albums(session, artist_id):
    # https://test.example.com/Items?IncludeItemTypes=MusicAlbum&Recursive=true&AlbumArtistIds=<artist_id>
    # Without Recursive we only get the main collections like Music or Movies
    return session.get_json(
        "/Items?IncludeItemTypes=MusicAlbum&Recursive=true&AlbumArtistIds="
        + str(artist_id)
    )


def get_episodes(session, season_id):
    # Search via 'Items' needed because there is no /Seasons/<season_id>/Episodes
    # https://test.example.com/Items?ParentId=<season_id>&Recursive=true
    return session.get_json("/Items?ParentId=" + str(season_id) + "&Recursive=true")


def get_seasons(session, show_id):
    # https://test.example.com/Shows/<show_id>/Seasons
    return session.get_json("/Shows/" + str(show_id) + "/Seasons")
