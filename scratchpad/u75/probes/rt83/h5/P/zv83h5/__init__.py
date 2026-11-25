import types


class _M(types.ModuleType):
    def __getattr__(self, name):
        if name == "_" + "_all__":
            return ["w"]
        raise AttributeError(name)


import zv83h5 as _s
_s.__class__ = _M
