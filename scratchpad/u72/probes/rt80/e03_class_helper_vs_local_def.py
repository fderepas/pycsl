from rt80_cls_h import C


#@ ensures \result == 2
#@ assigns \nothing
def helper() -> int:
    return 2


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return C().m() + helper()

if __name__ == "__main__":
    print(g())
