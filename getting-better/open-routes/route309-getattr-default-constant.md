# OPEN ROUTE #309 — `getattr(o, name, <call/collection default>)` LOWERS TO ONE SHARED CONSTANT, EVEN WHEN THE ATTRIBUTE EXISTS
**Status: REPAIRED (gen #37, 2026-10-23; opened the same day), Severity 1.** Red-team round 14; driver-reproduced on main (l10, l15 rc=0; CPython violates).
Witnesses `witnesses-r309/`: l10 (default's call dropped: its writes vanish), l15 (`getattr(a,"n",z()) - getattr(b,"n",z()) == 0`
for different receivers), l16 (a read before and after `a.n = 9` agree). Mechanism: expressions.py (~14408) emits the constant
`pycsl_getattr_default_<hash of default IR>` — an arm meant for a statically-absent attribute is reached when the receiver is a
known record that HAS the attribute; receiver, attribute and the default's effects are all ignored. Distinct from #306 (dict.get)
and #213/#214 (unknown receivers).
Repair: for a known record receiver with a literal attribute name, lower `getattr(o, "f", d)` to: evaluate o, evaluate d (eager,
Python order), then the field read if `f` is a field of o's class (CLASS-EXACT applies), else d; refuse anything else (non-literal
name, unknown receiver, absent-attribute constant arm) — never a hashed constant.

## REPAIR (2026-10-23, r308 executor off 35748ef0; commit daef3943 + route docs; inline, ledger 3)
Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`; corpus copies 3940-3949):

| shape | 35748ef0 | after |
|---|---|---|
| l10 `getattr(k, "n", inc(xs))`, claim `xs[0] == 0` (CPython 1) (3940) | PROVED | FAIL (`let _ = inc xs in k.n`) |
| l15 `getattr(a, "n", z()) - getattr(b, "n", z()) == 0`, a.n=4, b.n=5 (3941) | PROVED | FAIL (`a.n - b.n`) |
| l16 two reads around `a.n = 9` agree (3942) | PROVED | FAIL |
| absent attribute `getattr(k, "zz", inc(xs))`, claim `xs[0] == 0` (3943) | PROVED | FAIL (the default IS the answer) |
| `Any` receivers, `getattr(a, "n", z())` vs `getattr(b, "n", z())` (3944) | FAIL | REFUSED (R309) |
| `getattr(a, "n", {}) - getattr(b, "n", {})` on constructor locals (3945) | PROVED | FAIL (field reads) |
| `getattr(k, nm, 0)` non-literal name on a known record, claim `== 0` (3946) | PROVED | FAIL (per-site opaque) |
| walrus in the default rebinds the receiver `getattr(a, "n", z((a := K(7))))`, claim 7 (CPython 4) (3950) | FAIL | REFUSED (R309) |
| CONTROLS: record param + call default `== k.n` (3947) | PASS | PASS |
| CONTROLS: absent attribute + call default, `y == xs[0]` (3948); ctor local + call default `== 4` (3949) | FAIL | PASS |

Rules (`_lower_getattr`, no mirror twin; inline, no new def):
- `_triv309` default = literal / name / negative number / empty collection literal / argument-less builtin
  constructor (`set()`, `dict()`, `list()`, ...). Every corpus, pyref and mirror `getattr` default is trivial (AST
  census: 0 non-trivial), so those keep their emission except where the arm itself was unsound (below).
- a non-trivial default in a program context is sequenced first: `(let _ = D in o.f)` at all three DECLARED arms
  (symbol-table record, `_emitted_record_field_labels`, the `@mutable_state` self arm); a walrus in it is refused.
- the shared-constant arm (`nt` in DictLit/ArrayLit/SetLit/Call, or non-trivial): the receiver's class is also taken
  from `_current_record_var_classes` (the `c = C()` scan that method calls already use) -> DECLARED = the field read
  (D first), ABSENT = for a non-trivial non-literal D the lowered D itself; a non-literal NAME is UNKNOWN; UNKNOWN +
  non-trivial D is REFUSED (`PYCSL-SEM-GETATTR-DEFAULT-R309`); UNKNOWN + a trivial collection default takes the
  per-site, `_pyobj_state`- and receiver-keyed `pycsl_getattr_unknown_<site>` device of routes #197/#213/#239.
  The hashed `pycsl_getattr_default_<hash>` survives only for an ABSENT attribute with a literal default (its value
  IS the default, independent of the receiver; equal literals denote equal values — route #47's partition).
- the SCALAR tail: a non-literal name no longer counts as ABSENT (it took the default verbatim) -> the per-site device.

CENSUS of hash-named constants standing for a receiver-dependent value (`stable_hash(` / `pycsl_*_%d` producers in
`module6_whyml`): `pycsl_getattr_missing_` / `pycsl_getattr_unknown_` (state+receiver keyed, routes #213/#239: OK);
`pycsl_getattr_default_` (REPAIRED above); `pycsl_seeded_map_<hash of seed>` (`Counter(xs)`: keyed on the seed's
SYNTAX — two constructions from `xs` around a write share it; measured: the shape is an L3-tc rejection on map
compare/subscript, i.e. fail-closed, census 0 seeded live sites; a refusal was drafted and DROPPED because it adds a
raise to `_call_named_builtins`, whose mirror stub is `\trusted` without `#@ raises` — trusted-raises ratchet 62 > 61 —
RESIDUAL); `pycsl_nonempty_<name>` (per-NAME bool for a dict local's truthiness, `@mutable_state` mirror emission only:
RESIDUAL, route #55's device); `getattr_<cls>_poly self <hash of name>` (refine-tuple mirror only, keyed on self:
OK); field-name / string hashes (`hash_field`, `str(stable_hash(...))`, fold names): identifiers, not values.

