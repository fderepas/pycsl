from rt80_priv_a import x
from rt80_priv_b import y


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return x() + y()

if __name__ == "__main__":
    print(g())
