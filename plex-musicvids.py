import argparse
from pathlib import Path
import sys
from src.normalize_video import normalize_mp4
from src.playlist import PlexMusicVideoHelper

from src.project_settings import settings


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
            if infile.is_dir() or outfile.is_dir():
                raise NotImplementedError("Only files done")
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
        case _:
            parser.print_help()
            return 1


if __name__ == "__main__":
    sys.exit(main())
