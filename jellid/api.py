# URL structure
# /Users/<user-id>/ is not needed

def get_item_info(session, item_id):
    # https://test.example.com/Items/<item-id>
    return session.get_json("/Items/" + str(item_id))

def get_songs(session, album_id):
    # https://test.example.com/Items/?ParentId=<album-id>&Fields=MediaSources&SortBy=IndexNumber
    # MediaSources provides access to the Container
    # Sorting by IndexNumber needed to name songs after their album index 
    return session.get_json("/Items?ParentId=" + str(album_id) + "&Fields=MediaSources&SortBy=IndexNumber")

def get_albums(session, artist_id):
    # https://test.example.com/Items?IncludeItemTypes=MusicAlbum&Recursive=true&AlbumArtistIds=<album-id>
    # Without Recursive we only get the main collections like Music or Movies
    return session.get_json("/Items?IncludeItemTypes=MusicAlbum&Recursive=true&AlbumArtistIds=" + str(artist_id))