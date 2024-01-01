# Plex music video helper

Helper script to get music videos into Plex and form a large playlist of them

## Setup

```bash
pip install -r requirements.txt
```
In your environment or in a .env file, specify the location of 

- VIDS_FOLDER: a folder with your videos for "vids_folder". This is the same folder that you set up in "Local Media Assets" under "Agents -> artists" in Plex settings 
- PLAYLIST_NAME: the name of the playlist you made in plex
- DUMMY_ROOT: a folder to place dummy mp3s. This folder should be in your music library. (Highlight Library, click plus sign to add, specify folder in "Add folders to library")

## To Run:
```bash
python plex-musicvids.py [cmd]
```

Valid commands

- `playlist`: 