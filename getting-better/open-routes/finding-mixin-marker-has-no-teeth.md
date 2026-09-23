# FINDING (#49, gen #31) — `#@ mixin` has no enforced consequence, in either direction

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
