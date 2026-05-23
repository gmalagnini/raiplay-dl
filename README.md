# raiplay-dl

Command-line downloader for [RaiPlay](https://www.raiplay.it). Supports movies, TV series, and programs.

## Installation

Download the latest binary for your OS from the [releases](../../releases) and move it to a directory in your `$PATH`:

```bash
mv raiplay-dl /usr/local/bin/raiplay-dl
```

### From source

Requires [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/wetcork/raiplay-dl
cd raiplay-dl
uv run src/main.py --help
```

## Usage

```
raiplay-dl [-h] [-f FORMAT] [-F] [-s SEASON] [-e EPISODE] [-o PATH] URL
```

| Argument | Description |
|---|---|
| `URL` | RaiPlay content URL |
| `-f FORMAT` | Video format code (default: best available) |
| `-F` | List all available formats |
| `-s SEASON` | Season number(s), comma-separated |
| `-e EPISODE` | Episode number(s), comma-separated |
| `-o PATH` | Output directory (default: current directory) |

## Examples

List available formats:
```
raiplay-dl -F https://www.raiplay.it/programmi/thecircle

Formats available for "The Circle (2017)"
5000 - 1080p (4.82 GB)
2400 - 720p (2.06 GB)
1800 - 576p (1.53 GB)
1200 - 414p (1.03 GB)
```

Download best quality:
```
raiplay-dl https://www.raiplay.it/programmi/thecircle
```

Download specific quality:
```
raiplay-dl -f 2400 https://www.raiplay.it/programmi/thecircle
```

Download specific seasons and episodes:
```
raiplay-dl -s 9 -e 3,4 https://www.raiplay.it/programmi/donmatteo
```

## Features

- Download up to 1080p (bypasses the 720p limit on the website)
- Download the original MP4 file, not the HLS stream
- Bulk download entire TV series
- Filter by season and episode
- No account required

## Limitations

- Content is georestricted to Italy (a VPN/proxy may bypass this)
- DRM-protected content cannot be downloaded
