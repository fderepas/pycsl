r"""G29 NE-Q4 — `os.environ[k]` (an erased mapping) under no_exception KeyError."""
import os
_ = 0  # anchor


#@ no_exception KeyError
def probe() -> int:
    v = os.environ["PYCSL_SURELY_ABSENT_KEY_29"]
    return len(v)


if __name__ == "__main__":
    try:
        print("CPython:", probe())
    except Exception as e:
        print("CPython raises", type(e).__name__)
