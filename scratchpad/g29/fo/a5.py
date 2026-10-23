r"""continue in finally loop"""
_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    n = 0
    for i in range(3):
        try:
            if i == 1:
                break
        finally:
            n = n + 1
    return n


if __name__ == "__main__":
    print("CPython:", probe())
