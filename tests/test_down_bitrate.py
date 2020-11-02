import pytest
import random
from x264codec.x264codec import X264Codec


def test_down_bitrate():
    vh = X264Codec.from_format_video("tests/video_file/done_h.mp4")
    new_bitrate = random.randint(150, 650)
    print("")
    print(f"======= bitrate: {new_bitrate} =========")

    vh1 = vh.down_bitrate(new_bitrate)
    print(vh1)
    print(vh1.duration)
    print(vh1.bitrate)
