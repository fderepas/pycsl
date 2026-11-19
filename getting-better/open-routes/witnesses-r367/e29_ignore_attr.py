from enum import Enum

class C(Enum):
    _ignore_ = ["B"]
    A = 1
    B = 2

#@ no_exception \all
#@ ensures \result == True
def f() -> bool:
    x = C.B
    return x is x

if __name__ == "__main__":
    print(f())
