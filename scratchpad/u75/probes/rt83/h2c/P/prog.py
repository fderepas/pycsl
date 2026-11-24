import types
import zv83h2c

class K:
    @staticmethod
    def one() -> int:
        return 2


class _M(types.ModuleType):
    def __setattr__(self, name, value):
        if name == "b":
            value = K
        types.ModuleType.__setattr__(self, name, value)


zv83h2c.__class__ = _M
import zv83h2c.b


#@ ensures \result == 1
def g() -> int:
    return zv83h2c.b.one()


print("result", g())
