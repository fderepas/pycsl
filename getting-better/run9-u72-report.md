# run #9 u72 report -- O1-O5 repaired (one identity per definition), routes #628 / #629 / #630

Branch `run9-u72` (worktree /home/fabrice/git/pycsl-u72) = run9-u70 (40f4d17f3) + merge of ghost-assign-bc6
(L20; the base tree is f6435f70d, whose src / bin / test-suite / docs equal 4acebf73c). Not pushed.
Logs: `scratchpad/u72/logs/` (relative to the tree root). Tools: `scratchpad/u72/tools/`.

DRAFT -- filled in below as the measurements land.

## 1. Design (FAITHFUL repair, not a narrowing)

All code is inline in `src/pycsl/frontend/ir_resolve.py` (no helper extracted); every edited function's mirror
twin is `\trusted` (`_process_dependency`, `_inject_functions`, `_resolve_direct_imports`,
`_resolve_wildcard_imports`, `_resolve_module_imports`, `_resolve_imported_classes`,
`_resolve_imported_base_classes`). `pycsl.py`, `resolve_imports`, `_resolve_module_path` and the #621 / #622 /
rule-E code are untouched.

### 1.1 `_inject_functions`: one identity per definition (replaces the u70 blanket refusal)

Each batch entry carries its origin file (`_r143_dep_file`, set by `_process_dependency`) and its in-file name
(`_u72_orig` when a caller renamed it: an import alias, a followed re-export). Two transient markers set by the
callers and POPPED here (they never reach the IR): `_u72_bound` (the PROGRAM binds this emitted name to this def:
a from-import local, a wildcard name the program does not redefine, a class method reached by its mangled
`<class>__m`) and `_u72_keep` (the target of a module-qualified call). Per entry:

* name free and not reserved -> injected under its name (unchanged behaviour, byte-identical emission);
* the entry present under the name IS this def (same file, same IR minus `proof`) -> skipped (unchanged);
* program-bound and the name is held by another def -> REFUSED, `PYCSL-SEM-IMPORT-FUNCTION-NAME-CLASH`
  (one program name cannot denote both);
* otherwise (a transitive in-file callee, a module-qualified target, a class's module helper) -> injected
  under a fresh `<name>_from_<module>[_k]`; every call of the batch that CPython binds to it (the same file's
  calls, by in-file name, in bodies AND contracts) is rewritten on a deep copy (the cache is shared); a call
  whose callee is a formal parameter of the calling function is left alone. A renamed entry nothing in the
  batch reaches and the caller does not keep is dropped (as the old code dropped it), so a program whose own
  def wins (O1) emits exactly what L20 emitted.

The reservation table `_u72_reserved` (set by `_resolve_imported_classes`, the first pass; popped by
`_resolve_imported_base_classes`, the last): each from-import local of the program -> (file, imported name),
each builtin the program calls without defining it -> (None, name). A non-bound dependency def whose name is
reserved for ANOTHER binding is renamed, so it can never capture the program's own name (probes x02, x03).

### 1.2 Route #628 (`_process_dependency` + `_resolve_module_imports`)

A requested name that is not an in-file def is followed to its origin when the binding is statically certain:
bound at exactly one site of any form in the module (the route #474 census), no namespace writer pycsl cannot see
(`*`, `globals()`, `setattr`, `__dict__`, ...), and that site is a top-level `from M import X [as name]`
(relative included: package `__init__` re-exports) or `name = b.X` with `b` bound once by a top-level
`import M [as b]`; a package `__init__` hop is refused when a submodule of that name exists. Up to 8 hops. The
origin def is returned under the requested name with its own file tag and in-file name, so it gets its own
identity. The module-qualified caller binds `m.f` to the emitted name of that def; a non-dotted `m.f` that
reaches no def keeps the old bare rewrite (an opaque call) only when nothing can capture the bare name (no
function / type of the IR has it, the program does not call it bare, it is not reserved), and the bare name is
then reserved; otherwise `m.f` stays opaque. `m.C(...)` beside `from m import C` keeps constructing the class.

### 1.3 Route #629 (`_resolve_imported_base_classes`)

The importer's own source says which module each attribute base `r.T` names. For each tail: the file `r`
resolves to is T's only admissible source; REFUSED (`PYCSL-SEM-IMPORT-BASE-CLASS-AMBIGUOUS`) when one tail is
reached through two modules, also written bare with another source, or names a class the file imports under
that name from another module (a local class of that name stays route #345's). A bare-only base that a module
import defines is refused when the bare name is bound by a wildcard import, by a from-import of another source,
by another binding, or when two module imports define it.

### 1.4 Route #630 (`_resolve_imported_classes`, `_resolve_imported_base_classes`)

Methods and helpers go through `_inject_functions` as one batch: methods are program-bound (a program
`def base__m` / `def c__m` is refused), helpers take a fresh name when their name is taken and the batch's
method bodies / contracts are rewritten, so an inlined `obj.m()` calls the library's helper. The base-class pass
also brings, under a fresh name, each module helper a method calls whose name is taken or reserved.
