import pytest
import random
from x264codec.x264codec import X264Codec


def test_snapshot():
    vh = X264Codec.from_format_video("tests/video_file/done_h.mp4")
    for _ in range(10):
        start = random.random() * 100
        height = random.randint(240, 480)
        jpg = vh.snapshot(start, height)
        print(f"===== start: {start}, height: {height} =====")
        print(jpg)
