import rt77liba
import rt77libb


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return rt77liba.helper() + rt77libb.helper()

if __name__ == "__main__":
    print(g())
