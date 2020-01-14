import argparse

import set_root_path  # noqa
from image2ascii.image_converter import ImageConverter


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
    image_converter = ImageConverter(args.image_path, args.downsample_factor)
    chars = image_converter.convert_image_to_ascii(invert=args.invert)
    image_converter.print(chars)
    print(
        f'Converted image of size {image_converter.image.size} '
        f'by factor {args.downsample_factor}')
