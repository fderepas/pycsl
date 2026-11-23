from rt80_cls_h import C
import rt80_libb


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return rt80_libb.helper()

if __name__ == "__main__":
    print(g())
