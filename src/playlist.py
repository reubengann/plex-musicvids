import os
import sys
import shutil
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from fuzzywuzzy import process as fuzzy_process
from mutagen.easyid3 import EasyID3
import src.db_operations as db_operations

from src.video_types import VIDEO_TYPES


class PlexMusicVideoHelper:
    def __init__(
        self,
        playlist_name: str,
        vids_folder: str,
        dummy_root: str,
        temp_folder: str = R"C:\temp",
    ):
        self.engine = db_operations.make_engine()
        self.session = db_operations.make_session(self.engine)
        all_playlists = db_operations.get_playlists(self.session)
        self.playlist = find_playlist(playlist_name, all_playlists)
        self.videos_in_plex = db_operations.get_videos_in_plex(
            self.session, vids_folder
        )
        self.video_file_names_in_plex = [f.media_part.file for f in self.videos_in_plex]
        self.video_file_names = get_video_files(vids_folder)
        self.videos_in_playlist = db_operations.get_videos_in_playlist(
            self.session, self.playlist.id
        )
        self.dummy_root = dummy_root
        self.video_names_in_plex = [s.media_part.file for s in self.videos_in_plex]
        self.artists_in_plex = db_operations.get_artists_in_plex(self.session)
        self.tempfolder = temp_folder

    def print_summary(self):
        files_in_plex = self.video_file_names_in_plex
        # self.video_names_in_plex = [s.file for s in self.videos_in_plex]
        files_in_playlist = [f.media_part.file for f in self.videos_in_playlist]
        print(f"Videos in folder:   {len(self.video_file_names)}")
        print(
            f"Videos in Plex:     {len(set(files_in_plex))} (plus {len(files_in_plex)-len(set(files_in_plex))} duplicates)"
        )
        print(f"Videos in playlist: {len(files_in_playlist)}")
        print(
            f"Videos not in Plex: {len(self.video_file_names) - len(set(files_in_plex))}"
        )

    def make_dummies(self):
        vids_not_in_plex = list(
            set(self.video_file_names).difference(self.video_names_in_plex)
        )
        artists_not_in_plex = self.get_artists_not_in_plex(vids_not_in_plex)
        folders = get_folders(self.dummy_root)
        artists_folders_already_exist = False
        dummies_made = 0
        for artist in artists_not_in_plex:
            if os.path.join(self.dummy_root, artist) in folders:
                artists_folders_already_exist = True
            else:
                self.make_dummy_track(artist)
                dummies_made += 1
        print(f"Dummies made: {dummies_made}")
        if artists_folders_already_exist:
            print(
                """
Videos that should be recognized in Plex aren't in the database.
Some artists may have slightly different names than Plex expects.
You may need to go into Plex and "fix match" to the correct band.
You can also try re-running with -f."""
            )

    def analyze(self):
        vids_not_in_plex = list(
            set(self.video_file_names).difference(self.video_names_in_plex)
        )
        artists_not_in_plex = self.get_artists_not_in_plex(vids_not_in_plex)
        folders = get_folders(self.dummy_root)
        any_issues = False
        for artist in artists_not_in_plex:
            if os.path.join(self.dummy_root, artist) in folders:
                print(f"Possible issue with artist: {artist}")
                any_issues = True
        for vid in vids_not_in_plex:
            print(vid)
            any_issues = True
        if not any_issues:
            print("No issues found.")

    def fix_artists_with_bad_names(self):
        bad_names = []
        vids_not_in_plex = list(
            set(self.video_file_names).difference(self.video_names_in_plex)
        )
        artists_not_in_plex = self.get_artists_not_in_plex(vids_not_in_plex)
        artist_names_in_plex = [a.title for a in self.artists_in_plex]
        folders = get_folders(self.dummy_root)
        for artist in artists_not_in_plex:
            if os.path.join(self.dummy_root, artist) in folders:
                bad_names.append(artist)
        sequestered = []
        for artist in bad_names:
            searchresult = fuzzy_process.extract(artist, artist_names_in_plex, limit=1)
            correction = searchresult[0][0]
            input_var = input(f'Change "{artist}" to "{correction}? (Y/N): ')
            if input_var == "Y":
                vids_by_artist = self.get_vids_by_artist(artist)
                if vids_by_artist:
                    rename_videos_to_new_artist(vids_by_artist, correction)
                rename_dummy_artist(self.dummy_root, artist, correction)
                # Move the folder outside of the root so that it'll be removed
                shutil.move(
                    os.path.join(self.dummy_root, correction),
                    os.path.join(self.tempfolder, correction),
                )
                sequestered.append(correction)
        if sequestered:
            input(
                "Please rescan and press enter (this will temporarily remove the artists)"
            )
            for s in sequestered:
                # Move the folders back in
                shutil.move(
                    os.path.join(self.tempfolder, s), os.path.join(self.dummy_root, s)
                )
            input("Please rescan again and press enter (this puts them back in)")

    def add_videos_to_playlist(self):
        vids_to_add = []
        files_in_playlist = [a.media_part.file for a in self.videos_in_playlist]
        for vid in self.videos_in_plex:
            if vid.media_part.file not in files_in_playlist:
                vids_to_add.append(vid)
        if vids_to_add:
            self.add_videos_to_playlist_db(vids_to_add)
            print(f"Added {len(vids_to_add)} videos")
        else:
            print("All videos in Plex are in the playlist")

    def add_videos_to_playlist_db(self, videos_to_add):
        already_added = []
        for vid in videos_to_add:
            if vid.media_part.file not in already_added:
                db_operations.add_video_to_playlist(
                    self.session,
                    self.playlist.id,
                    vid,
                    (len(self.videos_in_playlist) + 1),
                )
                self.videos_in_playlist.append(vid)
                already_added.append(vid.media_part.file)

    def get_vids_by_artist(self, artist):
        return [
            a
            for a in self.video_file_names_in_plex
            if os.path.basename(a).startswith(artist)
        ]

    def make_dummy_track(self, artist):
        root = self.dummy_root
        trackname = get_a_song_name_by(self.video_file_names, artist)
        os.mkdir(os.path.join(root, artist))
        dummyfile = os.path.join(root, artist, f"{trackname}.mp3")
        shutil.copy2("dummy.mp3", dummyfile)
        meta = EasyID3(dummyfile)
        meta["title"] = os.path.splitext(trackname)[0]
        meta["artist"] = artist
        meta.save()

    def get_artists_not_in_plex(self, vids_not_in_plex):
        missing_artists = [
            os.path.basename(v).split(" - ")[0] for v in vids_not_in_plex
        ]
        missing_artists = sorted(list(set(missing_artists)))
        return list(set(missing_artists).difference(self.artists_in_plex))


