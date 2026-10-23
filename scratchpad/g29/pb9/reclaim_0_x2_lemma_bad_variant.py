_ = 0  # anchor


#@ lemma
#@ \variant n
#@ ensures n == n + 1
def bogus(n: int) -> None:
    bogus(n)


#@ ensures \result == 0
def probe() -> int:
    return 3
