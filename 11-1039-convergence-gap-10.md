# Convergence gap 10 — the module-global / logic-program duality gap (cross-import)

**Loop:** `config/skills/pycsl-stdlib-coverage` — Step 5 (tool gap blocking a model consequence).
**Iteration:** N = 10.
**Blocks:** the os-namespace consequence (`mkdir`→`access`-present) proving **through the public API** (`pure_lib_test/formal_os_namespace.py`). This is the LAST blocker after gap-9 landed the syscall-level proof (commit 134bc7f / `11-0743-convergence-spec-9.md`).

---

## 1. Symptom

`pure_lib/os/__init__.py`'s public wrappers already carry the presence-view contracts the consequence needs (the stdlib-agent added them when gap-9 landed):

```python
# pure_lib/os/__init__.py:115-118
#@ ensures (\result == 1) <==> (dir_lookup(_filesystem.disk, 5, filepath) >= 0)   # access
# pure_lib/os/__init__.py:130 region (mkdir): \result == 0 ==> dir_lookup(_filesystem.disk, 5, filepath) >= 0
```

The os module **emits and type-checks GREEN** with these (`pycsl --no-proof pure_lib/os/__init__.py` → `L3-tc ✓`). But the moment a driver IMPORTS those wrappers, emission fails to type-check:

```
$ .venv/bin/python3 src/pycsl/pycsl.py --no-proof --keep-mlw --deep pure_lib_test/formal_os_namespace.py
[*] Imported from 'pure_lib.os': ['mkdir', 'rmdir', 'unlink', 'link', 'rename', 'access'] (trusted stubs)
[level] L1 ✓  L2 ✓  L3-tc ✗
[!] Emitted WhyML does NOT type-check (L3-tc failed) — NOT a success:
File "pure_lib_test/formal_os_namespace.mlw", line 20, characters 47-55:
unbound function or predicate symbol 'get_disk'
```

The emitted driver `.mlw` head shows the cause precisely:

```whyml
(* pure_lib_test/formal_os_namespace.mlw — emitted *)
  val constant _filesystem : int          (* line 12 — the GLOBAL became an opaque int constant *)
  val get_disk (x: int) : int             (* line 13 — a PROGRAM val (no `function`) *)
  val function dir_lookup (disk: array int) (blk: int) (name: string) : int   (* line 15 — OK *)
  val access (filepath: string) (mode: int) : int
    requires { true }
    ensures  { ((result = 0) || (result = 1)) }
    ensures  { ((result = 1) <-> ((dir_lookup (get_disk _filesystem) 5 filepath) >= 0)) }  (* line 20 — get_disk in LOGIC position *)
```

Contrast with the SAME contract inside the os module's own emission, which type-checks:

```whyml
(* pure_lib/os/__init__.mlw — emitted, L3-tc ✓ *)
  let _filesystem : unixinodefilesystem = { disk = (Array.make 131072 0); ... }   (* line 89 — let-bound record *)
  ...
    ensures  { ((result = 1) <-> ((dir_lookup _filesystem.disk 5 filepath) >= 0)) }   (* line 356 — record-field projection: LEGAL in logic *)
```

So `_filesystem.disk` is a legal logic term **in-module** (a WhyML record-field accessor is a logic function) but degrades to an **illegal program getter** `(get_disk _filesystem)` **across the import boundary**.

---

## 2. Minimal two-file repro (no os, no axioms, 12 + 5 lines)

`/tmp/mgrepro/lib_mg.py`:
```python
class Store:
    #@ class invariant True
    #@ assigns \nothing
    def __init__(self):
        self.disk = 0

_store = Store()

#@ requires True
#@ assigns _store.disk
#@ ensures \result == _store.disk
def get_state() -> int:
    return _store.disk
```

`/tmp/mgrepro/drv_mg.py`:
```python
from lib_mg import get_state

#@ requires True
#@ ensures \result == \result
def use_it() -> int:
    return get_state()
```

Results:
* `pycsl --no-proof lib_mg.py` → **`L3-tc ✓`**. Emits `type store = { mutable disk: int }`, `let _store : store = { disk = 0 }`, `ensures { result = _store.disk }`.
* `pycsl --no-proof drv_mg.py` → **`L3-tc ✗`**, `unbound function or predicate symbol 'get_disk'`. Emits `val constant _store : int`, `val get_disk (x: int) : int`, `ensures { result = (get_disk _store) }`.

This is the exact os symptom, isolated from the directory-scan axiom and from os entirely.

---

## 3. Root cause (file:line)

The importer's IR never receives the dependency's `module_globals`, so when it lowers the injected stub's contract it cannot recognise `_filesystem` as a global record and falls through TWO opaque defaults:

1. **The global name → `val constant _filesystem : int`.**
   `src/pycsl/module6_whyml/expressions.py:1976-1991` — `_handle_var_expr`. The in-module path at **line 1976** (`if name in getattr(self, "_module_global_classes", {})`) resolves a known global to its record binding. The importer's `_module_global_classes` is **empty** (populated from `ir["module_globals"]` at `Module6_WhyMLTranspiler.py:71-72`, which the importer never got), so `_filesystem` misses that branch and hits the generic fallback at **line 1989-1991**: `val constant <name> : int`.

2. **The field access → `(get_disk _filesystem)` program val.**
   `src/pycsl/module6_whyml/expressions.py:1929-1943` — the attribute handler. The in-module path at **lines 1929-1934** (`_gcls = self._module_global_classes.get(_vn)` → `f"{ident}.{self._field_label(...)}"`, the legal record projection) is skipped for the same reason, so `_filesystem.disk` hits the generic fallback at **lines 1941-1943**: `self._add_abstract_op("val get_disk (x: int) : int")` + `(get_disk _filesystem)`. That `val` (no `function` keyword) is a PROGRAM symbol, illegal inside a logic `ensures`.

