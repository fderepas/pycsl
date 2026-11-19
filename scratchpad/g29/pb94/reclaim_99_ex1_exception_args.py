_ = 0  # anchor


#@ ensures \result == 99
def probe() -> int:
    try:
        raise ValueError("boom")
    except ValueError as e:
        return len(e.args)
