import tempfile
import os
import uuid
import numbers
from x264codec._models.classes import media_models
from x264codec._models.classes import media_attrs
from x264codec._models.utils import utils_video
from x264codec._models.utils import utils_common
from x264codec._models.variables import video_args as vargs
import x264codec._models.variables.ffmpeg_cmd as ffcmd


class X264Codec(media_attrs.VideoStreamInfo):
    filename = media_models.StrNonBlank()
    clearfile = media_models.Boolean()
    tmpfiles = media_models.TmpFileIter()   # 存放所有临时文件的集合

    def __init__(self, inpath: str, clearfile: bool = False):
        """
        这个类方法主要有如下作用:
        1.检查文件同时存在音视频流
        2.统一视频编码器为libx264, 像素格式为yuv420p, profile: v 为high, 分辨率为858x480, 最大码率为650kbps, 帧率24
        - 竖向视频, 则先左转90度, 变为横向视频再做出来
        - 分辨率比例不同时, 用黑边填充
        3.统一音频编码器为libfdk_aac, profile: a acc_he_v2, 采样率为44100hz
        :param inpath: 视频文件路径
        :param clearfile: 类被析构时是否删除 self.filename

        TODO: slice 视频截图(.jpg),视频片段截取(1s一个片段,.mp4) __getitem__
        """
        self.clearfile = clearfile
        width, height, bpf, _, _ = utils_video._ck_video(inpath)    # 检查输入视频文件
        if not all([width, height, bpf]):
            raise ValueError(f'{inpath} does not has video stream or audio stream.')
        tmp_outpath = f"{tempfile.mktemp(dir='/tmp')}.mp4"          # 转化为mp4时的临时输出文件
        self.tmpfiles = tmp_outpath                                 # 加入临时文件集合,以便集中处理
        if not utils_video._init_video2mp4(inpath, tmp_outpath):
            raise ValueError(f'{inpath} can not convert to mp4.')
        self.filename = f"{tempfile.mktemp(dir='/tmp')}.mp4"
        self.tmpfiles = self.filename                                   # 加入临时文件集合,以便集中处理
        # 格式化视频文件
        ret = utils_video._format_video(tmp_outpath, self.filename, width, height, bpf)
        if not ret:
            raise ValueError(f'{inpath} can not be formated.')
        self.tmpfiles.remove(self.filename)                             # 初始化成功,从临时文件集合中把 self.filename 删除
        _, _, _, self.bitrate, self.duration = utils_video._ck_video(self.filename)

    @classmethod
    def from_format_video(cls, inpath: str, clearfile: bool = False) -> 'X264Codec':
        """
        从符合格式要求的视频文件创建 X264Codec 对象,即像 __init__ 方法处理过的视频
        :param inpath: 视频文件路径
        :param clearfile: 类被析构时是否删除 self.filename
        :return: X264Codec 对象
        """
        obj = cls.__new__(cls)
        obj.clearfile = clearfile
        obj.filename = os.path.abspath(inpath)
        try:
            width, height, bpf, obj.bitrate, obj.duration = utils_video._ck_video(obj.filename)
        except ValueError:
            raise ValueError(f'{inpath} can not be initialize to {cls.__name__} object.')
        return obj

    @utils_video._x264operation_
    def add_logo(self, logo_imgpath: str, height_ratio: float, logo_type: vargs.LogoType = vargs.LogoType.FIXED,
                 pos_x: int = 35, pos_y: int = 35) -> 'X264Codec':
        """
        给视频添加水印
        :param logo_type: 水印类型, 固定位置或者移动水印
        :param logo_imgpath: 水印图片路径
        :param height_ratio: 水印高度占视频高度的比例,注意:水印宽度会等比例缩放
        :param pos_x: 水印在视频上x的坐标,注意:对于移动水印无意义
        :param pos_y: 水印在视频上y的坐标,注意:对于移动水印无意义
        :return: 新的 X264Codec 对象
        """

    @utils_video._x264operation_
    def add_ass(self, asspath: str) -> 'X264Codec':
        """
        添加ass字幕
        :param asspath: ass字幕路径
        :return: 新的 X264Codec 对象
        """

    @utils_video._x264operation_
    def del_logo(self, delogos: "list of vargs.delogo_args") -> 'X264Codec':
        """
        去除水印
        :param delogos: 去除水印参数的具名元祖列表
        :return: 新的 X264Codec 对象
        """

    @utils_video._x264operation_
    def cut_video(self, start: float, last: float) -> 'X264Codec':
        """
        裁剪视频
        :param start: 开始时间,单位秒
        :param last: 持续时间,单位秒
        :return: 新的 X264Codec 对象
        """

    @utils_video._x264operation_
    def down_bitrate(self, new_bitrate: int) -> 'X264Codec':
        """
        调低分辨率
        :param new_bitrate: 新的分辨率,100k - self.bitrate 之间的数
        :return: 新的 X264Codec 对象
        """

    def snapshot(self, start: float, height: int) -> str:
        """
        视频截图,从开始时间截取一帧作为图片
        :param start: 开始时间
        :param height: 图片高度(宽度等比缩放)
        :return: 成功: 图片路径 | 失败: None
        """
        try:
            if 0 <= start < self.duration and 0 < height <= vargs.VIDEO_HEIGHT:
                outpath = f"{tempfile.mktemp(dir='/tmp')}.jpg"  # 截图输出文件
                self.tmpfiles = outpath     # 加入临时文件集合,以便集中处理
                cmd = ffcmd.CMD_SNAPSHOT.format(inpath=self.filename, outpath=outpath,
                                                start=start, height=height)
                if utils_common._run_ffmpeg_cmd(cmd):
                    self.tmpfiles.remove(outpath)
                    return outpath
        except ValueError:
            pass

    def gif(self, start: float, last: float, height: int) -> str:
        """
        视频截图,从开始时间截取一帧作为图片
        :param start: 开始时间
        :param last: 持续时间,单位秒
        :param height: 图片高度(宽度等比缩放)
        :return: 成功: 图片路径 | 失败: None
        """
        try:
            if 0 < last <= self.duration and 0 <= start < self.duration - last \
                    and 0 < height <= vargs.VIDEO_HEIGHT:
                passlog_prefix = f"{tempfile.mktemp(dir='/tmp')}.png"
                self.tmpfiles = passlog_prefix  # 加入临时文件集合,以便集中处理
                outpath = f"{tempfile.mktemp(dir='/tmp')}.gif"  # gif 输出文件
                self.tmpfiles = outpath     # 加入临时文件集合,以便集中处理
                cmd = ffcmd.CMD_CREATEGIF.format(inpath=self.filename, outpath=outpath,
                                                 start=start, last=last, height=height,
                                                 passlog_prefix=passlog_prefix)
                if utils_common._run_ffmpeg_cmd(cmd):
                    self.tmpfiles.remove(outpath)
                    return outpath
        except ValueError:
            pass

    def hls(self, fixed: bool = False, encrypt: bool = False) -> str:
        """
        生成m3u8格式的文件
        :param fixed: 严格限制ts的时常
        :param encrypt: 是否加密
        :return: m3u8文件的所在的目录
        """
        fix_time = vargs.HLSTimeFixed.FIXED.value if fixed else vargs.HLSTimeFixed.NOFIXED.value
        encrypt_opts = utils_video._get_hls_enc_option() if encrypt else ''
        uuid_str = str(uuid.uuid1())
        output_dir = f'/tmp/{uuid_str}/ts'
        self.tmpfiles = output_dir
        ts_prefix = uuid_str
        outpath = f'/tmp/{uuid_str}/{uuid_str}.m3u8'
        # if not utils_common._run_ffmpeg_cmd(f'mkdir -pv {output_dir}'):
        #     return None
        try:
            cmd = ffcmd.CMD_HLS_VIDEO.format(
                inpath=self.filename, outpath=outpath, encrypt_opts=encrypt_opts,
                fix_time=fix_time, output_dir=output_dir, ts_prefix=ts_prefix
            )
            # print(cmd)
            if utils_common._run_ffmpeg_cmd(cmd):
                if utils_common._run_ffmpeg_cmd(f"sed -i s@/tmp/{uuid_str}/@@g {outpath}"):
                    self.tmpfiles.remove(output_dir)
                    return output_dir
        except ValueError:
            pass

    def move(self, newpath) -> bool:
        """
        将self.filename移动到newpath这个路径
        newpath 不能是目录, newpath必须以.mp4结尾
        :param newpath: self.filename 的新路径
        :return: 成功: True | 失败: False
        """
        newpath = os.path.abspath(newpath)
        if os.path.isdir(newpath):  # 新路径是目录
            return False
        if not newpath.endswith('.mp4'):    # 新路径不是.mp4结尾
            return False
        dir_path, file_path = os.path.split(newpath)
        if not utils_common._run_ffmpeg_cmd(f"mkdir -pv '{dir_path}'"):     # 创建新路径的目录
            return False
        if not utils_common._run_ffmpeg_cmd(f"mv -f '{self.filename}' '{newpath}'"):    # 移动文件
            return False
        self.filename = newpath
        return True

    def __repr__(self):
        return f'{self.__class__.__name__}({self.filename})'

    def __del__(self):
        if self.clearfile:      # 如果需要删除原文件,则删除
            utils_common._run_cmd(f"rm -rf '{self.filename}'")
        try:
            for tmpfile in self.tmpfiles:   # 这个属性有可能没被初始化
                utils_common._run_cmd(f"rm -rf '{tmpfile}'")
        except AttributeError:
            pass

    __str__ = __repr__

    def __len__(self):
        return int(self.duration)   # 视频长度(秒)

    def __add__(self, other: 'X264Codec'):
        """
        用于视频拼接
        """
        cls = self.__class__
        if not isinstance(other, cls):
            raise ValueError(f'{other} is not a instance of {cls.__name__}.')
        concat_file = f"{tempfile.mktemp(dir='/tmp')}.txt"
        self.tmpfiles = concat_file
        concat_file_contend = f"file '{self.filename}'\nfile '{other.filename}'\n"
        utils_common._write_file(concat_file, concat_file_contend)
        outpath = f"{tempfile.mktemp(dir='/tmp')}.mp4"  # 拼接后视频文件
        self.tmpfiles = outpath  # 加入临时文件集合,以便集中处理
        cmd = ffcmd.CMD_CONCAT_VIDEO_SAFE.format(concat_file=concat_file, outpath=outpath)
        if utils_common._run_ffmpeg_cmd(cmd):
            self.tmpfiles.remove(outpath)
            return self.__class__.from_format_video(outpath)
        else:
            raise OSError('can not add this two X264Video.')

    def __radd__(self, other):
        """
        定义这个完全是为了使用sum函数
        """
        cls = self.__class__
        if isinstance(other, cls):
            return other.__add__(self)
        else:
            return self

    def __getitem__(self, item):
        """
        - item是slice: 在slice中 start stop step 中的step和默认的有区别
          - 如果step是负数,则为截图操作,如 step = -7 则截7张图(高度240),返回一个[imgpath1,imgpath2,...], 其中imgpathX 就是图片路径
          - 如果step是正数,则原视频剪辑成step个1s长度的视频 [x264codec_obj1,x264codec_obj2,...],x264codec_objX为新的X264Codec对象
        - item是index: 返回1s长的视频的 x264codec_obj
        :param item: 可以是slice或者index
        :return:[list() of (str or x264codec_obj)] or x264codec_obj
        """
        cls = type(self)
        if isinstance(item, numbers.Integral):
            if item >= len(self) or item < 0:
                raise IndexError('Out range')
            return self.cut_video(item, 1)
        elif isinstance(item, slice):
            start, stop, step = item.indices(len(self))     # 这里 如果step == 0 的话,slice函数会抛出异常
            if start >= stop:
                return list()
            if abs(step) > stop - start:   # 调整 step 越界的情况
                step = 1 if step >= 0 else -1
            delta_time = (stop - start) / abs(step)
            cnt = abs(step)
            if step > 0:
                results = [self.cut_video(start + delta_time * i, 1) for i in range(cnt)]
            else:
                results = [self.snapshot(start + delta_time * i, 240) for i in range(cnt)]
            return [result for result in results if result is not None]
        else:
            msg = '{cls.__name__} indices must be integral'
            raise TypeError(msg.format(cls=cls))



