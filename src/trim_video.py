import json
from pathlib import Path
import subprocess
import uuid


def get_keyframes(ffprobe_path: Path, infile_path: Path) -> list[str]:
    args = [
        ffprobe_path,
        "-v",
        "error",
        "-print_format",
        "json",
        "-of",
        "json",
        "-select_streams",
        "v",
        "-skip_frame",
        "nokey",
        "-show_entries",
        "frame=pts_time",
        infile_path,
    ]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        print(err.decode("utf-8"))
        # raise Exception("Error probing file")
    print(out)
    streaminfo = json.loads(out)
    return [a["pts_time"] for a in streaminfo["frames"]]


def recode(
    ffmpeg_path: Path, input_file: Path, start: str, end: str, output_path: Path
):
    args = [
        ffmpeg_path,
        "-v",
        "error",
        "-i",
        input_file,
        "-ss",
        start,
        "-to",
        end,
        "-c:v",
        "libx264",
        "-c:a",
        "copy",
        "-force_key_frames",
        "expr:gte(t,n_forced*1)",
        output_path,
    ]
    print(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        print(err.decode("utf-8"))
        raise Exception("Error probing file")
    print(out)


def copy_second_segment(
    ffmpeg_path: Path, input_file: Path, start: str, end: str | None, output_path: Path
):
    args = [
        ffmpeg_path,
        "-v",
        "error",
        "-ss",
        start,
        "-i",
        input_file,
        "-c:v",
        "copy",
        "-c:a",
        "copy",
        "-avoid_negative_ts",
        "make_zero",
        "-movflags",
        "faststart",
        output_path,
    ]
    if end is not None:
        args += ["-to", end]
    print(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        print(err.decode("utf-8"))
        raise Exception("Error probing file")
    if out:
        print(out)


R"""
This works if you are going directly on a keyframe

ffmpeg -hide_banner -ss '54.35393' -i 'C:\omg\orig.mp4' -t '192.75923' -avoid_negative_ts make_zero -map '0:0' '-c:0' copy -map '0:1' '-c:1' copy -map_metadata 0 -movflags '+faststart' 
-default_mode infer_no_subs -ignore_unknown -f mp4 -y 'C:\Users\reube\Desktop\orig-00.00.54.354-00.04.07.113.mp4'

in between keyframes
ffmpeg -hide_banner -ss '54.35393' -i 'C:\omg\orig.mp4' -t '192.75923' -avoid_negative_ts make_zero -map '0:0' '-c:0' copy -map '0:1' '-c:1' copy -map_metadata 0 
-movflags '+faststart' -default_mode infer_no_subs -ignore_unknown -f mp4 -y 'C:\Users\reube\Desktop\orig-00.00.54.354-00.04.07.113.mp4'


echo -e "file 'file:C:\Users\reube\Desktop\orig-smartcut-segment-encode-0.mp4'\nfile 
'file:C:\Users\reube\Desktop\orig-smartcut-segment-copy-0.mp4'" 
| ffmpeg -hide_banner -f concat -safe 0 -protocol_whitelist 'file,pipe,fd' -i - -map '0:0' '-c:0' copy '-disposition:0' default -map '0:1' '-c:1' copy '-disposition:1' default 
-movflags '+faststart' -default_mode infer_no_subs -ignore_unknown -video_track_timescale 90000 -f mp4 -y 'C:\Users\reube\Desktop\orig-00.00.55.763-00.04.07.113.mp4'
"""


def trim_video(
    ffmpeg_bin_path: Path,
    infile_path: Path,
    output_path: Path,
    trim_start: str,
    trim_end: str | None,
):
    temp_folder = Path(R"C:\temp")
    temp_file = temp_folder / f"{uuid.uuid4()}.mp4"
    temp_file2 = temp_folder / f"{uuid.uuid4()}.mp4"
    print("Trim video")
    kfs = get_keyframes(ffmpeg_bin_path / "ffprobe", infile_path)
    print(kfs)
    for kf in kfs:
        if float(kf) >= float(trim_start):
            break
    else:
        raise Exception()
    print(f"Nearest keyframe after {trim_start} is {kf}")
    recode(ffmpeg_bin_path / "ffmpeg", infile_path, trim_start, kf, temp_file)
    copy_second_segment(
        ffmpeg_bin_path / "ffmpeg", infile_path, kf, trim_end, temp_file2
    )
    # print("wrote", temp_file)
    # input_text = temp_folder / "input.txt"
    # outpoint = ""
    # if trim_end is not None:
    #     outpoint = f"\noutpoint {trim_end}"
    # input_text.write_text(
    #     f"file '{temp_file}'\nfile '{infile_path}'\ninpoint {kf}{outpoint}"
    # )
    # args = [
    #     ffmpeg_bin_path / "ffmpeg",
    #     "-v",
    #     "error",
    #     "-f",
    #     "concat",
    #     "-safe",
    #     "0",
    #     "-i",
    #     temp_folder / "input.txt",
    #     "-c",
    #     "copy",
    #     output_path,
    # ]
    # process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # out, err = process.communicate()
    # if err:
    #     print(err.decode("utf-8"))
    #     raise Exception("Error assembling new video file")
    # print(out)
    # temp_file.unlink()
    # input_text.unlink()
