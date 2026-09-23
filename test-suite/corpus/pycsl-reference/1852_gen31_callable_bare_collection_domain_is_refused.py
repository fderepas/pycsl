r"""Test 1852 — gen #31 WITNESS: a BARE collection name as a `Callable` domain is refused.

annotations.md §12.17 states the C5 scope limit: "only `int`/`bool`/`str`/`float` and
record/variant names are admissible as arg/return types (stricter than S1, sound;
`bytes`/`list`/`dict`/`set`/`Any`/nested-`Callable`/ellipsis rejected with
`PYCSL-TY3-CALLABLE-SCOPE`)."

Five of those seven WERE rejected: `Any` by its own GT1 raise, the nested/subscripted
forms and the ellipsis by shape. `List[int]`/`Dict[k,v]`/`Set[t]` only because they are
SUBSCRIPTS — and that is the tell. The BARE spellings are plain `ast.Name` nodes,
so `_callable_type_tag` fell through to `return tag`, Module 6 found no record or variant
of that name, and the arrow domain DEFAULTED TO `int`. Measured, four files:

    Callable[[bytes], int]  ->  let function apply (f: int -> int) (x: int) : int
    Callable[[list],  int]  ->  let function apply (f: int -> int) (x: int) : int
    Callable[[dict],  int]  ->  let function apply (f: int -> int) (x: int) : int
    Callable[[set],   int]  ->  let function apply (f: int -> int) (x: int) : int

byte-identical to `Callable[[int], int]`. The class constant `_CALLABLE_SCALAR_TAGS` two
screens above the check is the residue of the rule that was meant to be there: defined,
and referenced nowhere in the file.

Found by taking §12's two-plane claims one at a time and writing the program each
describes — the same audit that produced the day's `mixin`, `thread_entry`, `releases`,
`reveal` and legacy-`Generic[T]` findings.

Controls: 1853 (`Callable[[int], int]` still verifies — the refusal is about the DOMAIN,
not about `Callable`) and 1854 (a bare RECORD name is still admissible, which is what
§12.17 promises and what the refusal must not break).
"""
# pycsl-expected: FAIL
from typing import Callable

_ = 0  # anchor


#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def apply(f: Callable[[bytes], int], x: int) -> int:
    return 0
