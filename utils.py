import os
import shutil
import datetime
from mutagen.easyid3 import EasyID3
from models import MetadataItem, PlayQueueGenerator, MediaItem, MediaPart

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