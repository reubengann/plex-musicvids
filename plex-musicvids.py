import argparse
from pathlib import Path
import sys
from src.normalize_video import normalize_mp4
from src.playlist import PlexMusicVideoHelper

from src.project_settings import settings
from src.trim_video import trim_video


def get_helper() -> PlexMusicVideoHelper | None:
    if settings.dummy_root is None:
        print(
            "DUMMY_ROOT is not set. Please modify your .env file or environment variables"
        )
        return None
    if settings.vids_folder is None:
        print(
            "VIDS_FOLDER is not set. Please modify your .env file or environment variables"
        )
        return None
    if settings.playlist_name is None:
        print(
            "PLAYLIST_NAME is not set. Please modify your .env file or environment variables"
        )
        return None
    return PlexMusicVideoHelper(
        settings.playlist_name, settings.vids_folder, settings.dummy_root
    )


def get_ffprobe_path() -> Path | None:
    if settings.ffmpeg_bin is None:
        print(
            "FFMPEG_BIN is not set. Please modify your .env file or environment variables"
        )
        return None
    ffmpeg_bin_path = Path(settings.ffmpeg_bin)
    if not ffmpeg_bin_path.exists():
        print(f"The ffmpeg binary file {ffmpeg_bin_path} does not exist")
        return None
    return ffmpeg_bin_path / "ffprobe"


def get_ffmpeg_bin_path() -> Path | None:
    if settings.ffmpeg_bin is None:
        print(
            "FFMPEG_BIN is not set. Please modify your .env file or environment variables"
        )
        return None
    return Path(settings.ffmpeg_bin)


def main() -> int:
    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(
        dest="subparser_name",
        help="Music video playlist utility for Plex",
    )

    subp.add_parser("analyze", help="Analyze current state of playlist")
    norm_p = subp.add_parser(
        "normalize", help="Normalize the volume of a video file or files"
    )
    norm_p.add_argument("infile", help="Input file or folder")
    norm_p.add_argument("outfile", help="Output file or folder")
    subp.add_parser(
        "make_dummies", help="Make dummy artists so that music videos will be picked up"
    )
    subp.add_parser("add_to_playlist", help="Add videos to the playlist")
    subp.add_parser("troubleshoot", help="Try to fix missing tracks")
    trim_p = subp.add_parser("trim", help="Trim a video (frame accurate)")
    trim_p.add_argument("--infile", help="Input file", required=True)
    trim_p.add_argument("--outfile", help="Output file", required=True)
    trim_p.add_argument("--start", help="Start time", required=True)
    args = parser.parse_args()
    match args.subparser_name:
        case "analyze":
            print("Analyzing current state of playlist")
            helper = get_helper()
            if helper is None:
                return 1
            helper.print_summary()
            helper.analyze()
            return 0
        case "normalize":
            print("Normalize the volume of a video file or files")
            if settings.ffmpeg_bin is None:
                print(
                    "FFMPEG_BIN is not set. Please modify your .env file or environment variables"
                )
                return 1
            infile = Path(args.infile)
            outfile = Path(args.outfile)
            if not infile.exists():
                print(f"{infile} does not exist")
                return 1
            if infile.is_dir():
                raise NotImplementedError("Multiple files not done")
            if outfile.is_dir():
                outfile = outfile / infile.name
            ffmpeg_bin_path = Path(settings.ffmpeg_bin)
            if not ffmpeg_bin_path.exists():
                print(f"The ffmpeg binary file {ffmpeg_bin_path} does not exist")
                return 1
            ffprobe_path = ffmpeg_bin_path / "ffprobe"
            ffmpeg_path = ffmpeg_bin_path / "ffmpeg"
            normalize_mp4(infile, outfile, ffprobe_path, ffmpeg_path)
            return 0
        case "make_dummies":
            helper = get_helper()
            if helper is None:
                return 1
            helper.print_summary()
            helper.make_dummies()
            return 0
        case "add_to_playlist":
            helper = get_helper()
            if helper is None:
                return 1
            helper.print_summary()
            helper.add_videos_to_playlist()
            return 0
        case "troubleshoot":
            helper = get_helper()
            if helper is None:
                return 1
            helper.print_summary()
            helper.troubleshoot()
            return 0
        case "trim":
            infile = Path(args.infile)
            outfile = Path(args.outfile)
            if not infile.exists():
                print(f"{infile} does not exist")
                return 1
            if outfile.exists():
                print(f"{outfile} already exists.")
                return 1
            ffmpeg_bin = get_ffmpeg_bin_path()
            if ffmpeg_bin is None:
                print("ffmpeg binary path not found")
                return 1
            start_timestamp = parse_timestamp(args.start)
            trim_video(ffmpeg_bin, infile, outfile, start_timestamp)
            return 0
        case _:
            parser.print_help()
            return 1


def parse_timestamp(s: str):
    if ":" not in s:
        return s
    minute_part, second_part = s.split(":")
    minute_secs = int(minute_part) * 60
    print(minute_secs)
    if "." in second_part:
        seconds, frac = second_part.split(".")
    else:
        seconds = second_part
        frac = "000"
    seconds = str(minute_secs + int(seconds))
    return f"{seconds}.{frac}"


if __name__ == "__main__":
    sys.exit(main())
