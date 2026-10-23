"""Test 0890 — G2: record string-field `.get == literal` routes through str_eq_op (POSITIVE).

09-2223 pure-classifier increment, recognizer G2. A `<record-var>.get("<str-field>") ==
"<literal>"` comparison lowers to `str_eq_op k.kind "method"` — a FAITHFUL string content
compare — instead of the unfaithful int-hash `(k_get_1 …) <> 317966025` (a string-vs-int
type clash / hash comparison). The precondition `k.kind == "method"` (a faithful spec-level
string equality) connects to the body branch ONLY through the shared `str_eq_op` semantics
(`ensures result <-> (a = b)`): under the requires, `str_eq_op k.kind "method"` is true, so
the `then` arm returns 1 and `\result == 1` proves. With the int-hash lowering the two
sides would not connect and the postcondition could not be discharged.

If this regresses, the G2 record-string-field comparison recognizer (or its `_is_string_expr`
routing of a `str`-typed record `.get`) broke.
"""
from typing import TypedDict


class KRec(TypedDict):
    kind: str


#@ requires k.kind == "method"
#@ ensures \result == 1
#@ assigns \nothing
def classify(k: KRec) -> int:
    if k.get("kind") == "method":
        return 1
    return 0
