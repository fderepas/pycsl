"""CAL good — bool=int is tau-blessed & lossless; a TRUE bool claim proves.
`\result == 1` holds because the guard returns 1 exactly when x is truthy and the
ensures is conditioned on x."""
_ = 0
#@ ensures x == True ==> \result == 1
#@ ensures x == False ==> \result == 0
def f(x: bool) -> int:
    if x:
        return 1
    return 0
