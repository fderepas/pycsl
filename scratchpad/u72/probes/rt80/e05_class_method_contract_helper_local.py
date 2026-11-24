from rt80_cls_h2 import C


#@ ensures \result == 2
#@ assigns \nothing
def helper() -> int:
    return 2


obj = C()


#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return obj.m()

if __name__ == "__main__":
    print(g())
