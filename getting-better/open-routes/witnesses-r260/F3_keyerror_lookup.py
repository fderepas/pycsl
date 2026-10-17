# FALSE CLAIM: `raise KeyError` inside `try` is caught by `except LookupError`
# (KeyError <: LookupError), so f() returns 7; the model raises KeyError past the handler.
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    r = 0
    try:
        raise KeyError("k")
    except LookupError:
        r = 7
    return r

if __name__ == "__main__":
    print(f())
