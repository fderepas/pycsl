# reconcile-ir-conformance.md — plan to green the IR-conformance golden gate

**Status:** ready to execute. **Branch:** `ghost-assign-bc6` (or a dedicated `ir-conformance-reconcile`).
**Owner:** src/pycsl owner. **Est.:** ~1–2h, dominated by the *audit* (regen itself is minutes).

This is a **maintenance reconcile**, not a language feature — so the "new reference-corpus" rule
does not apply (the conformance goldens under `test-suite/corpus/conformance/core/` ARE the corpus
being refreshed here). It follows the exact remedy `docs/ir.md §10` prescribes and that commit
`18e78c48` ("reconcile IR conformance drift — bump to v1.2, refresh goldens") executed before.

---

## 1. Problem

`bin/run-conformance.sh` is RED, and because it is a **leading hard gate** in
`bin/run-reference-tests.sh` (line ~144 — `if ! run-conformance.sh; then … exit`), it blocks the
whole reference-proof suite from running to completion.

Two corpora, one golden set in `test-suite/corpus/conformance/core/` (38 programs:
`NNNN.ir.json` = frozen *resolved* IR; `NNNN.expected.mlw` = frozen core-emitted WhyML):

- **front-end corpus** (`bin/frontend-only-conformance.py`): source → `--resolved` IR vs golden
  `.ir.json`. **Currently 0 OK / 38 MISMATCH.**
- **core corpus** (`bin/core-only-conformance.py`): golden `.ir.json` → core WhyML vs golden
  `.expected.mlw`. **Currently 37 OK / 1 MISMATCH (0004).**

## 2. Root cause & provenance (verified)

This drift is **pre-existing and multi-epoch** — it was already red at the WL-residual session's
start commit `a657569c`, and predominantly predates it:

| Drift | Source | Predates `a657569c`? |
|---|---|---|
| `ir_version` golden `1.2` vs derived `1.3` | TY1 NoReturn typing (`84357578`) | yes |
| `ir_version` derived `1.4` | TY3 TypeVar/Generic typing (`89f3acec`) | yes |
| `.functions[*]` keys `param_annotations`, `return_value_type` | emitted on *every* function now → explains 38/38 | yes |
| `.functions[*]` keys `param_list_flat_elem`, `param_list_nested_elem`, `param_list_elem_types` | WL-04a/b faithful list-element lowering | yes (04a/b) + extended by WL-04c–g |
| `.type_decls[*].mutable_state` | WL-05 param-mutation family | partly this session (WL-05c/d) |
| `.functions[*] … keywords` (CallExpr) | WL-07 record-ctor keyword capture | this session |
| core `0004.expected.mlw` (1007B vs 741B) | WL-02 true-division `/`→real (`4df1df05`) changed core emission from the same golden IR | yes |

Golden set (all 38 have a `pycsl-reference/NNNN.py` source): `0001 0002 0003 0004 0005 0012 0056
0057 0058 0062 0064 0065 0086 0100 0207 0211 0221 0233 0309 0319 0441 0442 0443 0444 0445 0448 0455
0549 0553 0554 0576 0577 0578 0583 0595 0602 0606 0650`.

**Note:** `IR_VERSION` is **already `1.4`** in `src/pycsl/ir_schema.py` and
`ACCEPTED_IR_VERSIONS = {1.0,1.1,1.2,1.3,1.4}`. So — unlike `18e78c48` — **no code bump is needed**;
the fix is a golden refresh + doc update only.

## 3. Design principle — refresh MUST NOT be a rubber-stamp

Regenerating goldens blesses whatever the current pipeline emits. Because this drift spans typing
work (TY1/TY3) and the WL campaign that this reconcile's author did not all individually review, the
**audit step is the deliverable**, not the regen. The invariant to prove before committing:

> Every `.ir.json` change is CONFINED to (a) the `ir_version` stamp and (b) a closed, enumerated set
> of **additive** keys that default to `false/""/[]` (so a 1.0/1.1 IR without them still validates —
> §7 back-compat check). Every `.expected.mlw` change traces to a KNOWN sound emission change
> (WL-02 division, WL faithful lowering). ANY unexplained content change → STOP, investigate, do NOT
> refresh over it.

