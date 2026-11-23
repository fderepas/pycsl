#@ ensures \result == 1
#@ assigns \nothing
def é() -> int:
    return 1


#@ ensures \result == 2
#@ assigns \nothing
def e() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return é()

if __name__ == "__main__":
    print(g())
