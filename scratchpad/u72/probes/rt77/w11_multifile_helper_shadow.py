from rt77lib_api import api


#@ ensures \result == 2
#@ assigns \nothing
def helper() -> int:
    return 2


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return api()

if __name__ == "__main__":
    print(g())
