# Plan: real verifiable `collections` models in PyCSL

## Context

PyCSL's `collections` support today is opaque trusted stubs (`src/pycsl_lib/collections.py`
returns ints, `--no-proof`), the demo is stale, and the only test asserts nothing about content.
The user wants **real models so example programs verify with content**, across all members,
tiered by feasibility. The key enabler: the dict model (`map int (option int)`, missing key → 0)
*already is* `defaultdict(int)`/`Counter` semantics, growable lists already work (append + a
length counter), and namedtuple maps onto the just-landed Tier-A parametrized record
construction. So most of this is *recognition + routing to existing proven paths*, not new theory.

**Resolved unknown (growable lists):** `ir_scanner.py::find_append_targets` + `statements.py`
back a `.append` list with `Array.make 1024 0` + `X_len : ref int`; `X.append(v)` →
`X[!X_len] <- v; X_len := !X_len+1`; `len(X)` → `!X_len`. So **deque append/index/len carry real
content**. But `.pop()` is not value-modeled and there is no left-end cursor, so
`appendleft`/`popleft`/`pop` are **infeasible** and documented out-of-scope.

## Per-member mapping

| Member | Tier | WhyML model | Reuses | Boundary |
|---|---|---|---|---|
| `defaultdict(int)` | 1 | `map int (option int)`, missing→0 | dict read/write | factory arg dropped; non-`int` factory out-of-scope |
| `Counter()` | 1 | same dict model | dict read/write | `c[k]+=1` needs the aug-subscript fix; `most_common`/ordering out |
| `deque()` | 1 | `array int`(1024) + `_len` | list/append model | only `append`/`dq[i]`/`len`; left-end & `pop` out |
| `namedtuple('P',[…])` | 1 | record `{x:int;…}` | Tier-A record ctor | literal fields only; dynamic fields → opaque |
| `OrderedDict()` | 2 | plain `map int (option int)` | dict model (alias) | insertion order NOT modeled |
| `ChainMap`/`User*` | 3 | opaque int handle | recognize-and-document | composition/subclass hooks out |

## Implementation (staged; gate each on a named driver, then re-run the corpus for zero regression)

Recognition is **import-independent** — match the bare constructor names (the form after
`from collections import X`), so construction-recognition takes precedence over the opaque stub
with **no `import_classifier` change** and no stub deletion.

- **Stage 0 — defaultdict + Counter (near-zero cost).** Route the three dict ctors to the dict
  model so a local `d = defaultdict(int)`/`Counter()`/`OrderedDict()` is dict-typed and `d[k]`
  read/write already prove. Edits: `ir_scanner.py::find_array_and_dict_vars` (~109-123, add the
  three names → dict-vars; `deque` → array-vars), `ir_scanner.py::uses_inline_set_or_dict_ops`
  (~156-174, preamble trigger), `expressions.py::_handle_call_expr` (~870-885, empty-ctor arms →
  `(const (None: option int))`, drop the factory/iterable arg), `Module5:1063-1065` (the
  `__init__`-field-typing ctor set, for `self.x = Counter()`). *Driver:* 0498 (defaultdict),
  0499 (Counter via explicit `c[k]=c[k]+1`).
- **Stage 1 — Counter `c[k] += 1`.** `Module5::_py_stmt_augassign` (~756-764) has no `Subscript`
  arm, so subscript aug-assign is silently dropped. Add a `Subscript` branch desugaring
  `c[k] op= v` → `ArraySet{array,index,value=BinOp(MapGet(array,index),op,v)}` (reuses the proven
  path; also fixes plain `arr[i] += v`). *Driver:* 0500 (committed `# pycsl-expected: FAIL`,
  flips to PASS).
- **Stage 2 — namedtuple.** New `Module5::_synthesize_namedtuple_records` pre-pass called from
  `visit_Module` (~40-62) BEFORE `generic_visit`: recognize a module-level `Name = namedtuple(<str
  literal>, <list/tuple of str | "x y" string>)` and synthesize a record `type_decl` (fields all
  `int`, defaults 0) with an implicit `__init__` (`init_params=[fields]`,
  `init_body=[{field, Var(field)}]`) in the exact `:1237-1244` shape. Then `Point(a,b)` reuses
  Tier-A `_call_record_constructor` → `{x=a; y=b}` and `p.x` is a record-field read (works today,
  cf. 0441). Non-literal fields → no record (opaque). *Driver:* 0502.
