import enum
from collections import namedtuple

"""
-preset 选项
调整编码速度,越慢编码质量越高
ultrafast,superfast,veryfast,faster,fast,medium,slow,slower,veryslow and placebo-这个太慢了,不实用
目前发现在新版的ffmpeg中,如果使用 h264_nvenc 编解码器,且带上 -preset 参数的话,则会报错
"""
H264_PRESET = '-preset veryslow'

"""
-crf 选项
CRF(Constant Rate Factor)
范围 0-51, 相对合理的区间是18-28:
- 0是编码毫无丢失信息
- 23 is 默认
- 51 是最差的情况
值越大,压缩效率越高,但也意味着信息丢失越严重,输出图像质量越差.crf每+6比特率减半;crf每-6比特率翻倍
"""
H264_CRF = 23

H264_CODEC = 'libx264'  # -vcodec 选项. 可选值 libx264 h264_qsv h264_nvenc

VIDEO_FPS = 24      # -r 选项,视频帧率

GIT_FPS = 5         # -r 选项,GIF图片帧率

HLS_TS_TIME = 8     # 8秒的 hls 切片时长


class HLSTimeFixed(enum.Enum):
    FIXED = '+split_by_time'
    NOFIXED = ''


"""
-g 选项,GOP的间隔
GOP96 = '96'    # 24fps ts长度4s时
GOP120 = '120'  # 30fps ts长度4s时
GOP192 = '192'  # 24fps ts长度8s时
GOP240 = '240'  # 30fps ts长度8s时 或者 24fps ts长度10s时
GOP300 = '300'  # 30fps ts长度10s时
"""
H264_GOP = VIDEO_FPS * HLS_TS_TIME

"""
-keyint_min 选项, 最小GOP的间隔
min_gop24 = '24'    # 24fps
min_gop30 = '30'    # 30fps
"""
H264_MIN_GOP = VIDEO_FPS

"""
-profile:v 选项
profile 参数 H.264 Baseline profile,Extended profile和Main profile都是针对8位样本数据,4:2:0格式(YUV)的视频序列
在相同配置情况下,High profile(HP)可以比Main profile(MP)降低10%的码率
根据应用领域的不同,Baseline profile多应用于实时通信领域,Main profile多应用于流媒体领域,High profile则多应用于广电和存储领域
constrained_baseline = 'baseline'   # 基本画质.支持I/P帧,只支持无交错(Progressive)和CAVLC
extended = 'extended'               # 进阶画质.支持I/P/B/SP/SI帧,只支持无交错(Progressive)和CAVLC  **ffmpeg 不支持**
main = 'main'                       # 主流画质.提供I/P/B帧,支持无交错(Progressive)和交错(Interlaced),也支持CAVLC和CABAC
high = 'high'                       # 高级画质.在main Profile的基础上增加了8x8内部预测,自定义量化,无损视频编码和更多的YUV格式
high10 = 'high10'                   # 不知道ffmpeg中是怎么支持的
high_422 = 'high422'                # "High 4:2:2", 像素格式需要使用 yuv422p
high_444_predictive = 'high444'     # "High 4:4:4 Predictive" 像素格式需要使用 yuv444p
"""
H264_PROFILE = 'high'

"""
-level 选项
level 参数定义可以使用的最大帧率,码率和分辨率
         level        max          max          max bitrate          max bitrate      high resolution
         number    macroblocks    frame      for profile baseline    for profile        @frame rate
                         per secs      size        extended main high         high
level_10 = '1'      #   1485         99             64 kbit/s           80 kbit/s         128x96@30.9
#                                                                     176x144@15.0
level_9 = '1b'      #   1485         99            128 kbit/s           160 kbit/s        128x96@30.9
#                                                                     176x144@15.0
level_11 = '1.1'    #   3000        396            192 kbit/s           240 kbit/s        176x144@30.3
#                                                                     320x240@10.0
#                                                                     352x288@7.5
level_12 = '1.2'    #   6000        396            384 kbit/s           480 kbit/s        320x240@20.0
#                                                                     352x288@15.2
level_13 = '1.3'    #   11880       396            768 kbit/s           960 kbit/s        320x240@36.0
#                                                                     352x288@30.0
level_20 = '2'      #   11880       396            2 Mbit/s             2.5 Mbit/s        320x240@36.0
#                                                                     352x288@30.0
level_21 = '2.1'    #   19880       792            4 Mbit/s             5 Mbit/s          352x480@30.0
#                                                                     352x576@25.0
level_22 = '2.2'    #   20250       1620           4 Mbit/s             5 Mbit/s          352x480@30.7
#                                                                     352x576@25.6
#                                                                     720x480@15.0
#                                                                     720x576@12.5
level_30 = '3'      #   40500       1620           10 Mbit/s            12.5 Mbit/s       352x480@61.4
#                                                                     352x576@51.1
#                                                                     720x480@30.0
#                                                                     720x576@25.0
level_31 = '3.1'    #   108000      3600           14 Mbit/s            17.5 Mbit/s       720x480@80.0
#                                                                     720x576@66.7
#                                                                     1280x720@30.0
level_32 = '3.2'    #   216000      5120           20 Mbit/s            25 Mbit/s         1280x720@60.0
#                                                                     1280x1024@42.2
level_40 = '4'      #   245760      8192           20 Mbit/s            25 Mbit/s         1280x720@68.3
#                                                                     1920x1088@30.1
#                                                                     2048x1024@30.0
level_41 = '4.1'    #   245760      8192           50 Mbit/s            50 Mbit/s         1280x720@68.3
#                                                                     1920x1088@30.1
#                                                                     2048x1024@30.00
level_42 = '4.2'    #   522240      8704           50 Mbit/s            50 Mbit/s         1280x1088@64.0
#                                                                     2048x1088@60.0
level_50 = '5'      #   589824      22080          135 Mbit/s           168.75 Mbit/s     1920x1088@72.3
#                                                                     2048x1024@72.0
#                                                                     2048x1088@67.8
#                                                                     2560x1920@30.7
#                                                                     3680x1536@26.7
level_51 = '5.1'    #   983040      36864          240 Mbit/s           300 Mbit/s        1920x1088@120.5
#                                                                     4096x2048@30.0
#                                                                     4096x2304@26.7
"""
H264_LEVEL = '4.2'

VIDEO_ROTATE = 2    # -vf 'transpose={}' 选项, 视频,2-左旋;1-右旋

VIDEO_PIXFMT = 'yuv420p'    # -pix_fmt 选项, 图片像素格式,其他可选 yuv420p yuv422p yuv444p

VIDEO_WIDTH = 858           # h264横向视频的目标高

VIDEO_HEIGHT = 480          # h264横向视频的目标宽

VIDEO_BIT_RATE = 650        # h264视频码率


class LogoType(enum.Enum):
    FIXED = 1
    MOVED = 2


"""
删除水印用的参数,多个 delogo_args 类型的值组成list,一次可以删除多个不同的水印
- pos_x: 水印的x轴的值
- pos_y: 水印的y轴的值
- width: 水印的宽
- height: 水印的高
- start: 水印出现的开始时间
- end: 水印的结束时间
"""
delogo_args = namedtuple('delogo_args', 'pos_x pos_y width height start end')




