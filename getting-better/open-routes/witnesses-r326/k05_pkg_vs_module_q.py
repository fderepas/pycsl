import dup19
#@ ensures \result == 2
#@ assigns \nothing
def g() -> int:
    return dup19.f()

if __name__ == "__main__":
    assert g() == 2, g()
