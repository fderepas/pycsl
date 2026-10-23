# Phase 0 — A-list / A-dict returned-collection census (re-classified under C/D/T1/T2)

**2026-07-09. MEASUREMENT ONLY** — no `src/pycsl` / mirror edits, ledger untouched, `\trusted`=1239.
Executes `bigger-build.md` §7 residual + `phase3.md` §2 (the collection go/no-go), **re-run with the
now-landed traversal mechanisms in scope** (`ir-traversal-residual-stand-alone-plan.md`): **C** (guard
classification — semantic guards are unconstrained booleans), **D** (traversal outlining — composition of
recognized sub-algebras), **T1** (functorial-map / reconstruction), **T2** (option/first-match), **A-bool**.

Reproducibility: `scratchpad/phase3_census.py` (AST pre-filter) + `scratchpad/phase3_census_rows.json`
(per-method rows). Every self-recursive candidate (the true fold set) was **hand-verified against its live
`src/pycsl` body**; the pre-filter alone over-counts (SKILL §10) and cannot decide.

---

## 0. Bottom line — GATE VERDICT

| family | pool (result-typed builders) | **CLEAN (live-verified)** | T1-covered | needs-new-capability | out-of-pattern | verdict |
|---|--:|--:|--:|--:|--:|---|
| **A-list** | 74 | **0** | 0 | 0 (1 borderline) | 73–74 | **BANK** (clean 0 < 5) |
| **A-dict** | 39 | **0** | 0 | 2 | 37 | **BANK** (clean 0 < 5) |

**Both families BANK.** C/D/T1/T2 **did NOT materially raise the clean count over phase3.0's 0 / 1** — and
the phase3.0 "1 clean A-dict" (`_subst_type_in_ir`) has since been **CONVERTED via T1** (it now carries a
full `requires/ensures/assigns \nothing` contract in the mirror and is gone from the trusted pool), so the
residual clean count is **0 / 0**. This is the honest, expected outcome the task framing anticipated.

**Why the mechanisms don't help here (the deciding reality):** the A-list/A-dict residual is not blocked by
*guards* (which C dissolves) or by *composition of recognized folds* (which D dissolves). It is blocked by
**external dependencies C/D cannot dissolve** — unresolved runtime context maps (`arg_nodes[k]`,
`rename_map[(g,c)]`, `param_map[nm]`, `getattr(self, "_module_..._map")`), non-algebra sibling helpers
(`_type_str`, `_expr_to_whyml`, `_py_expr_to_ir`, `_expand`/`_fresh`), string-theory ops
(`.rsplit`/`.partition`/`.split`/`.startswith`), and in-place subject rewrite. The one genuinely *new*
signal is a **2-method A-dict grouping shape** (returned string-keyed dict) — a clean structural fold that
needs only a returned-collection RESULT model — but 2 < 5 and it is not worth a per-family build alone.

**Proceed:** neither A-list nor A-dict GOes. Ledger the residual `TRUSTED(essential)`. If A-dict is ever
revisited, the **first build** is the returned **string-keyed dict** grouping fold (reusing the *already
certified* `sdict` from Phase C — **no new certificate**), converting `find_record_var_classes` +
`_collect_tuple_array_locals`; gated by whether 2 methods justify the template + recognizer work (they
do not, today).

---

## 1. Method — the self-recursive fold set is the only real candidate pool

A catamorphism needs a **self-recursive walk** (the descent into the tree). Of the 74 A-list + 39 A-dict
trusted builders, only **7 A-list + 7 A-dict are self-recursive** (`self_rec` in the rows). Every one was
read in full. The remaining **67 A-list + 32 A-dict are `no-self-recursion`** — flat single-level
iterations (`for stmt in body: … helper(stmt)`) that COMPOSE the emitter's non-algebra string builders
(`_expr_to_whyml`, `_py_expr_to_ir`, `_add_abstract_op`, `_emit_function`, …). **D does not dissolve these**
because D requires each sub-traversal to be a *recognized algebra*; these siblings are leaf string emitters,
not folds. They are definitionally out-of-pattern for a catamorphism generator (they are the emitter's
dispatch/build core), and are counted out-of-pattern without further per-method snippets.

