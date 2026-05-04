import math
import os
import sys

import requests


class AlreadyDownloadedError(Exception):
    pass


def get(url: str, stream=False, force_json=False) -> requests.Response:
    """
    Get the content of the url, with the right headers and stuff
    """
    if force_json:
        url = url.rstrip("/")
        if url.endswith(".html"):
            url = url.replace(".html", ".json")
        elif not url.endswith(".json"):
            url = url + ".json"

    return requests.get(
        url,
        stream=stream,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
        },
    )


def download(url: str, file_path: str) -> None:
    """
    Download the video from the url and save it in the file path
    """
    try:
        with open(file_path, "wb") as f:
            r = get(url, stream=True)
            total_length = r.headers["Content-Length"]

            if total_length is None:
                f.write(r.content)
            else:
                dl = 0
                total_length = int(total_length)
                for data in r.iter_content(chunk_size=4096):
                    dl += len(data)
                    f.write(data)
                    done = int(50 * dl / total_length)
                    percent = int(100 * dl / total_length)
                    sys.stdout.write(
                        f"\r[{'#' * done}{' ' * (50 - done)}] {percent}% of {convert_size(int(total_length))}"
                    )
                    sys.stdout.flush()
                print()
    except KeyboardInterrupt:
        os.remove(file_path)
        sys.exit("\n\n[info] Download canceled")


def convert_size(size_bytes: int) -> str:
    """
    Covert file size from bytes to the beast readable option
    """
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return "%s %s" % (s, size_name[i])


def _sanitize_path(s: str) -> str:
    return (
        s.replace(":", " -")
        .replace("<", " ")
        .replace(">", "<")
        .replace("|", "")
        .replace("*", "")
        .replace("?", "")
        .replace('"', "")
    )


def prepare_folder(out_dir: str, file_name: str) -> str:
    drive, rest = os.path.splitdrive(out_dir)
    out_dir = drive + _sanitize_path(rest)
    file_name = (
        file_name.replace(":", " -")
        .replace("<", " ")
        .replace(">", "<")
        .replace("|", "")
        .replace("*", "")
        .replace("?", "")
        .replace('"', "")
        .replace("/", "_")
        .replace("\\", "_")
    )
    file_path = os.path.join(out_dir, file_name)

    if not os.path.isfile(file_path):
        if not os.path.isdir(out_dir):
            os.makedirs(out_dir)
        return file_path
    else:
        raise AlreadyDownloadedError(f"{file_name} has already been downloaded")
