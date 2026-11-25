import types

class K:
    @staticmethod
    def one() -> int:
        return 2


class _M(types.ModuleType):
    def __call__(self):
        self.b = K
        return 0


import zv83h11 as _s
_s.__setattr__("__class__", _M)
