r"""lemma used by a caller to prove a false claim"""
_ = 0  # anchor


#@ lemma
#@ requires n >= 0
#@ ensures n + 0 == n
def triv(n: int) -> None:
    pass


#@ requires x >= 0
#@ ensures \result == x + 1
def probe2(x: int) -> int:
    triv(x)
    return x


#@ ensures \result == 0
def probe() -> int:
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
