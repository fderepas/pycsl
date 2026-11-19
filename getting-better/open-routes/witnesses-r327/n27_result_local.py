#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    result = 7
    py_result = 3
    return result

if __name__ == "__main__":
    assert g() == 3, g()
