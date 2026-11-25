from rt80_cls_h import C
import rt80_cls_h


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return C().m() + rt80_cls_h.helper()

if __name__ == "__main__":
    print(g())
