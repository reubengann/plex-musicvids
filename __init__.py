import os
import shutil
import datetime
import fuzzywuzzy.process as fuzz
from mutagen.easyid3 import EasyID3
# from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import MetadataItem, PlayQueueGenerator, MediaItem, MediaPart

PATH_TO_PLEX_DB = 'c:/Users/Reuben/AppData/Local/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'
VIDEOS_FOLDER = r'D:\Videos\Music Videos\On Media Center'
DUMMY_ROOT = r"D:\Videos\Music Videos\Dummy"

VIDEOTYPES = ["mp4", "avi", "m2t", "m2ts", "m2v", "m4v", "mkv", "mov", "mpeg", "mpg", "mts", 
              "3g2", "3gp", "asf", "asx", "avc", "avs", "bivx", "bup", "divx", "dv", "dvr-ms",
              "evo", "fli", "flv", "nsv", "nuv", "ogm", "ogv", "tp", "pva", "qt", "rm", "rmvb",
              "sdp", "svq3", "strm", "ts", "ty", "vdr", "viv", "vob", "vp3", "wmv", "wpl",
              "wtv", "xsp", "xvid", "webm"]

def get_playlist(session):
    playlists = session.query(MetadataItem).filter(MetadataItem.metadata_type==15).all()
    if not playlists:
        raise Exception("Playlist not found")
    return playlists[0]

def get_filenames_in_playlist(session, playlist):
    q = session.query(MediaPart).join(MediaItem).join(PlayQueueGenerator).filter(
        PlayQueueGenerator.playlist_id == playlist.id
    ).all()
    return [v.file for v in q]

def get_all_video_filenames(session):
    q = session.query(MediaPart).all()
    return [v.file for v in q]

def file_extension_is_video(filename):
    if '.' not in filename:
        return False
    ext = (os.path.splitext(filename)[1])[1:]
    return ext in VIDEOTYPES

def get_videos_in_folder():
    vid_files = [os.path.join(VIDEOS_FOLDER, f) for f in os.listdir(VIDEOS_FOLDER) if file_extension_is_video(f)]
    return vid_files

def get_artists_in_plex(session):
    q = session.query(MetadataItem.title).filter(MetadataItem.metadata_type == 8).all()
    artists = [a.title for a in q]
    return artists

def get_metadata_item_for_filenames(session):
    q = session.query(MediaPart).join(MediaItem).join(MetadataItem).all()
    return {v.file: v.media_item.metadata_item.id for v in q}

def add_to_playlist(session, playlist, files):
    metadata_item_id_map = get_metadata_item_for_filenames(session)
    # print(metadata_item_id_map)
    order = len(files_in_playlist) + 1
    added = 0
    for f in files_not_in_playlist:
        mid = metadata_item_id_map[f]
        pqg = PlayQueueGenerator(
            playlist_id=playlist.id,
            metadata_item_id=mid,
            order=1000*order,
            created_at=datetime.datetime.now(),
            updated_at=datetime.datetime.now()
            )
        session.add(pqg)
        order += 1
        added += 1
    playlist.media_item_count += added
    session.commit()
    return added

def extract_dummy_names(artists, filenames):
    d = {} # dict will automatically de-duplicate artists with multiple tracks
    for f in filenames:
        artist, songname = os.path.basename(f).split(' - ')
        d[artist] = os.path.splitext(songname.strip())[0]
    return [(a, d[a]) for a in artists]

def make_dummy_artists(song_tups):
    for t in song_tups:
        artist, songname = t
        print('Creating', os.path.join(DUMMY_ROOT, artist))
        os.mkdir(os.path.join(DUMMY_ROOT, artist))
        dummy_filename = os.path.join(DUMMY_ROOT, artist, songname + ".mp3")
        print('Creating', dummy_filename)
        shutil.copy2("dummy.mp3", dummy_filename)
        meta = EasyID3(dummy_filename)
        meta['title'] = songname
        meta['artist'] = artist
        meta.save()

if __name__ == '__main__':
    write_dummies = False
    cnx = 'sqlite:///' + PATH_TO_PLEX_DB
    engine = create_engine(cnx)
    Session = sessionmaker(bind=engine)
    session = Session()
    playlist = get_playlist(session)
    print("Found playlist", playlist.title)
    print("Items: ", playlist.media_item_count)
    files_in_playlist = get_filenames_in_playlist(session, playlist)
    files_in_folder = get_videos_in_folder()
    files_not_in_playlist = set(files_in_folder) - set(files_in_playlist)
    print(len(files_not_in_playlist), "files are in the folder but not in playlist")
    videos_in_plex = get_all_video_filenames(session)
    videos_not_in_plex = set(files_in_folder) - set(videos_in_plex)
    print("Videos not already in Plex: ", len(videos_not_in_plex))
    if videos_not_in_plex and write_dummies:
        print("Videos not already in Plex: ", len(videos_not_in_plex))
        print('Trying to add ...')
        artists_in_plex = set(get_artists_in_plex(session))
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
        song_tups = extract_dummy_names(artists_not_in_plex, files_not_in_playlist)
        make_dummy_artists(song_tups)
        print('Success! Reload library.')
        exit(0)
    
    if files_not_in_playlist:
        added = add_to_playlist(session, playlist, files_not_in_playlist)
        print("Added:", added)
    else:
        print('Up to date!')
    