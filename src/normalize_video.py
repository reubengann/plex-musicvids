# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 16:26:24 2020

@author: Reuben

Uses ffmpeg and ffprobe to normalize mp4 files to -23 LUFS
"""

import os
from pathlib import Path
import subprocess
import json
import re
import math
import shutil

TARGET_LUFS = -23


# def normalize_mp4s(measure_only: bool = False):
#     ffmpeg_bin = r"C:\ffmpeg\bin"
#     ffprobe_path = os.path.join(ffmpeg_bin, "ffprobe")
#     ffmpeg_path = os.path.join(ffmpeg_bin, "ffmpeg")

#     root_path = r"C:\Users\Reuben\Videos\fixed"

#     if not os.path.exists(os.path.join(root_path, "norm")) and not measure_only:
#         os.mkdir(os.path.join(root_path, "norm"))

#     for file_name in [s for s in os.listdir(root_path) if s.endswith("mp4")]:
#         file_path = os.path.join(root_path, file_name)
#         normalize_mp4(file_path, ffprobe_path, ffmpeg_path, measure_only)


def normalize_mp4(
    infile_path: Path,
    outfile_path: Path,
    ffprobe_path: Path,
    ffmpeg_path: Path,
    measure_only: bool = False,
):
    args = [
        ffprobe_path,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        infile_path,
    ]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        print(err.decode("utf-8"))
        raise Exception("Error probing file")

    streaminfo = json.loads(out)

    if len(streaminfo["streams"]) > 2:
        print("Warning: More than 1 audio stream!")

    for stream in streaminfo["streams"]:
        if stream["codec_type"] == "audio":
            break
    else:
        raise Exception("Could not find audio stream")

    if stream["codec_name"] != "aac":
        raise Exception("Not AAC")

    channel_index = stream["index"]
    args = [ffmpeg_path, "-v", "quiet"]
    args += ["-i", infile_path]
    args += [
        "-filter_complex",
        "ebur128=metadata=1,ametadata=print:key=lavfi.r128.I:file=-",
    ]
    args += ["-f", "null", "-"]

    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()

    if err:
        print(err.decode("utf-8"))
        raise Exception("Error measuring volume")

    volume_levels = out.decode("utf-8")
    pattern = re.compile("lavfi.r128.I=(.+)")

    volumes = []
    for line in volume_levels.split("\n"):
        m = re.match(pattern, line)
        if m:
            volumes.append(float(m.groups()[0]))

    current_lufs = max(volumes)
    gain_log = round(-(current_lufs - TARGET_LUFS), 2)

    if math.fabs(gain_log) > 1:
        print("adjusting", infile_path, "by", gain_log, "dB ... ", end="", flush=True)
        if measure_only:
            print("OK")
            return
        args = [ffmpeg_path, "-v", "quiet"]
        args += ["-i", infile_path]
        args += ["-af", "volume=volume={}dB".format(gain_log), outfile_path]

        process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = process.communicate()
        if err:
            print(err.decode("utf-8"))
            raise Exception("Problem adjusting audio")
        print("OK")
    else:
        print(infile_path, "is already normalized. Copying file as-is.")
        if measure_only:
            return
        shutil.copyfile(infile_path, outfile_path)
