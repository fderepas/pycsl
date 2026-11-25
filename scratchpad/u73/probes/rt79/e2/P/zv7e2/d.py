from . import b as b0
from . import c as c0
import zv7e2


def swap() -> None:
    import builtins
    builtins.setattr(zv7e2, "b", c0)


swap()
