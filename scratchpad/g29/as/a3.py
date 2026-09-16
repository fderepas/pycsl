r"""G29 AS3 — behaviors: `assumes` in a behavior clause used to discharge an unrelated ensures."""
_ = 0  # anchor


#@ behavior neg:
#@   assumes k < 0
#@   ensures \result == 7
#@ complete behaviors
def probe(k: int) -> int:
    return k


if __name__ == "__main__":
    print("CPython:", probe(-1))