---

## 2. A-list (74) — CLEAN 0 / T1-covered 0 / needs-cap 0 / out-of-pattern 74

### 2.1 The 7 self-recursive A-list candidates (all rejected)

| file::name | LIVE-body deciding feature | bucket |
|---|---|---|
| `module6_whyml/expressions.py::_subst_params` | T1 reconstruction, BUT leaf replaces `Var` by `arg_nodes[ir["name"]]` — **external context-map** substitution (runtime-key param dict → arbitrary pyval) | out-of-pattern |
| `frontend/monomorphize.py::_scan_node_for_subscript_calls` | returned `List[Tuple[str,str]]` (list-of-**tuple**) + sibling **`_type_str`** (non-algebra string renderer) | out-of-pattern (borderline: list-of-tuple result-model gap) |
| `module6_whyml/ir_scanner.py::_collect_mutations` | by-ref `List[node]` (appends whole IR nodes) + `func.rsplit(".",1)` **string op** + `_MUTATING_METHODS` membership; fixed-child recursion | out-of-pattern |
| `module6_whyml/ir_scanner.py::find_iteration_mutations` | builds `List[record-dict]` with computed fields + composed with `_collect_mutations` (by-ref sub-walk) | out-of-pattern |
| `frontend/ir_inline.py::_hoist_calls_in_expr` | T1 reconstruction, BUT calls `_global_call_target`/`_fresh`/`_expand` (effectful siblings) + `func.partition(".")` string op + mutates a `pre` list | out-of-pattern |
| `frontend/ir_inline.py::inline_stmts` | heavily composed (`_expand`,`_global_call_target`,`_hoist_calls_in_expr`) + `d.get(var)` + subject mutation | out-of-pattern |
| `frontend/monomorphize.py::_find_subscript_calls` (driver) | non-recursive wrapper over `_scan_node_for_subscript_calls` | out-of-pattern |

**No A-list method is a clean returned-list fold** (`out += self(v)` / `out.append(<literal-key read>)` of
a uniform element type). Every returned-list builder appends a *computed* payload (tuple, record-dict, whole
node) and/or carries an external context map, a non-algebra sibling, or a string-theory op. The closest to a
pure result-model gap is `_scan_node_for_subscript_calls` (list-of-tuple), but its `_type_str` sibling is
the disqualifying external dependency.

### 2.2 The 67 non-self-recursive A-list builders
Flat emitter builders composing non-algebra helpers (e.g. `_stmts_to_whyml`, `_handle_expr_stmt`,
`_py_stmt_*`, `_emit_function`, `_emit_contracts`, `_transpile_modular`). All **out-of-pattern** — no walk,
sibling glue to string emitters D cannot outline.

---

## 3. A-dict (39) — CLEAN 0 / T1-covered 0 / needs-cap 2 / out-of-pattern 37

### 3.1 The 7 self-recursive A-dict candidates

