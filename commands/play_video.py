import argparse
import time
import typing

import set_root_path  # noqa
from image2ascii.frame_converter import FrameConverter

import cv2
import pafy

"""
TODO: use target resolution instead of downsample factor
TODO: add option for flipping webcam frames horizontally
TODO: clear terminal using ANSI codes for rewriting existing lines
"""

DELTA = 0.000001


def parse_args():
    parser = argparse.ArgumentParser(
        description='Play video in terminal as ascii frames.')
    parser.add_argument(
        'source',
        type=str,
        help='"webcam" or youtube url')
    parser.add_argument(
        'downsample_factor',
        type=int,
        help='factor by which to scale down the frames')
    parser.add_argument(
        '--invert_brightness',
        '-i',
        action='store_const',
        const=True,
        default=False)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    target_frame_duration: float
    target_framerate: int

    # get source stream
    if args.source == "webcam":
        video_capture = cv2.VideoCapture(0)
        target_framerate = round(video_capture.get(cv2.CAP_PROP_FPS))
        target_frame_duration = 1 / target_framerate
    else:
        vPafy = pafy.new(args.source)
        play = vPafy.getbest()
        video_capture = cv2.VideoCapture(play.url)
        target_framerate = round(video_capture.get(cv2.CAP_PROP_FPS))
        target_frame_duration = 1 / target_framerate

    frame_converter = FrameConverter(
        downsample_factor=args.downsample_factor)
    last_frame_time: typing.Optional[float] = None
    this_frame_time: typing.Optional[float] = None

    # read from stream
    while (True):
        last_frame_time = this_frame_time
        this_frame_time = time.time()
        duration = (
            this_frame_time - last_frame_time
            if last_frame_time is not None else None)
        actual_framerate = (
            round(1 / (duration + DELTA))
            if duration is not None
            else target_framerate)
        if args.source != "webcam" and duration is not None:
            """
            For youtube, we try to show video at original speed
            """
            if duration > target_frame_duration:
                to_skip = round(duration / target_frame_duration)
                for i in range(to_skip):
                    video_capture.read()
            elif duration < target_frame_duration:
                actual_framerate = round(1 / target_frame_duration)
                sleeptime = target_frame_duration - duration
                time.sleep(sleeptime)
        has_frame, frame = video_capture.read()
        if not has_frame:
            break
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ascii_frame = frame_converter.convert_frame_to_ascii(
            rgb_frame, invert_brightness=args.invert_brightness)
        frame_converter.print_frame(ascii_frame)
        print(f"Framerate: {actual_framerate}fps")
    print("Video complete!")
