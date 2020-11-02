import pytest
import random
from x264codec.x264codec import X264Codec


def test_add_videos():
    vh = X264Codec.from_format_video("tests/video_file/done_h.mp4")
    vv = X264Codec.from_format_video("tests/video_file/done_v.mp4")

    vs = [vh, vv]
    v1 = vh+vv
    for _ in range(random.randint(3, 10)):
        v1 += vs[random.randint(0, 1)]
    print("")
    print(v1)
    print(v1.bitrate)
    print(v1.duration)
