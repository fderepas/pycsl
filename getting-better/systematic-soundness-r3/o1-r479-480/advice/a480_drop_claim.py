# advice audit (route #480 / #445 on a builtin receiver): corpus 7508 `return len.zz` with the
# `no_exception` claim DROPPED.
def f(n: int) -> int:
    return len.zz


if __name__ == "__main__":
    print("result", f(1))
