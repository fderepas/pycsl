r"""user exception called with tuple handler"""
_ = 0  # anchor


class E1(Exception):
    pass


class E2(Exception):
    pass


#@ ensures \result == 0
def probe() -> int:
    try:
        raise E2()
    except (E1, E2):
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
