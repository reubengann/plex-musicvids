import os
import datetime
from urllib.parse import quote_plus
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import MetadataItem, PlayQueueGenerator, MediaItem, MediaPart

PATH_TO_PLEX_DB = 'c:/Users/Reuben/AppData/Local/Plex Media Server/Plug-in Support/Databases/com.plexapp.plugins.library.db'
VIDEOS_FOLDER = r'D:\Videos\Music Videos\On Media Center'

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

def get_metadata_item_for_filenames(session):
    q = session.query(MediaPart).join(MediaItem).join(MetadataItem).all()
    return {v.file: v.media_item.metadata_item.id for v in q}

def add_to_playlist(session, playlist, files):
    metadata_item_id_map = get_metadata_item_for_filenames(session)
    print(metadata_item_id_map)
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


if __name__ == '__main__':
    print('running')
    cnx = 'sqlite:///' + PATH_TO_PLEX_DB
    some_engine = create_engine(cnx)
    Session = sessionmaker(bind=some_engine)
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
    added = add_to_playlist(session, playlist, files_not_in_playlist)
    print("Added:", added)
    