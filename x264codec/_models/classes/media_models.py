import abc
import numbers
from x264codec._models.utils.utils_common import _ck_type, _ck_value_ge


class AutoStorage:
    """
    数据描述符,用于保存对象属性,其主要目的是为了检查对象属性是否合法
    本类就是一个合法的数据描述符,可以直接使用.
    但是保存在对象中的实际属性名为:_类名#索引值
    """
    __counter = 0

    def __init__(self):
        cls = self.__class__
        prefix = cls.__name__   # 获取类名
        index = cls.__counter
        self.storage_name = f'_{prefix}#{index}'
        cls.__counter += 1      # 增加索引值

    def __get__(self, instance, owner):
        if instance is None:
            return self     # 用于函数
        else:
            return getattr(instance, self.storage_name)     # 返回对象属性值

    def __set__(self, instance, value):
        setattr(instance, self.storage_name, value)     # 设置对象属性值


class Validated(abc.ABC, AutoStorage):
    """
    判断输入是否合法的抽象基类
    """
    @abc.abstractmethod
    def validate(self, instance, value):
        """
        return validated value or raise ValueError
        """

    def __set__(self, instance, value):     # 覆盖父类的 __set__ 方法,加入属性值校验
        value = self.validate(instance, value)
        super().__set__(instance, value)


class ValidatedIter(abc.ABC, AutoStorage):
    """
    判断输入是否合法的抽象基类
    """
    @abc.abstractmethod
    def validate(self, instance, value):
        """
        return validated value or raise ValueError
        """

    def __set__(self, instance, value):  # 覆盖父类的 __set__ 方法,加入属性值校验
        v = getattr(instance, self.storage_name, None)  # 如果此属性没值,则新建属性
        if not v:
            v = set()
            super().__set__(instance, v)
        v.add(self.validate(instance, value))    # 如果已经存在,则添加新值到次集合


class IntNotNegative(Validated):
    def validate(self, instance, value):
        _ck_type(value, numbers.Integral)
        _ck_value_ge(value, 0)
        return value


class FloatNotNegative(Validated):
    def validate(self, instance, value):
        _ck_type(value, float)
        _ck_value_ge(value, 0)
        return value


class StrNonBlank(Validated):
    def validate(self, instance, value):
        _ck_type(value, str)
        value = value.strip()
        _ck_value_ge(len(value), 1)
        return value


class Boolean(Validated):
    def validate(self, instance, value):
        _ck_type(value, bool)
        return value


class TmpFileIter(ValidatedIter):
    def validate(self, instance, value):
        _ck_type(value, str)
        value = value.strip()
        _ck_value_ge(len(value), 1)
        return value


class EntityMeta(type):
    """
    元类,用于创建带有验证字段的业务实体
    """
    def __init__(cls, name, bases, attr_dict):
        """
        在超类(在这里是 type)上调用 __init__ 方法
        """
        super().__init__(name, bases, attr_dict)
        for key, attr in attr_dict.items():
            if isinstance(attr, Validated):
                type_name = type(attr).__name__
                attr.storage_name = f'_{type_name}#{key}'   # 修改 AutoStorage 中的默认值


class Entity(metaclass=EntityMeta):
    """
    这个类的存在只是为了用起来便利:
    这个模块的用户直接继承 Entity 类即可,无需关心 EntityMeta 元类,
    甚至不用知道它的存在
    """
    pass
