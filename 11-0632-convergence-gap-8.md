STATUS: OPEN — TOOL GAP (not an SMT wall; not Rocq+Lean-closable)

# Convergence gap — iteration 8 (the shared `name_present` view cannot cross the module-level `val` import boundary as a LOGIC symbol)

**Loop:** `config/skills/pycsl-stdlib-coverage`.
**Predecessor:** `11-0605-convergence-gap-7.md` (§A: the os namespace consequences are
Unknown through the public API because the syscall contracts are return-code-only).
**Iteration:** N = 8.

## Summary of the gap-7 fix attempt and where it WALLED

gap-7's prescribed fix is a SHARED abstract "name present" view that mutators establish
(`mkdir(d)` ⇒ `name_present(d)`) and observers reflect (`access(d) == 1 <==> name_present(d)`).
The mechanism that the contract language offers for a module-level shared logic symbol is
`#@ inductive` (a Why3 `inductive`/`predicate`). It works PERFECTLY inside the defining module
but is DROPPED across the `from pure_lib.os import mkdir, access` boundary that
`formal_os_namespace.py` crosses — and the abstract-op fallback the importer substitutes is
**type-illegal in logic position**, so the importing module does not even type-check.

### Reproducer (minimal, two files)

`osmod.py` (the model — proves in isolation as a logic predicate):
```python
#@ inductive present(name: str):
#@     present_intro: \forall n: str; present(n) ==> present(n)

#@ ensures \result == 0 or \result == -1
#@ ensures \result == 0 ==> present(filepath)
def mkdir(filepath: str, mode=0o777) -> int: ...

#@ ensures \result == 1 or \result == 0
#@ ensures (\result == 1) <==> present(filepath)
def access(filepath: str, mode) -> int: ...
```
`test_os.py` (the caller — the shape `formal_os_namespace.py` actually is):
```python
from osmod import mkdir, access
#@ ensures \result == 1
def mkdir_then_access_present(d: str) -> int:
    rc = mkdir(d, 0o777)
    if rc != 0: return 1
    return access(d, 0)
```

**Defining module (`osmod.mlw`) — CORRECT:** the predicate emits as a logic symbol and is
referenced in logic position:
```
inductive present string =
  | Present_intro : (forall n : string. ((present n) -> (present n)))
...
val access (filepath: string) (mode: int) : int
  ensures { ((result = 1) <-> (present filepath)) }
```

**Importing module (`test_os.mlw`) — BROKEN:** the import resolver
(`src/pycsl/frontend/ir_resolve.py`) injects the imported FUNCTION stubs but NOT the
`#@ inductive` declaration they reference. The importer therefore sees `present(filepath)` as
an unknown call and the abstract-op fallback (`src/pycsl/module6_whyml/expressions.py`,
`_handle_dotted_call` / the bare-`Call` arm) emits a PROGRAM value:
```
val present_1 (x0: int) : int          (* program val — NOT a logic predicate *)
...
ensures { ((result = 1) <-> (present_1 filepath)) }   (* present_1 in logic position *)
```
Two compounded faults, BOTH in `src/pycsl/` (cannot be fixed from the model side):

1. **Logic-vs-program kind.** `present_1` is emitted as a program `val` (effectful), which is
   ILLEGAL inside a Why3 `ensures` formula. Why3 reports
   `unbound function or predicate symbol 'present_1'`. (A logic `predicate`/`function` is
   required; the abstract-op fallback only ever emits a program `val`.)
