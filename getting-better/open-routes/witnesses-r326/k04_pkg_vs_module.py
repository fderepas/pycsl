from dup19 import f
#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    assert g() == 2, g()
