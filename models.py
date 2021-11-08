from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class PlexMetaDataItem(Base):

    __tablename__ = 'metadata_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    library_section_id = Column(Integer)
    parent_id = Column(Integer)
    metadata_type = Column(Integer)
    guid = Column(String(255))
    media_item_count = Column(Integer)
    title = Column(String(255))
    title_sort = Column(String(255))
    original_title = Column(String(255))
    studio = Column(String(255))
    rating = Column(Float)
    rating_count = Column(Integer)
    tagline = Column(String(255))
    summary = Column(Text)
    trivia = Column(Text)
    quotes = Column(Text)
    content_rating = Column(String(255))
    content_rating_age = Column(Integer)
    index = Column(Integer)
    absolute_index = Column(Integer)
    duration = Column(Integer)
    user_thumb_url = Column(String(255))
    user_art_url = Column(String(255))
    user_banner_url = Column(String(255))
    user_music_url = Column(String(255))
    user_fields = Column(String(255))
    tags_genre = Column(String(255))
    tags_collection = Column(String(255))
    tags_director = Column(String(255))
    tags_writer = Column(String(255))
    tags_star = Column(String(255))
    originally_available_at = Column(DateTime)
    available_at = Column(DateTime)
    expires_at = Column(DateTime)
    refreshed_at = Column(DateTime)
    year = Column(Integer)
    added_at = Column(DateTime)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    tags_country = Column(String(255))
    extra_data = Column(String(255))
    hash = Column(String(255))
    audience_rating = Column(Float)
    changed_at = Column(Integer, default=0)
    resources_changed_at = Column(Integer, default=0)
    remote = Column(Integer)


class PlexPlayQueueGenerator(Base):

    __tablename__ = 'play_queue_generators'

    id = Column(Integer, primary_key=True, autoincrement=True)
    playlist_id = Column(Integer, ForeignKey('metadata_items.id'))
    metadata_item_id = Column(Integer, ForeignKey('media_items.metadata_item_id'))
    uri = Column(String(255))
    limit = Column(Integer)
    continuous = Column(Boolean)
    order = Column(Float)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    changed_at = Column(Integer, default=0)
    recursive = Column(Boolean)
    type = Column(Integer)
    extra_data = Column(String(255))


class PlexMediaItem(Base):

    __tablename__ = 'media_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    library_section_id = Column(Integer)
    section_location_id = Column(Integer)
    metadata_item_id = Column(Integer, ForeignKey('metadata_items.id'), index=True)
    metadata_item = relationship("MetadataItem", backref="media_items")
    type_id = Column(Integer)
    width = Column(Integer)
    height = Column(Integer)
    size = Column(Integer)
    duration = Column(Integer)
    bitrate = Column(Integer)
    container = Column(String(255))
    video_codec = Column(String(255))
    audio_codec = Column(String(255))
    display_aspect_ratio = Column(Float)
    frames_per_second = Column(Float)
    audio_channels = Column(Integer)
    interlaced = Column(Boolean)
    source = Column(String(255))
    hints = Column(String(255))
    display_offset = Column(Integer)
    settings = Column(String(255))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    optimized_for_streaming = Column(Boolean)
    deleted_at = Column(DateTime)
    media_analysis_version = Column(Integer, default=0)
    sample_aspect_ratio = Column(Float)
    extra_data = Column(String(255))
    proxy_type = Column(Integer)
    channel_id = Column(Integer)
    begins_at = Column(DateTime)
    ends_at = Column(DateTime)
    color_trc = Column(String(255))


class PlexMediaPart(Base):

    __tablename__ = 'media_parts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    media_item_id = Column(Integer, ForeignKey('media_items.id'), index=True)
    media_item = relationship("MediaItem", backref="media_parts")
    directory_id = Column(Integer)
    hash = Column(String(255))
    open_subtitle_hash = Column(String(255))
    file = Column(String(255))
    index = Column(Integer)
    size = Column(Integer)
    duration = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    deleted_at = Column(DateTime)
    extra_data = Column(String(255))




class PlexLibrarySection(Base):

    __tablename__ = 'library_sections'

    id = Column(Integer, primary_key=True, autoincrement=True)
    library_id = Column(Integer)
    name = Column(String(255))
    name_sort = Column(String(255))
    section_type = Column(Integer)
    language = Column(String(255))
    agent = Column(String(255))
    scanner = Column(String(255))
    user_thumb_url = Column(String(255))
    user_art_url = Column(String(255))
    user_theme_music_url = Column(String(255))
    public = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    scanned_at = Column(DateTime)
    display_secondary_level = Column(Boolean)
    user_fields = Column(String(255))
    query_xml = Column(Text)
    query_type = Column(Integer)
    uuid = Column(String(255))
    changed_at = Column(Integer)
    content_changed_at = Column(Integer, default=0)
