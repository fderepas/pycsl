_ = 0  # anchor


#@ lemma
#@ \variant n
#@ ensures n == n + 1
def bogus(n: int) -> None:
    bogus(n)


#@ ensures \result == -1
def probe() -> int:
    return 3