| file::name | LIVE-body deciding feature | bucket |
|---|---|---|
| `module6_whyml/ir_scanner.py::find_record_var_classes` | **clean structural fold** (fixed-child recursion, `.update(self(...))` merge, `in record_types` = C-classifiable membership guard) building a **returned dict keyed by RUNTIME strings** (`out[tgt]=classname`) | **needs-new-capability** (returned string-keyed dict / by-key grouping) |
| `module6_whyml/types.py::_collect_tuple_array_locals` | clean fixed-child fold building `{runtime-str: int}` (`out[tgt]=arity`); reads ArrayLit/ListLit elts, computes arity; no external context, no sibling call | **needs-new-capability** (returned string-keyed dict, int values) |
| `module6_whyml/types.py::_collect_tuple_var_assigns` | grouping shape BUT `getattr(self, "_module_method_return_types")` = **external self context-map** + `rt.split/startswith/count` string ops + side-effects on `self._tuple_var_slot_types` | out-of-pattern |
| `frontend/monomorphize.py::_rewrite_subscript_calls_in_stmt` | T1 reconstruction, BUT branches at the `"func"` key to sibling `_rewrite_subscript_to_name` (mutual-recursion between two reconstruction folds) | out-of-pattern (needs mutual-T1 + the sibling's deps) |
| `frontend/monomorphize.py::_rewrite_subscript_to_name` | T1 reconstruction, BUT `rename_map[(gname,ct)]` = **external composite-key context-map** + `_type_str` sibling string helper | out-of-pattern |
| `frontend/ir_inline.py::_substitute` | T1 reconstruction, BUT `param_map[nm]` + `rename[nm]` external context-maps + `.partition(".")`/`startswith` string ops + `deepcopy` | out-of-pattern |
| `frontend/ir_resolve.py::_rewrite_ir_calls` | uniform `.values()` walk but **rewrites the walked node in place** (`obj["func"]=new_name`; accumulator == subject) | out-of-pattern (in-place subject mutation) |

### 3.2 The 32 non-self-recursive A-dict builders
Flat map-builders keyed by method/decl name over a flat list, composing helpers
(`_build_method_*_map` family calling `classify`/`refs_param`/`find_return_type`; `_collect_*` /
`_detect_*` calling non-algebra siblings; `_py_expr_*`). All **out-of-pattern** (no tree walk; non-algebra
glue).

---

## 4. Spot-check snippets (for verification)

### 4.1 needs-new-capability (clean fold shape, blocked ONLY on the returned string-keyed-dict model)

**`find_record_var_classes` (A-dict)** — a clean fixed-child structural fold; the only gap is a returned
dict keyed by *runtime* strings:
```python
def find_record_var_classes(stmts, record_types):
    out = {}
    for stmt in stmts:
        if stmt.get("stmt") == "Assign":
            val = stmt.get("value", {})
            if isinstance(val, dict) and val.get("type") == "Call" and val.get("func","") in record_types:
                tgt = stmt.get("target", "")
                if tgt:
                    out[tgt] = val.get("func", "")          # RUNTIME-string key + value
        for key in ("body", "orelse"):
            if key in stmt and isinstance(stmt[key], list):
                out.update(IRScanner.find_record_var_classes(stmt[key], record_types))  # merge fold
        if stmt.get("stmt") in ("While", "For"):
            out.update(IRScanner.find_record_var_classes(stmt.get("body", []), record_types))
        if stmt.get("stmt") == "Match":
            for c in stmt.get("cases", []):
                out.update(IRScanner.find_record_var_classes(c.get("body", []), record_types))
    return out
```
Clean: fixed-child self-recursion, `.update(self(...))` merge, `in record_types` guard is a C-classifiable
set-membership boolean, no sibling call, no in-place mutation. **Blocker:** `out[tgt]=…` inserts on a
runtime string key — needs a returned **string-keyed dict** result (the `sdict` datatype, already certified
in Phase C), not L1 `pydict` (whose keys are interned `irkey` constructors).

**`_collect_tuple_array_locals` (A-dict)** — same grouping shape, `{runtime-str: int}`:
```python
found = {}
for s in stmts:
    if s.get("stmt") == "Assign":
        val = s.get("value", {}); tgt = s.get("target", "")
        if isinstance(val, dict) and val.get("type") in ("ArrayLit","ListLit") and tgt:
            ...  # compute uniform tuple arity
            found[tgt] = arity
    for k in ("body","orelse"):
        if k in s: found.update(self._collect_tuple_array_locals(s[k]))
    ...
return found
```

### 4.2 out-of-pattern (deciding external dependency C/D cannot dissolve)

**`_rewrite_ir_calls` (A-dict)** — uniform walk, but rewrites the subject **in place** (acc == subject):
```python
def _rewrite_ir_calls(obj, old_name, new_name):   # returns None; mutates obj
    if isinstance(obj, dict):
        if obj.get("type") == "Call" and obj.get("func") == old_name:
            obj["func"] = new_name                 # in-place subject mutation
        for v in obj.values():
            _rewrite_ir_calls(v, old_name, new_name)
    elif isinstance(obj, list):
        for item in obj:
            _rewrite_ir_calls(item, old_name, new_name)
```

**`_substitute` (A-dict)** — T1 reconstruction shape, defeated by external context maps + string ops:
```python
if node.get("type") == "Var":
    nm = node.get("name")
    if nm in param_map:  return copy.deepcopy(param_map[nm])   # external context-map → arbitrary pyval
    if nm in rename:     return {"type":"Var","name": rename[nm]}  # external rename map
...
if fn.startswith("self."): new["func"] = self_name + fn[len("self"):]      # string op
elif "." in fn:  recv_part,_,method_part = fn.partition(".")               # string op
```

**`_subst_params` (A-list)** — T1 reconstruction, defeated by a context-substitution leaf:
```python
if isinstance(ir, dict):
    if ir.get("type") == "Var" and ir.get("name") in arg_nodes:
        return arg_nodes[ir["name"]]                            # external context-map substitution
    return {k: self._subst_params(v, arg_nodes) for k, v in ir.items()}   # (functorial map — the clean part)
if isinstance(ir, list):
    return [self._subst_params(x, arg_nodes) for x in ir]
return ir
```

**`_scan_node_for_subscript_calls` (A-list)** — list-of-tuple fold, defeated by the `_type_str` sibling:
```python
if node.get("type")=="Subscript" or node.get("stmt")=="Subscript":
    ...
    ct = _type_str(slice_node)          # sibling: non-algebra string renderer (returns Optional[str])
    if ct is not None: out.append((gname, ct))   # returned list-of-TUPLE
for v in node.values(): out.extend(_scan_node_for_subscript_calls(v, generic_names))
```

---

## 5. Certificates — do the families need new ones?

- **A-list:** L1 `list τ` + `size_list` already exist; a clean returned-list fold would reuse them — **no
  new certificate**. But **moot**: no A-list method is a clean returned-list fold (all carry an external
  dependency), so the list-result model is never reached.
- **A-dict:** The 2 grouping folds build dicts keyed by **runtime strings**, so **L1 `pydict` does NOT
  suffice** (its keys are interned `irkey` constructors). They need a returned **string-keyed dict**, i.e.
  the `sdict` datatype — **already certified axiom-free (Rocq 8.20 + Lean 4.29) in Phase C** for `_sa_walk`.
  So A-dict grouping needs **NO new certificate**, only a new RESULT-ALGEBRA template (returned-`sdict` fold
  with `out[k]=` insert + `.update` merge). Ledger would stay at 3.

---

## 6. GATE verdict (per family)

- **A-list: CLEAN 0 → BANK.** No self-contained returned-list fold exists in the residual; every candidate
  carries an external context map, a non-algebra sibling, a string-theory op, or subject mutation. C/D/T1/T2
  do not dissolve any of these. `TRUSTED(essential)`.
- **A-dict: CLEAN 0 → BANK.** The phase3.0 "1 clean" (`_subst_type_in_ir`) is now **CONVERTED via T1**
  (out of pool). The residual has **2 needs-new-capability** grouping folds (`find_record_var_classes`,
  `_collect_tuple_array_locals`) that are clean structural folds blocked only on a returned string-keyed
  dict result (reusing the certified `sdict`). 2 < 5 → below the GO threshold; not worth a per-family
  template + recognizer build for 2 methods. `TRUSTED(essential)`.

**Neither family proceeds.** If A-dict is revisited later, the **first per-family build** is the
returned-`sdict` grouping fold (no new certificate; convert the 2 grouping folds) — but it is explicitly
**not gated now**. This closes the A-list/A-dict returned-collection campaign at the honest clean floor
(0 / 0), consistent with phase3.0's finding and the VERIFIED SCALING REALITY in `bigger-build.md` §7: the
census over-counts, the real complexity lives in external dependencies, and the clean template yield is
bounded per-shape, not a free family slot.
