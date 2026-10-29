"""Helper for corpus 7289 (route #466 control): a circular import whose names are bound
BEFORE the cycle closes (CPython imports it fine)."""


#@ ensures \result == x
def g(x: int) -> int:
    return x


from multi_file_lib.x1_hc466c import k  # noqa: E402
