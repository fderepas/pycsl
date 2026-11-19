# route #510 residual (corpus 8294 / 8295): a module-scope `type g` after the def rebinds `g`
#@ ensures \result == n
def g(n: int) -> int:
    return n


type g = int
