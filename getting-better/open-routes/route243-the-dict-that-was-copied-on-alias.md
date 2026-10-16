# OPEN ROUTE #243 — A DICT / SET VALUE ALIASED THROUGH A SECOND NAME IS A COPY IN THE MODEL

**Status: REPAIRED (gen #36, 2026-10-16), Severity 1.** Repaired together with route #244 (fail-closed
refusal; no new carrier, no new axiom, ledger 3).

**Was: OPEN (gen #36, 2026-10-16), Severity 1.** Found by the ch16 (W-IPM S-A/S-D) chain agent while
spiking dict/set mutator lowerings; driver-reproduced at HEAD 4b894167: all four witnesses rc=0 "Verification
SUCCESS", CPython prints `True` for each (claims are `\result == False`).

## Witnesses (`witnesses-r243/`)
- `field_set_alias_local.py`: `a = self.s; self.s.add(1); return 1 in a` (existing @mutable_state set-field
  `.add` lowering).
- `field_alias1.py`: `self.d = {}; self.g = self.d; self.d[1] = 5; return 1 in self.g`.
- `field_alias2.py` / `field_alias3.py`: CROSS-METHOD — `link()` does `self.g = self.d`; `m()` stores
  `self.d[1] = 5` (dict) / `self.s.add(1)` (set) and returns `1 in self.g`; `m` proves with no precondition.

## Mechanism
Dict and set values are pure Why3 maps, so every assignment to a second name/field is a COPY; a later
in-place mutation through one name is invisible through the other. Route #59's guard only catches stores
through a LOCAL alias in the same function; the cross-method field alias cannot be caught by a per-function
guard.

## Repair direction (from the agent; needs a spike)
Either a by-reference (region) carrier for dict/set fields, or a CLASS-WIDE field-alias refusal (refuse any
`self.<f> = <expr naming another dict/set field or a local aliasing one>` and any local alias of a dict/set
field that is later read after an in-place mutation of the other name), plus fail-closed treatment of
mutation through an alias. Arrays are not affected (Why3 rejects record fields aliasing an array:
"mismatches regions").

## Probe table (base cdac19a6 -> repaired; CPython ground truth in each file's `__main__`)
Every false claim below PROVED (rc=0 "Verification SUCCESS") at cdac19a6.

| carrier | base | repaired | corpus |
|---|---|---|---|
| `self.g = self.d` then `self.d[1] = 5`, read `self.g` (same method) | PROVED | REFUSED (F) | 2296 |
| cross-method `link(): self.g = self.d`, dict store | PROVED | REFUSED (F, in `link`) | 2297 |
| cross-method set twin, `self.s.add(1)` | PROVED | REFUSED (F) | 2298 |
| `a = self.s; self.s.add(1); return 1 in a` | PROVED | REFUSED (#59 guard + mutator calls) | 2299 |
| `link(p): self.d = p`; caller keeps `p`, stores through `self.d`, reads `p` | PROVED | REFUSED (E, at the call) | 2300 |
| `a = self.d; self.g = a` (alias through a local) | PROVED | REFUSED (F) | 2301 |
| `__post_init__: self.g = self.d` (dropped by Module 5) | PROVED | REFUSED (ctor scan) | 2302 |
| set `discard` through the other field | PROVED | REFUSED (F) | 2303 |
| `link(p)` with `ensures self.d == p`; caller stores through `p`, reads `self.d` | PROVED | REFUSED (E/F) | 2304 |
| `e = d` (a dict PARAMETER) then `e[1] = 5`, read `d` | PROVED | REFUSED (#59 guard, formals) | 2305 |
| dataclass ctor `C(x)` (init_body stores `x`); `c.put()`; read `x` | PROVED | REFUSED (E, at `C(x)`) | 2306 |
| `a = set(); self.s = a; self.s.add(1); return 1 in a` (route #59 carrier 6, set) | PROVED | REFUSED (F) | 2307 |
| explicit `__init__(p): self.d = p; self.g = p` | PROVED | REFUSED (ctor scan) | 2308 |
| explicit `__init__: self.d = {}; self.g = self.d` (Module 5 havocs `g`) | PROVED | REFUSED (ctor scan) | 2309 |
| CONTROL dict field stored through, no alias anywhere | PASS | PASS | 2310 |
| CONTROL set local mutated and read | PASS | PASS | 2311 |
| CONTROL `self.g = dict(self.d)` (a fresh copy) in a mutating unit | PASS | PASS | 2312 |
| CONTROL read-only field copy `self.b = self.a`, no in-place mutation in the unit | PASS | PASS (not refused) | 1306 |

Measured but not proving at base (no repair needed; recorded so nobody re-probes them):
`a = self.d if c else {}` / `a, n = self.d, 0` / walrus `(a := self.s)` aliases (FAIL, undecided),
`g = c.get()` from a module function (FAIL), `b = a; b.add(2)` on a set local (refused: in-place
mutator refusal), `self.s |= {1}` beside an alias (refused by route #59, `FieldAugAssign`).

## Repair landed (gen #36, 2026-10-16)
Fail-closed. A dict/set value is a pure map, so the repair refuses every program in which one
dict/set object becomes reachable through two names while the unit can mutate one in place.
Three sites, all `\trusted` in the mirror (no re-port, no new def, no new field):

1. `functions.py::_reset_function_state`, end — the unit-wide rule (`PYCSL-WHYML-COLLECTION-ALIAS`).
   * SLOTS: a parameter slot ESCAPES when its callee stores it into a dict/set field (or a dataclass
     `__init__` does, read from `type_decls[*].init_body`), and MUTATES when the callee mutates it in
     place (route #244's shadow). Both are closed under forwarding (fixpoint over every function of
     the unit, imported/trusted bodies included).
   * UNIT-MUT: some function of the unit mutates a dict/set in place (store, `del`, mutator call,
     `|=`/`&=`/`^=`/`-=`) through a field, a parameter, or a non-PRIVATE local (private = bound only to
     fresh values, never given another name, never passed into an escaping slot).
   * (F) under UNIT-MUT, a store into a dict/set field (in any non-trusted function of the unit) must
     be FRESH (literal, comprehension, `set()`/`dict()`/`frozenset()`/`defaultdict()`..., `.copy()`)
     or a SINGLE-USE name; (E) under UNIT-MUT an argument in an escaping slot, and (M) ALWAYS an
     argument in a mutating slot, must be fresh or single-use. Single-use: not in a loop or
     comprehension, not used again in the statement or afterwards, never given another name before
     (stored / bound / returned / passed to anything but a harmless builtin), a local bound only to
     fresh values, a parameter not named by the function's contract.
2. `statements.py::_handle_assign_stmt` — route #59's local-alias guard now treats an in-place
   MUTATOR CALL (`add`/`discard`/`remove`/`pop`/`popitem`/`clear`/`update`/`setdefault`/`*_update`)
   and an `AugAssign` on either name as a store, and treats a dict/set PARAMETER as an alias source.
3. `pycsl.py::_run_pipeline` — the constructor scan (`PYCSL-SEM-COLLECTION-ALIAS`): `__init__`,
   `__post_init__` and `__new__` never reach Module 6 as bodies, so a store into a dict/set field
   there must be fresh or a parameter named exactly once, unless no in-place mutation in the parsed
   unit is rooted at the stored field, at a field the value reads, or (for a value reading a plain
   name) at any name.

## Blast radius (measured, base worktree at cdac19a6 vs repaired)
* Corpus byte-diff (`bin/byte-diff-sweep.sh` both trees, `bin/byte-diff-compare.py`): root
  1578/1578 `.mlw`, **2 MOVED, 0 GONE, 0 APPEARED** — 1146 and 1172, both route #244's shadow (see
  route #244); pyref 2198/2198, 0 MOVED / 0 GONE.
* Mirror (`bin/mirror-emit-sweep.sh`, `--min-files 50`): 53/53, **3 MOVED, 0 GONE** —
  `module6_whyml/{expressions,statements,stmt_control_flow}`, all route #244's shadow in four
  verified methods; `why3 prove --type-only` clean on all three.
* The FIRST cut (unconditional F/E, trusted bodies scanned) refused **4 corpus files** (1305, 1306,
  1307, 2009 — none of whose claims depends on aliasing: no in-place mutation anywhere in them, and
  1306 is a TRUE claim) and **3 mirror files** (`Module6_WhyMLTranspiler` via its `__init__`
  reading `self.ir.get(...)` into fields, `statements` and `pycsl` via `\trusted` bodies). The
  UNIT-MUT gate and the trusted exclusion took both to zero; no corpus or mirror file is refused.

## Residuals
* An alias made inside an IMPORTED (trusted-in-this-unit) method is not refused in the client unit
  — only the defining module's own run checks it, and that run is UNIT-MUT-gated on the defining
  module alone. Exposing it needs the client to mutate the field directly (`c.d[1] = 5` on a record
  local), which measured FAIL (undecided) at base (`c30_external_mutation_via_obj.py`), or through a
  method of the defining module (which then makes that module's own run refuse).
* Aliasing through containers (`L = [d]; L[0][1] = 5`), through a RECORD value holding a dict field
  (`r2 = r1`), and through module-global dicts is outside this rule (not probed to a proof here).
* `#@ requires 1 not in self.d` fails in the front end ("Undefined variable '_coll'") — fail-closed,
  unrelated to aliasing, recorded because two probes hit it.
