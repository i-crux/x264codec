"""
通用工具函数
"""
import subprocess
import functools
import os


def _filepath_(surf: str = None):
    """
    将参数名中带 path 的参数都换成据对路径
    检查 outpath 的后缀名是不是 surf
    :param surf: 后缀名字符串 ".mp4", ".m3u8", ".mov" 等
    :return: 函数装饰器
    """
    def ck_surf(fn):
        """
        本装饰器的作用就是将函数中使用的路径变为绝对路径
        """
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            args = list(args)   # 将参数从元祖改为列表,否则无法修改args中的元素
            fn_args_name = fn.__code__.co_varnames[:fn.__code__.co_argcount]
            for i in range(len(fn_args_name)):
                if fn_args_name[i].endswith('path'):
                    if fn_args_name[i] in kwargs:       # 处理 **kwargs
                        kwargs[fn_args_name[i]] = os.path.abspath(kwargs[fn_args_name[i]])
                        arg_value = kwargs[fn_args_name[i]]
                    else:
                        args[i] = os.path.abspath(args[i])  # 处理 *args
                        arg_value = args[i]
                    if fn_args_name[i] == 'outpath' and surf:
                        if not arg_value.endswith(surf):
                            return False
            return fn(*args, **kwargs)
        return wrapper
    return ck_surf


def _deal_value_error(fn):
    """
    处理 ValueError的装饰器
    """
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError:
            return False
    return wrapper


def _run_cmd(cmd: str, timeout: float = None) -> 'status,stdout,stderr':
    """
    普通的执行shell命令
    :param cmd: 需要执行的shell命令
    :param timeout: 命令执行超时时间
    :return: 返回 命令执行结果的状态, 标准输出, 标准错误
    """
    # debug
    # print(cmd)
    # end debug
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        stdout, stderr = proc.communicate(timeout=timeout)  # 等待命令执行完成
        try:
            stdout = stdout.decode('utf8')  # 尝试获取标准输出
            stderr = stderr.decode('utf8')  # 尝试获取标准错误
        except UnicodeDecodeError:
            stdout = 'UnicodeDecodeError'
            stderr = 'UnicodeDecodeError'
    except TimeoutError:
        proc.terminate()
        status = -1
        stderr = f'execute {cmd:s} timeout'
    else:
        status = proc.returncode
        if status != 0:
            stderr = f'execute {cmd:s} return {proc.returncode:d} and stderr -> {stderr:s}'
    return status, stdout, stderr


def _run_ffmpeg_cmd(cmd: str, timeout: float = None) -> bool:
    """
    执行ffmpeg相关的命令
    :param cmd: 需要执行的shell命令
    :param timeout: 命令执行超时时间
    :return: 成功 True| 失败: False
    """
    status, _, _ = _run_cmd(cmd, timeout)
    if status != 0:
        return False
    return True


def _ck_type(value, instance):
    """
    检查值的类型是否是某实例对象, 否则 raise ValueError
    :param value: 待确定的值
    :param instance: 实例类型
    :return: void
    """
    if not isinstance(value, instance):
        raise ValueError(f'should be {instance}')


def _ck_value_ge(value, cmpval):
    """
    确认value是否大于 cmpval, 否则 raise ValueError
    :param value: 待比较的值
    :param cmpval: 被比较的目标值
    :return: void
    """
    if not value >= cmpval:
        raise ValueError(f'{value} should greater then {cmpval}')


@_filepath_()
def _write_file(outpath: str, contend):
    """
    将contend写入文件 outpath
    :param outpath: 文件路径
    :param contend: 要写入的内容
    :return: 成功: True | 失败: False
    """
    outpath = os.path.abspath(outpath)
    with open(outpath, 'w') as f:
        f.write(contend)
