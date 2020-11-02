import json
import random
import x264codec._models.utils.utils_common as utilscomm
import x264codec._models.variables.ffmpeg_cmd as ffcmd
from x264codec._models.utils.utils_common import _run_cmd
import x264codec._models.variables.video_args as vargs


@utilscomm._filepath_()
def _get_pic_wh(inpath: str) -> tuple:
    """
    获取图片宽高
    :param inpath:
    :return:
    """
    width = None
    height = None
    status, stdout, _ = _run_cmd(ffcmd.CMD_GET_META.format(inpath=inpath))
    if status != 0:
        return None, None
    try:
        video_attr = json.loads(stdout)     # 从json中获取视频元数据到字典中
    except json.decoder.JSONDecodeError:
        return None, None
    else:
        try:
            # 以下检查图片中是否有视频流视频流
            for stream in video_attr['streams']:
                if stream['codec_type'] == 'video':
                    width = int(stream['width'])
                    height = int(stream['height'])
            if not all((width, height)):
                return None, None
        except KeyError:
            return None, None
    return width, height


def _computer_height(ratio: float, imgwidth: int, imgheight: int, pos_x: int, pos_y: int) -> tuple:
    """
    根据图片的高宽和图片的高占视频高的比例,计算图片的目标高度
    :param ratio: 水印高度占视频高度的比例,注意:水印宽度会等比例缩放
    :param imgwidth: 图片原始宽度
    :param imgheight: 图片原始高度
    :param pos_x: 水印在视频上x的坐标,通过计算后如果图片越界将使函数返回None
    :param pos_y: 水印在视频上y的坐标,通过计算后如果图片越界将使函数返回None
    :return: 成功返回 图片的目标宽度度,图片的目标高度 | 否则返回:0,0
    """
    if not 0.0 < ratio < 1.0:   # 检查比例是否正常
        return 0, 0
    if not all([imgheight > 0, imgwidth > 0]):  # 检查输入图片的宽高是否正常
        return 0, 0
    if not (0 <= pos_x < vargs.VIDEO_WIDTH and 0 <= pos_y < vargs.VIDEO_HEIGHT):    # 检查x或y是否越界
        return 0, 0
    theight = int(vargs.VIDEO_HEIGHT * ratio)                     # 计算图片目标高度
    twidth = int(theight * (imgwidth / imgheight))      # 图片目标宽度
    if pos_x + twidth > vargs.VIDEO_WIDTH or pos_y + theight > vargs.VIDEO_HEIGHT:  # 检查目标宽高是否越界
        return 0, 0
    return twidth, theight


def _computer_LX(img_w: int, video_w: int) -> int:
    """
    通过图片宽度和视频宽度计算水印的起始x轴位置
    :param img_w: 图片宽度
    :param video_w: 视频宽度
    :return: 水印起始x轴位置
    """
    LX_low = 30 if img_w + 30 <= video_w else 0
    LX_high = 100 if img_w + 100 <= video_w else \
        ((video_w - img_w) // 4)
    if LX_low > LX_high:
        LX_low = LX_high // 8
    return random.randint(LX_low, LX_high)


def _computer_LY(img_h: int, video_h: int) -> int:
    """
    通过图片高度和视频高度计算水印的起始y轴位置
    :param img_h: 图片高度
    :param video_h: 视频高度
    :return: 水印起始y轴位置
    """
    LY_low = 30 if img_h + 30 <= video_h else 0
    LY_high = 50 if img_h + 50 <= video_h else \
        ((video_h - img_h) // 4)
    if LY_low > LY_high:
        LY_low = LY_high // 8
    return random.randint(LY_low, LY_high)


def _computer_MX(img_w: int, video_w: int) -> int:
    """
    通过图片高度和视频高度计算水印的中部x轴位置
    :param img_w: 图片宽度
    :param video_w: 视频宽度
    :return: 水印中部x轴位置
    """
    i = 0
    while True:
        mid_width = (video_w // 2) - (img_w // (2 ** i))
        if mid_width >= 0:
            break
        i += 1
    i = 0
    while True:
        MX_low = mid_width - 100 // (2 ** i)
        if MX_low >= 0:
            break
        i += 1
    i = 0
    while True:
        MX_high = mid_width + 100 // (2 ** i)
        if MX_high + img_w <= video_w:
            break
        i += 1
    if MX_low > MX_high:
        MX_low = MX_high // 4
    return random.randint(MX_low, MX_high)


def _computer_MY(img_h: int, video_h: int) -> int:
    """
    通过图片高度和视频高度计算水印的中部x轴位置
    :param img_h: 图片高度
    :param video_h: 视频高度
    :return: 水印中部x轴位置
    """
    MY_low = (video_h - 150) if img_h <= 150 and video_h - 150 >= 0 else ((video_h - img_h) // 4)
    MY_high = (video_h - 80) if img_h <= 80 and video_h - 80 >= 0 else (video_h - img_h)
    if MY_low > MY_high:
        MY_low = MY_high // 4
    return random.randint(MY_low, MY_high)


def _computer_RX(img_w: int, video_w: int) -> int:
    RX_low = (video_w - img_w - 100) if video_w >= img_w + 100 else ((video_w - img_w) // 2)
    RX_high = (video_w - img_w - 20) if video_w >= img_w + 20 else (video_w - img_w)
    if RX_low > RX_high:
        RX_low = RX_high // 2
    return random.randint(RX_low, RX_high)
