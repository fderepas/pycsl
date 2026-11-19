#@ no_exception \all
def f(n: int) -> str:
    return f"{n:F}"


if __name__ == "__main__":
    try:
        r = f(10**400)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
