# FALSE: for any 1-char str s, ord(s) < 256 claimed (s = "€" gives 8364).
#@ requires len(s) == 1
#@ ensures \result < 256
#@ assigns \nothing
def f(s: str) -> int:
    return ord(s)

if __name__ == "__main__":
    print(f("€"))
