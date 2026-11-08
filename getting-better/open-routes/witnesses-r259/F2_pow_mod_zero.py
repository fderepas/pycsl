# FALSE CLAIM: `pow(x, 2, m)` raises ValueError when m == 0; route #160's pow check only
# inspects the exponent, so `no_exception \all` proves with an unconstrained modulus.
#@ no_exception \all
#@ assigns \nothing
def f(x: int, m: int) -> int:
    return pow(x, 2, m)

if __name__ == "__main__":
    try: print(f(2, 0))
    except Exception as e: print(type(e).__name__, e)
