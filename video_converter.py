import os
import random
import typing

import numpy as np
from scipy.spatial import KDTree


DELTA = 0.001
BLACK_WHITE_THRESHOLD = 40
SATURATION_THRESHOLD = 10

COLOR_TO_INT_MAPPING = {
    "BLACK": 0,
    "RED": 1,
    "GREEN": 2,
    "YELLOW": 3,
    "BLUE": 4,
    "PINK": 5,
    "CYAN": 6,
    "GRAY": 7
}

COLOR_TO_RGB_MAPPING = {
    "BLACK": (0, 0, 0),
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "YELLOW": (255, 255, 0),
    "BLUE": (0, 0, 255),
    "PINK": (255, 0, 255),
    "CYAN": (0, 255, 255),
    "GRAY": (255, 255, 255),
}

FOREGROUND_OFFSET = 30
BACKGROUND_OFFSET = 40


class FrameConverter:
    ASCII_TIERS_BY_BRIGHTNESS = [
        ['.', '`', ',', '"'],
        [':', '^', '-', '~'],
        ['>', 'i'],
        ['±', 'k', 'y', 'p', 'd', 'm'],
        ['&', 'W', '§'],
        ['@', '#']]

    def __init__(
            self,
            downsample_factor: int):
        self.downsample_factor_y = downsample_factor
        self.downsample_factor_x = round(downsample_factor / 2)
        self.color_names_list = []
        self.rgb_list = []
        for color_name, rgb in COLOR_TO_RGB_MAPPING.items():
            self.color_names_list.append(color_name)
            self.rgb_list.append(rgb)
        self.color_spacedb = KDTree(self.rgb_list)

    def get_ascii_for_pixel(
            self,
            pixel: typing.Tuple[int, int, int],
            invert_brightness: bool = False) -> str:
        """
        Use pixel brightness to choose ascii character
        """
        brightness = (pixel[0] / 256 + pixel[1] / 256 + pixel[2] / 256) / 3
        if invert_brightness:
            brightness = 1 - brightness
        tier = int(round(brightness * (
            len(type(self).ASCII_TIERS_BY_BRIGHTNESS) - 1)))
        return random.choice(type(self).ASCII_TIERS_BY_BRIGHTNESS[tier])

    def get_color_for_pixel(
            self,
            pixel: typing.Tuple[int, int, int]) -> str:
        if max(pixel) < BLACK_WHITE_THRESHOLD:
            return "BLACK"
        if min(pixel) > 255 - BLACK_WHITE_THRESHOLD:
            return "GRAY"
        if max(pixel) - min(pixel) < SATURATION_THRESHOLD:
            return "GRAY"

        # scale pixel to 0-255 range before evaluating
        translated_pixel = [v - min(pixel) for v in pixel]
        scale_ratio = 255 / (max(translated_pixel) + DELTA)
        scaled_pixel = [v * scale_ratio for v in translated_pixel]
        _, index = self.color_spacedb.query(scaled_pixel)

        return self.color_names_list[index]

    def get_string_for_pixel(
            self,
            pixel: typing.Tuple[int, int, int],
            invert_brightness: bool = False) -> str:
        char = self.get_ascii_for_pixel(pixel, invert_brightness)
        color = self.get_color_for_pixel(pixel)
        string = '\x1b[{};{};{}m{}\x1b[0m'.format(
            0,
            COLOR_TO_INT_MAPPING[color] + FOREGROUND_OFFSET,
            COLOR_TO_INT_MAPPING["BLACK"] + BACKGROUND_OFFSET,
            char)
        return string

    def convert_frame_to_ascii(
            self,
            frame: np.ndarray,
            invert_brightness: bool = False
    ) -> typing.Sequence[typing.Sequence[str]]:
        """
        Resize image and return list of characters corresponding
        to brightness of each pixel
        """
        downsampled = frame[
            ::self.downsample_factor_y,
            ::self.downsample_factor_x]
        return [
            [
                self.get_string_for_pixel(
                    pixel, invert_brightness=invert_brightness)
                for pixel in row]
            for row in downsampled]

    def print_frame(
            self,
            ascii_frame: typing.Sequence[typing.Sequence[str]]) -> None:
        """
        Print characters as lines
        """
        os.system('clear')
        output = "\n".join([
            "".join(row)
            for row in ascii_frame])
        print(output)
