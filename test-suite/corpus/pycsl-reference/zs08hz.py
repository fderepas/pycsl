# u69 witness 10408 (review rt78 s1, route #622 control): the module both the dependency's own run and the
# program's run load (both first roots are the program directory).


#@ ensures \result == 1
#@ assigns \nothing
def one() -> int:
    return 1
