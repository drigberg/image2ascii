import pytest

from video_converter import FrameConverter


class TestFrameConverter:
    @pytest.mark.parametrize("pixel,expected_result", [
        ((0, 0, 0), "BLACK"),
        ((10, 10, 10), "BLACK"),
        ((0, 50, 0), "GREEN"),
        ((250, 0, 0), "RED"),
        ((100, 0, 0), "RED"),
        ((255, 200, 200), "RED"),
        ((255, 249, 240), "GRAY"),
        ((200, 100, 200), "PINK"),
        ((100, 200, 200), "CYAN"),
        ((200, 170, 100), "YELLOW"),  # skin tone
        ((0, 0, 250), "BLUE")])
    def test_get_color_for_pixel(self, pixel, expected_result):
        converter = FrameConverter(
            downsample_factor=10)
        assert converter.get_color_for_pixel(pixel) == expected_result
