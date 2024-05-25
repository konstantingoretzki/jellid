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
    - Album: `./jellid.py -s https://test.example.com -a <id> <id2> ...`
    - Artist: `./jellid.py -s https://test.example.com -art <id> <id2> ...`
    - Movie: `./jellid.py -s https://test.example.com -m <id> <id2> ...`
    
There are flags for specifing the location directory (`-dir`) and using the silent mode (`-yes`) that does not ask for confirmation and uses automatic 'yes' for prompts. The script detects already downloaded items (albums, artists) and skips them.


## TODO
- [ ] **Improve auth**: Using env variables is far from best practices. Username and password should be read from a file.
- [ ] **Auto detect type**: Call correct type downloader without having to set the type manually. 
- [ ] **Support more collection types**: There are more then these basic item types that should be supported. Probably more and better error handling is needed.
- [ ] **Add interactive mode**: Find item names via CLI instead of having to extract them from the URL.
