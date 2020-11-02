import pytest
from x264codec.x264codec import X264Codec
from x264codec._models.variables.video_args import LogoType


def test_add_logo():
    vh = X264Codec.from_format_video("tests/video_file/done_h.mp4")
    vv = X264Codec.from_format_video("tests/video_file/done_v.mp4")

    assert vh.add_logo('tests/video_file/ffmpeg-logo.png', 2, LogoType.FIXED, 35, 35) is None
    assert vv.add_logo('tests/video_file/ffmpeg-logo.png', 2, LogoType.FIXED, 65, 65) is None
    assert vh.add_logo('tests/video_file/ffmpeg-logo.png', 2, LogoType.MOVED, 35, 35) is None
    assert vv.add_logo('tests/video_file/ffmpeg-logo.png', 2, LogoType.MOVED, 65, 65) is None

    assert vh.add_logo('tests/video_file/no-logo.png', 0.3, LogoType.FIXED, 35, 35) is None
    assert vh.add_logo('tests/video_file/no-logo.png', 0.25, LogoType.MOVED, ) is None
    assert vv.add_logo('tests/video_file/no-logo.png', 0.3, LogoType.FIXED, 65, 65) is None
    assert vv.add_logo('tests/video_file/no-logo.png', 0.25, LogoType.MOVED, ) is None

    vh1 = vh.add_logo('tests/video_file/ffmpeg-logo.png', 0.3)
    vh2 = vh.add_logo('tests/video_file/ffmpeg-logo.png', 0.25, LogoType.MOVED)
    vv1 = vv.add_logo('tests/video_file/ffmpeg-logo.png', 0.3, LogoType.FIXED, 65, 65)
    vv2 = vv.add_logo('tests/video_file/ffmpeg-logo.png', 0.25, LogoType.MOVED)

    print("")
    print('============== vh1 ===============')
    print(vh1)
    print(vh1.bitrate)
    print(vh1.duration)
    print('============== vh2 ===============')
    print(vh2)
    print(vh2.bitrate)
    print(vh2.duration)
    print('============== vv1 ===============')
    print(vv1)
    print(vv1.bitrate)
    print(vv1.duration)
    print('============== vv2 ===============')
    print(vv2)
    print(vv2.bitrate)
    print(vv2.duration)



