import argparse

from PIL import Image

import set_root_path  # noqa
from image2ascii.frame_converter import FrameConverter
from image2ascii.images import get_frame_from_image


def parse_args():
    parser = argparse.ArgumentParser(description='Convert image to ascii.')
    parser.add_argument(
        'image_path',
        type=str,
        help='path to image file')
    parser.add_argument(
        'downsample_factor',
        type=int,
        help='factor by which to scale down the image')
    parser.add_argument(
        '--invert',
        '-i',
        action='store_const',
        const=True,
        default=False)
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    image = Image.open(args.image_path)
    frame_converter = FrameConverter(
        downsample_factor=args.downsample_factor)
    frame = get_frame_from_image(image)
    ascii_frame = frame_converter.convert_frame_to_ascii(
        frame, invert_brightness=args.invert)
    frame_converter.print_frame(ascii_frame)
    print(
        f'Converted image of size {image.size} '
        f'by factor {args.downsample_factor}')
