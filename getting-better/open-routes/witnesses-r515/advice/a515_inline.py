# advice of PYCSL-R515-IMMEDIATELY-INVOKED-LAMBDA applied to 8195 (`w = (lambda m: "ab" * m)(n)`): body written inline, bound stated
#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int, s: str) -> int:
    w = "ab" * n
    return 1


if __name__ == "__main__":
    print("result", f(5, "ab"))
