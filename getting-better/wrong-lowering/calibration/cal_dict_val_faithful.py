"""CAL good — Dict[str,int] is a faithful `map string (option int)`; read-back proves."""
_ = 0
#@ ensures \result == 5
def f() -> int:
    d = {}
    d["a"] = 5
    return d["a"]
