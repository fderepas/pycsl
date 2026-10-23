"""Test 0981 — the SHADOW-LOCAL half of test 0980's route: `self.<field>.append(v)` is
REFUSED when it would be emitted against a fresh local array.

`.append` on an array target lowers to `arr[!arr_len] <- v; arr_len := !arr_len + 1`,
which is faithful for a LOCAL accumulator. For a `self.<field>` receiver the array is a
FRESH `Array.make 1024 0` with no write-back, so the field is untouched in the model.
Measured, before this refusal:

    #@ class invariant \length(self.xs) == 2
    @mutable_state
    class C:
        #@ assigns self.xs
        def __init__(self) -> None:   self.xs: List[int] = [0, 7]
        #@ ensures \length(self.xs) == 2               <-- FALSE OF THE PROGRAM
        #@ assigns \nothing
        def go(self) -> None:         self.xs.append(9)

    [+] Verification SUCCESS! All contracts formally proven.

Real Python makes the length 3. The emitted body was

    let self_xs = Array.make 1024 0 in
    let self_xs_len = ref 0 in
    self_xs[!self_xs_len] <- 9; self_xs_len := !self_xs_len + 1

The FAITHFUL self-field append arms — the `Seq.snoc` write-back used for a `seq hval`
field and for a `@mutable_state` list field — sit above this one and are untouched;
reaching the array-local arm with a `self.` receiver means none of them matched.
`Module5_IREmitter._collect_final_registry`'s three `self._final_registry.append(...)`
calls take a faithful arm and still verify.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL
from typing import List


#@ class invariant \length(self.xs) == 2
@mutable_state
class C:
    #@ requires True
    #@ ensures True
    #@ assigns self.xs
    def __init__(self) -> None:
        self.xs: List[int] = [0, 7]

    #@ requires True
    #@ ensures \length(self.xs) == 2
    #@ assigns \nothing
    def go(self) -> None:
        self.xs.append(9)
