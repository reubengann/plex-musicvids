import os
import fuzzywuzzy.process as fuzz
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import utils

PATH_TO_PLEX_DB = 'c:/Users/Reuben/AppData/Local/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'
VIDEOS_FOLDER = r'D:\Videos\Music Videos\On Media Center'
DUMMY_ROOT = r"D:\Videos\Music Videos\Dummy"

if __name__ == '__main__':
    write_dummies = False
    cnx = 'sqlite:///' + PATH_TO_PLEX_DB
    engine = create_engine(cnx)
    Session = sessionmaker(bind=engine)
    session = Session()
    playlist = utils.get_playlist(session)
    print("Found playlist", playlist.title)
    print("Items: ", playlist.media_item_count)
    files_in_playlist = utils.get_filenames_in_playlist(session, playlist)
    files_in_folder = utils.get_videos_in_folder()
    files_not_in_playlist = set(files_in_folder) - set(files_in_playlist)
    print(len(files_not_in_playlist), "files are in the folder but not in playlist")
    videos_in_plex = utils.get_all_video_filenames(session)
    videos_not_in_plex = set(files_in_folder) - set(videos_in_plex)
    print("Videos not already in Plex: ", len(videos_not_in_plex))
    if videos_not_in_plex and write_dummies:
        print("Videos not already in Plex: ", len(videos_not_in_plex))
        print('Trying to add ...')
        artists_in_plex = set(utils.get_artists_in_plex(session))
        artists_of_missing_vids = {os.path.basename(v).split(' - ')[0] for v in videos_not_in_plex}
        artists_not_in_plex = artists_of_missing_vids - artists_in_plex
        artists_with_videos_not_picked_up = artists_in_plex & artists_of_missing_vids
        if artists_with_videos_not_picked_up:
            print(artists_with_videos_not_picked_up)
            raise Exception('Folder is not clean')
            
        for a in artists_not_in_plex:
            res = fuzz.extract(a, artists_in_plex, limit=1)
            if res[0][1] > 90:
                print('I think "{}"'.format(a), 'corresponds to', res[0][0], 'which is already in the library')
                print('Delete the dummy and try again')
                raise Exception('Folder is not clean')
        song_tups = utils.extract_dummy_names(artists_not_in_plex, files_not_in_playlist)
        utils.make_dummy_artists(song_tups)
        print('Success! Reload library.')
        exit(0)
    
    if files_not_in_playlist:
        added = utils.add_to_playlist(session, playlist, files_not_in_playlist)
        print("Added:", added)
    else:
        print('Up to date!')
    