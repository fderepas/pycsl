# u71 witness 10436 helper: loaded only by `from zp36.sub import *`; its import-time code rebinds zh36.one.
import zh36


def _two() -> int:
    return 2


zh36.one = _two
