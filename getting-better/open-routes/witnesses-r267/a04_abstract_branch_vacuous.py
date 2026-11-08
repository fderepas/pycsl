# FALSE: \abstract post is unsatisfiable only at x == 5; the caller reaches it only on that branch.
#@ \abstract
#@ ensures x != 5
def oracle(x: int) -> int: ...

#@ ensures \result == 1
#@ assigns \nothing
def g(x: int) -> int:
    if x == 5:
        oracle(x)
        return 2
    return 1

if __name__ == "__main__":
    print(g(5))
