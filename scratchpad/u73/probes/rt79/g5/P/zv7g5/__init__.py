from . import alt as _alt


def __getattr__(name: str) -> object:
    return _alt.two
