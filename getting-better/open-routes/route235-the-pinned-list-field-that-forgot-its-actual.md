# OPEN ROUTE #235 — THE PINNED-RECORD LIST FIELD THAT FORGOT ITS ACTUAL

**Status: OPEN (gen #36, 2026-10-14), Severity 1.** Surfaced by the driver while re-validating the
gen #36 WIP `List[str]`-field-from-seq-local binding (whose comment says the `Seq.empty` default
"DROPPED the caller's list"); reproduced in the corpus language at HEAD d272c684.

## Witness (PROVED at HEAD; CPython `count(["a","b","c"])` returns 3, `count2()` returns 2)
`witnesses-r235/pinned_list_field_actual_dropped.py`:

    @dataclass
    class Entry:
        kind: str
        line: int
        items: List[str] = field(default_factory=list)
    ...  # some method returns List[Entry]  => Entry is a PINNED (pure, seq-field) record
    #@ requires len(xs) == 3
    #@ ensures \result == 0          <-- PROVED
    def count(self, xs: List[str]) -> int:
        e = Entry("block", 1, xs)
        return len(e.items)

Emission: `let e = { kind = "block"; line = 1; items = Seq.empty } in (Seq.length e.items)`.

## Mechanism
`expressions.py` record-literal builder: a collection-typed field whose initialiser is a bound
actual "keeps its typed default (array/map construction over a param is out of Tier-A scope)"
unless one of the narrow faithful binders fires. For a PINNED record (element type of a
`List[<record>]`, so the list field is the pure `seq <elem>`), `_field_default` returns the
DEFINITE `Seq.empty` — ignoring routes #87/#89's `field_list_unknown` / `init_unknown_cf_fields`
fences, which only the `array` arm consults. So the supplied list is replaced by the empty one.

## Related shapes probed at HEAD (driver)
| shape | verdict |
|---|---|
| pinned `List[str]` field, actual = param / local literal | **UNSOUND** (witness) |
| pinned `List[int]` field, same | emits `Seq.empty`; refused only because `seq.Seq` was not `use`d in that file (fail-closed by LUCK) |
| non-pinned `List[str]` / `List[int]` dataclass field | `(Array.make 0 0)`; Why3 type error for str, length-op type error for int (fail-closed by luck) |
| plain class `self.items = xs` | `(Array.make 0 0)`, refused downstream by luck |

## Repair direction
A collection field whose initialiser depends on a SUPPLIED actual and that no faithful binder
captures must be UNCONSTRAINED (`any_seq`/`any_array`/`any_map`, polymorphic, as #86/#87), never
the definite empty value; the pinned arm must honour the same unknown fences as the array arm.
