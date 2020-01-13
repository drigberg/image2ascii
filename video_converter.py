import os
import random
import typing

import numpy as np
import webcolors


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


COLOR_TO_HEX_MAPPING = {
    "BLACK": "#000000",
    "RED": "#ff0000",
    "GREEN": "#008000",
    "YELLOW": "#ffff00",
    "BLUE": "#0000ff",
    "PINK": "#ff00ff",
    "CYAN": "#00ffff",
    "GRAY": "#ffffff",
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
        """
        Adapted from https://stackoverflow.com/questions/9694165/
                     convert-rgb-color-to-english-color-name-like-green-with-python
        """
        min_colors = {}
        for name, hex_code in COLOR_TO_HEX_MAPPING.items():
            r_c, g_c, b_c = webcolors.hex_to_rgb(hex_code)
            rd = (r_c - pixel[0]) ** 2
            gd = (g_c - pixel[1]) ** 2
            bd = (b_c - pixel[2]) ** 2
            min_colors[(rd + gd + bd)] = name
        color = min_colors[min(min_colors.keys())]
        return color

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
