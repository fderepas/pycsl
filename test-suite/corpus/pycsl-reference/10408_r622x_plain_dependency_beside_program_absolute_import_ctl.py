r"""Test 10408 -- run #9 u69, review rt78 s1, route #622 control (PASS). The dependency zs08dep.py sits beside
the program as a plain file (not a symlink) and imports `from zs08hz import one`: its own first root and the
program's are both the program directory, so the u69 rule keeps one view and `cd <tree root> && python <this
file>` prints "result 1". (The symlinked-dependency shape of rt78 s1 / s7 stays a probe: the corpus holds no
symlinks.)
"""
# pycsl-expected: PASS
from zs08dep import g


#@ ensures \result == 1
#@ assigns \nothing
def h() -> int:
    return g()


if __name__ == "__main__":
    print("result", h())
