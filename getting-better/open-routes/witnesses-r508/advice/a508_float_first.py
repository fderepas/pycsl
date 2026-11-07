# advice of PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED applied to 8060 (`v = {n * 1.5}`): bound + explicit float(n)
#@ requires -1000 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int, x: float) -> int:
    y = float(n)
    v = {y * 1.5}
    return 1


if __name__ == "__main__":
    print("result", f(7, 0.5))
