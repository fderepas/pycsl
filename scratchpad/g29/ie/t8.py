r"""control: an explicit FileNotFoundError caught by except OSError"""
_ = 0  # anchor


#@ requires k >= 0
#@ ensures \result == 9
def probe(k: int) -> int:
    try:
        if k >= 0:
            raise FileNotFoundError()
        return 1
    except OSError:
        return 9


if __name__ == "__main__":
    print("CPython:", probe(3))
