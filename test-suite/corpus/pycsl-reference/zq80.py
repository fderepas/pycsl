# u66 control 10382 (review rt76 r5): a MODULE zq80 beside a namespace directory zq80/ in the corpus directory.
# CPython's FileFinder takes the module, so `from zq80 import b` binds this function.


#@ ensures \result == 1
#@ assigns \nothing
def b() -> int:
    return 1
