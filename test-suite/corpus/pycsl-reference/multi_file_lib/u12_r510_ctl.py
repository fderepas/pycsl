# route #510 residual control (corpus 8300): a module-scope alias that rebinds no value it exports
type Vec = list[int]


#@ ensures \result == n + 1
def inc(n: int) -> int:
    return n + 1
