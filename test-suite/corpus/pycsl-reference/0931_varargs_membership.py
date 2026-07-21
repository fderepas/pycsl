r"""Test 0931 — VARARGS-MEMBERSHIP: `*vals: str` as a real `seq string` (W8 capability (ii)).

THE FACADE THIS REPLACES. Before this capability a `*vals` parameter was DROPPED from
the WhyML signature entirely and every read of the name fell through to an
unconstrained module-level `val constant vals : int`. The parser predicate

    def at_op(self, *vals): t = self.cur(); return t.type == OP and t.string in vals

therefore emitted

    val constant vals : int
    val contains_check (x: int) (c: int) : bool          (* no ensures at all *)
    ... (contains_check (str_hash_op t.string) vals) ...

— an int-hash of the needle tested against a constant with NO relation to the
arguments actually passed. Mutating the caller's literals could not change the goal:
a total facade.

THE FAITHFUL MODEL. A `str`-ANNOTATED vararg (`*vals: str`) is now a real trailing
parameter of type `seq string` — Why3's IMMUTABLE sequence, matching the immutable
tuple Python builds (an `array` is mutable and cannot be a pure parameter here).

  * membership   `x in vals`   ->  `(seq_mem_str x vals)`
  * truthiness   `not vals`    ->  `(not (Seq.length vals > 0))`
  * length       `len(vals)`   ->  `(Seq.length vals)`
  * CALL SITE    `f(a, "+", "-")` -> `(f a (Seq.cons "+" (Seq.cons "-"
                                          (Seq.empty: seq string))))`

`seq_mem_str` is a `val` whose `ensures` DEFINES it — `result <-> exists i. 0 <= i <
Seq.length v /\ Seq.get v i = x` — exactly the existing `str_contains_op` /
`str_eq_op` shape. It is not an axiom and assumes nothing beyond its definition;
membership simply is not decidable in Why3's string model, so it cannot be a
`function`. In SPEC context the existential is emitted inline (a program `val` is
illegal in a formula), which is what lets `#@ requires x in vals` be written at all.

NON-VACUITY / ANTI-FACADE — three independent controls, all falsifiable:

 1. `member_holds` / `nonmember_fails` pin the BODY. Their preconditions are the
    membership predicate itself and their postconditions fix the coerced result; they
    are discharged ONLY because `seq_mem_str`'s defining `ensures` is the SAME
    existential the `requires` lowers to. An opaque `contains_check` (no ensures)
    leaves both Unknown.

 2. `call_hit` / `call_miss` pin the CALL-SITE PACKING, which is the half that makes
    the model mean what Python means. `call_hit` returns `member_of("+", "+", "-")`
    and asserts `\result == 1`; it is provable only because the callee's `vals` is
    PROVABLY the caller's literal sequence. MUTATION TEST: change `call_hit`'s needle
    from `"+"` to `"*"` and the goal is Unknown — the emitted `.mlw` and the proof
    both track the caller's literals. Under the old facade both spellings emitted the
    same unconstrained constant and neither could be proved.

 3. `empty_call` pins the ZERO-ARGUMENT case: `member_of("+")` passes the EMPTY
    sequence, so membership must be FALSE (`\result == 0`) — the control that a
    packing which silently dropped or defaulted the tail could not pass.

`any_or_member` is the `at_name` / `at_bs` shape verbatim: `not vals or x in vals`,
i.e. "no explicit values were given, so accept anything". `count` pins `len(vals)`.

GATING / BYTE-INERTNESS. Module5 records the vararg ONLY when it carries a `: str`
annotation; an unannotated `*args` keeps the legacy drop. No corpus or `pycsl_lib`
function annotates a vararg, so the full 774-file corpus byte-diff is 0.
Ledger-neutral: no new axiom, allowlist untouched, `seq.Seq` is Why3 stdlib.
"""


#@ requires True
#@ ensures x in vals ==> \result == 1
#@ ensures not (x in vals) ==> \result == 0
def member_of(x: str, *vals: str) -> bool:
    return x in vals


#@ requires x in vals
#@ ensures \result == 1
def member_holds(x: str, *vals: str) -> bool:
    return x in vals


#@ requires not (x in vals)
#@ ensures \result == 0
def nonmember_fails(x: str, *vals: str) -> bool:
    return x in vals


#@ requires True
#@ ensures len(vals) == 0 ==> \result == 1
def any_or_member(x: str, *vals: str) -> bool:
    return not vals or x in vals


#@ requires True
#@ ensures \result == len(vals)
def count(*vals: str) -> int:
    return len(vals)


#@ requires True
#@ ensures \result == 1
def call_hit() -> bool:
    return member_of("+", "+", "-")


#@ requires True
#@ ensures \result == 0
def call_miss() -> bool:
    return member_of("*", "+", "-")


#@ requires True
#@ ensures \result == 0
def empty_call() -> bool:
    return member_of("+")


if __name__ == "__main__":
    assert member_of("+", "+", "-")
    assert not member_of("*", "+", "-")
    assert member_holds("+", "+", "-")
    assert not nonmember_fails("*", "+", "-")
    assert any_or_member("z")
    assert count("a", "b") == 2
    assert call_hit()
    assert not call_miss()
    assert not empty_call()
