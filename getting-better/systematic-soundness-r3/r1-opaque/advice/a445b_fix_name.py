# Advice probe (route #445, builtin receiver): red-team c42_a018 `n.bit_lenght` with the attribute name fixed (`n.bit_length()`).
#@ no_exception \all
def f(n: int) -> int:
    return n.bit_length()
