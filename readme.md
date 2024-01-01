# Plex music video helper

Helper script to get music videos into Plex and form a large playlist of them

## Caveats

This program _modifies your Plex database_. I have never had an issue with this, but if you are at all worried or attached
to your current Plex setup, **make sure you backup your database before using this!**. 

I have only tested this in Windows.

## Setup

```bash
pip install -r requirements.txt
```
(See below for step-by-step instructions.) In your environment or in a .env file, specify the location of 

- VIDS_FOLDER: a folder with your videos for "vids_folder". This is the same folder that you set up in "Local Media Assets" under "Agents -> artists" in Plex settings 
- PLAYLIST_NAME: the name of the playlist you made in plex
- DUMMY_ROOT: a folder to place dummy mp3s. This folder should be in your music library. (Highlight Library, click plus sign to add, specify folder in "Add folders to library")
- FFMPEG_BIN: path to FFMPEG (something like c:\ffmpeg\bin). Only required if you want to use the normalize option

## To Run
```bash
python plex-musicvids.py [cmd]
```

Valid commands

- `analyze`: Determine if there are any detectable problems
- `normalize [infile] [outfile]`: adjust the audio of a file or multiple files
- `make_dummies`: add artists to Plex library by making a fake mp3
- `add_to_playlist`: add music videos to the playlist

## Step-by-step

### Creating the library

1. Make sure your videos are all in one folder and named like `FolderName/Artist Name - Descriptive Text.ext`
2. (Optional) Normalize your tracks with `python plex-musicvids.py normalize`
3. Launch the Plex Web App
4. Choose Settings from the top right of the Home screen, then choose the Server from the settings sidebar
5. Choose Extras (and make sure that you’re showing Advanced settings)
6. In the Global music video path field, specify the full filesystem path to the location of 
where your music videos are stored
7. Save the setting
8. Create a playlist
9. Create a folder for dummy tracks
10. Add the dummy folder as a music library
11. Run `copy .env.template .env`. Open .env and enter your dummy folder, music video folder, and playlist name.
12. Run `python plex-musicvids.py make_dummies` and then refresh your library
13. Go to the artists and make sure the music videos are found
14. Run `python plex-musicvids.py analyze` to check for any problems. You may need to adjust some artist names in 
the video files to match what Plex expects
15. Once you have all the videos recognized, add them to the playlist using `python plex-musicvids.py add_to_playlist`

### Updating the library

After the collection is working, you can add new videos easily. If the new videos are already known artists, you can just
`python plex-musicvids.py add_to_playlist`. Otherwise, you may need to `make_dummies` first.

My preferred way to add them is 
```bash
python plex-musicvids.py normalize path_of_new_video music_video_folder
python plex-musicvids.py make_dummies
python plex-musicvids.py add_to_playlist
```
