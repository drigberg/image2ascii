import argparse

import set_root_path  # noqa
from video_converter import FrameConverter

import cv2
import pafy


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

    if args.source == "webcam":
        video_capture = cv2.VideoCapture(0)
    else:
        vPafy = pafy.new(args.source)
        play = vPafy.getbest()
        video_capture = cv2.VideoCapture(play.url)
    frame_converter = FrameConverter(
        downsample_factor=args.downsample_factor)
    while (True):
        ret, frame = video_capture.read()
        ascii_frame = frame_converter.convert_frame_to_ascii(
            frame, invert_brightness=args.invert_brightness)
        frame_converter.print_frame(ascii_frame)
