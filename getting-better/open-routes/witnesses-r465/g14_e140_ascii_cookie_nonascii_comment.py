# -*- coding: ascii -*-
# café

#@ no_exception \all
def f(n: int) -> int:
    return n + 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
