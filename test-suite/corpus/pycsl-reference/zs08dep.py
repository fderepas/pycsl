# u69 witness 10408 (review rt78 s1, route #622 control): a dependency beside the program (a plain file, not
# a symlink) whose absolute import resolves from the same first root in its own run and in the program's.
from zs08hz import one


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return one()
