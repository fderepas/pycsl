A = [1, 2]

#@ no_exception \all
#@ ensures \result == 1
def f() -> int:
    s = {A[5]}
    return 1

if __name__ == "__main__":
    print(f())