def get_folders(root):
    directory_list = list()
    for root, dirs, _ in os.walk(root, topdown=False):
        for name in dirs:
            directory_list.append(os.path.join(root, name))
    return directory_list


def get_a_song_name_by(video_file_names, artist):
    for vid in video_file_names:
        if os.path.basename(vid).startswith(artist):
            trackname = os.path.splitext(os.path.basename(vid))[0]
            return trackname.split(" - ")[1]


def get_video_files(vids_folder):
    return [
        os.path.join(vids_folder, f)
        for f in os.listdir(vids_folder)
        if get_extension(f) in VIDEO_TYPES
    ]


def get_extension(path):
    if "." not in path:
        return ""
    ext = (os.path.splitext(path)[1])[1:]
    if ext in VIDEO_TYPES and " - " not in path:
        raise ValueError(
            f"Video file name is not formatted correctly: {path}\nPlease use 'Artist - Title.mp4'"
        )
    return ext


def find_playlist(playlist_name, playlists):
    for playlist in playlists:
        if playlist.title == playlist_name:
            print(f"Playlist found: {playlist_name}")
            break
    else:
        raise Exception(f"Playlist {playlist_name} not found")
    return playlist


def rename_videos_to_new_artist(vids_by_artist, new_artist):
    for vid in vids_by_artist:
        _, track = os.path.basename(vid).split(" - ")
        # Rename video
        newpath = os.path.join(os.path.dirname(vid), new_artist + " - " + track)
        os.rename(vid, newpath)


def rename_dummy_artist(dummy_root, old_artist, new_artist):
    for file in os.listdir(os.path.join(dummy_root, old_artist)):
        # rename all the mp3s
        if file.endswith(".mp3"):
            meta = EasyID3(os.path.join(dummy_root, old_artist, file))
            meta["artist"] = new_artist
            meta.save()
    # rename the path
    os.rename(
        os.path.join(dummy_root, old_artist), os.path.join(dummy_root, new_artist)
    )


# if __name__ == "__main__":
#     args = sys.argv[1:]
#     helper = PlexMusicVideoHelper()
#     helper.print_summary()
#     if "-a" in args:
#         print("Adding videos to playlist")
#         helper.add_videos_to_playlist()
#     if "-d" in args:
#         print("Making dummies")
#         helper.make_dummies()
#     if "-l" in args:
#         print("Analyzing")
#         helper.analyze()
#     if "-f" in args:
#         print("Fixing artists")
#         helper.fix_artists_with_bad_names()
