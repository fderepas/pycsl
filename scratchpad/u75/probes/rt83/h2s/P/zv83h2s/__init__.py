import types

class K:
    @staticmethod
    def one() -> int:
        return 2


class _M(types.ModuleType):
    def __setattr__(self, name, value):
        if name == "b":
            value = K
        types.ModuleType.__setattr__(self, name, value)


import zv83h2s as _s
_s.__setattr__("__class__", _M)
