from u72_absl import h


#@ requires x >= 0
#@ ensures \result == 14
#@ assigns \nothing
def g(x: int) -> int:
    return abs(x) + h(x)

if __name__ == "__main__":
    print(g(3))