The deeper origin is at import resolution: `src/pycsl/frontend/ir_resolve.py:284-353` (`_resolve_direct_imports`) injects the dependency's function STUBS (with their contracts) and propagates `module_constants` (lines 319-324) and `inductive_decls` (lines 337-348) — **but NOT `module_globals`**. So the injected `access`/`mkdir` stubs carry contracts referencing `_filesystem`, a name the importer has no IR record for. (The os module's own `module_globals` is set at `Module5_IREmitter.py:148-152`; cross-module it is dropped.)

The matching emitter site for the WORKING in-module form is `src/pycsl/module6_whyml/preamble.py:1102-1123` (`_emit_module_globals`): `let {name} : {rec} = {literal}` — the `let`-bound record whose field projection is logic-legal.

---

## 4. Why the obvious "logic accessor" patch does NOT work (measured)

The naive fix — emit a standalone pure logic symbol for the field, e.g. `val function _filesystem_disk : array int`, and bind the cross-import `_filesystem.disk` to it — is **rejected by Why3**:

```
$ why3 prove -P alt-ergo /tmp/mgrepro/fixed.mlw
File ".../fixed.mlw", line 7: This value is mutable, it cannot be used as pure
```

`array int` is a mutable type, so it cannot be the result of a pure `val function`. The disk view is inherently a mutable array; a standalone pure accessor for it is ill-typed. (Same error for `val constant _filesystem : store` where `store` has a `mutable disk` field — see §5.) This rules out the "logic-view-as-new-symbol" path the dispatch sketched as option A.

---

## 5. Proposed fix — propagate the global as a `let`-bound record (option B), the only form that type-checks

Make the importer reuse the EXACT in-module form: a `let`-bound concrete record plus its record type, so `_filesystem.disk` lowers to the same legal record-field projection the dependency uses. Confirmed VALID end-to-end:

```
$ why3 prove -P alt-ergo /tmp/mgrepro/fixed3.mlw
Goal _filesystem'vc.                       Valid (0.02s, 6 steps)
Goal mkdir_then_access_present'vc.         Valid (0.04s, 13 steps)
```

`fixed3.mlw` is the hand-fixed driver: `type store = { mutable disk: array int }` + `let _filesystem : store = { disk = (Array.make 8 0) }` + the two wrapper `val`s' ensures referencing `_filesystem.disk` + the driver calling `mkdir d; access d`. The consequence threads `mkdir`→`access` through the SHARED `_filesystem.disk` projection and proves VALID — the end-to-end API flip.

The fix is therefore a **propagation in `_resolve_direct_imports`** (`ir_resolve.py`, mirroring the `module_constants`/`inductive_decls` blocks at lines 319-348):

1. Read the dependency's `module_globals` from the cache (`cache[abspath(resolved)]["module_globals"]`).
2. Copy each entry whose name is **referenced by an injected stub's contract** (scope it like the inductive-decl propagation at lines 337-348, so only globals the public contracts actually mention cross — `_filesystem` does) into `ir_data["module_globals"]`, de-duped by name.
3. Ensure the global's record type is RETAINED in the importer's `type_decls` (the `UnixInodeFileSystem` record; it is imported transitively but pruned when otherwise unused — the propagated global re-references it so it must survive type-decl pruning).

Module6 then emits `let _filesystem : unixinodefilesystem = <literal>` (`preamble.py:1102-1123`) in the importer, `_module_global_classes` is populated (`Module6_WhyMLTranspiler.py:71-72`), and the contract reference resolves through the WORKING in-module branches (`expressions.py:1929-1934` and `1976-1977`) instead of the opaque fallbacks — byte-identically to how the os module already emits it.

This is faithful by CONSTRUCTION: the importer's `_filesystem.disk` is the *same* record-field projection symbol the dependency uses, not a fresh axiom-free symbol that could diverge.

---

## 6. Cascade-risk check (the spec-9 warning) — does NOT materialize

The spec-9 report warned that crossing `_filesystem` concretely "cascades into method-inlining of the other imported wrappers." Measured, it does not:

* `apply_inline_globals` (`ir_inline.py:375`) runs on the importer after import resolution and is the inliner. It inlines `g.method(args)` RECEIVERS. The driver functions (`mkdir_then_access_present`, …) call the PUBLIC wrappers (`mkdir(d)`, `access(d)`), never `_filesystem.sys_*()`. There are **no global-method receivers in the driver bodies**, so the inliner is a no-op there.
* The injected wrappers are emitted as **body-less `val` stubs** (`val access … ensures …` — confirmed at `formal_os_namespace.mlw:17`, NOT `let access`). They carry no body to inline and no body for the Phase-3 no-alias check (`ir_inline.py:333-353`) to walk.
* The no-alias check only walks `f["body"]` of the importer's own functions; those never reference `_filesystem`, so it does not fire.

So propagating the global does NOT pull in wrapper bodies. The driver stays the body-less-stub-plus-driver shape it already has.

---

## 7. Follow-on (model turn, after this tool fix lands APPROVED)

With the propagation in place, `pure_lib_test/formal_os_namespace.py`'s `mkdir_then_access_present` / `file_present_after_mkdir` flip **Unknown → VALID through the public API** with no model change (the wrapper ensures are already in `pure_lib/os/__init__.py`). The stdlib-agent's follow-on is only to extend the dual absence/presence ensures to `rmdir`/`unlink`/`link`/`rename` (gap-9 §SCOPE beachhead boundary) — out of scope here.
