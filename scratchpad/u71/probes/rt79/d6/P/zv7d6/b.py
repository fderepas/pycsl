import sys
import types


class _M(types.ModuleType):
    def __call__(self) -> int:
        return 2


print("b.py loaded")
sys.modules[__name__].__class__ = _M
