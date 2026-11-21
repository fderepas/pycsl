# advice of PYCSL-R507 (route #512 branch) applied to 8180 (`v = {"k": bytes(n)}`): the constructor bound first in a plain statement, bound stated
#@ requires 0 <= n and n <= 1000
#@ no_exception \all
#@ ensures \result == 1
def f(n: int) -> int:
    b = bytes(n)
    k = 0
    if n > 0:
        k = b[0]
    v = {"k": k}
    return 1


if __name__ == "__main__":
    print("result", f(5))
