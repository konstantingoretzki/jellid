import errno
import re
import os


def valid_url(url):
    # Regex to check for a valid URL
    # https://mathiasbynens.be/demo/url-regex
    # Fails on TLD check
    regex = "^(https?)://[^\s/$.?#].[^\s]*$"

    # String is empty or regex hasn't matched
    if (url == None) or (not bool(re.search(regex, url))):
        return False
    else:
        return True


def subs_path(path):
    bad_chars = []

    # Windows bad dir / file chars
    # WSL will be detected as Linux so OS check can be skipped
    bad_chars = ["\\", "/", ":", "*", "?", '"', "<", ">", "|"]

    # Should be fast
    # https://stackoverflow.com/a/27086669
    for c in bad_chars:
        if c in path:
            path = path.replace(c, " -")

    return path


def save_mkdirs(dir):
    try:
        os.makedirs(dir)
    except OSError as e:
        # Directory already exists
        if e.errno == errno.EEXIST:
            pass
        else:
            raise
    except Exception as err:
        print(f"\n{err}")
        exit(1)
