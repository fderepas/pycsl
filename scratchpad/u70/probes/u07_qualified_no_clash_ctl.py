import rt77liba as A


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return A.helper() + A.helper()

if __name__ == "__main__":
    print(g())
