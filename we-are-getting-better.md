# we-are-getting-better.md — the int-lowering leaks we found (and mostly fixed)

**Context.** Under the *no-more-int* doctrine (stop modelling every Python value as WhyML `int`;
lower each type to its faithful class — `emit_ir`/`string`/`array`/`map`/`seq`/`real`/record/variant),
the self-TCB-reduction campaign (1294 → 1273 trusted, 23 `_handle_*` handlers converted) surfaced a
long tail of **incorrect `int` lowerings**: places where a value that is really an IR node, a string,
a collection, or an optional was silently modelled as `int` (or `set() → 0`, or `int_to_string`-
wrapped), producing a `This expression has type … but is expected to have type int` type error.

Each one below was a *bug the conversion exposed* — and each fix pushes a value off `int` onto its
real type. That's the "getting better": the trusted core shrinks **and** the model gets more faithful.

Legend: **[FIXED]** landed byte-diff-0 + proven · **[OPEN]** diagnosed, needs a feature · every item
was an actual `expected int` (or int-default) leak seen during a conversion.

---

## A. IR-node parameters/locals typed `int` instead of `emit_ir`

The keystone class: a value that is a typed IR node (`ExprIR`/`StmtIR`, or `x.to_dict()`) was typed
`int`, so any reflection (`.kind`, `.get`, subscript) or recursion (`_expr_to_whyml`) mismatched.

1. **[FIXED]** `node: "ExprIR"` param → `int` (not `emit_ir`). The founding leak — mapped IR-node
   params to `emit_ir` at both the symbol-table and signature layers.
2. **[FIXED]** `pp: Dict[str, Any]` in fstring's hoisted `_fstring_str_part` → `int`; needed `"ExprIR"`.
3. **[FIXED]** `d: Any` in ifexpr's hoisted `_cf5_arr` → `int`; needed `"ExprIR"`.
4. **[FIXED]** `sl: Dict[str, Any]` in slice_access's `_slice_array_or_opaque` → `int`; needed `"ExprIR"`
   (`sl = node.slice.to_dict()` is an emit_ir sub-node).
5. **[FIXED]** `expr: int` in the call-handler helper stubs — `_call_named_builtins`, `_handle_struct_call`,
   `_recognize_field_decode_idiom`, `_emit_contract_logic_symbol`, `_handle_string_value_method` — the
   caller passes `expr = node.to_dict()` (emit_ir); each stub defaulted the param to `int`.
6. **[FIXED]** `_a = expr["args"]` (a SUBSCRIPT node-list) mis-declared `ref 0` (int) instead of an
   `array emit_ir` local; also the `.get`/attribute forms (`node.elts`/`node.parts`).
7. **[FIXED]** `elts = node.elts` mis-declared `ref (IrOther "")` — a *scalar* emit_ir — instead of
   an `array emit_ir`, because `_is_emit_ir_expr` treated a node-LIST attr as a scalar sub-node.

## B. Cross-file method stubs default to `int` (params AND return)

A call from `expressions.py` to a method in `statements.py`/`types.py`/the facade generated a stub
`val self__m (x0:int)(x1:int):int`, discarding the callee's real signature.

8. **[FIXED]** `_seq_operand` (statements.py, real `(ExprIR, set) -> str`) stubbed `(int,int):int` —
   fixed by `#@ requires_method` declaring the real signature.
9. **[FIXED]** `_field_type_of` (types.py, `(ExprIR) -> str`) stubbed to `int`; its result was then
   compared `== "list"` via an int hash. Same `#@ requires_method` fix.
10. **[FIXED]** `_wrap_unannotated_call_with_strict_assert` / `_wrap_call_with_callee_raises_assert`
    (facade) returned `int` → the handler's `return` mismatched `string`. `#@ requires_method` fix.
11. **[FIXED]** A `-> str` cross-file callee was **`int_to_string`-wrapped** at the call site: the
    `_mixin_dep_pseudo_functions` generator dropped a `str` return annotation (kept only
    list/set/dict/frozenset), so the return was treated as `int`. Now `str` propagates.

## C. Undeclared record fields collapse to `set() → 0` (int)

A `getattr(self, "_field", set())` on an *undeclared* mixin field defaults to `set()`, which lowers
to `0`; then `x in <field>` becomes `contains_check x 0` (a string vs int mismatch).

