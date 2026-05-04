import os
import sys
from collections import namedtuple

from natsort import natsorted, ns

import helpers

FormatResolution = namedtuple("FormatResolution", ["format", "resolution"])

_URL_ROOT = "https://www.raiplay.it"

_FORMAT_RESOLUTION_LIST: list[FormatResolution] = [
    FormatResolution("5000", "1080p"),
    FormatResolution("3200", "810p"),
    FormatResolution("2401", "720p"),
    FormatResolution("2400", "720p"),
    FormatResolution("1800", "576p"),
    FormatResolution("1200", "414p"),
    FormatResolution("0", "396p"),
    FormatResolution("800", "288p"),
    FormatResolution("700", "288p"),
    FormatResolution("400", "288p"),
    FormatResolution("250", "198p"),
]


_OVERRIDE = "&overrideUserAgentRule=mp4-"


class NoResolutionFoundError(Exception):
    pass


# VALIDATION


def check_url(url) -> None:
    """
    Check if given url is valid
    """
    if _URL_ROOT in url:
        try:
            if helpers.get(url).status_code == 404:
                sys.exit("[error] Can't connect to the url.")
            else:
                return
        except Exception:
            sys.exit("[error] Connection error")
    else:
        sys.exit("[error] Invalid url")


def check_drm(data: dict) -> None:
    """
    Check if the content is DRM protected
    """

    if "ContentItem" in data["id"]:
        data = helpers.get(
            _URL_ROOT + data["program_info"]["path_id"], force_json=True
        ).json()

    try:
        if data["program_info"]["rights_management"]["rights"]["drm"]["VOD"]:
            print('[drm error] "%s" is DRM protected.' % (data["name"]))
    # TODO: why is that????
    except Exception:
        return
    else:
        sys.exit("[drm error] This script can't bypass DRM protection.")


def is_series(data: dict) -> bool:
    """
    Check if the media is a tv series/show or a movie
    """
    layout = data["program_info"]["layout"]
    if layout == "single":
        return False
    elif layout == "multi":
        return True
    else:
        sys.exit("Error while defining series.")


# LISTING


def list_formats(
    data: dict, season_list: list[str], episode_list: list[str]
):  # List the formats
    if not is_series(data=data):
        if "Page" in data["id"]:
            data = helpers.get(
                _URL_ROOT + data["first_item_path"], force_json=True
            ).json()

        title: str = data["program_info"]["name"]
        year: str = data["program_info"]["year"]
        url: str = data["video"]["content_url"]

        print(f'Formats available for "{title.strip()} ({year})"')

        _pretty_print_formats(url)

    else:
        if "ContentItem" in data["id"]:
            name: str = data["program_info"]["name"]
            season: str = data["season"]
            episode: str = data["episode"]
            episode_title: str = data["episode_title"]
            year: str = data["track_info"]["edit_year"]
            url: str = data["video"]["content_url"]

            print(
                f'Formats avaiable for "{name.strip()} - {season.zfill(2)}x{episode.zfill(2)} - {episode_title.strip()} ({year})"'
            )

            _pretty_print_formats(url)

            return

        if "Page" in data["id"]:
            name: str = data["name"]
            year: str = data["program_info"]["year"]

            print(f'Formats available for "{name.strip()} ({year})"\n')

            for block in data["blocks"]:
                # TODO: prompt the user to select the block he wants to download from

                # each season has name, id, type, path_id: str, episode_size: { label: str, number: int}
                seasons: list[dict] = [season for season in block["sets"]]

                if season_list[0] != "all":
                    try:
                        temp = [seasons[int(s) - 1] for s in season_list]
                    except ValueError:
                        sys.exit(f"[error] Invalid season number. {season_list}")

                    seasons = temp

                for season in seasons:
                    season_data = helpers.get(
                        _URL_ROOT + season["path_id"], force_json=True
                    ).json()

                    episodes = season_data["items"]

                    print("[Season %s]" % (episodes[0]["season"]))

                    if episode_list[0] != "all":
                        temp = [episodes[int(e) - 1] for e in episode_list]
                        episodes = temp

                    for episode in episodes:
                        print(
                            f'Ep {episode["episode"]} - "{episode["episode_title"].strip()}"'
                        )

                        url = episode["video_url"]
                        _pretty_print_formats(url)

                        print()


def _pretty_print_formats(url: str) -> None:
    for fr in _FORMAT_RESOLUTION_LIST:
        override_url = url + _OVERRIDE + fr.format

        r = helpers.get(override_url, stream=True)

        if r.headers["Content-Type"] == "video/mp4":
            size = helpers.convert_size(int(r.headers["Content-Length"]))
            print(f"{fr.format} - {fr.resolution} ({size})")


