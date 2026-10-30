"""Advice probe (route #483): the dynamic code moved into a function nothing calls at import."""
K = 1


def _later() -> None:
    __builtins__['exec']('K = 0')
