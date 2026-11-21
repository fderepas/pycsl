# route #510 residual advice: corpus 8294 with the dependency's alias renamed (`type GT = int`); VERIFIES
from a510r_dep_renamed import g


#@ ensures \result == 3
def f() -> int:
    return g(3)


if __name__ == "__main__":
    print(f())
