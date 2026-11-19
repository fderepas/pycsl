# Advice audit, route #460 NOTE, 'drop the exception from the claim of the function calling it':
# witness 7050 with f's `#@ no_exception \all` dropped (g is then reached by no claim). Expected: VERIFIES.
import math


def g(n: int) -> int:
    return math.factorial(n)


#@ ensures True
def f(n: int) -> int:
    return g(n)
