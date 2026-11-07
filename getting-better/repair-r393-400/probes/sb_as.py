from builtins import sum as total
#@ ensures \result == 3
def f() -> int:
    return total([1, 2], **{"start": 10})

if __name__ == "__main__":
    print("result", f())
