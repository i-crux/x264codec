import x264codec._models.variables.com_args as com_args
import x264codec._models.variables.audio_args as audio_args
import x264codec._models.variables.video_args as video_args

"""
确认视频编码器符合要求
"""
CMD_ENSURE_VCODEC = f"'{com_args.FFMPEG}' -hide_banner -codecs | grep -E '^ DEV' | grep '{video_args.H264_CODEC}'"

"""
确认音频编码器符合要求
"""
CMD_ENSURE_ACODEC = f"'{com_args.FFMPEG}' -hide_banner -codecs | grep -E '^ DEA' | grep '{audio_args.AAC_CODEC}'"

"""
# 获取视频元数据,以json格式输出视频元信息
"""
CMD_GET_META = f"'{com_args.FFPROBE}' -v quiet -print_format json -show_format -show_streams" r" '{inpath:s}'"

"""
修改视频元数据 meta_key 为元数据的关键字, meta_value 为元数据的值
f"'{com_args.FFMPEG}' -hide_banner -y " r"-i '{inpath:s}' "
r"-metadata:s:v '{meta_key:s}'='{meta_value:s}' "
r"-c copy '{outpath:s}'"
但是我们只需要去除视频旋转的元数据,并将视频流的索引变为0,音频流的索引变为1
"""
CMD_CH_VIDEO_META = f"'{com_args.FFMPEG}' -hide_banner " r"-i '{inpath:s}' " \
                    r"-metadata:s:v 'rotate'='0' " \
                    r"-codec copy -map 0:v:0 -map 0:a:0 -y -f mp4 '{outpath:s}'"

"""
旋转视频,此命令未使用
"""
CMD_ROTATE_VIDEO = f"'{com_args.FFMPEG}' -hide_banner -i " r"'{inpath:s}' -y " \
                   f"-vf 'transpose={video_args.VIDEO_ROTATE}' -f mp4 " r"'{outpath}'"

"""
将视频编码为h264(libx264),音频编码为aac(libfdk_aac),要想准确控制bitrate(-b:v), 需要使用 -pass
-coder 1 CABAC 压缩算法; -bf b帧数量; -flags +loop -deblock -1:-1 使用去块滤波器
-partitions i4x4+i8x8+p8x8+b8x8 宏块的划分; -me_method umh 运动评估算法， 不均衡的六边形算法
"""
CMD_VIDEO2H264 = f"'{com_args.FFMPEG}' -hide_banner -f mp4 -i " r"'{inpath:s}' {inimgs} -threads 0 -y " \
                 r"-pass 1 -passlogfile {passlog_prefix:s} {filter_opts} " \
                 f"-vcodec {video_args.H264_CODEC} -coder 1 -movflags +faststart " \
                 f"{video_args.H264_PRESET} -crf {video_args.H264_CRF} "\
                 f"-pix_fmt {video_args.VIDEO_PIXFMT} -r {video_args.VIDEO_FPS} " \
                 f"-profile:v {video_args.H264_PROFILE} -level {video_args.H264_LEVEL} " \
                 f"-g {video_args.H264_GOP} -keyint_min {video_args.H264_MIN_GOP} " \
                 f"-bf {video_args.MAX_BFRAME} -flags +loop -deblock -1:-1 " \
                 r"-partitions i4x4+i8x8+p8x8+b8x8 -me_method umh " \
                 r"-b:v {vbitrate}k -an -f mp4 /dev/null && " \
                 f"'{com_args.FFMPEG}' -hide_banner -f mp4 -i " r"'{inpath:s}' {inimgs} -threads 0 -y " \
                 r"-pass 2 -passlogfile {passlog_prefix:s} {filter_opts} " \
                 f"-vcodec {video_args.H264_CODEC} -coder 1 -movflags +faststart " \
                 f"{video_args.H264_PRESET} -crf {video_args.H264_CRF} "\
                 f"-pix_fmt {video_args.VIDEO_PIXFMT} -r {video_args.VIDEO_FPS} " \
                 f"-profile:v {video_args.H264_PROFILE} -level {video_args.H264_LEVEL} " \
                 f"-g {video_args.H264_GOP} -keyint_min {video_args.H264_MIN_GOP} " \
                 f"-bf {video_args.MAX_BFRAME} -flags +loop -deblock -1:-1 " \
                 r"-partitions i4x4+i8x8+p8x8+b8x8 -me_method umh " \
                 r"-b:v {vbitrate}k " \
                 f"-acodec {audio_args.AAC_CODEC} -profile:a {audio_args.AAC_PROFILE} " \
                 f"-ar {audio_args.AUDIO_SIMPLE_RATE} -ac 2 " \
                 r"-f mp4 '{outpath:s}'"

