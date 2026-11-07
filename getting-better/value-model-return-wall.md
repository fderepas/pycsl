# value-model-return-wall.md — the faithful `List[τ]` / `Dict[str,τ]` RETURN value model

**For review. State-of-the-art report on the wall the self-tcb-reduction frontier now sits against.**

## 1. Global picture
PyCSL is a deductive verifier for a Python subset: a 6-module compiler lowers annotated Python to WhyML,
discharged by Why3/SMT (Z3, Alt-Ergo). The **self-annotation** effort mirrors the live emitter
(`src/pycsl/`) into `src/self-annotate/src/` and drives its `#@ \trusted` stub count DOWN by converting each
stub to a **verified body** under a fixed type-safety+frame contract (`requires True / ensures True / assigns
<frame>`), gated by three disjoint oracle planes: fidelity (mirror==live verbatim), whole-file Why3 proof,
and corpus byte-diff-0. Count is **1030**; ledger is **3 axioms** (must stay 3).

## 2. Where the wall sits
A read-only triage (post-commit ce71e3ab, which banked the `pyast_stmt`/psl-loop statement-body-iteration
capability and converted `_collect_class_constants`) found **`no_cheap_remaining`**: the frontier is at a
**value-model floor**. Five otherwise-reachable "collector" stubs are ALL blocked by the SAME thing — the
value model of their RETURN types:

| stub (Module5_IREmitter) | return type | other blockers |
|---|---|---|
| `_extract_generic_arg_names` | `List[str]` | none (pure — the CLEANEST) |
| `_collect_typevar_registry` (§8d) | `Dict[str, Dict[str, Any]]` | dict-literal-variable-value drop; paren bug |
| `_collect_type_params` | `List[Dict[str,Any]]` | `type(tp).__name__` reflection |
| `_collect_union_arms` (§8c) | `Optional[List[emit_ir]]` | worklist termination; is_binop wiring |
| `_collect_class_fields` | `Tuple[List[Dict],Dict[str,int]]` | `ast.walk` descent |

The **common denominator** is: **the emitter int-erases `List[τ]` and `Dict[str,τ]` RETURN types**, so a method
that builds and returns such a value cannot be lowered faithfully. Breaking this one wall unblocks the whole
cluster incrementally (starting with the pure ones).

## 3. The measured defects (the deeper truth — modeling choice, NOT a Why3 limit)
Two independent Gate-S spikes (`scratchpad/gateS_nestedmap.mlw`, `gateS_record.mlw`) proved the FAITHFUL
shapes are **Why3-representable and axiom-free** (Valid, evil-twin refuted). So the wall is a **tool lowering
choice**, not a fundamental limit. The tool's *actual* emission (`scratchpad/tv_probe.mlw`, and the
`_collect_union_arms` emission in §8c) is defective three ways:

1. **`List[τ]` return int-erased.** `List[emit_ir]`/`List[str]` return → a variant arm payload `Arm_k_0 int`,
   so the real element accessor (`args_of : array emit_ir`, or a string list) type-mismatches `int`. The
   value model has no element-typed list return.
2. **[SOUNDNESS] Variable-valued dict-literal construction DROPPED.** `d: Dict[str,τ] = {"k": var}` emits
   `ref (const (None: option int))` — an **empty** map; the `"k": var` entry is never built and `var` is
   unused. A method returning it returns an EMPTY map — a consistent-but-wrong (facade-grade) lowering.
   **byte-diff-0 does NOT catch this** (it is stable across the corpus). If any VERIFIED method (mirror or
   corpus) builds `{"k": var}`, its proof is against wrong semantics → a latent unsoundness. **Needs a
   targeted audit** (grep verified bodies for str-literal-keyed dict literals with variable values).
3. **`Any` int-erased + a type-printer paren bug.** `Dict[str,Any]` → `map string (option int)` (a no-more-int
   leak); and the nested return prints `map string (option map int (option int))` — MISSING parens around the
   inner `(map int (option int))` — which does not even typecheck. The paren bug is a small isolated fix.

