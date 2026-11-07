# OPEN ROUTE #235 — THE PINNED-RECORD LIST FIELD THAT FORGOT ITS ACTUAL

**Status: REPAIRED (gen #36, 2026-10-14), Severity 1.** Was: OPEN (gen #36, 2026-10-14). Surfaced by the driver while re-validating the
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

## Wider probe (executor, base df9fa4e6) — the defect is not pinned-specific
The definite empty collection default was reached by FOUR channels, all PROVED at base once the
emission type-checks (the "fail-closed by luck" rows above are only luck for `len()`, which lowers
through `iter_length` on an array; truthiness / membership type-check and DECIDE):
| shape | base | repaired |
|---|---|---|
| pinned `List[str]` field, actual = param / local literal / keyword (2006/2007/2008, witness) | **PROVED** `len == 0` | `any_seq` — FAIL |
| plain class pinned by a `-> List[Item]` function, `self.items = xs` (2010) | **PROVED** | `any_seq` — FAIL |
| `Dict[int, int]` dataclass field from a supplied actual, positional (2009) / keyword | **PROVED** `1 in e.d` False | `any_map` — FAIL |
| `self.items = list(xs)` / `[x for x in xs]` / `sorted(xs)`, `if b.items:` (2013) | **PROVED** (`Array.make 0 0`) | `any_array` — FAIL |
| `self.items = dict(m)` / `{k: v for ...}`, `1 in b.items` (2014) | **PROVED** (`const None`) | `any_map` — FAIL |
| `n: int = 3`, `self.items = [0] * n`, `Item()` (2016) | **PROVED** | `any_array` — FAIL |
| `@dataclass` field `default_factory=lambda: [1, 2, 3]`, actual omitted (2017) | **PROVED** | `any_array` — FAIL |
| `self.items = list(BASE)`, `BASE` a module global (2018) | **PROVED** | `any_array` — FAIL |
| pinned `List[int]` / non-pinned `List[str]`/`List[int]` with `len()` | refused (type error) | refused (type error / unprovable) |
| CONTROLS: omitted `default_factory=list` (2011), `len >= 0` on the supplied actual (2012), `self.items = list()` (2015) | PROVED | PROVED (faithful `Seq.empty` / `Array.make 0 0` kept) |

## Repair landed (gen #36, 2026-10-14)
* Module 6 `_call_record_constructor` (mirror `\trusted`):
  - the PINNED arm of `_field_default` honours the route #87/#89 fences the array arm already
    consulted (`init_unknown_cf_fields`, `field_list_unknown`, a non-empty `field_list_literals`)
    -> polymorphic `any_seq`; only a genuinely empty initialiser keeps `Seq.empty`;
  - a collection field whose captured initialiser mentions a BOUND name (supplied positional or
    keyword actual, or a parameter bound from its known default) or an omitted parameter of
    unknown default, and that no faithful binder captured, is `any_seq` (pinned) / `any_array` /
    `any_map` instead of falling through to `_field_default`.
* Module 5 (`construction_synth._collect_init_construction`, not mirrored; `visit_ClassDef`,
  mirror `\trusted`, inline): a collection-typed field whose last top-level `__init__` store is a
  non-captured expression over a parameter, or a non-literal, and a `@dataclass` collection field
  (synthesized `__init__`) whose `default_factory` is not the bare `list`/`dict`/`set`/`frozenset`,
  join `init_unknown_cf_fields` (the channel the collection arms read). Scalars are not added,
  so their IR is unchanged.

Gates (base worktree at df9fa4e6): corpus 2 MOVED (0661/0662: an unused `val any_array` decl
only; both still PROVE), pyref 1 MOVED of 2198 (0091: `list(data)` field now `any_array`; still
FAIL, expected FAIL); mirror 0/53 MOVED.

A collection-builtin call is exempt (keeps its literal treatment) only with NO argument
(`list()`, `dict()` — genuinely empty) or a name-free `bytearray`/`bytes` size (route #79's 0452
length capture); `list(BASE)` over a module global (2018), `set([1, 2])`, `dict(a=1)` are unknown.
