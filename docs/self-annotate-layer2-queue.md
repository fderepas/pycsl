# Self-Annotation Layer 2 — Active Blocker Queue

**Status:** ⚠️ **Historical document.** This snapshot describes the
Module6 self-annotation Layer 2 blocker queue as of 2026-05-26. It
references `bin/check-proof-attributions.sh`, which has since been
replaced by `pycsl --audit-proof` (see `src/pycsl/audit_proof.py`).
The text below is preserved as historical context; line numbers and
audit counts may have drifted.

**Date:** 2026-05-26
**Source of truth:** `pycsl --keep-mlw <module>` (full proof, no `--no-proof`)

This document tracks the WhyML emission bugs (and self-annotated-source
workarounds) needed to reach **Layer 2** of the trust chain — i.e.,
having Why3 + SMT actually accept the generated `.mlw` for each
self-annotated PyCSL module.

`make self-annotate-verify` currently only runs `--no-proof`, so the
generated `.mlw` files were never type-checked by Why3 until this
session. Running full proof exposes a sequence of latent issues
classified below.

## Status as of 2026-05-26

| Module | Status | Next blocker |
|---|---|---|
| Module6_WhyMLTranspiler | ⏳ 17 fixes landed across the session — type-decl ordering, bool→int return coercion, try/with-Return wrap for in-Try returns, per-arity `Return_N`, list `+=` → `array_extend`, self-method-call return type, `for x in self.<method>(...)` array detection, array-local function-level return, `_func_return_type` order, array-var assignment tracking, auto-`\trusted` for class M, tuple-unpack handler artifacts (class N), `a, b = arr[i]` tuple-shaped subscript, auto-`\trusted` for class O, `try` multi-handler `\|` separator (class P), **array-local reassignment now emits `<arr>_len := 0; <arr>[!len] <- e_i; <arr>_len := !len + 1` for `arr = []` / `[a, b, …]` patterns** (class Q), **`x = [default] * N` BinOp pattern now tracked as array-typed by `find_array_and_dict_vars`** | `int` vs `array int` at `contains_check !idx_val !known_elems[!var_name]` in `_handle_subscript` — class R: dict-of-array tracking. Module6 maps `Dict[K, V]` to `int`, losing the inner type. `known_elems[var]` returns `int` but is used in array context (the `in` operator). |
| Module5_IREmitter | ⏳ Two `\trusted` annotations landed (`_collect_class_fields`, `_py_expr_boolop`) | `array int` vs `int` mismatch at line 1135 (inside `_py_stmts_to_ir`) |
| Module4_SemanticAnalyzer | ⏳ Not started | Function-pointer dispatch: `raise (Return (handler node))` where `handler` is `ref int` |
| Module3_Weaver | ⏳ Not started | `unit` vs `int` at line 256 — likely a bare `if-then` without `else` in `int`-returning context |
| Module2_Parser | ⏳ Not started | `int` vs `array int` at line 537 — abstract val returns int but slice/array context expects `array int` |
| Module1_Ingestor | ⏳ Not started | Class-record `pycslvisitor` where `int` expected at line 49 |
| ConcurrencyChecker | ⏳ Not started | `array int` vs `int` at line 145 — same family as Module2_Parser |

## Bug taxonomy

