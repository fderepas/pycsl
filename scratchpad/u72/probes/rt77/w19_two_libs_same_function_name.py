import rt77liba
import rt77libb


#@ ensures \result == 2 or \result == 4
#@ assigns \nothing
def g() -> int:
    return rt77liba.helper() + rt77libb.helper()

if __name__ == "__main__":
    print(g())