12. **[FIXED]** Declared, in waves as handlers surfaced them: `_variant_types`, `_seq_locals`,
    `_scope_must`/`_scope_all`/`_scope_params`, `_seq_value_types`, `_array_elem_types`,
    `_current_array1d_params`, `_inductive_preds`, `_axiom_logic_funcs`, `_module_func_names`,
    `_sibling_concrete_methods`, `_composed_provider_methods`, `_decode_to_string`, plus the E-1 set
    (`_in_spec`, `_value_semantic`, `_result_alias`, `_heap_var`, …). Each was an `int`-typed `0`
    standing in for a `map int (option _)`.

## D. Union / nested value types collapsed to `int`

13. **[FIXED]** `_module_constants` values are `Union[str,int]`; `_cv = self._module_constants[name]`
    typed `int`, so `_cv.replace(...)` lowered as `replace_2` over ints. Modelled the value type as
    `str` (var union-narrowing) so `isinstance(_cv, str)` is always-true and both branches type-check.
14. **[FIXED]** `_class_constants: Dict[str, Dict[str,int]]` flattened to `map int (option int)` —
    `.get(self_type, {})` came out `'mu -> option int` and the double-subscript `[…][…]` couldn't
    type. Built the nested-map feature (`map int (option (map int (option int)))`); also the inner
    map was `map string`-keyed (should be int-keyed + `str_hash_op`, uniform with the model).
15. **[FIXED]** `_module_method_formal_params.get(func_name, [])` → `array int` (a `Dict[str,List[str]]`
    dict-of-lists, flattened) — **the example that prompted this file.** Built the nested dict-of-lists
    model: `Dict[str, List[T]]` → `map int (option (seq T))`; `.get(k, [])` reads the inner `seq T`
    (empty-seq default), and a local bound to it is classified `seq T` (no snapshot, no int leak).
    Byte-diff 0 + proven; ref test 0746.

## E. Attribute / projection reads → `svalue_of`/`int` instead of the name/discriminant

16. **[FIXED]** `<emit_ir>.kind` → `svalue_of` (a node) instead of `kind_of` (the discriminant string);
    generalized into `_EMIT_IR_STR_ATTRS` for `.var`/`.op`/`.label`/`.name`/`.func`/`.base`/`base1`/
    `base2` — all array-name/name reads that were flowing as int/node.
17. **[FIXED]** A collected string LOCAL (`var = node.var` → `name_of`) was not recognized as `string`
    by `_is_string_expr(Var)` (it checked only the symbol table, not `_string_local_vars`), so
    `var in self._seq_locals` used the *unhashed* `!var` into an int-keyed map.
18. **[FIXED]** `_field_label`'s `record_lower: Optional[str]` collapsed (not `string`) → retyped `str`.

## F. Membership / collection ops → opaque `contains_check` (int)

19. **[FIXED]** `name in self._module_binding_names()` — a method returning `Set[str]` was stubbed
    `int`, so membership fell to `contains_check` (int). Retyped the stub + added method-call-set
    membership recognition.
20. **[FIXED]** `x in getattr(self, "_set_field", set())` did NOT hash the string key for a **set**
    field (only dict fields), so `Map.get _seq_locals !var` used an unhashed string into an int-keyed
    map. Extended the getattr-set-membership `str_hash_op` to set fields.
21. **[FIXED]** `field in self._class_constants.get(self_type, {})` — membership over the inner map of
    a nested-dict `.get` fell to `contains_check` (int) until the nested-map membership was recognized.

## G. Optionals and truthiness → `int`

22. **[FIXED]** `Optional[str]` returns + `if x is not None: return x` couldn't type (the `int`/option
    model of `None`); resolved with the `""`-sentinel + truthiness convention in `_var_todict_alias`
    and (attempted) the call-handler leaves.
23. **[FIXED]** `if subst:` / `if sl.get("lower"):` — truthiness of a `map`/`Optional[ExprIR]` lowered
    as `<> 0` (int). Recognized the present-guard: `map`/`set` param → `true`; emit_ir sub-node → `true`.
24. **[FIXED]** `subst: Optional[Dict[str,str]]` param synthesized a Union variant / int; desugared to
    `Dict` (None ≡ empty map) before lowering.
25. **[FIXED]** `sl["lower"]`/`sl.get("upper")` (SliceExpr bounds) → `subscript_get`/`svalue_of` with an
    int truthiness; routed `lower`/`upper` to the sub-node projection + emit_ir-truthiness.
26. **[FIXED]** `local_refs or set()` (a map-or) lowered as a bool/`int` (`(const None) <> 0`); the
    `_ifexpr_seq_arm` isolate replaced it with `local_refs` (present-set no-op).

