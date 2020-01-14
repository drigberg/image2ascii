import random
import typing

import numpy as np


BLANK_SCREEN = "".join(["\n" for i in range(50)])


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
            downsample_factor: int,
            window):
        self.downsample_factor_x = downsample_factor
        # terminal characters are twice as tall as they are wide
        self.downsample_factor_y = downsample_factor * 2
        self.window = window

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
                self.get_ascii_for_pixel(
                    pixel, invert_brightness=invert_brightness)
                for pixel in row]
            for row in downsampled]

    def print_frame(
            self,
            ascii_frame: typing.Sequence[typing.Sequence[str]]) -> None:
        """
        Print characters as lines
        """
        output = "\n".join([
            "".join(row)
            for row in ascii_frame])
        self.window.erase()
        self.window.addstr(output)
        self.window.refresh()
