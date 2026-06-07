# pure_lib/insp — pure-Python inspect module
# unwrap: Modelled (loop following __wrapped__). signature: Stubbed.
# cleandoc: Specified (string-heavy).


#@ requires func >= 0
#@ ensures \result >= 0
def unwrap(func) -> int:
    return func


#@ ensures \result >= 0
def signature(func) -> int:
    return 0


#@ requires doc >= 0
#@ ensures \result >= 0
def cleandoc(doc) -> int:
    return doc
