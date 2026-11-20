# run #8 u58, corpus witness 10304 (review rt69 G7): a module in the TREE ROOT, which is pycsl's working
# directory in every corpus sweep and which CPython's script mode never searches. Do not import it.
print("CWD r613y_cwd_helperq.py loaded:", __file__)


#@ ensures \result == 1
#@ assigns \nothing
def one() -> int:
    return 1
