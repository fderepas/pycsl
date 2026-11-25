from . import b as b0
from . import c as c0
import zv7e3


def swap() -> None:
    sa = setattr
    sa(zv7e3, "b", c0)


swap()
