#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    py_model = 7
    model = 3
    return py_model

if __name__ == "__main__":
    assert g() == 3, g()