- **Stage 3 — deque (partial).** Covered by the Stage-0 array-var routing + the append model.
  *Driver:* 0501 (`append`/`dq[i]`/`len`); explicitly NO `popleft` test.
- **Stage 4 — OrderedDict + Tier-3 + demo + docs.** OrderedDict falls out of Stage 0 (dict alias).
  ChainMap/User* stay opaque int handles (keep a stub so imports resolve). Rewrite
  `src/pycsl_lib/collections_demo.py` to a real content showcase (Tier-1 functions carry content,
  NO `\trusted`) + Tier-3 opaque wrappers. *Drivers:* 0503 (OrderedDict), 0505 (Tier-3 smoke).

## Reference corpus (`test-suite/corpus/pycsl-reference/`, next free 0498; docstring + `# pycsl-flags:` + `_ = 0 # anchor`)

0498 defaultdict (missing→0, set, postcondition) · 0499 Counter explicit increment
(`c[k]=c[k]+1`) · 0500 Counter `+=` (committed FAIL → flips at Stage 1) · 0501 deque
append/index/len · 0502 namedtuple `Point(a,b).x == a` · 0503 OrderedDict key/value · 0504
**negative** false Counter contract (`ensures c[k]==old+2` after one `+=1`, `# pycsl-expected:
FAIL`) · 0505 Tier-3 ChainMap/UserDict opaque-handle smoke.

## Soundness / out-of-scope (documented, not faked)

deque left-end (`appendleft`/`popleft`) + `pop` not modeled (only right-end append/index/len);
deque/Counter from an iterable modeled as EMPTY (sound under-approximation — never proves
falsely); OrderedDict ordering unmodeled; ChainMap composition + Counter `most_common` ranking
unmodeled; `defaultdict(list/set)` (non-int factory) out-of-scope (the missing-key default is
hard-wired 0); dynamic/non-literal namedtuple fields → opaque factory.

## Verification

Per file: `PYTHONHASHSEED=0 .venv/bin/python src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0498.py`
… 0505 (Tier-1/2 VERIFIED with content; 0500-pre-fix and 0504 FAIL). Full corpus sweep
(`/tmp/proof_sweep.sh` pattern, honor `# pycsl-flags:`/`# pycsl-expected:`, diff vs baseline) after
each stage — edits are additive (new ctor names + a new aug-assign branch + a namedtuple-guarded
pre-pass), so non-collections emission is unchanged. Demo verifies with no `\trusted` on Tier-1.
Docs: `docs/stdlib-coverage.md` + a collections note in static-semantics §1.4 / translational;
`bin/doc-coherency.py --check` green.

## Critical files

- `src/pycsl/module6_whyml/ir_scanner.py` — `find_array_and_dict_vars` (~100-154, local dict/array
  typing — the main recognition edit), `uses_inline_set_or_dict_ops` (~156-174).
- `src/pycsl/module6_whyml/expressions.py` — `_handle_call_expr` empty-ctor lowering (~870-885);
  dict read (~1099) and `_call_record_constructor` (~929) reused, no edit.
- `src/pycsl/Module5_IREmitter.py` — `_py_stmt_augassign` subscript arm (~756-764);
  `_synthesize_namedtuple_records` pre-pass at `visit_Module` (~40-62); `__init__`-field ctor set
  (~1063-1065).
- `src/pycsl/module6_whyml/statements.py` — dict write (~751) / growable-list append model
  (~1121-1388): verify, no edit.
- `src/pycsl_lib/collections_demo.py` — rewrite to content showcase + Tier-3 opaque wrappers;
  `test-suite/corpus/pycsl-reference/0498–0505.py`; `docs/stdlib-coverage.md` + doc surfaces.
