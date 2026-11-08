"""PROBE: a \trusted stub whose body RAISES but declares no `#@ raises`."""
_ = 0  # anchor

#@ \trusted reviewer: probe
#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    raise ValueError("always")

#@ requires True
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    try:
        return g()
    except ValueError:
        return 9

if __name__ == "__main__":
    print(f())
