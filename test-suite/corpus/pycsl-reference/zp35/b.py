# u71 witness 10435 helper: loaded only by a wildcard import of zp35 (through `__all__`); its import-time
# code rebinds zh35.one.
import zh35


def _two() -> int:
    return 2


zh35.one = _two