Blast radius: corpus root 1 MOVED (2760_gen36_route214_two_unknown_receivers_getattr_eq_closed — UNKNOWN + `{}`
default, shared constant -> receiver-keyed device; re-proved: FAIL = its label), 0 GONE, 0 APPEARED (12 new
emitting sources ignored; 2048 base / 2060 candidate); pyref 0/0/0 (2186/2186); mirror 3 MOVED / 0 / 0 (53/53):
`frontend__desugar` (`getattr(sub, "keywords", [])`), `frontend__exec_splice` (`getattr(call, "args", [])`),
`module6_whyml__functions` (`getattr(self, ..., set())` on the mixin self, UNKNOWN) — all three the UNKNOWN +
empty-collection arm; L3-tc rc=0 each. Whole-file proofs: desugar rc=0, exec_splice rc=0 (PROVED); functions OWED:
`HEAVY_LOW=1 /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh env PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py
src/self-annotate/src/module6_whyml/functions.py --import-path src/pycsl` (the move: 3 `contains_check (...) <set>` reads
of `getattr(self, "_x", set())` became `(pycsl_getattr_unknown_<site> self)` instead of one shared constant).
Gates (both routes, one landing; logs in the r308 worktree `scratch-r308/`): witnesses table above and route #308's;
byte-diff-compare root rc=0 with `--expect-moved 2760_...` (2760 re-proved FAIL), pyref rc=0; mirror-emit-sweep base/after
rc=0, compare `--min-files 50` rc=1 with exactly the 3 movers above (L3-tc ok); check-self-annotate-sync.sh rc=0 (926
verbatim); self-annotate-mirror-check.sh rc=0; run-soundness-planes.sh fast 61/61 rc=0 (final tree; the first run was
RED 2/61 on my own additions — two control helpers `z()` with a tail-return-only contract (vacuous-drivers ratchet) and
the walrus-default raise with no witness (witness-coverage ceiling) — both fixed: helpers uncontracted, witness 3950);
doc-coherency --check rc=0; check-assumed-facts rc=0; check-trusted-raises-honesty rc=0 (61 SILENT, unchanged);
check-refusal-witness-coverage rc=0 (254 demonstrated / 5); census rows for 3930-3936, 3940-3946, 3950 by `_census_row`.
Ledger 3. Latent false proofs found: none (no previously-proved corpus file moved).
Residuals: seeded-map constant (above); `pycsl_nonempty_<name>`; the UNKNOWN + scalar-literal default keeps the
per-site keyed device (sound, value-opaque); a constructor local reassigned from two classes resolves to the last
`c = C()` (a mixed-type local is an L3-tc rejection, fail-closed).
