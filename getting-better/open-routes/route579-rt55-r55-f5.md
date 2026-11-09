# OPEN ROUTE #579 — #567 / #574 THE NON-IR NARROWING TRUSTS A CLASS BY NAME: A FILE-DEFINED CSLFieldAccess, OR ast.Name / ast.Call WHERE ast IS A USER CLASS / ALIASED USER MODULE, IS TREATED AS AN IR CLASS
**Status: REPAIRED (driver run #6, executor u36 off 822621340 = ghost-assign-bc6 at run #6 start, branch run6-u36; annotations §7.579). Mechanism: IR-class identity by RESOLUTION -- `pycsl.py::_run_pipeline` collects every binding of every name of the source and hands Module 6 `ir_class_targets_r579`, the names bound ONLY by one import of a real pycsl IR module found at the real file (`frontend.pure_ast` as `ast`, `frontend.Module2_Parser.FieldAccess` as `CSLFieldAccess`, `ir_schema.<Node>`) or of the standard-library `ast`; the isinstance-on-emit_ir recognizers and route #567's narrowing judge admit a class only through it (`expressions.py::_handle_isinstance` / `_handle_attribute_expr`, twins `\trusted`; inline, no new def, no axiom); a projector read on a value narrowed by an unresolved IR-class spelling is refused, new `PYCSL-R579-IR-CLASS-NOT-RESOLVED`.** Opened as: Status OPEN, Severity 1 (driver run #5, 2026-11-07, red team rt55 family R55-F5). Evidence: the REPAIR section below.
Exemplar witnesses-r579/gg1609_user_cslfieldaccess.py. Driver repro 2026-11-07T19:4xZ (scratchpad/run5/rt55repro.txt): Verification SUCCESS on BOTH main (pycsl-mainbase, before the L1 landing) and run5-int51, while CPython breaks the claim — PRE-EXISTING, not introduced by the run #5 changes being landed.

## REPAIR (driver run #6, executor u36, base 822621340, branch run6-u36, commit c0058a372 + the docs commit)

- RULE (annotations §7.579): `pycsl.py::_run_pipeline` walks the standard-library AST of the source and collects every
  binding of every name (imports, `def`s, classes, stores, parameters, `except` / `match` captures, `global` / `nonlocal`,
  type parameters; all scopes, flow-insensitive). A name is RESOLVED only when ALL its bindings are one import of
  `ast` (standard library), `frontend.pure_ast` (as `ast`), `frontend.Module2_Parser.FieldAccess` or `ir_schema.<Node>`,
  the pycsl module found by pycsl's own import resolution (`ir_resolve._resolve_module_path`) AT THE REAL FILE
  (`realpath` under the running `src/pycsl`); a star import or `globals()` / `vars()` / `exec` / `eval` / `__import__` /
  `.modules` leaves every name unresolved. The table goes to Module 6 as `transpiler.ir_class_targets_r579` (absent:
  nothing resolves). `_handle_isinstance`: an unresolved `ast` namespace is re-spelled so no `ast`-keyed recognizer fires
  (the test takes the generic uninterpreted arm); the CSL recognizer needs `CSLFieldAccess` resolved; the two
  `ast.Constant` compound guards need `ast` resolved. `_handle_attribute_expr` (route #567's judge): a bare name is an IR
  class only when resolved, `<ns>.<Node>` only when `<ns>` is a resolved `ast`; a projector read on a value narrowed by an
  unresolved spelling route #567 used to trust is refused with `PYCSL-R579-IR-CLASS-NOT-RESOLVED` (naming the spelling),
  every other narrowing keeps `PYCSL-R567-EMITIR-ATTR-ON-NONIR` (message unchanged). Mirror twins all `\trusted`; inline,
  no new def, no new emitter field, no axiom (ledger 3).
- WITNESSES (`--no-proof` front end; x default / typed / store): the 7 rt55 witnesses 21/21 REFUSED R579 (at base: all
  EMITTED; the driver measured gg1609 PROVED). u36 probes `witnesses-r579/u36-probes/` (a `class ast:` with nested
  dataclasses, `ast` rebound at module level, a parameter named `ast`, the `irm.Name` namespace, `sys.modules["ast"] =
  ...`, `from rt55dep_ir import Name as CSLFieldAccess`, a tuple `(ast.Name, CSLFieldAccess)`): 21/21 REFUSED (R579 x 5
  per model; the module-level rebinding and the `sys.modules` write by the pre-existing name-rebinding / namespace rules).
- CORPUS: 9270-9276 FAIL (PROVED at base 822621340, default model; REFUSED R579 x 3 models at HEAD), 9277 (`irm.Name`)
  and 9278 (tuple) FAIL (at base Verification FAILED by a 30 s postcondition timeout over the `kind_of` misprojection,
  as route #567's 9025; REFUSED at HEAD). Controls 9279 (`import ast` resolved in a file that also defines a
  `CSLFieldAccess`: `node.id` read twice is one value, `\result == 1`) and 9295 (R579's advice: `node: CSLFieldAccess`,
  no isinstance, two-sided claim; = `witnesses-r579/advice/a579_record_typed_param.py`) PASS at base and HEAD.
- OVER-REFUSAL / INERTNESS: see the run #6 README entry (corpus root, pyref, mirror and rt55 controls unchanged).
- RESIDUAL (named): the pure_ast parser's own `isinstance(x, _N("<Cls>"))` recognizer is gated on the parser's file
  signature (`_Parser._fin`), not on a resolution.
- INERTNESS (vs the driver base scratchpad/run6/base): corpus root 3023 -> 3030 .mlw 0 MOVED / 0 GONE / 0 APPEARED (+7 new
  controls), python-reference 2185 0 / 0 / 0, mirror 53/53 0 / 0 / 0 (nothing owed); rt55's 208 honest controls (CPython
  does not breach them): front-end verdicts identical, 81 emissions byte-identical. Fidelity / planes: run #6 README entry.
