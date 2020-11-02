from setuptools import setup
from setuptools import find_packages
setup(name='x264codec',
      version='0.1.1',
      description='h264 and aac codec with ffmpeg',
      long_description='',
      author='i-crux',
      author_email='i-crux@none.com',
      url='https://github.com/i-crux/x264codec.git',
      license='MIT',
      # install_requires=['aiofiles>=0.4.0'],
      python_requires='>= 3.7',
      classifiers=[
            # 发展时期,常见的如下
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',
            # 开发的目标用户
            'Intended Audience :: Developers',
            'Operating System :: POSIX',
            # 目标 Python 版本
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Bug Tracking',
      ],
      packages=find_packages(exclude=["*tests*"]),
      # entry_points={
      #     'console_scripts': [
      #           'm3u8down' = x264codec.cmdline_tool:main',
      #  ]
      # }

      # package_dir = {'':'x264codec'},
      # py_modules=['x264codec', '_models',]
      )
