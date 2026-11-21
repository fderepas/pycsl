r"""G29 J7 — route #143 via an IMPORTED CLASS whose method's raises condition names its module's LIM."""
_ = 0  # anchor
from multi_file_lib.r143_cls import K

LIM = 5


#@ assigns \nothing
#@ no_exception ValueError
def caller(k: int) -> int:
    o = K(1)
    return o.m(k)


if __name__ == "__main__":
    print("CPython:", caller(3))
