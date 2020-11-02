import pytest
import random
from x264codec.x264codec import X264Codec


def test_cut_video():
    vh = X264Codec.from_format_video("tests/video_file/done_h.mp4")
    for _ in range(10):
        start = random.random() * 100
        last = random.random() * 100
        vh1 = vh.cut_video(start, last)
        print(f"===== start: {start}, last: {last} =====")
        print(vh1)
        print(vh1.duration)
        print(vh1.bitrate)
