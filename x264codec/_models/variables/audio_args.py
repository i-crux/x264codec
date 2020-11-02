AUDIO_SIMPLE_RATE = 44100       # -ar 选项,音频采样率,编码后为 44100hz

AAC_CODEC = 'libfdk_aac'        # -acodec 选项,音频编码器,可选 aac, libfdk_aac

"""
-profile:a 选项,音频编码版本,可选 aac_he_v2 acc_he aac_low
ffprobe 中获取的值:
- 'aac_low':    LC          aac 编解码器就可以,为了更好的(播放器)兼容性,128kbps
- 'aac_he':     HE-AAC      libfdk_aac 才可以  64kbps
- 'aac_he_v2':  HE-HE-AACv2 libfdk_aac 才可以  32kbps
"""
AAC_PROFILE = 'aac_he_v2'