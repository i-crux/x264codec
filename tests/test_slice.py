import pytest
import random
from x264codec.x264codec import X264Codec


def test_slice():
    vh = X264Codec.from_format_video("tests/video_file/done_h.mp4")
    v1 = vh[179]
    print("")
    print(len(vh))
    print(v1)
    print(vh[11:20:10])
    print(vh[1:8:-10])
    vh2 = vh[::10]
    print(vh2)
    print(sum(vh2))
    print(vh[1:8:-6])