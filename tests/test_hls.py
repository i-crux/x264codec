import pytest
import random
from x264codec.x264codec import X264Codec


def test_hls():
    vh = X264Codec.from_format_video("tests/video_file/done_h.mp4")
    print('')
    print(vh.hls(True, True))
    print(vh.hls(encrypt=True))
    print(vh.hls())
