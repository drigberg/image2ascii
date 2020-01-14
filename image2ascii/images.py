import typing

from PIL import Image
import numpy as np


def get_frame_from_image(image: Image, down) -> np.ndarray:
    """
    Get numpy array of rows from flat Pillow list of pixels
    """
    image_width = image.size[0]
    image_height = image.size[1]
    image_data = list(image.getdata())
    frame: typing.MutableSequence[
        typing.Sequence[typing.Tuple[int, int, int]]] = []
    for y in range(image_height):
        row: typing.MutableSequence[typing.Tuple[int, int, int]] = []
        for x in range(image_width):
            pos = y * image_width + x
            row.append(image_data[pos])
        frame.append(row)
    return np.array(frame)