If a diff shows a key that is NOT additive (changes an existing key's value in an unexplained way,
or a `.mlw` byte change with no feature behind it), that is a **latent regression the gate just
caught** — treat it as a bug to fix first, exactly as `18e78c48` treated `0100` (a real emitter fix)
and NOT paper over it.

---

## 4. Procedure

### Step 0 — preconditions
- Clean working tree (ignore the `why3-semantics` submodule). `PYTHONHASHSEED=0` for every command
  (the goldens are canonical/hash-stable; §3 determinism obligation in `docs/ir.md`).
- Capture the baseline: `bin/run-conformance.sh 2>&1 | tee /tmp/ircfm_before.txt`.

### Step 1 — enumerate & classify the live drift (audit input)
For each golden, structurally diff derived-vs-golden and collect the union of divergent keys:
```
PYTHONHASHSEED=0 .venv/bin/python3 bin/frontend-only-conformance.py 2>&1 | grep -E 'KEYS|VAL' | sort -u
```
Produce a table: `key → originating feature/commit → additive? (default value) → downstream consumer`.
Cross-check each key is declared in `ir_schema.py` (schema) and defaults inert. This table is pasted
into the commit body (the §2 table is the starting point; confirm nothing beyond it appears).

### Step 2 — regenerate the 38 `.ir.json` goldens
Reuse the runner's OWN serialization (`derive_resolved_ir`) so byte-identity is guaranteed:
```python
# bin/regen-ir-conformance-goldens.py  (throwaway; delete after, or keep gated)
import os, glob, importlib.util
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = os.path.join(ROOT, "test-suite/corpus/conformance/core")
REF  = os.path.join(ROOT, "test-suite/corpus/pycsl-reference")

# import derive_resolved_ir from the front-end runner (identical canonical json.dumps(indent=2))
spec = importlib.util.spec_from_file_location("feconf", os.path.join(ROOT,"bin","frontend-only-conformance.py"))
fe = importlib.util.module_from_spec(spec); spec.loader.exec_module(fe)

for g in sorted(glob.glob(os.path.join(CORE, "*.ir.json"))):
    name = os.path.basename(g)[:-len(".ir.json")]
    ir = fe.derive_resolved_ir(os.path.join(REF, f"{name}.py"))   # source -> resolved IR, canonical
    open(g, "w").write(ir)
    print("ir.json", name)
```
Run under `PYTHONHASHSEED=0`.

### Step 3 — AUDIT the `.ir.json` diff (gate #1)
```
git diff --stat test-suite/corpus/conformance/core/*.ir.json
git diff test-suite/corpus/conformance/core/*.ir.json | grep '^[+-]' | grep -vE '"ir_version"' \
  | grep -oE '"\w+":' | sort | uniq -c | sort -rn
```
- Confirm the ONLY added/removed lines correspond to the classified additive keys + `ir_version`.
- If any *existing* key's value changed (not just added keys), open that file and justify or STOP.

### Step 4 — regenerate the 38 `.expected.mlw` from the NEW goldens
Reuse the core-only path exactly (`Module6_WhyMLTranspiler(wire).transpile()`, no front-end import):
```python
# append to the regen script, or a second script that imports ONLY the core
import json
from pycsl.core_ir.validate import validate_ir            # (match the imports core-only-conformance uses)
from pycsl.core_ir.semantic import run_ir_semantic_checks  # ← confirm exact module paths from that runner's header
from pycsl.module6_whyml import Module6_WhyMLTranspiler
for g in sorted(glob.glob(os.path.join(CORE, "*.ir.json"))):
    base = g[:-len(".ir.json")]; wire = open(g).read()
    ir = json.loads(wire); validate_ir(ir); run_ir_semantic_checks(ir)
    open(base + ".expected.mlw", "w").write(Module6_WhyMLTranspiler(wire).transpile())
```
(Take the precise `validate_ir` / `run_ir_semantic_checks` / transpiler import lines verbatim from the
top of `bin/core-only-conformance.py` so the emission matches the gate byte-for-byte.)

