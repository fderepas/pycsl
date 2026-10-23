"""Test 1255 — route #93, NEGATIVE: a `total` target may not be `\abstract` either.

The second arm of route #93's repair. `emit_as_val = func_trusted or func_abstract or
func_trusted_parent`, so `#@ \abstract` strips the body exactly as `#@ \trusted` does, and the
H-D termination VC vanishes the same way. This file pins that the repair rejects BOTH markers
rather than only the one the exploit happened to use — a repair measured on one arm of a
disjunction has not been measured on the other (the campaign learned this from route #86: two
carriers that produce the same verdict are indistinguishable until one is closed).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy availability:
#@     targets parse
#@     total
class Parser:
    #@ \abstract
    #@ requires n >= 0
    #@ ensures \result >= 0
    def parse(self, n: int) -> int:
        i: int = 0
        acc: int = 0
        while True:
            acc = acc + 1
        return acc