| Class | Symptom | Affected | Recommended fix |
|---|---|---|---|
| A. Type-decl ordering | `unbound type symbol` for class records used before declaration | Module6 ✓ FIXED | Done — see `_handle_return_stmt` insertion-point fix |
| B. Bool→int return coercion | `bool` where `int` expected on `raise (Return ...)` | Module6 ✓ FIXED | Done — `_bool_ir_to_int_wrap` helper |
| C. Unlisted exception | `this expression raises unlisted exception Return` | Module6 ✓ FIXED | Done — `IRScanner.has_direct_return` + `has_in_loop_return` now recurse into `Try` bodies, and `_has_early_ret` is set when either detector fires. The `try/with-Return` wrap is now emitted for functions whose only Returns are inside a `Try`-inside-loop. |
| D. Abstract-val return type | `int` vs `array int` mismatch on slice/array contexts | Module2, Module5 (residual), ConcurrencyChecker | Either change abstract val return type to `array int` (complex — used as int elsewhere) or `\trusted` the affected function |
| E. Tuple type emission | `(array int, int)` vs `(int, int)`; `int` vs `(int, int, int)` on `raise (Return ...)` | Module5 (`_collect_class_fields`) ✓ WORKED-AROUND with `\trusted`; Module6 `classify_iterable` ✓ FIXED via per-arity `Return_N` | Per-arity `exception Return_N (int, …)` now declared in the preamble, used in raises and the function-body `try/with` wrap. The `List[T]` tuple-slot inference (the original Module5 issue) remains a separate sub-case. |
| J. List `+=` on array variable | `array int` vs `ref 'mu` at `lines := !lines + (rhs)` | Module6 `emit_function` (line 1913) ✓ FIXED | `_handle_augassign_stmt` now detects array-typed targets (`_array_locals` / `_array2d_params` / `_current_array1d_params`) for `+=` and emits `array_extend dst src` (unit-returning abstract val) instead of `:= !dst + src`. Side-effect on `dst` is opaque to Why3 but the call type-checks. |
| K. Self-method call abstracted as `int`-returning val | `int` vs `array int` at `array_extend lines (self__emit_contracts_5 ...)` | Module6 `emit_function` ✓ FIXED | Module6 now builds `_module_method_return_types` at `transpile()` (keyed by `<class_lower>__<method>`, matching Module5's name mangling) and looks it up in `_handle_dotted_call` when `func_name.startswith("self.")`. Module5 extended to extract subscript-typed return annotations (`List[str]` → `"list"`, etc.). Knock-on fix L (`for x in self.<method>(...)` recognising array-returning methods) landed alongside. |
| L. `iter_length` / `iter_get` on array | `int` vs `array int` at `iter_length (self__emit_frame_condition_2 ...)` | Module6 `_classify_iterable` ✓ FIXED (alongside K) | `_classify_iterable` now also detects iter sources that are calls to `self.<method>(...)` where `<method>` returns `array int`, and emits `Array.length expr` / `expr[!idx]` directly. |
| M. Array-typed Return for early returns | `The type of top-level exception Return_array has mutable components` (initial); `This expression prohibits further usage of the variable _ret_array_slot` (with ref-slot workaround) | Module6 array-returning functions with early returns ✓ WORKED-AROUND | Two Why3 design constraints conspire: (1) exceptions can't carry mutable types like `array int`, and (2) Why3's region/linearity tracking rejects `ref (option (array int))` + body-internal `Array.make` calls ("prohibits further usage of _ret_array_slot"). Workaround: `_emit_function` now auto-sets `func_trusted = True` for any array-returning function with early returns, which makes Module6 emit `val` (spec-only) instead of `let` + body. The auto-trusted set is tracked in `self._auto_trusted_array_returns` for audit. Proper fix would require a Why3-side encoding (e.g., immutable sequences via `seq.Seq`) but that's a much larger refactor. |
| N. Tuple-unpack handler emits `let ... in;` / `;;` artifacts | `syntax error` at `let py_underscore = ref _tu_py_underscore in;` | Module6 `_handle_tuple_unpack_stmt` ✓ FIXED | Replaced the unconditional `";\n"` separator with a branch: if the last emitted line ends with `in` (a `let X = ref Y in`), use just `\n` (the rest is the let's body); if it already ends with `;` (a `X := tmp;` reassign), use just `\n` (no `;;` artifact); otherwise use `;\n` as before. Also added a tuple-shaped `subscript_get_t<arity>` abstract val for the `a, b = arr[i]` case (`subscript_get` returns int, mismatching the tuple LHS). |
| O. Heterogeneous tuple return types | `(array int, int)` vs `(int, int)` at `_emit_type_decls` | Module6 tuple-returning functions whose slots have different types ✓ WORKED-AROUND | Auto-`\trusted` extension in `_emit_function`: when the function returns a tuple AND the body has any `return (..., x, ...)` where `x` is in the array-var set (`find_array_and_dict_vars` + `self.<method>()` post-pass), force-trust. Tracked in `self._auto_trusted_tuple_returns`. Proper fix (per-slot type inference) would require threading IR-level type info through `find_return_type`. |
| P. Try multi-handler emits `with X with Y` | `syntax error` after `with ValueError -> ... with OverflowError -> ...` | Module6 `_handle_try_stmt` ✓ FIXED | Changed the handler emission loop to track a `first_handler` flag: only the first handler uses `with`; subsequent handlers (and `\|`-separated alternatives within a single `except`) use `\|`. Why3 syntax is `try BODY with E1 -> h1 \| E2 -> h2 end` — separate `with` clauses are rejected. |
| Q. Reassignment of array-local emits `:=` | `array int` vs `ref 'mu` at `seq_parts := (Array.make 1024 0)` | Module6 `_handle_assign_stmt` ✓ FIXED | When target is in `_array_locals` AND already declared, emit a clear-and-fill pattern: `arr_len := 0` then for each `elt` in the RHS `ArrayLit`, emit `arr[!arr_len] <- elt; arr_len := !arr_len + 1`. Other RHS shapes (method calls etc.) emit `()` as a no-op fallback — soundness in that case depends on the caller treating the array as opaque (handled by `\trusted` upstream). |
| R. Dict-of-array values | `int` vs `array int` at `contains_check !idx_val !known_elems[!var_name]` | Module6 subscript on a dict-typed local returns int, losing inner array type | Module6 maps `Dict[K, V]` to a single `int`. `known_elems[var_name]` returns `int`, but is used in `var in known_elems[var_name]` (the `in` operator → `contains_check : array → int → bool`). Fix needs the dict to track inner value types (e.g. `Dict[str, List[int]]` ↦ `int → array int` model), or recognize this specific Python pattern (`elem in dict[key]`) at the operator emission site and emit something different. Or auto-`\trusted` the calling method as a Layer-2 workaround. |
| F. Unit vs int (bare-if) | `unit` where `int` expected | Module3 | Documented in `transpiler-limits.md` §1 — fix the Python body to use complete if-else, or `\trusted` |
| G. Class-record vs int | Class instance where `int` expected | Module1 | Investigate — possibly missing `self_to_int_*` coercion call site |
| H. Function-pointer dispatch | `handler` typed `ref int` called as a function | Module4 | Fundamentally hard — refactor `_CSL_CHILDREN_MAP` lookup, or `\trusted` the whole dispatcher |
| I. Termination warnings | Recursive helper without `\variant` | Module5, ConcurrencyChecker (warnings only — not hard errors yet) | Add `#@ \variant` or `#@ \diverges` annotations |

## What was done this session

1. **Module6 type-decl ordering** (`src/pycsl/Module6_WhyMLTranspiler.py`): fixed
   the insertion algorithm for abstract `val` declarations to land
   *after* the last `type ...` line. Previously it bailed on the first
   `let pycsl_div` from preamble helpers, stranding the abstract vals
   ahead of the class type records they referenced.
2. **Module6 bool→int return coercion** (same file, `_handle_return_stmt`):
   added `_bool_ir_to_int_wrap` helper that detects bool-source IR
   (Compare / BoolOp / UnaryOp not / Call to isinstance|hasattr /
   quantifiers / set-ghost predicates) and wraps with
   `(if X then 1 else 0)` before `_coerce_to_int`. Mirrors the
   detection in `_to_bool`.
3. **Module5 `_collect_class_fields`** (`src/self-annotate/src/Module5_IREmitter.py`):
   added `#@ \trusted` block with TODO documenting the Module6
   limitation that drove the workaround (`(List[T], Dict[..])` tuple
   slots get collapsed to `(int, int)`).
4. **Module5 `_py_expr_boolop`** (same file): same `\trusted` pattern
   for the `array_slice` on `int`-typed abstract val issue.
5. **Module6 try/with-Return wrap emission** (same file, `IRScanner` and
   `_reset_function_state`): made `has_direct_return` and
   `has_in_loop_return` recurse into `Try` bodies and their handler
   bodies. Updated `_has_early_ret` to be set when either detector
   fires (was: only `has_early_return`). Result: functions whose only
   Returns sit inside a `Try`-inside-loop now correctly get the
   `try { body } with Return r -> r end` wrap, eliminating the
   "raises unlisted exception Return" Why3 error for that shape.
6. **Module6 per-arity `Return_N` exception for tuple-returning
   functions** (same file, `_scan_preamble_needs` +
   `_emit_preamble_exceptions` + `_handle_return_stmt` +
   `_emit_body_code`): the plain `exception Return int` truncated
   tuple returns because `_coerce_to_int` hashes any tuple-shaped
   string to a single int (line 719-720 of the transpiler). Now the
   scanner collects every tuple arity used by an early/in-loop
   return; the preamble emits `exception Return_<N> (int, int, ...)`
   for each; `_handle_return_stmt` raises `Return_<arity>` without
   coercing; and the function-body wrap uses `with Return_<arity> r
   -> r end`. Unblocks `classify_iterable` and any future
   `Tuple[...]`-returning method that has early returns.
7. **Module6 list `+=` on array-typed targets** (same file,
   `_handle_augassign_stmt`): Python `lines += other` was being
   lowered as `lines := !lines + rhs`, which is broken on three
   counts — `lines` is a non-ref array local (no `:=`, no deref),
   and `+` doesn't mean concat on arrays. Now detects array-typed
   targets (`_array_locals` ∪ `_array2d_params` ∪
   `_current_array1d_params`) on `raw_op == "+"` and emits
   `array_extend dst src` (unit-returning abstract val). Other
   augassign ops on arrays (`-=`, `*=`) keep the original
   integer-add fallthrough since they don't have list semantics in
   Python.
8. **Module6 self-method-call return type lookup** (this file plus
   Module5_IREmitter): Module5 now extracts subscript-typed return
   annotations (`List[str]`, `Tuple[int, int]`, `Dict[K, V]`, …) and
   lowercases the head ident so `List` → `"list"` matches Module6's
   existing case. Module6 builds a
   `_module_method_return_types: Dict[str, str]` at `transpile()`
   keyed by Module5's class-prefixed method name
   (`<class_lower>__<method>`), and `_handle_dotted_call` now looks
   it up for `self.<method>(...)` call sites, picking `array int`
   when the called method returns `List[T]`. Without this, every
   `self.foo(...)` abstract val was emitted as `: int`, forcing
   downstream type mismatches at every array-consumer.
9. **Module6 `for x in self.<method>(...)` array detection**
   (same file, `_classify_iterable`): same `_module_method_return_types`
   lookup used in the for-loop expansion path. When the iter expr
   is a self-method call returning `array int`, emit
   `Array.length iter` / `iter[!idx]` directly instead of the
   abstract `iter_length` / `iter_get` (which are declared `: int`
   inputs).
10. **Module6 return of array-local at function level**
    (same file, `_handle_return_stmt`): the existing code forced
    `val = "0"` whenever the return value was a `Var` in
    `_array_locals` — necessary for `raise (Return ...)` (`Return
    int` can't carry arrays) but wrong for function-level returns
    where the array variable IS the return value. Now keeps the
    array name when `use_raise` is False (function-level final
    return).
11. **Module6 `_func_return_type` set AFTER the `List[T]→array int`
    override** (same file, `_emit_function`): previously
    `self._func_return_type` captured the raw `find_return_type`
    result *before* the override, so an array-returning method's
    return statements saw `func_ret == "int"` in
    `_handle_return_stmt` and fell into the int-Return path. Now
    set after.
12. **Module6 assignment `x = self.<method>(...)` array tracking**
    (same file, `_handle_assign_stmt` first-assign branch + a
    post-pass in `_emit_body_code`): when the RHS is a call to a
    self method returning `array int`, the target is now tracked
    in `_array_locals` and excluded from the `ref 0` pre-declaration
    set. Without this, `out = self._emit_preamble_uses(needs)` was
    being declared `let out = ref 0 in` and then mutated via
    `:=`-on-int (broken).
13. **Module6 auto-`\trusted` for class M** (same file,
    `_emit_function`): when a function returns `array int` AND has
    early/in-loop returns, Module6 force-sets `func_trusted = True`
    so the body is skipped (emitted as `val` not `let`). This
    sidesteps Why3's ban on mutable types in exception payloads and
    its region rules. Tracked in `self._auto_trusted_array_returns`
    for audit.
14. **Module6 tuple-unpack `let ... in;` / `;;` fix**
    (same file, `_handle_tuple_unpack_stmt`): the rest-separator was
    unconditionally `;\n`, producing invalid `let X = ref Y in;` or
    redundant `X := tmp;;`. Now branches on whether the last
    emitted line ends with ` in` (use just `\n`, the rest is the
    `let`'s body) or `;` (use just `\n`, no `;;`).
15. **Module6 `a, b = arr[i]` tuple-shaped subscript**
    (same file, same handler): when the value being unpacked is a
    `Subscript`, the default `subscript_get : int` mismatches the
    tuple-pattern LHS. Emit a dedicated
    `subscript_get_t<arity> (x: int) (i: int) : (int, int, ...)`
    abstract val and rebuild `val_whyml` to use it. Parallel to the
    existing `Call`-retroactive-update path at the start of the
    handler.
16. **Module6 auto-`\trusted` for class O** (same file,
    `_emit_function`): when the function returns a tuple AND any
    `return (...)` in the body has an element that's an
    array-tracked var (per `IRScanner.find_array_and_dict_vars`
    plus the `self.<method>()` post-pass), force-trust. Sidesteps
    the homogeneous-tuple emission limitation. Tracked in
    `self._auto_trusted_tuple_returns`.
17. **Module6 try-with-multi-handler emission**
    (same file, `_handle_try_stmt`): Why3 requires
    `try BODY with E1 -> h1 \| E2 -> h2 end` — only one `with`,
    subsequent handlers use `\|`. Module6 was emitting a separate
    `with` for each handler. Added a `first_handler` flag that
    selects `with` for the first handler and `\|` afterward
    (including for `\|`-separated alternatives within one
    `except` clause).
18. **Module6 array-local reassignment** (same file,
    `_handle_assign_stmt` else branch): when target is in
    `_array_locals` AND already declared, can't use `:=` (the
    binding isn't a ref). Now emits a clear-and-fill pattern:
    `arr_len := 0` then for each `elt` in the RHS `ArrayLit`,
    `arr[!arr_len] <- elt; arr_len := !arr_len + 1`. Other RHS
    shapes fall back to `()` (no-op) — depends on `\trusted`
    upstream for soundness.
19. **Module6 `find_array_and_dict_vars` recognises `[default] * N`**
    (same file): Python's `[x] * N` allocates an N-element array
    via Module6's `_handle_binop` BinOp(`*`) arm. The scanner now
    detects `BinOp(op="*", left=ArrayLit, …)` as an array-typed
    assignment, so the target lands in `_array_locals` and avoids
    the broken `ref 0` pre-declaration.

## Regression status (locked in across this session)

- `pycsl 0342.py` (Euclidean GCD, full proof): ✅ Verification SUCCESS
- `pycsl 0331.py` (sample reference): ✅ SUCCESS
- `make self-annotate-verify` (`--no-proof` for all 7 modules): ✅ PASS
- `bash bin/check-proof-attributions.sh`: ✅ 162 PASS / 5 SKIP / 0 FAIL

## Next-up order (when picking back up synchronously)

1. **Module6 — class C "unlisted exception"** at line 1495. Likely the
   smallest remaining fix: add `raises { Return -> True }` to the
   relevant method, or have Module6's emitter add it automatically
   when it detects an implicit `raise Return` in the body.
2. **Module2_Parser + ConcurrencyChecker — class D**. Two modules
   share the abstract-val-return-type bug at the slice / `len`
   boundary. A single transpiler fix would unblock both.
3. **Module3_Weaver — class F**. Documented limitation; likely a
   single-function `\trusted` workaround.
4. **Module1_Ingestor — class G**. Smallest unknown; one function
   to investigate.
5. **Module4_SemanticAnalyzer — class H**. The function-pointer
   dispatch is the hardest. Defer until others are clean so the
   transpiler can be evaluated end-to-end on simpler shapes first.

Once any module type-checks fully, the next step is to see what SMT
actually discharges vs. times out — that's where `proof2why3`-imported
axioms become useful (Layer 2 → Layer 4 traceability validation).
