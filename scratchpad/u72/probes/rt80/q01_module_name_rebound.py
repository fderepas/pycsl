import rt80_liba
import rt80_libb
rt80_liba = rt80_libb


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt80_liba.helper()

if __name__ == "__main__":
    print(g())
