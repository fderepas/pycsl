from . import b as b0
from . import c as c0
import zv7e7


def swap() -> None:
    zv7e7.__dict__.update(b=c0)


swap()
