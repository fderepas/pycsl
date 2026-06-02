#@ proof rocq: double_value
#@ proof rocq: double_is_even
#@ proof lean: double_value
#@ proof lean: double_is_even
#@ ensures \result == (x * 2)
#@ ensures \result % 2 == 0
#@ assigns \nothing
def double(x: int) -> int:
    return x * 2
