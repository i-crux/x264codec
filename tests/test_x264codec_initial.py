import pytest
from x264codec.x264codec import X264Codec


def test_x264codec_init():
    with pytest.raises(ValueError):
        X264Codec('no-this-file')
    video_h = X264Codec('tests/video_file/h.mp4')
    video_v = X264Codec('tests/video_file/v.mp4')
    print('============== video_h ===============')
    print(video_h)
    print(video_h.bitrate)
    print(video_h.duration)
    video_h.move("tests/video_file/done_h.mp4")
    print(video_h)
    print('============== video_v ===============')
    print(video_v)
    print(video_v.bitrate)
    print(video_v.duration)
    video_v.move("tests/video_file/done_v.mp4")
    print(video_v)


"""
if __name__ == '__main__':
    video1 = X264Codec('/root/out.mp4')
    print('============= video1 ================')
    print(video1)
    print(video1.bitrate)
    print(video1.duration)
    video2 = X264Codec.from_format_video('/tmp/tmpqs6hby7p.mp4')
    print('============= video2 ================')
    print(video2)
    print(video2.bitrate)
    print(video2.duration)
    video3 = video1.add_logo(vargs.LogoType.FIXED, '/root/ffmpeg-logo.png', 0.3, pos_x=65, pos_y=65)
    print('============= video3 ================')
    print(video3)
    video4 = X264Codec.from_format_video('/tmp/tmp6pm29zbq.mp4')
    print('============= video4 ================')
    print(video4)
    print(video4.bitrate)
    print(video4.duration)
    video5 = video4.add_logo(vargs.LogoType.MOVED, '/root/ffmpeg-logo.png', 0.25)
    print('============= video5 ================')
    print(video5)
    print(video5.bitrate)
    print(video5.duration)
"""