## H. Tuple-unpack / list-comprehension typing (int / wrong container)

27. **[FIXED]** Tuple-unpack targets typed `int`: ifexpr's `_bd, _od = a.to_dict(), b.to_dict()`
    (emit_ir) and `_b_str, _o_str = …` / `_b_none, _o_none = …` / `_b_ir, _o_ir = …` (bool) all came out
    as int tuple-targets. Split each into single assignments so each types individually.
28. **[FIXED]** `_seq_value_types.get(d.get("name")) == "string"` compared a map-read to an int hash
    because `_seq_value_types` was undeclared (see C) — the value was `string`, hashed as int.

---

## Meta-pattern (why this list matters)

Every leak here is the same shape: **the int-collapse default fired where a faithful type was
available.** The recurring *sources* of an accidental `int` are now catalogued:

- an **IR-node** without an `emit_ir` annotation (A),
- a **cross-file callee** whose real signature wasn't propagated (B),
- an **undeclared field** defaulting to `set() → 0` (C),
- a **union/nested container** the model can't hold in one slot (D),
- a **projection/attribute** read routed to the opaque node/int instead of its name/discriminant (E),
- a **membership** falling to `contains_check` instead of a hashed `Map.get` (F),
- an **Optional/truthiness** modelled as `None ≡ 0` (G),
- a **tuple/comprehension** target getting the scalar-int default (H).

Fixing them one conversion at a time is exactly the no-more-int doctrine executed as a squeeze: the
count came down 21 markers, and along the way ~28 distinct value-flows moved off `int` onto
`emit_ir`/`string`/`array`/`map`/`seq`. The last **[OPEN]** one (#15, `Dict[str,List]`) is now **[FIXED]** too — `Dict[str, List[T]]`
lowers to `map int (option (seq T))`. Every int-leak class catalogued **in Round 1** now has a faithful
lowering — but the bottom-up-DAG leaf-conversion campaign (2026-07-03) surfaced MORE; see **Round 2**.

---

## Round 2 — int-leaks from the leaf-conversion campaign (2026-07-03)

Converting the giant-DAG helper leaves (`giant-recursion.md`; count 1273 → 1266) surfaced a fresh batch
of accidental-`int` lowerings — the same meta-pattern (the int-collapse default firing where a faithful
type was available), in new spots. 3 fixed, 3 still open.

29. **[FIXED]** a **class-constant lookup dict** (`_METATYPE_TAGS = {"int":"tag_int", …}`) was an opaque
    `getattr` (int) → `k in self.TAGS`/`self.TAGS[k]` failed. Annotate it `Dict[str,str]` → a declared
    abstract `map int (option string)` (contents unmodelled; sound). Converted `_tag_of_type`. Test 0750.
30. **[FIXED]** a **LOCAL dict literal** with all-string values (`scalars = {"int":"int", …}`) →
    `scalars[k]` defaulted to `0` (int); Module5 now infers `dict[_, str]` (default `""`). Test 0751.
31. **[FIXED]** **`str(x)` typed int** — not recognized as string, so `str(x).lower()` fell to an opaque
    scalar op instead of the faithful `str_lower_op`. `_is_string_expr` now treats `str(…)` as string.
    Converted `_quant_binder_whyml`. Test 0751.
32. **[OPEN]** a **string SLICE** `var[len("self."):]` (prefix strip) is typed `int`, so `f"self.{field}"`
    wraps it in `int_to_string`. The slice recognizer + `var=node.var` str-attr recognizer exist but
    hit the **cross-collector fixpoint gap** (the slice checks `_string_local_vars`, but the base is only
    in the accumulating set of `_collect_str_call_result_locals`). Blocks `_handle_arraylen_expr`.
33. **[OPEN]** a **set-valued local/return** (`x=set(); x|=…`, `-> Set[T]`) declares as `ref 0` (int).
    Blocks `_module_binding_names`, the quant-binder push/pop pair. Needs set-local declaration.
34. **[OPEN]** a **BinOp-operand read** `ir.get("left")`/`.get("right")` → opaque `int` (the `emit_ir`
    ADT has no BinOp arm — `left`/`right` aren't projectable). Blocks `_is_float_expr`.

**Round-2 status:** every int-leak class here has a *diagnosis*; #29–31 have a faithful lowering, #32–34
are the next features (mirrored in `giant-recursion.md` §14's OPEN list). The doctrine holds — the
int-collapse default keeps surfacing, and each fix moves one more value-flow off `int`.
