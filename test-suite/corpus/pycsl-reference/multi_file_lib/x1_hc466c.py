"""Helper for corpus 7289 (route #466 control): the other half; `k` is bound BEFORE this module
imports `g`, so either half may be imported first (CPython imports both fine)."""


def k(x: int) -> int:
    return g(x)


from multi_file_lib.x1_hc466b import g  # noqa: E402
