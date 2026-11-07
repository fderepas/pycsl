# advice of PYCSL-R507-OVERFLOW-SITE-UNLOWERED applied to 8050 (`v = {"ab" * n}`): bind first, bound stated
#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    t = "ab" * n
    v = {t}
    return 1


if __name__ == "__main__":
    print("result", f(5))
