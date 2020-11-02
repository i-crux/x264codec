import x264codec._models.classes.media_models as md


class VideoStreamInfo(md.Entity):
    """
    视频流的信息
    """
    # stream_index = md.IntNotNegative()      # 在流中的索引 index, 将处理成 0
    bitrate = md.IntNotNegative()           # 码率,单位 kbps
    duration = md.FloatNotNegative()        # 视频长度


class AudioStreamInfo(md.Entity):
    """
    音频流的信息
    """
    # stream_index = md.IntNotNegative()      # 在流中的索引 index, 将处理成 1
    bitrate = md.IntNotNegative()           # 码率,单位 kbps
    duration = md.FloatNotNegative()        # 视频长度