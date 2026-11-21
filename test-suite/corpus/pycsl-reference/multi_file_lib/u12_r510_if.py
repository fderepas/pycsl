# route #510 residual (corpus 8296): `type g` in an `if` body at module scope rebinds `g`
#@ ensures \result == n
def g(n: int) -> int:
    return n


if True:
    type g = int
