# FALSE CLAIM: `2 ** n` with n < 0 is a float (0.5 for n=-1); the model lowers `**` to an
# int-valued `py_pow`, so `x % 1 == 0` (integrality) is provable. CPython: 0.5 % 1 == 0.5.
#@ requires n < 0
#@ ensures \result == True
#@ assigns \nothing
def f(n: int) -> bool:
    x = 2 ** n
    return x % 1 == 0

if __name__ == "__main__":
    print(f(-1))