"""
截图命令,截取一帧做为图片,仅输出 jpg 的图片
"""
CMD_SNAPSHOT = f"'{com_args.FFMPEG}' -hide_banner " r"-ss {start:f} -i '{inpath:s}' -threads 0 " \
               r"-vf 'scale=-2:{height:d}' -f image2 -vframes 1 -y '{outpath:s}'"

"""
视频裁剪命令
"""
CMD_CUTVIDEO = f"'{com_args.FFMPEG}' -hide_banner " r"-ss {start:f} -t {last:f} -i '{inpath:s}' -threads 0 " \
               r"-codec copy -f mp4 -y '{outpath:s}'"

"""
生成GIF
"""
CMD_CREATEGIF = f"'{com_args.FFMPEG}' -hide_banner " r"-ss {start:f} -t {last:f} -i '{inpath:s}' -threads 0 -an " \
                f"-vf 'fps={video_args.GIF_FPS}," \
                r"scale=-2:{height:d}:flags=lanczos,palettegen' -y '{passlog_prefix:s}' && " \
                f"'{com_args.FFMPEG}' -hide_banner " r"-ss {start:f} -t '{last:f}' -i '{inpath:s}' " \
                r"-i '{passlog_prefix:s}' -threads 0 -an -f gif " \
                f"-lavfi 'fps={video_args.GIF_FPS}," r"scale=-2:{height:d}:flags=lanczos[x];[x][1:v]paletteuse' " \
                r"-y '{outpath:s}'"

"""
# 视频拼接命令
# 有gpu转码的时候首选CMD_CONCAT_VIDEO命令,如果CMD_CONCAT_VIDEO失败则使用CMD_CONCAT_VIDEO_SAFE
# 没有gpu转码的时候选用CMD_CONCAT_VIDEO_SAFE
# CMD_CONCAT_VIDEO 能保证音轨同步, CMD_CONCAT_VIDEO_SAFE 拼接速度快
CMD_CONCAT_VIDEO = r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file1:s}' -i '{input_file2:s}' " \
                   r"-threads 0 -c:v {encode_lib:s} -pass 1 -an -f mp4 -movflags +faststart -passlogfile {prefix:s} " \
                   r"-filter_complex '[0:0] [0:1] [1:0] [1:1] concat=n=2:v=1:a=1 [v] [a]' -map '[v]' -map '[a]' " \
                   r" -g {frame:d} -r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                   r"-level {level:s} -b:v {video_rate:d}k /dev/null && " \
                   r"'{ffmpeg_bin:s}' -hide_banner -y -i '{input_file1:s}' -i '{input_file2:s}' " \
                   r"-threads 0 -c:v {encode_lib:s} -c:a aac -b:a {audio_rate:d}k -pass 2 -f mp4 " \
                   r"-movflags +faststart -passlogfile {prefix:s} " \
                   r"-filter_complex '[0:0] [0:1] [1:0] [1:1] concat=n=2:v=1:a=1 [v] [a]' -map '[v]' -map '[a]' " \
                   r"-g {frame:d} -r {frame:d} -preset {preset_type:s} -crf {crf_num:d} -profile:v {profile_type:s} " \
                   r"-level {level:s} -b:v {video_rate:d}k '{output_file:s}'"

concat_file 的格式:
file mediafile1
file mediafile2
"""
CMD_CONCAT_VIDEO_SAFE = f"'{com_args.FFMPEG}' -f concat -safe 0 " r"-i '{concat_file:s}' -codec copy '{outpath}'"

"""
HLS 切片命令
TODO: 加密用的参数
"""
CMD_HLS_VIDEO = f"'{com_args.FFMPEG}' -hide_banner " r"-i '{inpath:s}' -threads 0 " \
                f"-codec copy -hls_init_time {video_args.HLS_TS_TIME} -hls_time {video_args.HLS_TS_TIME} " \
                r"-hls_list_size 0 {encrypt_opts} -use_localtime 1 -hls_flags " \
                r"second_level_segment_size+second_level_segment_index+second_level_segment_duration{fix_time} " \
                r'-strftime 1 -strftime_mkdir 1 -f hls -y ' \
                r'-hls_segment_filename "{output_dir}/{ts_prefix:s}-%%013t-%%08s-%%010d.ts" ' \
                r"'{outpath:s}'"