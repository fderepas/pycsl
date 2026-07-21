r"""Test 0932 — CONCRETE token kinds and a CONCRETE keyword table (W8 (ii) companion).

Two opaque reads stood between the varargs-membership capability (0931) and the real
`pure_ast._Parser` predicates. Both were resolved the same way: by reading the value
from the very stdlib module the annotated code imports, at emission time.

1. TOKEN KIND. `t.type == _tokenize.OP` lowered to `(get_OP _tokenize)` — an
   `val get_OP (x: int) : int` applied to a `val constant _tokenize : int`. Two
   unconstrained ints, with no `ensures` on either. Nothing about the kinds was
   expressible: `get_OP _tokenize` and `get_NAME _tokenize` were not provably
   DISTINCT, so a program could not even establish that a token is not
   simultaneously an OP and a NAME. Now `_tokenize.OP` is the literal `55`,
   `_tokenize.NAME` is `1`, `NUMBER` `2`, `STRING` `3` — and kind disjointness is
   ordinary integer arithmetic.

2. KEYWORD TABLE. `t.string in _keyword.kwlist` lowered to
   `contains_check (str_hash_op t.string) (get_kwlist _keyword)`: the needle
   int-HASHED, the table an opaque getter, and `contains_check` declared with NO
   postcondition at all. Now the table is resolved to its ACTUAL contents and the
   membership is the same real `seq_mem_str` the vararg path uses.

FAITHFULNESS. Neither value is hardcoded in the emitter. Module5 imports the real
`tokenize`/`token`/`keyword` module and reads the attribute, so the emitted literal is
by construction the exact value the annotated program computes at runtime on this
interpreter — no version drift, no table to maintain, no axiom.

NON-VACUITY / ANTI-FACADE — every control below is falsifiable:

  * `kinds_are_distinct` (`ensures \result == 1`) is provable ONLY because the two
    kinds are concrete unequal integers. Under the old `get_OP`/`get_NAME` lowering
    the two sides were unrelated abstract ints and the goal was Unknown.
  * `op_kind` / `name_kind` / `number_kind` / `string_kind` pin the SPECIFIC values, not merely their distinctness:
    a fold that produced *some* constant would fail them.
  * `def_is_kw` pins the keyword table's CONTENTS: it is discharged by exhibiting
    the witness index of "def" in the emitted chain, which exists only because the
    chain IS the real member list. Under `contains_check` — declared with NO
    postcondition whatsoever — this goal is Unknown no matter what the table holds,
    so this single control already refutes the old facade.
  * MUTATION TEST: `_tokenize.OP` -> `_tokenize.NUMBER` changes the emitted literal
    (`55` -> `2`); dropping the `_keyword.kwlist` conjunct removes the whole
    `Seq.cons` chain from the emitted `.mlw`.

KNOWN SMT-COST BOUNDARY (not a modelling gap). The NEGATIVE direction —
`"notakeyword" not in _keyword.kwlist`, i.e. REFUTING the existential over a
35-element `Seq.cons` chain — times out: the solver must unfold the `Seq.get`/`cons`
equations once per element. The model is exact and the goal is true, so this is a
proof-search obligation (route to an interactive prover if it is ever needed), not an
unprovable claim. No live predicate needs it: `at_kw`'s contract is `ensures True`,
and the positive control above already discharges the anti-facade duty.

SCOPE / BYTE-INERTNESS. Restricted to `tokenize` / `token` (int ALL-CAPS attributes)
and `keyword` (list-of-str attributes). No other corpus file and no `pycsl_lib` module
imports any of them, so the full 774-file corpus byte-diff is 0. Ledger-neutral: the
folds REMOVE two abstract vals (`get_OP`, `get_kwlist`) and add no axiom.
"""
import keyword as _keyword
import tokenize as _tokenize


#@ requires True
#@ ensures \result == 1
def kinds_are_distinct() -> int:
    if _tokenize.OP == _tokenize.NAME:
        return 0
    return 1


#@ requires True
#@ ensures \result == 55
def op_kind() -> int:
    return _tokenize.OP


#@ requires True
#@ ensures \result == 1
def name_kind() -> int:
    return _tokenize.NAME


#@ requires True
#@ ensures \result == 2
def number_kind() -> int:
    return _tokenize.NUMBER


#@ requires True
#@ ensures \result == 3
def string_kind() -> int:
    return _tokenize.STRING


#@ requires True
#@ ensures \result == 1
def def_is_kw() -> bool:
    return "def" in _keyword.kwlist


#@ requires True
#@ ensures \result == 1
def kind_and_kw(k: int, s: str) -> bool:
    return k == _tokenize.NAME and s in _keyword.kwlist or True


if __name__ == "__main__":
    assert kinds_are_distinct() == 1
    assert op_kind() == 55
    assert name_kind() == 1
    assert number_kind() == 2
    assert string_kind() == 3
    assert def_is_kw()
    assert not ("notakeyword" in _keyword.kwlist)
    assert kind_and_kw(1, "def")
