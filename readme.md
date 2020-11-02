[TOC]

**请确保你的ffmpeg程序支持 libfdk_aac ass libx264, 具体安装方法可参照附录**

# 模块安装
进入代码目录执行
```shell script
python setup.py sdist
python setup.py install
```

# 测试
```shell script
pip install pytest
# 进入代码目录执行
pytest -s -v
```

# 使用简介
## 导入模块
```python
from x264codec.x264codec import X264Codec
```

## 对象初始化
```python
from x264codec.x264codec import X264Codec
v = X264Codec('path/to/video_file')
```

X264Codec 类初始化时,会将视频的格式统一为:
- mp4容器格式
- 视频编码: h264
- 音频编码: aac_he_v2
- 视频分辨率: 858x480
- 视频帧率: 24帧
- 视频码率: 650k
**以上个数值可以在 x264codec._models.variables.video_args 修改**
```python
VIDEO_WIDTH = 858           # h264横向视频的目标高

VIDEO_HEIGHT = 480          # h264横向视频的目标宽

VIDEO_BIT_RATE = 650        # h264视频码率
```

## 重命名以初始化的视频
```python
from x264codec.x264codec import X264Codec
v = X264Codec('path/to/video_file')
v.move("new_path")
```

## 降低视频码率
```python
from x264codec.x264codec import X264Codec
v = X264Codec('path/to/video_file')
v1 = v.down_bitrate(350)    # 将码率降低到 350k, v1 为新的 X264Codec 对象
```

## 视频添加ass字幕
```python
from x264codec.x264codec import X264Codec
v = X264Codec('path/to/video_file')
v1 = v.add_ass('path/to/ass_file')  # v1 为新的 X264Codec 对象
```

## 视频添加图片水印
```python
from x264codec.x264codec import X264Codec
from x264codec._models.variables import video_args as vargs
v = X264Codec('path/to/video_file')
v1 = v.add_logo(
    'path/to/logo_image', 
    0.3, vargs.LogoType.FIXED, pos_x=10, pos_y=20
)  # v1 为新的 X264Codec 对象, 添加固定位置水印

v2 = v.add_logo(
    'path/to/logo_image', 
    0.3, vargs.LogoType.MOVED
)  # v2 为新的 X264Codec 对象, 添加移动水印
```

## 视频拼接
```python
from x264codec.x264codec import X264Codec
v1 = X264Codec('path/to/video_file1')
v2 = X264Codec('path/to/video_file2')
v3 = v1+v2  # v3 为新的 X264Codec对象
```

## 创建gif图片
```python
from x264codec.x264codec import X264Codec
v = X264Codec('path/to/video_file1')
gif_path = v.gif(10, 5, 320) # 生产从视频第10秒开始,持续5秒,高为 320 的 gif
```

## 裁剪视频长度
```python
from x264codec.x264codec import X264Codec
v = X264Codec('path/to/video_file1')
v1 = v.cut_video(10, 100) # v1 为新的 X264Codec 对象, 里面的视频为原视频 10秒开始,持续100秒的视频
```

## 删除水印
```python
from x264codec.x264codec import X264Codec
from x264codec._models.variables import video_args as vargs
delogos = []
# 这里假设视频有两处水印
# 第一处: x:10, y:20, 宽:100, 高:20, 开始时间5s, 结束时间 30s
delogos.append(vargs.delogo_args(10, 20, 100, 20, 5, 30))
# 第二处: x:100, y:300, 宽:30, 高:20, 开始时间100s, 结束时间 800s
delogos.append(vargs.delogo_args(100, 300, 30, 20, 100, 800))
v = X264Codec('path/to/video_file1')
v1 = v.del_logo(delogos) # v1 为新的 X264Codec 对象
```

## 截图
```python
from x264codec.x264codec import X264Codec
v = X264Codec('path/to/video_file1')
jpg_path = v.snapshot(10, 320) # 视频10秒时截一张320高的jpg
```

## hls
```python
from x264codec.x264codec import X264Codec
v = X264Codec('path/to/video_file1')
m3u8_dir = v.hls(encrypt=True)  # 生产加密的 ts 切片, 返回的是 m3u8 文件所在的目录 
```

## 批量截图和生产预览视频
```python
from x264codec.x264codec import X264Codec
v = X264Codec('path/to/video_file1')
pics = v[::-20]     # 从视频的开始到结束截20张图
v_pre = v[::10]     # 从视频的开始到结束生产10秒的预览视频 v_pre 为新的 X264Codec 对象
```



# 附录
- [在centos上安装ffmpeg](./docs/centos7x64_ffmpeg_install.md)
- [在ubuntu/debian上安装ffmpeg](./docs/ubuntu18.04x64_ffmpeg_install.md)