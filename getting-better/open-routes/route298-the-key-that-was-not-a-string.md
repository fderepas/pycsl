# OPEN ROUTE #298 — THE hval MODEL ASSUMES EVERY NESTED DICT HAS str KEYS (undeclared)
**Status: DECLARED (model assumption HVAL-STR-KEYS + opt-in `--strict-hval-keys`; gen #37, 2026-10-22; opened 2026-10-22), Severity 1.** Found by the r296 executor; driver-reproduced at 249ded4d (rc=0; CPython False).
Witness `witnesses-r298/c08_items_local.py`: `xs = d["xs"]; for k, v in xs.items(): return isinstance(k, str)` with
`ensures \result == True` proves; CPython `f({"xs": {1: 2}})` is False. `Dict[str, PyVal]` constrains only the TOP-level keys; a
nested `PyVal` dict may have int/tuple/None keys, but the hval carrier `HMap (pairs of string * hval)` (and every key view:
`.items()/.keys()`, bare iteration after #296, `in`, `.get` with a non-str key) models them as strings. Repair: either a faithful
key carrier (hval key = hval) or refuse/opaque every key-typed observation of a nested hval map whose key type is not
proven str, or DECLARE the assumption (HVAL-STR-KEYS, `--soundness-report` relied_on_by every nested-key read, +docs, strict
mode refusing) per the FLOAT-FINITE/LATIN1-STR precedent — measure the corpus/mirror cost of each and choose.

## REPAIR (2026-10-22, worktree pycsl-r298 off 47f53c06) — DECISION (B) BY MEASUREMENT
Root cause (located on the witness emission): the hval carrier `HMap hpairs` keys every NESTED dict by `string`,
and two lowerings read a nested map's key as a str: the `.items()` walk over an hval LOCAL/param read
(`_hval_items_local_recv`) binds `let k = ref (hval_keys_get (hval_as_map xs) !i)` and symbol-types `k` "str"
(so `isinstance(k, str)` folds to `1 = 1`, `isinstance(k, int)` to `1 = 0`), and the route-#296 bare-loop `HMap`
arm binds `HStr (hval_keys_get ..)`. `Dict[str, PyVal]` constrains only the top-level keys.

Measurement of (A), the faithful key (prototype = exactly the `--strict-hval-keys` lowering below, applied by
default): the key becomes an unknown-carrier `hval` (`hval_keys_hget`), a pyval local. Corpus: 11 root `.mlw`
MOVED (the r296 files 3490-3500, whose bare-arm text changes; pyref 0) and the r296 control 3497 (literal holder
`{"m": {"a": 1}}`) PASS -> FAIL. Mirror: 3 mirror files FAIL L3-tc (`stmt_control_flow`: `none_ctor :=
ctor_name` hval vs string; `functions`: `Map.get !_st _k`; `expressions`: `return ctor_name`), because the
mirror's 7 `.items()` loops over a pyval local (5 converted methods: `_union_none_ctor_for` x2,
`_try_union_is_none_match`, `_union_ctor_for_arm_tag`, `_maybe_inject_union_return` x2,
`_refine_tuple_return_type`) feed the key into 13 `str` sinks of 7 kinds (`"None" in k`, assignment to a str
local, `seq string` append, `return k` / tuple return from `-> str`, an f-string, a `map string` get/set).
Making them type-check needs a NEW pyval-to-str coercion at each sink kind in the live emitter (itself
mirrored) plus three owed whole-file mirror re-proofs — disproportionate against (B), which is byte-inert
(0 MOVED everywhere). (A) is shipped as the opt-in strict mode instead.

Probe table (`pycsl.py`, rc; CPython ground truth in each file's `__main__`; base = 47f53c06; logs under the
session scratchpad `r298/logs`):

| shape | base | after (default) | after `--strict-hval-keys` |
|---|---|---|---|
| route witness c08 / 3550 `xs = d["xs"]; for k, v in xs.items(): return isinstance(k, str)` | PROVED | PROVED (declared HVAL-STR-KEYS) | 3554 FAIL |
| 3551 `... return not isinstance(k, int)` | PROVED | PROVED (declared) | 3555 FAIL |
| 3552 `for k, v in d.get("xs", {}).items(): return isinstance(k, str)` | PROVED | PROVED (declared) | 3556 FAIL |
| 3553 nested target `for row in d["rows"]: for k, v in row.items(): ...` | PROVED | PROVED (declared) | 3557 FAIL |
| route witness c24 bare `m = d["m"]; for k in m: return isinstance(k, str)` | FAIL | FAIL | FAIL |
| bare guarded `if isinstance(m, dict): for k in m` (probe c04) | FAIL (HNode arm) | FAIL | FAIL |
| `.items()` key `type(k) == str` (c03), `k + "x"` under `no_exception` (c13), `f"{k}" != "1"` (c14) | emit: str ops | unchanged | L3-tc (fail-closed) |
| `k != 1` (c07), `.keys()` (c01), comprehension/`all`/`sorted`/`list(m.keys())` (c09-c11, c18) | opaque / int-erased | unchanged | unchanged / `HInt` arm |
| `1 in m` (c05), `m.get(1)` (c06): a non-str needle | L3-tc (int vs string) | unchanged | unchanged |
| controls 3558 (HArr real elements; key test decides 0/1; key unobserved) | PASS | PASS | PASS |
| r296 control 3497 (literal str-keyed holder) | PASS | PASS | FAIL (the strict cost) |

Rule (inline in `_classify_iterable` / `_handle_for_stmt`, whose mirror twins are `\trusted`; no new def/field
— the flag is read by `getattr(self, "strict_hval_keys", False)` like `strict_latin1`; no axiom): (i) DEFAULT
unchanged, and the assumption is DECLARED: `--soundness-report` lists HVAL-STR-KEYS (statement,
counterexample 3550-3553, strict mode) relied on by every loop/comprehension of a function holding an
`Any`/PyVal value whose iterable is an `.items()`/`.keys()` view or a bare iteration of a non-parameter,
non-field value (over-, never under-reported; a list carrier is reported too); a `.items()` over a declared
`Dict[str, PyVal]` self-field or parameter is not reported (its keys are the annotated top level). (ii)
`--strict-hval-keys`: the `.items()` key over an hval LOCAL/param read binds the uninterpreted `val function
hval_keys_hget (m: map string (option hval)) (i: int) : hval` (added via `_add_abstract_op`, no spec) as an
immutable pyval local (never symbol-type "str"), and the bare loop's `HMap` arm binds the same term instead of
`HStr (hval_keys_get ..)`. Reads by a `str` needle (`pairs_get`) are unchanged in both modes. Docs: README
(declared-assumptions paragraph), static-semantics App. C.1 (table row + "What `--strict-hval-keys`
covers"), translational §T.10 table row + §T.10.5 entry, `bin/check-assumed-facts.py` docstring.

Census: key views of a nested hval map = `.items()` key over a local / `.get(..)` / `.get(.., {})` /
subscript / nested loop target (PROVED -> declared), bare loop `HMap` arm (FAIL at base: a pyval local's
carrier is never statically `HMap`; covered by the declaration and by strict mode), `.keys()` / bare via
comprehension / `sorted` / `list(..)` / `all(..)` (opaque, fail), `type(k)`, string methods, f-strings of a
key (str ops on the str key under the assumption; L3-tc under strict), non-str needle `in` / `.get` (L3-tc in
both modes). `len(k)` under `no_exception` (c12) PROVES in both modes: it is TypeError, outside the
`no_exception` universe (`KNOWN_EXCEPTIONS`), the same declared scope limit as `ord` (also c20 `len(x)` of a
non-sized hval element).

Blast radius (base = worktree at 47f53c06, after = 20a2af36+; full sweeps via heavy.sh): corpus root 0 MOVED /
0 GONE / 0 APPEARED (1945 -> 1954 .mlw; the 9 extra are the new sources 3550-3558, `--new-source`), compare
rc=0; pyref 0/0/0 (2186/2186) rc=0; mirror 0/0/0 (53/53) rc=0. No mirror moved, so NO whole-file proof is owed.
Gates (logs under the session scratchpad `r298/`): witness table above (base: 3550-3553 rc=0; after default
3550-3553 rc=0 = declared counterexamples with `# pycsl-model-assumption: HVAL-STR-KEYS`; strict 3554-3557
rc=1; controls 3558 rc=0 both modes); check-self-annotate-sync.sh rc=0 (925 verbatim);
self-annotate-mirror-check.sh rc=0 (53); doc-coherency --check rc=0; check-assumed-facts (on the after sweep)
rc=0 (85 facts, unchanged families); `run-soundness-planes.sh` fast rc=0 (61/61); `--slow` NOT completed (rc=124 at the 595 s tool cap after the
61 fast planes re-passed; the 23 prover/emission planes are OWED to the driver: `bin/run-soundness-planes.sh --slow`). Ledger unchanged (3
axioms); no `\trusted` marker added; no new def/field; no refusal added (the refusal-witness census does not
move).
Residuals: (1) DECLARED, not repaired: the default mode keeps proving 3550-3553 (CPython False) — the honest
state is the soundness-report entry plus the strict flag. Repairing the default needs a pyval-to-str
coercion at the 7 sink kinds above (the mirror's union-constructor walk is the only consumer) — a candidate
Tier-5 item. (2) The strict flag is not run on the mirror (it fails L3-tc there by design); a mirror run never
passes it. (3) `--soundness-report`'s population is syntactic (an `Any`-typed name in the symbol table + a
key-view iterable), so a list carrier is over-reported.
