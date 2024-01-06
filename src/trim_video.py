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
        "-vcodec",
        "copy",
        "-acodec",
        "copy",
        output_path,
    ]
    # print(args)
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        print(err.decode("utf-8"))
        raise Exception("Error probing file")
    print(out)


def trim_video(
    ffmpeg_bin_path: Path, infile_path: Path, output_path: Path, trim_start: str
):
    temp_folder = Path(R"C:\temp")
    temp_file = temp_folder / f"{uuid.uuid4()}.mp4"
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
    print("wrote", temp_file)
    input_text = temp_folder / "input.txt"
    input_text.write_text(f"file '{temp_file}'\nfile '{infile_path}'\ninpoint {kf}")
    args = [
        ffmpeg_bin_path / "ffmpeg",
        "-v",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        temp_folder / "input.txt",
        "-c",
        "copy",
        output_path,
    ]
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate()
    if err:
        print(err.decode("utf-8"))
        raise Exception("Error assembling new video file")
    print(out)
    temp_file.unlink()
    input_text.unlink()
