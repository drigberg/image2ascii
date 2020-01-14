import pytest

from image2ascii.video_converter import FrameConverter


class TestFrameConverter:
    @pytest.mark.parametrize("pixel,expected_tier", [
        ((0, 0, 0), 0),
        ((255, 255, 255), 5)])
    def test_get_ascii_for_pixel(self, pixel, expected_tier):
        converter = FrameConverter(
            downsample_factor=10)
        for i in range(10):
            char = converter.get_ascii_for_pixel(pixel)
            assert char in FrameConverter.ASCII_TIERS_BY_BRIGHTNESS[
                expected_tier]
