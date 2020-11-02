"""
视频相关工具函数
"""
import os
import json
import time
import tempfile
import random
import functools
from numbers import Integral
from x264codec._models.utils.utils_common import _run_cmd, _run_ffmpeg_cmd
import x264codec._models.variables.ffmpeg_cmd as ffcmd
import x264codec._models.utils.utils_common as utilscomm
import x264codec._models.variables.video_args as vargs
import x264codec._models.utils.utils_pics as utilspics

_video_handle_func = dict()


def _register_video_handle_(fn):
    _video_handle_func[fn.__name__] = fn
    return fn


def _x264operation_(fn):
    """
    本装饰器用于对视频文件处理的固有流程
    创建临时文件的名字 --> 加入临时文件列表 --> 执行成功从临时文件列表中删除该项
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        outpath = f"{tempfile.mktemp(dir='/tmp')}.mp4"  # 添加水印的输出文件
        self = args[0]
        self.tmpfiles = outpath  # 加入临时文件集合,以便集中处理
        args = list(args)[1:]   # 去掉 self
        func = _video_handle_func[f'_{fn.__name__}']    # 获取处理函数
        br = int(round(self.bitrate / 1000))
        br = br if br < vargs.VIDEO_BIT_RATE else vargs.VIDEO_BIT_RATE
        ret = func(self.filename, outpath, br, *args, **kwargs)
        if ret:
            self.tmpfiles.remove(outpath)  # 添加水印成功,从临时文件中删除文件
            return self.__class__.from_format_video(outpath)
        return None
    return wrapper


@utilscomm._deal_value_error
def _run_video2h264_cmd(inpath: str, inimgs: str, outpath: str, filter_opts: str, vbitrate: int) -> bool:
    """
    执行 ffcmd.CMD_VIDEO2H264 命令
    :param inpath: 输入文件路径
    :param inimgs: 输入图片路参数
    :param outpath: 输出文件路径
    :param filter_opts: 过滤器参数
    :param vbitrate: 视频码率
    :return: 命令执行成功: True | 失败: False
    """
    passlog_prefix = f'/tmp/ffmpeg2passlog.{time.time()}.{os.path.split(tempfile.mktemp())[1]}'
    cmd = ffcmd.CMD_VIDEO2H264.format(
        inpath=inpath, inimgs=inimgs, outpath=outpath, passlog_prefix=passlog_prefix,
        filter_opts=filter_opts, vbitrate=vbitrate,
    )
    # print(cmd)
    ret = _run_ffmpeg_cmd(cmd)              # 执行 ffmpeg 命令
    _run_cmd(f'rm -rf {passlog_prefix}*')   # 删除pass日志
    return ret


@utilscomm._deal_value_error
def _run_cutvideo_cmd(inpath: str, outpath: str, start: float, last: float) -> bool:
    """
    将视频从start处开始,裁剪到start+last处
    :param inpath: 输入文件路径
    :param outpath: 输出文件路径
    :param start: 开始时间
    :param last: 持续时间
    :return: 命令执行成功: True | 失败: False
    """
    cmd = ffcmd.CMD_CUTVIDEO.format(inpath=inpath, outpath=outpath, start=start, last=last)
    # print(cmd)
    return _run_ffmpeg_cmd(cmd)


def _get_pad_option(ori_w: Integral, ori_h: Integral,
                    tgt_w: Integral, tgt_h: Integral) -> str:
    """
    根据视频原高度,宽度和目标高度宽度,来获取视频缩放选项
    :param ori_h: 原视频高度
    :param ori_w: 原视频宽带
    :param tgt_h: 目标高度
    :param tgt_w: 目标宽度
    :return: 频缩放选项字符串
    """
    # 视频缩放选项的基础参数
    opts_vf = r'-vf "scale={target_width:d}:{target_height:d}{pad_options:s}"'
    # 视频填充时的参数
    # 左右填充的参数
    opts_pad_lr = r",pad={target_width:d}:{target_height:d}:({target_width:d}-iw)/2:0:black"
    # 上下填充的参数
    opts_pad_ud = r",pad={target_width:d}:{target_height:d}:0:({target_height:d}-ih)/2:black"
    if ori_h == tgt_h and ori_w == tgt_w:
        return ''
    # 判断视频的宽高比
    # 计算目标视频宽高比,保留2位小数
    target_whratio = round(float(tgt_w) / float(tgt_h), 2)
    # 计算原视频宽高比,保留2位小数
    origin_whratio = round(float(ori_w) / float(ori_h), 2)
    # 计算原目标视频比例和原视频比例的差值
    diff = round(target_whratio - origin_whratio, 2)
    # 根据宽高比生成不同的命令
    if abs(diff) <= 0.01:
        # 缩放长宽比相同,两者之间的差值小于 0.01 视为相等
        pad_options = ''
    elif diff > 0.01:
        # 缩放后视频的宽度比原视频宽,需要在缩放后的视频两边填充黑边
        pad_options = opts_pad_lr.format(
            target_width=tgt_w,
            target_height=tgt_h,
        )
        # 修正目标宽
        tgt_w = int(round(tgt_h * origin_whratio, 0))
        tgt_w = int(int(tgt_w / 2) * 2)
    else:
        # 缩放后视频的高度比原视频高,需要在缩放后的视频上下填充黑边
        pad_options = opts_pad_ud.format(
            target_width=tgt_w,
            target_height=tgt_h,
        )
        # 修正目标高
        tgt_h = int(round(tgt_w / origin_whratio, 0))
        tgt_h = int(int(tgt_h / 2) * 2)

    return opts_vf.format(
        target_width=tgt_w,
        target_height=tgt_h,
        pad_options=pad_options
    )


@utilscomm._filepath_()
def _get_fixed_logo_option(inpath: str, height_ratio: float, pos_x: int, pos_y: int) -> tuple:
    """
    生成 ffcmd.CMD_VIDEO2H264 中的 inimgs 和 filter_opts 的字符串
    :param inpath: 水印图片路径
    :param height_ratio: 水印高度占视频高度的比例,注意:水印宽度会等比例缩放
    :param pos_x: 水印在视频上x的坐标
    :param pos_y: 水印在视频上y的坐标
    :return: 成功: inimgs, filter_opts | 失败: None, None
    """
    imgwidth, imgheight = utilspics._get_pic_wh(inpath)
    if not all([imgwidth, imgheight]):  # 检查图片是否有效
        return None, None
    _, theight = utilspics._computer_height(height_ratio, imgwidth, imgheight, pos_x, pos_y)
    if not theight:
        return None, None
    filter_opts = f'-filter_complex "[1:v]scale=-2:{theight}[ovrl],[0:v][ovrl]overlay={pos_x}:{pos_y}"'
    inimgs = f'-i {inpath}'
    return inimgs, filter_opts


@utilscomm._filepath_()
def _get_moved_logo_option(inpath: str, height_ratio: float) -> tuple:
    """
    生成 ffcmd.CMD_VIDEO2H264 中的 inimgs 和 filter_opts 的字符串
    :param inpath: 水印图片路径
    :param height_ratio: 水印高度占视频高度的比例,注意:水印宽度会等比例缩放
    :return: 成功: inimgs, filter_opts | 失败: None, None
    """
    imgwidth, imgheight = utilspics._get_pic_wh(inpath)
    if not all([imgwidth, imgheight]):  # 检查图片是否有效
        return None, None
    twidth, theight = utilspics._computer_height(height_ratio, imgwidth, imgheight, 0, 0)
    if not all([twidth, theight]):
        return None, None
    # 移动水印
    ST = random.randint(30, 60)     # 水印暂停的时间间隔
    TT = ST * 3 + 6                 # 移动水印一个循环的总时间
    LX = utilspics._computer_LX(twidth, vargs.VIDEO_WIDTH)
    MX = utilspics._computer_MX(twidth, vargs.VIDEO_WIDTH)
    RX = utilspics._computer_RX(twidth, vargs.VIDEO_WIDTH)
    LY = utilspics._computer_LY(theight, vargs.VIDEO_HEIGHT)
    MY = utilspics._computer_MY(theight, vargs.VIDEO_HEIGHT)
    inimgs = f"-i '{inpath}' -i '{inpath}' -i '{inpath}' -i '{inpath}' -i '{inpath}' -i '{inpath}'"
    filter_opts = f'-filter_complex "[1]scale=-2:{theight:d}[img1];'\
                  f"[0][img1]overlay=x='if(between(mod(t,{TT:d}),0,{ST:d}),{LX:d},NAN)':y={LY:d}[ovrl1]," \
                  f"[2]scale=-2:{theight:d}[img2];"\
                  f"[ovrl1][img2]overlay=x='if(between(mod(t,{TT:d}),{ST:d},{ST:d}+2)," \
                  f"{LX:d}+(({MX:d}-{LX:d})/2)*(mod(t,{TT:d})-{ST:d}),NAN)':" \
                  f"y='{LY:d}+(({MY:d}-{LY:d})/2)*(mod(t,{TT:d})-{ST:d})'[ovrl2]," \
                  f"[3]scale=-2:{theight:d}[img3];"\
                  f"[ovrl2][img3]overlay=x='if(between(mod(t,{TT:d}),{ST:d}+2,{ST:d}*2+2),{MX:d},NAN)':"\
                  f"y={MY:d}[ovrl3],[4]scale=-2:{theight:d}[img4];"\
                  f"[ovrl3][img4]overlay=x='if(between(mod(t,{TT:d}),{ST:d}*2+2,{ST:d}*2+4)," \
                  f"{MX:d}+(({RX:d}-{MX:d})/2)*(mod(t,{TT:d})-(({ST:d}*2)+2)),NAN)':" \
                  f"y='{MY:d}-(({MY:d}-{LY:d})/2)*(mod(t,{TT:d})-(({ST:d}*2)+2))'[ovrl4]," \
                  f"[5]scale=-2:{theight:d}[img5];"\
                  f"[ovrl4][img5]overlay=x='if(between(mod(t,{TT:d}),{ST:d}*2+4,{ST:d}*3+4),{RX:d},NAN)':"\
                  f"y={LY:d}[ovrl5],[6]scale=-2:{theight:d}[img6];"\
                  f"[ovrl5][img6]overlay=x='if(between(mod(t,{TT:d}),{ST:d}*3+4,{ST:d}*3+6)," \
                  f"{RX:d}-(({RX:d}-{LX:d})/2)*(mod(t,{TT:d})-(({ST:d}*3)+4)),NAN)':y={LY:d}\""
    return inimgs, filter_opts


@utilscomm._filepath_()
def _get_ass_option(inpath: str) -> str:
    """
    生成 ffcmd.CMD_VIDEO2H264 中的 filter_opts 的字符串用于添加ass字幕
    :param inpath: ass 字幕文件路径
    :return: filter_opts 字符串
    """
    if not os.path.exists(inpath):
        return None
    filter_opts = f'-vf "ass=\'{inpath}\'"'
    return filter_opts


def _get_delogo_option(delogos: "list of vargs.delogo_args") -> str:
    """
    处理去除水印参数,如果参数有明显越界,返回''空字符串
    :param delogos: 去除水印参数的具名元祖列表
    :return: 返回去除水印选项的字符串
    """
    delopt = r"delogo=x={X:d}:y={Y:d}:w={width:d}:h={height:d}:enable='between(t,{start:d},{end:d})'"
    delopts = list()

    for delogo in delogos:
        # 以下检查删除水印的参数是否合法
        if 0 <= delogo.start < delogo.end and 0 < delogo.width <= vargs.VIDEO_WIDTH and \
           0 < delogo.height <= vargs.VIDEO_HEIGHT and 0 <= delogo.pos_x <= vargs.VIDEO_WIDTH - delogo.width and \
           0 <= delogo.pos_y <= vargs.VIDEO_HEIGHT - delogo.height:
            delopts.append(delopt.format(X=delogo.pos_x, Y=delogo.pos_y, width=delogo.width, height=delogo.height,
                                         start=delogo.start, end=delogo.end))
    if delopts:
        return f'-vf "{",".join(delopts)}"'
    return None


def _get_hls_enc_option() -> str:
    """
    获取 hls 加密选项字符串
    :return: hls 加密选项字符串
    """
    encrypt_opts = r"-hls_enc 1 -hls_enc_key {enc_key:s} -hls_enc_iv {enc_iv:s}"
    enc_key_seed = '0123456789abcdef'
    enc_key = ''.join([random.choice(enc_key_seed) for _ in range(32)])
    enc_iv = ''.join([random.choice(enc_key_seed) for _ in range(32)])
    return encrypt_opts.format(enc_key=enc_key, enc_iv=enc_iv)


def _get_bpf(fps: int, br: int) -> float:
    """
    根据帧率,码率获取每帧素数据量,单位和码率相同
    :param fps: 帧率
    :param br:码率
    :return: 每帧数据量
    """
    return round(br / fps, 4)


def _get_br(fps: int, bpf: float) -> int:
    """
    根据帧率,每帧数据量获取码率,单位kbps
    :param fps: 帧率
    :param bpf: 每帧数据量
    :return: 码率,单位kbps
    """
    return int(round(bpf * fps / 1000))


@utilscomm._filepath_()
def _ck_video(inpath: str) -> tuple:
    """
    检查视频文件是否合规,至少有一路视频流和一路音频流
    :param inpath: 视频文件
    :return: 合规: 视频的宽,视频的高,视频每帧数据量,码率,视频长度 | 不合规 None, None, None, None, None
    """
    width = None
    height = None
    bpp = None
    has_video = False
    has_audio = False
    # 获取多媒体文件的元数据
    status, stdout, stderr = _run_cmd(ffcmd.CMD_GET_META.format(inpath=inpath))
    if status != 0:     # 命令执行失败
        return None, None, None, None, None
    try:
        video_attr = json.loads(stdout)     # 从json中获取视频元数据到字典中
    except json.decoder.JSONDecodeError:
        return None, None, None, None, None
    else:
        try:
            # 以下检查音视频流是否齐全
            for stream in video_attr['streams']:
                if stream['codec_type'] == 'video':
                    has_video = True
                    width = int(stream['width'])
                    height = int(stream['height'])
                    br = int(stream['bit_rate'])    # 码率
                    duration = round(float(stream['duration']), 2)  # 视频长度
                    # 以下计算视频帧率
                    fps_list = stream['r_frame_rate'].split('/')
                    if len(fps_list) == 1:
                        fps_list[1] = '1'
                    fps_list = [int(i) for i in fps_list]
                    fps = int(round(fps_list[0]/fps_list[1]))
                    if not all((width, height, br, fps, duration)):
                        return None, None, None, None, None
                    bpf = _get_bpf(fps, br)
                elif stream['codec_type'] == 'audio':
                    has_audio = True
            if not all((has_video, has_audio)):
                return None, None, None, None, None
        except KeyError:
            return None, None, None, None, None
    return width, height, bpf, br, duration


@utilscomm._filepath_('.mp4')
def _init_video2mp4(inpath: str, outpath: str) -> bool:
    """
    将视频容器格式转化为mp4,并去除旋转元数据,统一视频流的index == 0, 音频流的index == 1
    并且会去掉字幕流
    :param inpath: 视频输入文件
    :param outpath: 视频输出文件
    :return: 成功: True| 失败: False
    """
    return _run_ffmpeg_cmd(ffcmd.CMD_CH_VIDEO_META.format(inpath=inpath, outpath=outpath))


@utilscomm._filepath_('.mp4')
def _format_video(inpath: str, outpath: str, width: int, height: int, bpf: float) -> bool:
    """
    统一多媒体文件的格式: 视频编码:h264, 24fps, 650k以下; 音频编码:aac, aac_he_v2, 44100hz, 2 channels
    :param inpath: 输入文件路径
    :param outpath: 输出文件路径
    :param width: 输入文件宽
    :param height: 输入文件高
    :param bpf: 输入文件每帧数据量
    :return: 成功: True | 失败: False
    """
    br = _get_br(vargs.VIDEO_FPS, bpf)
    br = br if br < vargs.VIDEO_BIT_RATE else vargs.VIDEO_BIT_RATE
    filter_opts = _get_pad_option(width, height, vargs.VIDEO_WIDTH, vargs.VIDEO_HEIGHT)
    return _run_video2h264_cmd(inpath, '', outpath, filter_opts, br)


@_register_video_handle_
@utilscomm._filepath_('.mp4')
def _add_logo(inpath: str, outpath: str, br: int,
              logo_imgpath: str, height_ratio: float,
              logo_type: vargs.LogoType = vargs.LogoType.FIXED,
              pos_x: int = 35, pos_y: int = 35) -> bool:
    """
    给视频加水印
    :param inpath: 输入文件路径
    :param outpath: 输出文件路径
    :param br: 视频码率
    :param logo_type: 水印类型, 固定位置或者移动水印
    :param logo_imgpath: 水印图片路径
    :param height_ratio: 水印高度占视频高度的比例,注意:水印宽度会等比例缩放
    :param pos_x: 水印在视频上x的坐标,注意:对于移动水印无意义
    :param pos_y: 水印在视频上y的坐标,注意:对于移动水印无意义
    :return: 成功: True | 失败: False
    """
    if logo_type == vargs.LogoType.FIXED:
        inimgs, filter_opts = _get_fixed_logo_option(logo_imgpath, height_ratio, pos_x, pos_y)
    elif logo_type == vargs.LogoType.MOVED:
        inimgs, filter_opts = _get_moved_logo_option(logo_imgpath, height_ratio)
    else:
        return False
    if not all([inimgs, filter_opts]):
        return False
    return _run_video2h264_cmd(inpath, inimgs, outpath, filter_opts, br)


@_register_video_handle_
@utilscomm._filepath_('.mp4')
def _add_ass(inpath: str, outpath: str, br: int, asspath: str) -> bool:
    """
    给视频添加ass字幕
    :param inpath: 输入文件路径
    :param outpath: 输出文件路径
    :param br: 视频码率
    :param asspath: ass字幕文件路径
    :return: 成功: True | 失败: False
    """
    filter_opts = _get_ass_option(asspath)
    if filter_opts is None:
        return False
    return _run_video2h264_cmd(inpath, '', outpath, filter_opts, br)


@_register_video_handle_
@utilscomm._filepath_('.mp4')
def _del_logo(inpath: str, outpath: str, br: int, delogos: "list of vargs.delogo_args") -> bool:
    """
    给视频添加ass字幕
    :param inpath: 输入文件路径
    :param outpath: 输出文件路径
    :param br: 视频码率
    :param delogos: 去除水印参数的具名元祖列表
    :return: 成功: True | 失败: False
    """
    filter_opts = _get_delogo_option(delogos)
    if filter_opts is None:
        return False
    return _run_video2h264_cmd(inpath, '', outpath, filter_opts, br)


@_register_video_handle_
@utilscomm._filepath_('.mp4')
def _cut_video(inpath: str, outpath: str, _: int, start: float, last: float) -> bool:
    """
    裁剪视频的长度
    :param inpath: 输入文件路径
    :param outpath: 输出文件路径
    :param _: 占为符
    :param start: 开始时间
    :param last: 持续时间
    :return: 成功: True | 失败: False
    """
    return _run_cutvideo_cmd(inpath, outpath, start, last)


@_register_video_handle_
@utilscomm._filepath_('.mp4')
def _down_bitrate(inpath: str, outpath: str, br: int, new_bitrate: int) -> bool:
    """
    降低视频码率
    :param inpath: 输入文件路径
    :param outpath: 输出文件路径
    :param br: 视频码率
    :param new_bitrate: 新的分辨率,150k - self.bitrate 之间的数
    :return: 成功: True | 失败: False
    """
    if 100 <= new_bitrate < br:
        return _run_video2h264_cmd(inpath, '', outpath, '', new_bitrate)
    return False
