# advice of PYCSL-R510-TYPE-STATEMENT-NAME-READ applied to g811_o8001 (`type K = int` after `K = 5`): rename the alias
K = 5


#@ no_exception \all
#@ ensures \result == n // 5
def f(n: int) -> int:
    return n // K


type KT = int


if __name__ == "__main__":
    print("result", f(10))
