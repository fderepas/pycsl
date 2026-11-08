_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    try:
        raise ValueError("boom")
    except ValueError as e:
        return len(e.args)
