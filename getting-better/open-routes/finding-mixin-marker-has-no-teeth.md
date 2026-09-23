# FINDING (#49, gen #31) — `#@ mixin` has no enforced consequence, in either direction
# (HALF CLOSED the same day — see CLOSURE at the end; the instantiation half is still open)

**STATUS: CONFIRMED LIVE by measurement. NOT a soundness route.** Found by
`bin/check-directive-enforcement.py` while trying to write the directive's enforcement
pair: **there is no violating program to write.**

## THE TWO DOCUMENTED CONSEQUENCES, BOTH MEASURED ABSENT

`test-suite/annotations.md` §2.7 table row 1: *"Mixin — `#@ mixin` — `class` — Marks the
class as a composable mixin (not instantiated directly)."*

| claim | experiment | result |
|---|---|---|
| only a `#@ mixin` class is composable | the flagship `0549` with `#@ mixin` DELETED from `CoreEmit`, still named in `#@ compose_from CoreEmit, MapOps` | **SUCCESS** — flattened and verified exactly as before |
| a `#@ mixin` class is not instantiated directly | a `#@ mixin` class with a real `__init__`, instantiated and called from a free function | **SUCCESS** — and SUCCESS again with the marker deleted, so the two halves are indistinguishable |

`ir_resolve.py`'s composition checker reads `mixin_names = comp["mixins"]` — the names the
`#@ compose_from` line lists — and never consults whether those classes carry the marker.
Nothing anywhere rejects direct instantiation.

## WHY IT IS NOT A ROUTE

No false claim is provable through it. The composition machinery's real guarantee comes from
FLATTENING: each provided method is cloned into the composer and **re-verified against the
concrete composer**, which is the compensation `ir_resolve` documents for the unimplemented
S2b obligation (finding w66, route #95). That compensation does not depend on the marker, so
deleting the marker removes a label, not a check. Two probes confirmed the compensation still
bites with the marker gone:

* a provider whose contract does not refine the declared `#@ depends_method` contract —
  FAILS at the clone (`facade__handle_get`), while the isolated `mapops__handle_get` proves
  against the assumed `val self_emit_1 ensures { result >= 1 }`;
* a `#@ class invariant self.n >= 10` on the provider, composed into a `Facade` whose
  `__init__` sets `self.n = 0`, claiming `run() >= 10` — FAILS.

## WHAT IT COSTS

A directive with no teeth is a directive a reader trusts for a guarantee that is not there.
The specific reading at risk: "this class is a mixin, so it is never instantiated, so I need
not reason about its `__init__` or its class invariant standing alone." That reading is
currently unsupported. The cheap fix is a Module-4 check with two clauses — every name in a
`#@ compose_from` list must carry `#@ mixin`, and a `#@ mixin` class must not appear in a
constructor call — both fail-closed, both with named refusals.

Until one exists, `mixin` stays in the UNCOVERED list of
`bin/check-directive-enforcement.py`. Writing it a pair would mean writing a violating
program that verifies, i.e. certifying the directive by lowering the bar to the
implementation — the exact failure the plane was built to catch.

Measured 2026-09-23.


---

## HALF CLOSED (2026-09-23, gen #31)

**The compose-side half is now a refusal.** `#@ compose_from` naming a class that does not
carry `#@ mixin` is rejected with `PYCSL-SEM-COMPOSE-FROM-NOT-A-MIXIN`, witness `1857`,
control `1858` (the identical file with the marker restored, which verifies — 0549's
shape, so if the control ever starts being refused the repair has become a ban on mixin
composition rather than a rule about declaring one).

`#@ mixin` therefore LEAVES the uncovered list of `bin/check-directive-enforcement.py`:
45 of 53, up from 44.

**WHERE IT HAD TO GO, and it is a measurement rather than a preference.** The natural home
is `ir_resolve.apply_composition`, which already raises this whole family of error. It
cannot work there: that pass reads `is_mixin` off the class's `type_decl`, and
**`type_decls` is EMPTY for exactly the classes that are mixins** — a class with no fields
and no `__init__` produces no record decl (its Why3 type is the `int` alias), and the
flagship mixin shape has neither. Instrumented on the violating file, `apply_composition`
printed

    DBG decls: [] mixins: ['CoreEmit', 'MapOps']

so the pass cannot see the marker it would need. The refusal went to `_run_pipeline`, which
has the SOURCE TEXT and whose mirror twin is `\trusted` and already in the raises-honesty
population — the choke-point rule (routes #206-#215, #222, #223).

CENSUS: 17 sources declare `#@ mixin`, ZERO name an unmarked class in a `#@ compose_from`
list; all ten corpus `#@ compose_from` drivers keep their exact verdicts and their own
refusal messages (0550 "dependency has NO provider", 0551 "writes `self.cache`", 0552
"provided by more than one mixin", 1259 route #95, 1814 element-write). Corpus-inert.

## STILL OPEN — "not instantiated directly"

The other documented consequence is unenforced: a `#@ mixin` class constructed directly
still verifies. The enforcement plane's `mixin` pair deliberately does NOT reach for it —
a pair that passes on the half that works would make the directive look fully covered.

The capability: a `#@ mixin` class name appearing as a CONSTRUCTOR CALL is an AST question
(`ast.Call(func=ast.Name(id=<marked class>))`), so it fits the same `_run_pipeline` scan
that now holds the compose-side half — the marked-name set is already computed there.
What has NOT been measured is whether any legitimate shape constructs a mixin (a test
double, a `__init__`-only base), which is the census that has to come first.
