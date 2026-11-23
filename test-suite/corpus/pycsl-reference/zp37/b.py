# u71 witness 10437 helper: loaded only by a wildcard import of zp37; its import-time code rebinds zh37.one.
import zh37


def _two() -> int:
    return 2


zh37.one = _two
