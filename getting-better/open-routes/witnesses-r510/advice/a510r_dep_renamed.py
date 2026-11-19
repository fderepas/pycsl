# route #510 residual advice dependency: the alias renamed (`type GT = int`) shadows nothing it exports
#@ ensures \result == n
def g(n: int) -> int:
    return n


type GT = int
