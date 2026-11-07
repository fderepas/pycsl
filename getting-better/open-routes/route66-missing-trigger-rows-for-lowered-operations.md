# OPEN ROUTE #66 — OPERATIONS PyCSL LOWERS HAVE NO TRIGGER ROW AT ALL
# (found 2026-09-11 by relaunch #55, at `d07b09e7`, immediately after closing #65)

## TWO CARRIERS, BOTH `[+] Verification SUCCESS`

```python
#@ no_exception KeyError
#@ ensures True
def f() -> int:
    d: Dict[int, int] = {1: 1}
    del d[5]                      # CPython: KeyError: 5
    return 0
```

```python
#@ no_exception ValueError
#@ ensures True
def f() -> int:
    return int("abc")             # CPython: ValueError: invalid literal for int()
```

**BOTH OPERATIONS REALLY LOWER** — this is not an emission failure masquerading as a proof:

    del d[5]      ~>  d := map_update_none !d 5        (faithful key removal, no assert)
    int("abc")    ~>  val str_to_int (s: string) : int  (opaque, no assert)

There is simply no `TRIGGERS` row for `DelSubscript` or for `int(<str>)`, so no obligation is
injected and `no_exception` discharges vacuously.

## THIS IS THE THIRD DISTINCT EXCEPTION-MODEL DEFECT IN ONE SESSION

  * **#64 — a MISSING row** for a `bytes` element store (`ValueError`, byte range).
  * **#65 — DEAD rows**: four rows present in the table that no emitter site ever looks up,
    one of them (`divmod`) carrying a perfectly good condition, one (`.index`) a `"true"`
    tautology with zero discrimination.
  * **#66 — MISSING rows** for `del d[k]` and `int(<str>)`.

Three different ways for the same table to be wrong, found within about an hour of each
other. **The pattern is not "this row is bad" — it is that NOTHING RELATES THE TABLE TO THE
SET OF OPERATIONS THE EMITTER ACTUALLY LOWERS.** Patching rows one at a time will keep
finding these.

## THE LIMIT OF THE PLANE ADDED FOR #65 — STATED PLAINLY

`bin/check-trigger-rows-live.py` checks that every row in the table is CONSULTED or REFUSED,
and that no row discharges on a tautology. **It cannot see a MISSING row**, because it starts
from the table. It would have reported green on both carriers above, and did.

That is not a flaw in the plane — it is the other half of the same property, and it needs the
opposite direction of scan: **enumerate the operations the emitter LOWERS (or the exceptions
CPython can raise for them) and check each has a row.** The `no_exception \all` form makes
this sharp: `\all` claims the entire `KNOWN_EXCEPTIONS` set, so every omission is a false
proof waiting for someone to write the contract.

## THE REPAIR SHAPE

Same posture as #65: under a `no_exception` context naming the relevant exception (or
`\all`), REFUSE the construct rather than discharge a claim nothing checks.

  * `del <dict>[k]` with `KeyError` in scope — refuse. (A faithful obligation is available in
    principle — `Map.get d k <> None`, the same condition the orphaned `("attr_call","pop")`
    row already carries — so this one could later be WIRED rather than refused.)
  * `int(<str>)` with `ValueError` in scope — refuse. `str_to_int` is opaque, so there is no
    faithful condition to inject; refusal is the only honest answer.

## THE FOLLOW-UP THAT MATTERS MORE THAN EITHER CARRIER

Build the complementary gate: a census of lowered operations against `TRIGGERS`. Until it
exists, `#@ no_exception \all` should be read as "none of the exceptions this table happens
to model", which is NOT what the directive says and NOT what a user will assume.

## STATUS: **CLOSED** — THREE CARRIERS, TWO DIFFERENT REPAIRS, AND THE DIFFERENCE IS THE POINT

| carrier | CPython | repair | why |
|---------|---------|--------|-----|
| `del d[k]`, key absent | `KeyError` | **WIRED** — new `("subscript","del")` row carrying `Map.get {0} {1} <> None` | the receiver is a REAL MODELLED MAP, so the condition is faithful |
| `chr(n)`, n out of range | `ValueError` | **WIRED** — new `("call","chr")` row carrying `0 <= n < 1114112` | the bound is EXACT |
| `int(<str>)` | `ValueError` | **REFUSED** | it lowers to an OPAQUE `val str_to_int`; there is nothing truthful to inject |

**WIRING BEATS REFUSING WHEREVER A FAITHFUL CONDITION EXISTS**, because it keeps the
completeness. Both wired rows DISCRIMINATE, measured: `del d[5]` (absent) fails and
`del d[1]` (present) proves; `chr(-1)` fails and `chr(65)` proves. A refusal would have
satisfied the negatives and quietly cost every correct program.

**`chr` WAS WORSE THAN A MISSING ROW.** The abstract `val chr_op` carried
`ensures { String.length result = 1 }` UNCONDITIONALLY — asserting a TOTALITY Python does
not have. A missing trigger says nothing; a total contract on a partial function says
something FALSE, and every consumer of `chr_op` inherited it.

Witnesses `1154`/`1155` (del), `1156`/`1157` (int), `1158`/`1159` (chr) — a negative and a
positive control for each. All three negatives anti-vacuity-verified in both directions.

## THE AUDIT THAT FOUND `chr`, AND THE TRAP IT NEARLY WALKED INTO

Ten operations that raise in CPython, each under `#@ no_exception \all`. The first run
returned TEN clean "refused/failed" verdicts — and every one of them was
`ERROR: 'why3' command not found`. **A MISSING TOOL LAUNDERED INTO WHAT READ EXACTLY LIKE
TEN CONFIRMED SAFE BOUNDARIES.** Re-run with `why3` on PATH, one of the ten PROVED.

The other nine are genuinely covered or unreachable, and the classification is worth keeping:

  * REFUSED outright: `list.pop()` on empty, `list.remove(absent)`, a `[::0]` slice.
  * EMISSION-FAIL (unsupported, so unreachable today): `"ab"[5:6]`, `min([])`, `max([])`.
  * CORRECTLY NOT DISCHARGED, through the WIRED `in_bounds` / `map_get` rows: `xs[5]`,
    `d[5]`, `bytes([300])`.

That last group is the honest control for the whole exception-model campaign: where a row is
wired, the obligation bites.
