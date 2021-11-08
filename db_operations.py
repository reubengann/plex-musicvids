import datetime
import os
from collections import namedtuple
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import PlexMetaDataItem, PlexMediaItem, PlexMediaPart, PlexPlayQueueGenerator

PlexVideo = namedtuple('PlexVideo', ['media_item', 'media_part'])
PlexPlaylistVideo = namedtuple('PlexPlaylistVideo', ['media_item', 'media_part', 'queue_generator'])

PLAYLIST_METADATA_TYPE = 15
ARTIST_METADATA_TYPE = 8


def get_playlists(session):
    return session.query(PlexMetaDataItem).filter(PlexMetaDataItem.metadata_type == PLAYLIST_METADATA_TYPE).all()


def get_videos_in_plex(session, vids_folder):
    results = session.query(PlexMediaItem, PlexMediaPart).join(PlexMediaPart, PlexMediaItem.id == PlexMediaPart.media_item_id).all()
    results = [PlexVideo(*r) for r in results]
    return [r for r in results if r.media_part.file.startswith(vids_folder)]


def get_videos_in_playlist(session, playlist_id):
    results = session.query(PlexMediaItem, PlexMediaPart, PlexPlayQueueGenerator) \
        .join(PlexMediaPart, PlexMediaItem.id == PlexMediaPart.media_item_id) \
        .join(PlexPlayQueueGenerator, PlexPlayQueueGenerator.metadata_item_id == PlexMediaItem.metadata_item_id) \
        .filter(PlexPlayQueueGenerator.playlist_id == playlist_id) \
        .all()
    return [PlexPlaylistVideo(*r) for r in results]


def get_artists_in_plex(session):
    return session.query(PlexMetaDataItem).filter(PlexMetaDataItem.metadata_type == ARTIST_METADATA_TYPE)


def add_video_to_playlist(session, playlist_id, vid, place):
    item = PlexPlayQueueGenerator()
    item.playlist_id = playlist_id
    item.metadata_item_id = vid.media_item.metadata_item_id
    item.order = 1000.0 * place
    item.created_at = datetime.datetime.now()
    item.updated_at = datetime.datetime.now()
    session.add(item)
    session.commit()


def make_engine():
    db_location = os.path.join(
        os.getenv('LOCALAPPDATA'),
        "Plex Media Server",
        "Plug-in Support",
        "Databases",
        "com.plexapp.plugins.library.db")
    return create_engine("sqlite:///" + db_location)


def make_session(engine):
    Session = sessionmaker(bind=engine)
    return Session()
