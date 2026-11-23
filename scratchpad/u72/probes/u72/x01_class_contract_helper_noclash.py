from rt80_cls_h2 import C


obj = C()


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return obj.m()

if __name__ == "__main__":
    print(g())