# DOWNLOAD


def download_videos(
    data, season_list: list[str], episode_list: list[str], format, out_dir
):
    """
    Get all the infos to start the download
    """
    if not is_series(data=data):
        if "Page" in data["id"]:
            data = helpers.get(
                _URL_ROOT + data["first_item_path"], force_json=True
            ).json()

            url: str | None = _get_override_url(data, format)

            if not url:
                sys.exit("[error] No format has been found for the given title.")

            _prepare_and_download(
                url=url,
                name=data["program_info"]["name"],
                season="",
                episode="",
                episode_title="",
                year=data["program_info"]["year"],
                out_dir=out_dir,
            )

    if "ContentItem" in data["id"]:
        url: str | None = _get_override_url(data, format)

        if url is None:
            sys.exit("[error] No format has been found for the given title.")

        _prepare_and_download(
            url=url,
            name=data["program_info"]["name"],
            season=data["season"],
            episode=data["episode"],
            episode_title=data["episode_title"],
            year=data["track_info"]["edit_year"],
            out_dir=out_dir,
        )

    elif "Page" in data["id"]:
        name: str = data["name"].strip()
        year: str = data["program_info"]["year"]
        print(f'Downloading "{name.strip()} ({year})"\n')

        for block in data["blocks"]:
            seasons: list[dict] = [season for season in block["sets"]]

            if season_list[0] != "all":
                try:
                    temp = [seasons[int(s) - 1] for s in season_list]
                except ValueError:
                    sys.exit(f"[error] Invalid season number. {season_list}")

                seasons = temp

            for season in seasons:
                season_data = helpers.get(
                    _URL_ROOT + season["path_id"], force_json=True
                ).json()

                episodes = season_data["items"]

                fn_season = episodes[0]["season"]
                print(f"[Season {fn_season}]")

                out_sub_dir = os.path.join(
                    out_dir, f"{name} ({year})\\Season {fn_season}"
                )

                if episode_list[0] != "all":
                    temp = [episodes[int(e) - 1] for e in episode_list]
                    episodes = temp

                for episode in episodes:
                    fn_episode = episode["episode"]
                    fn_episode_title = episode["episode_title"]
                    url = _get_override_url(
                        helpers.get(
                            _URL_ROOT + episode["weblink"], force_json=True
                        ).json(),
                        format,
                    )

                    if not url:
                        print("[error] No format has been found for the given title.")
                        continue
                    _prepare_and_download(
                        url=url,
                        name=name,
                        season=fn_season,
                        episode=fn_episode,
                        episode_title=fn_episode_title,
                        year=year,
                        out_dir=out_sub_dir,
                    )

                    print()


def _get_override_url(data: dict, format: str) -> str | None:
    """
    Generate the mp4 video url
    """
    url = data["video"]["content_url"]

    if format != "best":
        url_override = url + _OVERRIDE + format
        if _url_exists(url_override):
            return url_override
        else:
            print(
                "[info] Selected format is not available, fallback to the best available format"
            )

    for fr in _FORMAT_RESOLUTION_LIST:
        url_override = url + _OVERRIDE + fr.format
        if _url_exists(url_override):
            return url_override

    print("[error] No format has been found for the given title")
    return None


def _url_exists(url: str) -> bool:
    return helpers.get(url=url, stream=True).headers["Content-Type"] == "video/mp4"


def _prepare_and_download(
    url: str,
    name: str,
    season: str,
    episode: str,
    episode_title: str,
    year: str,
    out_dir: str,
) -> None:
    try:
        definition: str | None = _get_resolution_from_format(url[url.find("-") + 1 :])
    except NoResolutionFoundError:
        print("[error] No format has been found for the given title.")
    else:
        file_name = f"{name} - {season.zfill(2)}x{episode.zfill(2)} - {episode_title.strip()} ({year}) [{definition}].mp4"

        try:
            file_path = helpers.prepare_folder(out_dir, file_name)
            helpers.download(url, file_path)
        except helpers.AlreadyDownloadedError as e:
            print(f"[warn] {e}")


def _get_resolution_from_format(format: str) -> str | None:
    """
    Retrieve the video quality
    """
    for fr in _FORMAT_RESOLUTION_LIST:
        if fr.format == format:
            return fr.resolution

    raise NoResolutionFoundError(f"No resolution found for the format {format}.")
