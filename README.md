# Jellid

Jellid (jellyfin item downloader) is an **unofficial** [Jellyfin](https://github.com/jellyfin/jellyfin) item downloader using the [Jellyfin (Web) API](https://api.jellyfin.org/). Currently the download of collections (albums and artists) and movies are supported. The script provides downloading while showing a progress bar and uses session resumption in order to survive interrupted downloads.

## Installation
1. Clone the repo: `git clone https://github.com/konstantingoretzki/jellid`
2. Give execution permission: `cd jellid/ && chmod +x jellid/jellid.py`
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python3 ./jellid/jellid.py`

## Usage
1. Set your Jellyfin Web username and password: 
    - `export JELLYFIN_USERNAME=<username>`
    - `export JELLYFIN_PASSWORD=<password>`
    
2. Get the item ids by requesting the corresponding page:
    - Request the page of an album, an artist or a movie and extract the item ID from the URL
    - e.g. `https://test.example.com/web/index.html#!/details?id=<item-id>&serverId=<server-id>` --> `<item-id>`
    
3. Call `jellid.py` by using the correct item type:
    - Movies: `python3 ./jellid/jellid.py -s https://test.example.com -m <id> <id2> ...`
    - Seasons: `python3 ./jellid/jellid.py -s https://test.example.com --seasons <id> <id2> ...`
    - Shows: `python3 ./jellid/jellid.py -s https://test.example.com --shows <id> <id2> ...`
    - Albums: `python3 ./jellid/jellid.py -s https://test.example.com -a <id> <id2> ...`
    - Artists: `python3 ./jellid/jellid.py -s https://test.example.com -art <id> <id2> ...`
    
There are flags for specifing the location directory (`-dir`) and using the silent mode (`-yes`) that does not ask for confirmation and uses automatic 'yes' for prompts. The script detects already downloaded items skips them. If you want to overwrite them instead, you can use the flag `-over`.