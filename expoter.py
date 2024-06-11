import os
import subprocess


def exportVideo(
    inputPath: str,
    outputPath: str,
    trimStartPosMs: int,
    trimEndPosMs: int,
    resolution: str,
    framerate: int,
    size: int,
    noAudio: bool,
):

    duration = round((trimEndPosMs - trimStartPosMs) / 1000, 2)
    bitRateKB = min(int(size * 850 / duration), 10000)
    noAudioArg = "-an" if noAudio else ""

    encoder = "h264_nvenc"

    args = f'-ss {round(trimStartPosMs / 1000,2)}  -i "{inputPath}" -t {duration} -s {resolution} -r {framerate} -c:v {encoder} -b:v {bitRateKB}KB {noAudioArg} -y "{outputPath}"'

    result = subprocess.run(
        f"./ffmpeg {args}",
        creationflags=subprocess.CREATE_NO_WINDOW,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        encoder = "h264"
        args = f'-ss {round(trimStartPosMs / 1000,2)}  -i "{inputPath}" -t {duration} -s {resolution} -r {framerate} -c:v {encoder} -b:v {bitRateKB}KB {noAudioArg} -y "{outputPath}"'
        result = subprocess.run(
            f"./ffmpeg {args}",
            creationflags=subprocess.CREATE_NO_WINDOW,
            capture_output=True,
            text=True,
        )

    return result
