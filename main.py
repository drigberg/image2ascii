import argparse
import random
import typing

from PIL import Image


class Converter:
    ASCII_TIERS_BY_BRIGHTNESS = [
        ['.', '`', ','],
        [':', '^'],
        ['>', 'i', '~', '-'],
        ['±', 'k'],
        ['&', 'W', '§'],
        ['@']
    ]

    def __init__(
            self,
            image_path: str,
            downsample_factor: int):
        self.image = Image.open(image_path)
        self.image_width = self.image.size[0]
        self.image_height = self.image.size[1]
        self.downsample_factor_y = downsample_factor
        self.downsample_factor_x = round(downsample_factor / 2)
        self.target_width = round(
            self.image_width / self.downsample_factor_x)
        self.target_height = round(
            self.image_height / self.downsample_factor_y)

    def get_ascii_for_pixel(
            self,
            pixel: typing.Tuple[int, int, int],
            invert: bool = False) -> str:
        avg = (pixel[0] / 256 + pixel[1] / 256 + pixel[2] / 256) / 3

        if invert:
            avg = 1 - avg
        tier = round(avg * 4)
        return random.choice(type(self).ASCII_TIERS_BY_BRIGHTNESS[tier])

    def get_downsampled_pixel(
            self,
            pixels: typing.Sequence[typing.Tuple[int, int, int]],
            target_x: int,
            target_y: int) -> typing.Tuple[int, int, int]:
        pixel = (0, 0, 0)
        count = 0
        orig_x = target_x * self.downsample_factor_x
        orig_y = target_y * self.downsample_factor_y

        for x_step in range(self.downsample_factor_x):
            for y_step in range(self.downsample_factor_y):
                offset = x_step + y_step
                pos = orig_y * self.image_width + orig_x + offset
                if (pos < len(pixels)):
                    pixel = (
                        ((pixel[0] * count) + pixels[pos][0]) / (count + 1),
                        ((pixel[1] * count) + pixels[pos][1]) / (count + 1),
                        ((pixel[2] * count) + pixels[pos][2]) / (count + 1)
                    )
                count += 1
        return pixel

    def downsample(self) -> typing.Sequence[typing.Tuple[int, int, int]]:
        pixels = list(self.image.getdata())
        downsampled: typing.MutableSequence[typing.Tuple[int, int, int]] = []
        for y in range(self.target_height):
            for x in range(self.target_width):
                pixel = self.get_downsampled_pixel(pixels, x, y)
                downsampled.append(pixel)
        return downsampled

    def convert(self, invert: bool = False) -> typing.Sequence[str]:
        downsampled = self.downsample()
        return list(map(
            lambda pix: self.get_ascii_for_pixel(pix, invert),
            downsampled))

    def print(self, chars: typing.Sequence[str]):
        for y in range(self.target_height):
            row = ''
            for x in range(self.target_width):
                pos = y * self.target_width + x
                row += str(chars[pos])
            print(row)
        print(f'Converted image of size {self.image.size}')


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
    converter = Converter(args.image_path, args.downsample_factor)
    chars = converter.convert(invert=args.invert)
    converter.print(chars)
