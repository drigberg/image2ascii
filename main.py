import argparse
import dataclasses
import random
import typing

from PIL import Image


@dataclasses.dataclass(frozen=True)
class Pixel:
    r: int
    g: int
    b: int

    @property
    def brightness(self):
        return (self.r / 256 + self.g / 256 + self.b / 256) / 3


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
            pixel: Pixel,
            invert: bool = False) -> str:
        brightness = pixel.brightness if not invert else (1 - pixel.brightness)
        tier = round(brightness * (
            len(type(self).ASCII_TIERS_BY_BRIGHTNESS) - 1))
        return random.choice(type(self).ASCII_TIERS_BY_BRIGHTNESS[tier])

    def get_downsampled_pixel(
            self,
            pixels: typing.Sequence[Pixel],
            target_x: int,
            target_y: int) -> Pixel:
        count = 0
        r = 0
        g = 0
        b = 0
        orig_x = target_x * self.downsample_factor_x
        orig_y = target_y * self.downsample_factor_y

        # determine average r, g, and b values for pixels in area
        for x_step in range(self.downsample_factor_x):
            for y_step in range(self.downsample_factor_y):
                offset = x_step + y_step
                pos = orig_y * self.image_width + orig_x + offset
                assert pos < len(pixels)
                pixel = pixels[pos]
                r = (r * count + pixel.r) / (count + 1)
                g = (g * count + pixel.g) / (count + 1)
                b = (b * count + pixel.b) / (count + 1)
                count += 1
        return Pixel(r, g, b)

    def downsample(self) -> typing.Sequence[Pixel]:
        image_data = list(self.image.getdata())
        pixels = [
            Pixel(r=datum[0], g=datum[1], b=datum[2])
            for datum in image_data]
        downsampled: typing.MutableSequence[Pixel] = []
        for y in range(self.target_height):
            for x in range(self.target_width):
                pixel = self.get_downsampled_pixel(pixels, x, y)
                downsampled.append(pixel)
        return downsampled

    def convert_image_to_ascii(
            self,
            invert: bool = False) -> typing.Sequence[str]:
        downsampled = self.downsample()
        return [
            self.get_ascii_for_pixel(pixel, invert=invert)
            for pixel in downsampled]

    def print(self, chars: typing.Sequence[str]):
        for y in range(self.target_height):
            row = []
            for x in range(self.target_width):
                pos = y * self.target_width + x
                row.append(str(chars[pos]))
            print("".join(row))


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
    chars = converter.convert_image_to_ascii(invert=args.invert)
    converter.print(chars)
    print(
        f'Converted image of size {converter.image.size} '
        f'by factor {args.downsample_factor}')
