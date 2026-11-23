from rt80_cls_h import C, helper


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return C().m() + helper()

if __name__ == "__main__":
    print(g())
