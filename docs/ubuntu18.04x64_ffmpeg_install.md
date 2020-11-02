# 安装前准备
## 安装依赖

```shell
sudo apt-get update
sudo apt-get -y install autoconf automake build-essential libfreetype6-dev \
  libtheora-dev libtool pkg-config texinfo zlib1g-dev unzip cmake mercurial libssl-dev

# 如果需要ffplay,请安装 SDL2
# sudo apt-get install libsdl2-dev
```

## 关闭图形界面(服务器环境)
```shell
sudo systemctl set-default multi-user.target
```

## 创建编译用的目录
```shell
mkdir -pv /opt/ffmpeg/{ffmpeg_sources,ffmpeg_build,bin}
```

- ffmpeg_sources: 存放源码
- ffmpeg_build: 存放目标文件
- bin: 存放二进制文件

## 安装会变编译器
### nasm
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://www.nasm.us/pub/nasm/releasebuilds/2.13.03/nasm-2.13.03.tar.bz2 && \
tar xjvf nasm-2.13.03.tar.bz2 && \
cd nasm-2.13.03 && \
./autogen.sh && \
./configure --prefix="/opt/ffmpeg/ffmpeg_build" --bindir="/opt/ffmpeg/bin" && \
make -j8 && \
make install
```

### yasm
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://www.tortall.net/projects/yasm/releases/yasm-1.3.0.tar.gz && \
tar xzvf yasm-1.3.0.tar.gz && \
cd yasm-1.3.0 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure --prefix="/opt/ffmpeg/ffmpeg_build" --bindir="/opt/ffmpeg/bin" && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

## 编译安装其他依赖包

* Tip: If you do not require certain encoders you may skip the relevant section 
* and then remove the appropriate ./configure option in FFmpeg. 
* For example, if libvorbis is not needed, then skip that section 
* and then remove --enable-libvorbis from the Install FFmpeg section. 

### libx264
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
git clone --depth 1 https://code.videolan.org/videolan/x264.git && \
cd x264 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure --prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" --enable-static && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

### libx265
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
hg clone http://hg.videolan.org/x265 && \
cd /opt/ffmpeg/ffmpeg_sources/x265/build/linux && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
cmake -G "Unix Makefiles" \
-DCMAKE_INSTALL_PREFIX="/opt/ffmpeg/ffmpeg_build" \
-DENABLE_SHARED:bool=off ../../source && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

### libass
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
git clone https://github.com/libass/libass.git && \
cd libass && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./autogen.sh && \
./configure --prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" --enable-static && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install && \
ln -sv /opt/ffmpeg/ffmpeg_build/lib/libass.so.9 /lib64/ 
```

### libfdk_aac
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
git clone --depth 1 https://github.com/mstorsjo/fdk-aac && \
cd fdk-aac && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
autoreconf -fiv && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

### libmp3lame
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://downloads.sourceforge.net/project/lame/lame/3.100/lame-3.100.tar.gz && \
tar xzvf lame-3.100.tar.gz && \
cd lame-3.100 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared --enable-nasm && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```


### libopus
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L https://archive.mozilla.org/pub/opus/opus-1.2.1.tar.gz && \
tar xzvf opus-1.2.1.tar.gz && \
cd opus-1.2.1 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

### libogg
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://downloads.xiph.org/releases/ogg/libogg-1.3.3.tar.gz && \
tar xzvf libogg-1.3.3.tar.gz && \
cd libogg-1.3.3 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

### libvorbis
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L http://downloads.xiph.org/releases/vorbis/libvorbis-1.3.5.tar.gz && \
tar xzvf libvorbis-1.3.5.tar.gz && \
cd libvorbis-1.3.5 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--with-ogg="/opt/ffmpeg/ffmpeg_build" \
--bindir="/opt/ffmpeg/bin" \
--disable-shared && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```

### libvpx
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
git clone --depth 1 https://chromium.googlesource.com/webm/libvpx.git && \
cd libvpx && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
--prefix="/opt/ffmpeg/ffmpeg_build" \
--disable-examples \
--disable-unit-tests \
--enable-vp9-highbitdepth \
--as=yasm && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
make install
```


# 编译安装ffmpeg
```shell
cd /opt/ffmpeg/ffmpeg_sources && \
curl -O -L https://ffmpeg.org/releases/ffmpeg-snapshot.tar.bz2 && \
tar xjvf ffmpeg-snapshot.tar.bz2 && \
cd ffmpeg && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:/usr/local/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
./configure \
  --prefix="/opt/ffmpeg/ffmpeg_build" \
  --pkg-config-flags="--static" \
  --extra-cflags="-I/opt/ffmpeg/ffmpeg_build/include" \
  --extra-ldflags="-L/opt/ffmpeg/ffmpeg_build/lib" \
  --extra-libs=-lpthread \
  --extra-libs=-lm \
  --bindir="/opt/ffmpeg/bin" \
  --enable-gpl \
  --enable-openssl \
  --enable-libass \
  --enable-libfdk_aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-nonfree \
  --enable-static \
  --disable-shared && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make -j8 && \
PKG_CONFIG_PATH="/opt/ffmpeg/ffmpeg_build/lib/pkgconfig:$PKG_CONFIG_PATH" \
PATH="/opt/ffmpeg/bin:$PATH" \
make install && \
hash -r
```
**PATH="/opt/ffmpeg/bin:$PATH" 添加次PATH,ffmpeg即可使用了**
