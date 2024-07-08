import time
from urllib.parse import urljoin, urlparse
import requests
from os import path


class NetworkSession:
    def __init__(self, url, username, password, overwrite=False):
        self.url = urlparse(url)
        self.username = username
        # Use hacky private attribut self.__password instead?
        self.password = password

        # Overwrite already existing items
        self.overwrite = overwrite

        # Request session
        self.session = requests.Session()

        self.headers = {
            "Host": self.url.hostname,
            "Accept": "application/json",
        }

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # Terminate the request session
        self.session.close()

    def set_post_auth_headers(self):
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

        # E.g. https://test.example.com/Users/authenticatebyname
        response = self.session.post(
            urljoin(self.url.geturl(), "Users/authenticatebyname"),
            headers=headers_auth,
            json=data_auth,
        )
        response_json = response.json()

        self.token = response_json["AccessToken"]
        self.set_post_auth_headers()

    def get_json(self, path):
        url = urljoin(self.url.geturl(), path)
        response = self.session.get(url, headers=self.headers)
        response_json = response.json()
        return response_json

    def download_part(self, url, filename, byte_position):
        headers = self.headers
        headers["Range"] = f"bytes={byte_position}-"
        # print(f"DEBUG: {headers}")

        with open(filename, "ab") as f:
            try:
                start = time.perf_counter()
                r = self.session.get(url, stream=True, headers=headers, timeout=10)
                content_range = r.headers.get("Content-Range")
                # print(content_range)

                # Download will fail for servers that do not support partial download
                if (r.status_code != 206) or (content_range is None):
                    raise Exception("Server does not support partial download.")

                total = int(content_range.split("/")[1])
                # Use only downloaded bytes instead of written bytes?
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
        url = urljoin(self.url.geturl(), "Items/" + str(item_id) + "/Download")

        # Skip already downloaded items
        if path.exists(item_path) and (not self.overwrite):
            print("Item already exists - skipping ...")
            return

        max_tries = 5
        current_try = 1

        total_written = 0
        file_size = 0

        while current_try <= max_tries:

            written, file_size = self.download_part(
                url,
                item_path,
                f"{total_written}",
            )
            total_written += written
            # print(f"\nWrote {total_written}/{file_size}")

            # Download is done
            if total_written == file_size:
                # print("\nDownload of the complete file is done.")
                break

            # Only a part could be downloaded
            else:
                print("Download interrupted - resuming session ...\n")
                current_try += 1

        print("")
