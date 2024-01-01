import argparse
import sys
from src.playlist import PlexMusicVideoHelper

from src.project_settings import settings


def main() -> int:
    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(
        dest="subparser_name",
        help="Music video playlist utility for Plex",
    )

    # Add commands
    cmd1_p = subp.add_parser("analyze", help="Analyze current state of playlist")

    # Add command line arguments to the commands
    # cmd1_p.add_argument("query")
    args = parser.parse_args()
    match args.subparser_name:
        case "analyze":
            print("Analyzing current state of playlist")
            if settings.dummy_root is None:
                print(
                    "DUMMY_ROOT is not set. Please modify your .env file or environment variables"
                )
                return 1
            if settings.vids_folder is None:
                print(
                    "VIDS_FOLDER is not set. Please modify your .env file or environment variables"
                )
                return 1
            if settings.playlist_name is None:
                print(
                    "PLAYLIST_NAME is not set. Please modify your .env file or environment variables"
                )
                return 1
            helper = PlexMusicVideoHelper(
                settings.playlist_name, settings.vids_folder, settings.dummy_root
            )
            helper.print_summary()
            helper.analyze()
            return 0
        case "cmd2":
            print("Running command 2")
            return 0
        case _:
            parser.print_help()
            return 1


if __name__ == "__main__":
    sys.exit(main())
