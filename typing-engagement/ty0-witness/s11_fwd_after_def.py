class Bar:
    pass


#@ requires True
#@ ensures \result == x
def f_after(x: Bar) -> Bar:
    return x
