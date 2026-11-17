import tomllib


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


if __name__ == "__main__":
    a = tomllib.loads("a = 1")["a"]
    b = tomllib.loads("a = 1")["a"]
    print("result", a, b, "OK" if a == b == 1 else "VIOLATION (tomllib runs forged bytecode)")