2. **Argument mistyping.** The fallback defaults the predicate's arg to `int`
   (`param_types.append("int")`), so even were it logic-kinded it would be `present_1 : int → …`
   applied to a `string` — a type error. The enclosing imported stub's own symbol table DOES
   know `filepath : string` (it is the stub's declared parameter), but the abstract-op generator
   never consults it for a contract-referenced symbol (it infers only `int` or `array int`).

Because of (1)+(2), `pycsl pure_lib_test/formal_os_namespace.py` cannot even type-check once the
os public contracts carry a `name_present` predicate — so NONE of the seven consequences can flip
Unknown→Valid through the module-level API as the test is written today.

## Why this is NOT model-fixable and NOT an SMT/Rocq+Lean wall

- It is **not** an SMT/Alt-Ergo/Z3 timeout on an inductive/loop property, so the standing
  "close it with a cross-validated Rocq + Lean axiom" valve does NOT apply — the file never
  reaches the prover (it fails the L3 type-check gate first).
- It is **not** fixable in `pure_lib/os/` (the stdlib-agent's surface): the defining module is
  already correct; the fault is purely in how the IMPORTER lowers a contract symbol it did not
  receive a logic declaration for.
- It is **not** fixable in `formal_os_namespace.py` without simulating: the test imports only the
  public functions (`mkdir`/`access`/…), as a caller must; it does NOT (and per the loop rule
  MUST NOT) import os internals or a `name_present` predicate. The module-level wrappers go through
  the pure-`val` boundary that drops the global `_filesystem`, so the two `val`s share no state and
  the ONLY thing that can tie them is a shared logic symbol — exactly what the boundary drops.

  (Contrast: `formal_os_io.py` proves some scenarios because it constructs `UnixInodeFileSystem()`
  LOCALLY and calls INSTANCE methods — those carry `self` + `writes self.disk` + self-field
  ensures across the boundary. The namespace test uses the GLOBAL `_filesystem` via module
  wrappers, which the importer abstracts to stateless `val`s.)

## EXACT tool fix required (for a tool-agent — `src/pycsl/`)

The shared "name present" view CAN be carried across the import; the resolver+emitter must
propagate a contract-referenced LOGIC symbol as a logic symbol. Two coordinated changes:

1. **`src/pycsl/frontend/ir_resolve.py`** — when injecting imported function stubs, ALSO inject
   the `#@ inductive` (and any module-level logic `predicate`/`function`) declarations that those
   stubs' contracts reference, so the importer emits the real `inductive present string = …`
   (and registers `present` in `_inductive_preds`). Today only `ir_data["functions"]` and
   `module_constants` are propagated; `inductive_decls` (carried in the dep IR, emitted by
   `module6_whyml/preamble.py:_emit_inductive_decls`) is not.

2. **`src/pycsl/module6_whyml/expressions.py`** (fallback, in case the decl is genuinely absent) —
   when a contract references an UNKNOWN symbol in logic position, emit it as a logic
   `predicate <name> <argtypes>` / `function <name> <argtypes> : <ret>` (NOT a program `val`),
   and TYPE its args from the enclosing stub's symbol table (`_current_symbol_table` /
   `_formal_params`) so a `str`-typed parameter yields a `string` arg, not `int`.

### THE EXACT shared lemma the consequences then rest on (name it for the registry)

Once the predicate crosses correctly, the seven consequences reduce to instances of ONE
universally-quantified namespace law that the syscall contracts express and the bodies must
discharge (the byte-codec connection between the dirent writes and `_dir_lookup`'s scan):

> **`namespace_present_after_mkdir`** — for all filesystem states `s` and names `d`:
> if `sys_mkdir(s, d)` returns `0` then `name_present(s', d)` holds in the post-state `s'`,
> where `name_present(s, d) ≡ _dir_lookup(s, 5, d) >= 0`; and dually
> `access`/`_dir_lookup` reflects it: `sys_access(s, d) == 0 <==> name_present(s, d)`.

The body proof of `namespace_present_after_mkdir` connects `_write_entry`'s `_pad_name`
byte writes (`disk[off+k] = ord(d[k])`) to `_dir_lookup`'s 16-slot decode-and-compare scan.
That scan's "exists a slot whose decoded name == d" is the **quantified-slot / variable-length
loop round-trip** already flagged as an SMT wall in `10-2204-convergence-gap-4.md` §4a and
`10-2300-convergence-gap-5.md` (the inductive step `out == substring(name, 0, j)` over the decode
loop). THAT inductive lemma — and ONLY that one, AFTER the tool fix above lets the predicate cross —
is the legitimate **cross-validated Rocq + Lean** target (skill Step 5b, `_AXIOM_REGISTRY`):

> **Rocq+Lean lemma `dirent_scan_reflects_present`**: for a directory block whose slot `k` holds
> `_pad_name(d)` with a nonzero inode, the bounded scan `_dir_lookup` returns that inode
> (`>= 0`); and for a block containing no slot decoding to `d`, it returns `-1`. I.e. the
> 16-slot decode-and-compare scan is a faithful reflection of `name_present`. (Z3/Alt-Ergo
> Unknown/timeout on the quantified-slot existential; the per-char codec round-trip
> `chr(ord(c)) == c` is already a theory lemma — gap-5 — so only the scan quantifier remains.)

## What WAS landed this turn (the achievable, byte-safe model improvements)

- **gap-7 §B fixed:** `stat`/`lstat`'s `filepath` param annotated `: str`
  (`pure_lib/os/__init__.py:307,314`), so an inode-returning observer is str-usable through the
  API (no longer a WhyML `int`-vs-`string` emission error). os still proves (1804/1804 Valid VCs);
  corpus byte-diff IDENTICAL; conformance 38/38; doc-coherency green.
- **The `name_present` post-state `ensures` were NOT added to the public wrappers**, because doing
  so makes `formal_os_namespace.py` fail the L3 type-check (the predicate-crossing tool gap above) —
  i.e. it would turn a documented Unknown into a hard EMISSION error for the caller, which is worse.
  They are held until the tool fix lands. (The instance-method `sys_*` contracts CAN carry a
  `name_present(self, …)` over `self.disk` — that is the next sound step once a namespace
  formal test drives a LOCALLY-constructed `UnixInodeFileSystem()`, the `formal_os_io.py` shape.)

## Honest gate status this turn

1. `formal_os_namespace.py`: still 7/7 Unknown (UNCHANGED). The targeted consequences do NOT yet
   prove through the module-level API — blocked by the predicate-crossing TOOL gap above, not by
   the model contracts and not by an SMT wall the model can close.
2. os re-proves: SUCCESS, 1804/1804 Valid VCs (the `stat`/`lstat` str annotation is discharged).
3. Byte-diff sweep (corpus): IDENTICAL before/after.
4. Conformance 38/38; doc-coherency green.
