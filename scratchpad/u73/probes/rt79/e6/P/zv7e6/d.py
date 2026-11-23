from . import b as b0
from . import c as c0
import zv7e6


def swap() -> None:
    object.__setattr__(zv7e6, "b", c0)


swap()
