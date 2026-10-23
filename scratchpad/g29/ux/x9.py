r"""G29 UX-X9 — an unannotated callee raises Sub, the caller catches Base."""
_ = 0  # anchor


class Base(Exception):
    pass


class Sub(Base):
    pass


def boom() -> int:
    raise Sub()


#@ ensures \result == 0
def probe() -> int:
    try:
        boom()
    except Base:
        return 9
    return 0


if __name__ == "__main__":
    print("CPython:", probe())