## 4. SOTA lens
This is the **no-more-int doctrine** applied to return values: lower each Python type to its faithful WhyML
type class (string/array/map/record), never a convenience int-erase. The faithful targets already exist for
FIELDS/PARAMS in places (e.g. `map string (option ν)` for `set[str]` fields, `array emit_ir` for `args_of`);
the gap is specifically the **RETURN-type printer** and **container-literal construction**.

## 5. Honestly-costed routes
- **R1 (cheapest, recommended first): faithful `List[str]`/`List[emit_ir]` RETURN typing** — make the
  return-type printer emit `array/seq <element>` (not `int`), and the `return [x for …]`/list-build lower to a
  real element-typed seq. Make-or-break: convert **`_extract_generic_arg_names`** (`List[str]`, no other
  blocker) end-to-end, gated. This is the smallest viable increment and validates the mechanism.
- **R2: the paren-fix** (§3.3) — isolated, small; a prerequisite for any nested Dict return.
- **R3: faithful `Dict[str,τ]` + variable-valued dict-literal construction** (§3.2, the soundness fix) — bigger;
  unblocks `_collect_typevar_registry`. Do after R1/R2.
- **Deferred:** the reflection (`type().__name__`), `ast.walk`, and worklist-termination sub-walls on the other
  collectors are ORTHOGONAL to the value model and stay walled after this.

## 6. Honest limits
Full faithful `Dict[str,Any]` typing is a long-term, EXTREME-RIGOR effort (the doctrine says so). This report
does NOT claim to break all five at once. It claims: **R1 (faithful `List[str]` returns) is a bounded,
spike-checkable increment that converts one collector (`_extract_generic_arg_names`) and validates the
return-value model** — the make-or-break the impl plan must spike BEFORE any build. Any new value shape
co-lands an axiom-free Phase2e-style cert (ledger stays 3). The dict-literal-drop is flagged as a **soundness
concern requiring a separate targeted audit** regardless of the conversion.

## 7. The make-or-break question for review
Is **faithful `List[str]` RETURN typing** (route R1) — the return-type printer emitting `array string`/`seq
string` + a real element-typed list build, converting `_extract_generic_arg_names` — achievable as a bounded,
byte-diff-0-gated, axiom-free increment? Or does the return-value model have a deeper obstruction (e.g. the
variant-arm-payload representation is load-bearing elsewhere and cannot carry a seq)? An oracle run (a hand
`.mlw` emitting the faithful `List[str]` return + a `pycsl --fun` on a minimal `List[str]`-returning function)
should CONFIRM or REFUTE before any emitter edit.

## 8. Post-R1 follow-on survey (2026-07-20 driver run) — `no_cheap_liststr`
R1's `Return_seq_str` capability uniquely fit `_extract_generic_arg_names`. Every other `List[str]`-returning
`\trusted` stub carries a DISTINCT second blocker (none cheap):
- `_split_tuple_type` (types.py:568) — return ALREADY lowers (`array string` via `_split_comp_array_string`);
  ONLY 3 intermediate string ops wall it: `str.startswith`/`str.endswith` (bool string ops, not in
  `_STR_VALUE_METHODS`) + string slice `inner[1:-1]`. **The cleanest next conversion** (fix the string ops → it converts).
- ~25 module6 WhyML-text emitters (`_emit_preamble_*`/`_emit_contracts`/`_emit_function`/…) — `out.append("<literal>")`
  hits the **string-LITERAL int-hash** (`_coerce_str_arg`/`stable_hash`, expressions.py:473 — the fable-flagged leak);
  biggest class BUT each also reads dict fields off `needs`/`ir`, so the literal-hash fix alone converts NONE.
- `_collect_2d_params` (Set[str]+sorted+recursive dict-walk); `_coerce_dotted_args` (zip+f-string+coercion chain);
  Module1_Ingestor `_normalize_leading`/`_fold_blocks` (str.strip/regex substrate); from_sexp `_walk_*` (raw Python tuples).
NEXT ESCALATION: faithful `str.startswith`/`str.endswith` + string slice → converts `_split_tuple_type` (spike the slice first).