### Step 5 — AUDIT the `.expected.mlw` diff (gate #2)
```
git diff --stat test-suite/corpus/conformance/core/*.expected.mlw
```
- **Expectation:** very few `.mlw` change. The new IR keys are metadata → mostly emission-inert.
- **0004** MUST change (WL-02 division fix) — open it, confirm the change is int-div→real-div /
  the reclassified contract, i.e. the sound WL-02 behavior, matching `pycsl-reference/0004`'s current
  proof. Any OTHER `.mlw` that changes must be traced to a specific WL/typing emission change and
  confirmed sound (re-prove the corresponding `pycsl-reference/NNNN.py` → still SUCCESS). Unexplained
  `.mlw` drift → STOP (a real regression the gate caught).

### Step 6 — update `docs/ir.md`
- Add the `1.3` and `1.4` rows to the version table (fields introduced: TY1 NoReturn markers → 1.3;
  TY3 monomorphization → 1.4; and the WL additive keys `param_list_*`, `param_annotations`,
  `return_value_type`, `mutable_state`, CallExpr `keywords`), each with type + default + downstream
  consumer, mirroring the §2 (v1.2) documentation style.
- Confirm `ir_schema.py`'s `_REQUIRED_*` and field docs already list these keys (they're emitted, so
  they should be — if a key is emitted but undocumented in `ir_schema.py`, add it there too).
- Run `bin/doc-coherency.py --check` (unrelated to ir.md but keep it green).

### Step 7 — verify (all must pass)
```
PYTHONHASHSEED=0 bin/run-conformance.sh          # → core 38/38, front-end 38/38 (0 skew), determinism 10/10
```
- **Back-compat:** a pre-refresh 1.0/1.1/1.2 IR (e.g. `git show a657569c:test-suite/corpus/conformance/core/0001.ir.json`)
  still passes `validate_ir` (the ACCEPTED set includes it) — confirms the refresh is additive, not
  a breaking bump.
- **Determinism:** the runner's built-in 10/10 PYTHONHASHSEED 0-vs-1 sample must stay green.
- **Leading-gate unblocked:** `bin/run-reference-tests.sh` now passes its conformance gate and proceeds
  (spot-run a slice, e.g. `--start-at 1 --stop-at 20`, to confirm it no longer aborts at the gate).

### Step 8 — commit
```
fix(ir): reconcile IR conformance drift — refresh 38 goldens to ir_version 1.4 (TY1/TY3 + WL additive keys)
```
Body: paste the Step-1 classification table (key → feature → additive/default → consumer); state that
`IR_VERSION` was already 1.4 (no code bump); list the `.expected.mlw` files that changed with the
per-file sound-change justification (expected: only 0004 + any traced WL emission file); note the
back-compat + determinism verifications. Delete the throwaway regen script (or keep it as
`bin/regen-ir-conformance-goldens.py` with a header if it's judged reusable). End with the
`Co-Authored-By: Claude Opus 4.8` trailer. Do NOT touch `why3-semantics`.

---

## 5. Safety / abort conditions (when NOT to refresh)
- A `.ir.json` diff touches a key NOT in the classified additive set, or mutates an existing key's
  value inexplicably → STOP; that key change is a candidate regression, fix the emitter first.
- A `.expected.mlw` changes for a program with no WL/typing feature behind it → STOP; re-derive and
  investigate (this is exactly what the core gate exists to catch — treat like `18e78c48`'s 0100).
- Determinism sample goes non-green → a hash/set-ordering leak was introduced; fix the sort at the
  set→list boundary (`docs/ir.md §3`) before refreshing.

## 6. Rollback
`git checkout -- test-suite/corpus/conformance/core/ docs/ir.md` (goldens + doc are the only touched
tracked files; the regen script is untracked). Nothing else is affected — this reconcile is confined
to the IR/conformance layer (no emitter, prover-dispatch, or corpus-source change).

## 7. Out of scope
- No change to `src/pycsl/` emission logic — if the audit finds a real regression, that is a
  SEPARATE bug/commit, fixed before the refresh proceeds.
- The self-annotation mirror-sync gate (already green) and the WhyML byte-diff additivity gate
  (green) are untouched.
- Any future IR field must follow `docs/ir.md §10` at introduction time (bump + refresh + doc in the
  same commit) so this multi-epoch drift does not recur.
