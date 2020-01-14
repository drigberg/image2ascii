import argparse
import curses
import math
import time
import typing

import set_root_path  # noqa
from image2ascii.frame_converter import FrameConverter

import cv2
import numpy as np
import pafy

"""
TODO: clear terminal using ANSI codes for rewriting existing lines
"""

DELTA = 0.000001


OUTPUT_WIDTHS_BY_LABEL = {
    "XS": 36,
    "S": 78,
    "M": 120,
    "L": 162,
    "XL": 204,
    "XXL": 246,
    "XXXL": 288}


def parse_args():
    parser = argparse.ArgumentParser(
        description='Play video in terminal as ascii frames.')
    parser.add_argument(
        'source',
        type=str,
        help='"webcam" or youtube url')
    parser.add_argument(
        'size',
        type=str,
        choices=list(OUTPUT_WIDTHS_BY_LABEL.keys()),
        help='output size')
    parser.add_argument(
        '--invert-brightness',
        '-i',
        dest='invert_brightness',
        action='store_const',
        const=True,
        default=False)
    parser.add_argument(
        '--flip-horizontally',
        '-f',
        dest='flip_horizontally',
        action='store_const',
        const=True,
        default=False)
    args = parser.parse_args()
    return args


def get_video_capture(source: str) -> cv2.VideoCapture:
    target_frame_duration: float
    target_framerate: int

    # get source stream
    if source == "webcam":
        video_capture = cv2.VideoCapture(0)
    else:
        vPafy = pafy.new(source)
        play = vPafy.getbest()
        video_capture = cv2.VideoCapture(play.url)
    return video_capture


def get_frame_index_for_time_elapsed(
        target_framerate: int, time_elapsed: float):
    """
    Based on time elapsed and frame rate, figure out which frame we
    should be showing
    """
    return math.floor(time_elapsed * target_framerate)


def play_video(
        video_capture: cv2.VideoCapture,
        window,
        downsample_factor: int) -> None:
    frame_converter = FrameConverter(
        downsample_factor=downsample_factor,
        window=window)

    # init timing variables
    target_framerate = round(video_capture.get(cv2.CAP_PROP_FPS))
    target_frame_duration = 1 / target_framerate
    last_frame_time: typing.Optional[float] = None
    this_frame_time: typing.Optional[float] = None

    # we start at frame 1 instead of 0 because we read the first
    # frame to get the video dimensions
    current_frame_index = 1
    video_start_time = time.time()

    # read from stream
    while (True):
        if args.source != "webcam":
            # For youtube, we try to show video at original speed
            time_elapsed = time.time() - video_start_time
            expected_frame_index = get_frame_index_for_time_elapsed(
                target_framerate, time_elapsed)
            if expected_frame_index > current_frame_index:
                frames_to_skip = expected_frame_index - current_frame_index
                for i in range(frames_to_skip):
                    video_capture.read()
                current_frame_index = expected_frame_index
            elif expected_frame_index < current_frame_index:
                # we're running ahead: wait a bit and loop again
                time.sleep(target_frame_duration / 2)
                continue

        # display frame
        has_frame, frame = video_capture.read()
        if not has_frame:
            break
        current_frame_index += 1
        if args.flip_horizontally:
            frame = np.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        ascii_frame = frame_converter.convert_frame_to_ascii(
            rgb_frame, invert_brightness=args.invert_brightness)
        frame_converter.print_frame(ascii_frame)

        # display performance stats
        last_frame_time = this_frame_time
        this_frame_time = time.time()
        time_elapsed = this_frame_time - video_start_time
        duration = (
            this_frame_time - last_frame_time
            if last_frame_time is not None else None)
        actual_framerate = (
            round(1 / (duration + DELTA))
            if duration is not None
            else target_framerate)
        window.addstr(f"\nFramerate: {actual_framerate}fps")
        window.addstr("\n<Press any key to exit>")
        window.refresh()
        char = window.getch()
        if char != -1:
            break


if __name__ == "__main__":
    args = parse_args()
    video_capture = get_video_capture(args.source)
    has_frame, frame = video_capture.read()
    original_width = frame.shape[1]
    output_width = OUTPUT_WIDTHS_BY_LABEL[args.size]
    downsample_factor = math.ceil(original_width / output_width)
    output_height = int(frame.shape[0] / downsample_factor)

    # setup window with hidden cursor
    w = curses.initscr()
    w.nodelay(1)
    curses.curs_set(0)

    error = None
    try:
        play_video(video_capture, w, downsample_factor)
    except Exception as e:
        error = e
    w.erase()
    w.refresh()
    curses.endwin()
    if error is not None:
        print(
            "Encountered error: most likely, the window is too small "
            "for the output size selected.")
