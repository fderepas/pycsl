#@ no_exception \all
def f(s: str) -> int:
    xs = [ord(c) for c in s]
    return len(xs)


if __name__ == "__main__":
    print("result", f("ab"))
