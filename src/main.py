import argparse
import sys

import helpers
import raiplay


def main(
    url: str, format: str, list_formats: bool, seasons: str, episodes: str, out_dir: str
) -> None:
    raiplay.check_url(url)

    data = helpers.get(url, force_json=True).json()

    raiplay.check_drm(data)

    season_list = [x.strip() for x in seasons.split(",")]
    episode_list = [x.strip() for x in episodes.split(",")]

    if list_formats:
        try:
            raiplay.list_formats(data, season_list, episode_list)
        except KeyboardInterrupt:
            sys.exit("\n[info] Format listing interrupted")
    else:
        raiplay.download_videos(data, season_list, episode_list, format, out_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="raiplay-dl", description="Downloader for RaiPlay"
    )
    parser.add_argument("url", metavar="URL", help="Content URL")
    parser.add_argument(
        "-f",
        "--format",
        metavar="FORMAT",
        dest="format",
        default="best",
        help="Video format code",
    )
    parser.add_argument(
        "-F",
        "--list-formats",
        dest="list_formats",
        help="List all available formats",
        action="store_true",
    )
    parser.add_argument(
        "-s", "--season", metavar="SEASON", dest="seasons", default="all", help="Season"
    )
    parser.add_argument(
        "-e",
        "--episode",
        metavar="EPISODE",
        dest="episodes",
        default="all",
        help="Episode",
    )
    parser.add_argument(
        "-o",
        "--output",
        metavar="PATH",
        dest="out_dir",
        default=".",
        help="Set the output directory",
    )
    args = parser.parse_args()
    main(*vars(args).values())
