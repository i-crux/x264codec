import pytest
from x264codec.x264codec import X264Codec


def test_add_ass():
    vh = X264Codec.from_format_video("tests/video_file/done_h.mp4")
    vv = X264Codec.from_format_video("tests/video_file/done_v.mp4")

    assert vh.add_ass('tests/video_file/ffmpeg-logo.png') is None
    assert vh.add_ass('tests/video_file/no.ass') is None
    assert vv.add_ass('tests/video_file/ffmpeg-logo.png') is None
    assert vv.add_ass('tests/video_file/no.ass') is None

    vh1 = vh.add_ass('tests/video_file/test.ass')
    vv1 = vv.add_ass('tests/video_file/test.ass')
    print("")
    print('============== vh1 ===============')
    print(vh1)
    print(vh1.bitrate)
    print(vh1.duration)
    print('============== vv1 ===============')
    print(vv1)
    print(vv1.bitrate)
    print(vv1.duration)
