import pytest
from random import randint as ri
from x264codec.x264codec import X264Codec
import x264codec._models.variables.video_args as vargs


def test_del_logo():
    vh = X264Codec.from_format_video("tests/video_file/done_h.mp4")
    delogos = [
        vargs.delogo_args(
            ri(0, vargs.VIDEO_WIDTH),
            ri(0, vargs.VIDEO_HEIGHT),
            ri(0, vargs.VIDEO_WIDTH),
            ri(0, vargs.VIDEO_HEIGHT),
            ri(0, 90),
            ri(45, 180)
        )
        for _ in range(10)
    ]
    print("")
    vh1 = vh.del_logo(delogos)
    print(vh1)
    print(vh1.bitrate)
    print(vh1.duration)
