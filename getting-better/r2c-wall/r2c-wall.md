# Wall: mutation of the IR tree — stores into the CALLER's tree ("r2c-ir-tree-mutation")

**Status:** state-of-the-art wall report (Phase 2 of the self-tcb-reduction driver), waiting for an
INDEPENDENT review. The reviewer has the repo and the oracles, and none of our history.
**Author:** the driver's report author. Treat every sentence as a claim to CONFIRM or REFUTE. Each
claim cites a file:line, a commit, an artifact under `getting-better/r2c-wall/`, or a command.
**Date:** 2026-10-22. **Tree:** `/home/fabrice/git/pycsl`, branch `ghost-assign-bc6`, HEAD `348874ab`.
No `src/` file was changed for this report.

---

## 0. Summary

* The census ranked "mutation of the IR tree (R2c-caller)" as the first blocker of the P/J value-model
  clusters, with **11 markers** (`chain-plan-g36.md` §"Re-measurement at HEAD — ch29", "Ranked next
  blockers" item 1). Re-reading the 11 live bodies (§3) shows the label covers **four different
  shapes**. Only **3** of the 11 store into a tree that a *parameter* owns (`_rewrite_annotations`,
  `_inline_calls`, `_emit_specializations`). **2** store into a tree held in a *self field*
  (`self.program_ir`). **4** store into a *locally built* tree, which is R2c-local, not R2c-caller.
  **2** do not touch the IR tree at all: they mutate self-state sets.
* **The value model can carry a caller-tree store.** This is measured, not argued. A dict parameter
  with `#@ assigns d` is ALREADY lowered to `d: ref (map string (option τ))` with `writes { d }`, and
  the caller sees the write (probe q2, L3-tc clean). A hand spike over the landed hval ADT lowers
  `for f in ir["functions"]: f["symbol_table"] = v` to a write-back along the access path. It proves
  **37/37 VCs Valid in Z3, 1.5 s in total**, and its false twin times out
  (`spike/r2c_writeback.mlw`, `.z3.out`).
* **What the value model cannot carry is aliasing.** The same spike PROVES a false claim when a second
  name shares the element (`alias_hole`, Valid). The live code relies on exactly that sharing in at
  least one marker: `_inline_calls(funcs, .., rewrite_funcs=body_funcs)` where
  `body_funcs = [f for f in funcs if not f.get("trusted")]` (`ir_inline.py:527,538`). The callee
  writes through `rewrite_funcs`, and both the caller and the callee's own `_Inliner(funcs, ..)` read
  the result through `funcs`.
* **Verdict to adjudicate:** for the IR tree, caller-tree mutation is a **modelling choice** whenever
  the written root is alias-free, and that can be shown by type or by construction. It is
  **fundamental for a value-model verifier** only where the program relies on two names for one
  object (`_inline_calls`). That case needs a heap or ownership model (route b), or it stays trusted.
* **Markers unlocked by any single route: 0.** Every one of the 11 chains has at least 2 other
  blockers (§3, §5). The wall is necessary but not sufficient, as ch29 already found for R2a/R2b.

---

## 1. Global picture (for a reader with no history)

**Pipeline.** PyCSL verifies Python annotated with `#@` contracts (`requires`, `ensures`, `assigns`,
loop invariants). `src/pycsl/frontend/Module1_Ingestor.py` → `Module2_Parser.py` →
`Module3_Weaver.py` → `Module5_IREmitter.py` produce an IR made of plain Python `dict`s and `list`s.
`core_ir_semantic.py` checks it. Module 6 (`src/pycsl/Module6_WhyMLTranspiler.py` and the mixins in
`src/pycsl/module6_whyml/`) emits WhyML, and Why3 (`/home/fabrice/.opam/framac-coq8/bin/why3`)
discharges it with Z3 or Alt-Ergo. Entry point:
`.venv/bin/python src/pycsl/pycsl.py f.py --import-path src/pycsl [--no-proof --keep-mlw]`. The
default memory model is `hoare`, a VALUE semantics (`pycsl.py:210-214`; `typed`/`store` use a global
`map loc int` heap, and are not used by the mirror).

**The self-annotation mirror.** `src/self-annotate/src/` is a copy of PyCSL's own source annotated
with PyCSL contracts. A function the tool cannot verify yet is a bodyless stub marked `#@ \trusted`.
There are **449** of them today (`grep -rc '#@ \\trusted'` over the mirror). The base loop
(`config/skills/self-tcb-reduction/SKILL.md`) converts stubs one at a time. Each conversion ports the
live body verbatim (`bin/port-one-mirror-body.py --convert`) under a fixed contract shape:
`requires True` / `ensures True` / `assigns <frame>`. So a converted method certifies type-safety,
absence of the modelled exceptions, termination (or `\diverges`), and the **frame**. The frame is the
only caller-visible semantic claim.

**The three L-planes (hard lower bounds; a conversion must pass all three).**
1. **Fidelity:** the mirror body equals the live body (`bin/check-self-annotate-sync.sh`,
   `self-annotate-mirror-check.sh`). Annotations are the modelling layer, and Python ignores them:
   `errors.py:24` `PyVal = Any`.
2. **Whole-file Why3:** every moved mirror file re-proves with 0 non-Valid goals (`heavy.sh`, LOW
   queue, minutes to hours per file).
3. **Corpus byte-diff:** every emitter change is byte-inert on the reference corpus and pyref, except
   for its declared movers, which are re-proved to their expected label.

Around these: `check-trusted-reasons.py`, the soundness planes (`bin/run-soundness-planes.sh`, fast
and `--slow`), and the frame planes (`check-assigns-*`, below). The **axiom ledger is 3**
(`src/pycsl/proof_axiom_allowlist.py`). A new value shape must land an axiom-free certificate under
`src/formal-semantics/` (Rocq + Lean). The hval precedent is `rocq/Phase2f_PyVal.v` and
`Phase2c_PyValDict.v`.

---

## 2. The hval value model, and the frame discipline

### 2.1 hval (dict-value-wall, R2a / R2b / ch30 / ch31)

A heterogeneous IR dict annotated `Dict[str, PyVal]` lowers to `map string (option hval)` at the top
level. Nested values are a pure ADT (verbatim from any emit, e.g. `probes/q1_param_store.mlw:12-14`):

```
type hval = HStr string | HInt int | HArr hval_list | HMap hpairs | HNode hval
with hval_list = HNil | HCons hval hval_list
with hpairs   = PNil | PCons string hval hpairs
```

* Reads go through `pairs_get` over the assoc list. Key equality is the realizable `val function
  hpairs_key_eq (a b: string) : bool ensures { result <-> a = b }`: a task axiom of the file, not a
  kernel axiom, so the ledger is unchanged. That was R2a. Before it, present keys could not be read.
* **R2b** (ch29): `for x in <hval seq>` becomes an index loop over `hval_list_len`/`hval_list_nth`;
  `"k" in <hval>`; `<pyval> == "lit"`.
* **ch30:** a `List[Dict[str, PyVal]]` / `List[PyVal]` parameter, plus hval element → `Dict[str, PyVal]`
  parameter coercion.
* **ch31:** `bool(<hval>)` → `hval_truthy`, `len`/f-string of `HStr`, `in` on an `HMap` subscript.
* **HVAL-STR-KEYS:** keys are `string`, not hashed ints. The dict model is keyed by the raw string, so
  string literals separate (Z3 is needed; Alt-Ergo cannot separate literals,
  `dict-value-wall-response.md` §9.1).
* **No store path.** hval is immutable data. There is no `pairs_set`, `hval_list_set`, or snoc on an
  `HArr` anywhere in `src/pycsl` (`grep -rhoE "pairs_set|hval_list_set|hval_list_snoc|hmap_set"` → 0
  hits). Build PREPENDS a binding (comment at the `pairs_get` definition), which is fine for literals
  but would be wrong for a store (§4a).
* The `dict-value-wall` review (`dict-value-wall-response.md` §R2c, §9.2) CONFIRMED the wall is a
  modelling choice, with one exception: R2c split into **local tree** (a value question) and
  **caller's tree** (memory model). The impl plan ranked R2c-caller second to last, "boundary until
  assigns-through-path exists" (`dict-value-wall-impl.md:6-7,47-58`). R2c-local (Step 3) was planned
  but never executed.

### 2.2 Frames (`#@ assigns`) and what they lower to

* A **top-level dict parameter** in `#@ assigns d` becomes `(d: ref (map string (option τ)))` +
  `writes { d }`, and a store becomes `d := map_update_some !d k v`. The caller passes its own `ref`,
  so **the write is caller-visible**. Measured in `probes/q2_int_map_caller.mlw:16-26` (L3-tc ✓):
  `setk d; return d["k"]` under `ensures \result == 5`. The same holds for a `Dict[str, PyVal]`
  parameter (`probes/q1_param_store.mlw:74-77`: `func := map_update_some !func "symbol_table" v`).
  q1's only error is `v: PyVal` lowering to `int`, a separate scalar-PyVal gap.
* A **self field** typed `Dict[str, PyVal]` is a mutable record field. A top-level store emits
  `self.program_ir <- map_update_some self.program_ir "constructors" (..)`, and Why3 infers the
  `writes` (`probes/q8_self_tree.mlw:77-79`, L3-tc ✓). `program_ir` is already declared
  `Dict[str, PyVal]` in the M5 mirror (`src/self-annotate/src/frontend/Module5_IREmitter.py:35`).
* A **list parameter** with `assigns` follows the precedent of the stmt-list-append wall: the
  "mutable-ref append convention", `ref (seq stmt_ir)` + a real `writes`
  (`20260718-0633-stmt-list-append-mutation-wall-STATUS.md` item 1; fable verdict BREAKABLE,
  `..-response.md:145-155`). It was keyed on "None-returning + `assigns list-param`", and it coexists
  with the return-a-list model.
* **The frame planes** (`check-assigns-*`, inside `run-soundness-planes.sh`) catch an
  under-declared `assigns` and a vacuous frame (`check-emitted-vacuity`, ch22: an append on an
  int-erased param lowered to a fresh local `Array.make` and `assigns \nothing` held vacuously). Under
  the fixed shape `ensures True`, a `-> None` mutator certifies nothing unless the written root is in
  the frame. `dict-value-wall-response.md` §R2c: "vacuous unless the frame names the root".

### 2.3 The refusals that block these shapes today (all fail-closed, all measured false proofs)

| route | where | what it refuses | why (its measured false proof) |
|---|---|---|---|
| #280 | `module6_whyml/expressions.py:10436-10530` | a mutator (`append/pop/update/setdefault/add/…`) on a COMPUTED receiver (`d[k].append`, `d.get(k, []).append`, `t[0].append`) | the generic arm minted an int `val` with no `writes` and dropped the receiver; `d[0].append(1)` proved `len(d[0]) == \old(len(d[0]))` |
| #283 | `module6_whyml/statements.py:613-626, 3737-3763` | a mutation through a list local bound from a call / conditional (partner set) | `b = ident(a); b.append(1); return len(a)` proved 1 |
| #288 | `statements.py:627-638` | an element store through a list returned by a call | `b = ident2(a); b[0] = 5; return a[0]` proved 1 |
| #295 | `statements.py:639-660` | the same for a DICT/SET bound from a call (`e = idd(d); e[1] = 2`) | a dict parameter is a map VALUE, so even a straight `return x` is a copy; `return d[1]` proved 1 |
| #289 | `pycsl.py:6391-6416` | ANY emitted `subscript_set` (store through a value the model does not represent: a tuple element, an hval element) | `subscript_set` is a no-effect `val`; `b = t[0]; b[0] = 5; return xs[0]` proved `\old(xs[0])` |
| #290 | `pycsl.py:1671-1690`, `expressions.py:8507` | mutation "by another name" (dunders, `getattr(xs,'reverse')()`, computed callee) | 22/56 census probes proved an unchanged list |

Probes at HEAD, all under `probes/`:
* `q3_loop_elem_store.py` (`for f in fns: f["k"] = v`) and `q4_nested_path.py`
  (`ir["functions"][0]["k"] = v`) are refused by **#289**.
* `q5_local_tree.py` (`g["methods"].append(x)` on a local) is refused by **#280**.
* `q6_ra.py` (the live `_rewrite_annotations` body, retyped) is refused by **#289**.

Every one of these refusals exists because a value model **copies**. Each records a place where
Python shares an object and the emission did not.

---

## 3. The wall: the 11 markers, re-read at the live source

Line numbers are live `src/pycsl/` at HEAD. Class: **C** = parameter-owned (caller) tree,
**S** = self-held tree, **L** = locally built tree (R2c-local), **X** = not the IR tree. The ch29
first blocker comes from `chain-plan-g36.md` ch29 table. The "other blockers" column is measured by
ch29/ch31 and by this report's q6/q7.

| # | marker | class | mutation shape(s) (live line) | other blockers in the chain |
|---|---|---|---|---|
| 1 | `monomorphize._rewrite_annotations` (ra) | **C** | `for func in ir_data.get("functions", []): … func["symbol_table"] = new_st` (672); `func["return_annotation"] = …` (675): **store into an element of a list inside the caller's dict** | measured q7 (store removed): `st = func.get(..) or {}` pre-declared `ref 0` (prescan, ch29 #5) → L3-tc; `st.items()` on an hval local → opaque `st_items_0 ()`, `k, v = any int` (FACADE); `isinstance(ra, str)` → `any bool`; `new_st = {}` → `map string (option string)`, which **cannot be turned into an `HMap`** (a Why3 `map` is not iterable) |
| 2 | `ir_inline._inline_calls` (ic) | **C + alias** | `f["body"] = body` (505) for `f in rewrite_funcs`; local `_cb.add/.update` (492-494, the ch29 first blocker) | **`rewrite_funcs` elements ARE `funcs` elements** (`body_funcs = [f for f in funcs if …]`, `ir_inline.py:527`, call 538); `_Inliner(funcs, …)` reads callee bodies that earlier iterations rewrote through the alias; `_walk_dicts` generator; inliner object state |
| 3 | `monomorphize._emit_specializations` (es) | **C** (top level) + L | `ir_data["type_decls"] = new_type_decls`, `ir_data["functions"] = new_functions` (508-509): top-level store into the parameter; `by_generic.setdefault(gname, []).append(ct)` (445, local, #280); `spec["name"] = …` (489, 503) on call results | `Set[Tuple[str,str]]`/`Dict[Tuple,..]` keys; `sorted(instantiations)`; a local `List[Dict[str, PyVal]]` → `HArr` conversion (none exists); calls sd/sf/ra; **`generics[..]["methods"]` holds the same func objects as `ir_data["functions"]`** (built by cgd), so ra's in-place writes are visible through `generics` |
| 4 | `Module5._emit_protocol_interface` (m5-epi) | **S** | `self.program_ir["type_decls"].append({…})` (3143), `self.program_ir.setdefault("constructors", {})` + `self.program_ir["constructors"][p] = {…}` (3152-3153), `self.program_ir["functions"].append(member_ir)` (3172); `member_ir["abstract"] = True …` (3167-3171) on a call result | dict literals → hval; `getattr(child, "lineno", 0)` (AST); `self._protocols[p] = members` (Set field); `_build_function_ir` result typing |
| 5 | `Module5._populate_protocol_conformance` (m5-ppc) | **S** | `self.program_ir.setdefault("overrides", []).append({…})` (3238) | AST walking, `own_methods`/`own_method_tails` locals, protocol lookup |
| 6 | `monomorphize._collect_generic_decls` (cgd) | **L** | `generics[self_type]["methods"].append(func)` (138): nested append into a LOCAL dict, storing a caller element | ch29: R2b loop target not prescan-seeded (`ref 0`); dict literal into a `Dict[str, PyVal]` local → `any_map ()`; `func not in generics[..]["methods"]` needs structural hval `in` |
| 7 | `monomorphize._specialize_decl` (sd) | **L** | `spec = copy.deepcopy(decl)`; `spec.pop("type_params", None)` (530); `for f in spec.get("fields", []): f["type"] = concrete` (534, **loop-element alias into a local tree**); list-comp stores (536-546) | `copy.deepcopy`; `_subst_type_in_ir` callee; comprehensions over hval (opaque `list_content_comp_0`, ch29 `_strip_dir_scan_proofs`) |
| 8 | `monomorphize._specialize_function` (sf) | **L** | `contracts = spec.get("contracts") or {}; contracts[clause] = […]` (569-570): **a store through a CONDITIONAL alias**. It writes into `spec` iff `spec["contracts"]` is truthy, and into a fresh dict otherwise. `spec["symbol_table"] = {dict comp}` (557), `spec.pop` (579) | deepcopy, dict comprehension over `.items()`, `_subst_type_in_ir` |
| 9 | `scc.sort_functions_by_scc` (scc) | **L** | `sorted_names.append(func["name"])` (184), refused by #283 per ch29 | returns `[func_by_name[n] …]`: **aliases of caller elements in a fresh list** (fine for a value model only if no caller writes through it and reads the original) |
| 10 | `FunctionEmission._emit_function` (ef) | **X** | `_nd = _ndp[1]` (7021, a set inside a TUPLE in self field `_r242_nondet`); `_nd.add(_n)` (7035, 7058); `getattr(self, "_emitted_logic_funcs", set()).discard(_n)` (7065) | regex on emitted text, `lines[0] = …` local string list; self-state, not the IR tree |
| 11 | `FunctionEmission._param_type_str` (pts) | **X** | `self._record_locals.add(arg)` (230), `self._record_param_classes[arg] = wn` (231), `self._record_array_params[arg] = _wn` (209) | self-field Set/Dict state of the emitter; 245-line dispatcher |

**Reading.** "Mutation of the IR tree, R2c-caller, 11" is really:
* C = 3 (ra, ic, es),
* S = 2 (the M5 pair),
* L = 4 (cgd, sd, sf, scc),
* X = 2 (ef, pts).

The ranking still holds as "the most frequent first-or-second blocker". But the research-grade part
(aliasing across names into a caller-owned tree) applies to **ic, and es through `generics`**. The
rest is the value question that `dict-value-wall-response.md` §R2c already called cheaper.

---

## 4. Is caller-tree mutation fundamental for a value-model verifier?

**Claim (to CONFIRM/REFUTE): it is a modelling choice for alias-free roots and fundamental only
for observed sharing.** Evidence, cheapest first:

1. **The calling convention already exists.** A `Dict` parameter in `assigns` is a `ref` with
   `writes` (§2.2, q1/q2). A self field is a mutable record field (q8). The question is therefore
   not "how does the callee's write reach the caller" (it does, through the `ref`), but "how does a
   write at a PATH below the root become a write of the root".
2. **The path write-back proves, cheaply.** `spike/r2c_writeback.mlw` (hand-written, 120 lines,
   verbatim hval types + `hpairs_key_eq` + `pairs_get`) adds definitional ops:
   * `pairs_set` — replace the first binding in place, else **append at the end**, which is Python's
     insertion order. Prepending would make `.items()` / `.values()` / `len` see a duplicate.
   * `hval_list_len`, `hval_list_nth`, `hval_list_set` — structural `let rec function`s.
   * their lemmas `pairs_set_get`, `list_set_len`, `list_set_nth` — `let rec lemma`s, no axiom.

   `rewrite_all (ir: ref (map string (option hval))) (v: hval) writes { ir }` is the ported loop
   `for f in ir["functions"]: f["symbol_table"] = v`. Each iteration does
   `ir := map_update_some !ir "functions" (HArr (hval_list_set l i (upd f v)))`. Its postconditions
   are: length preserved, element j = `upd (old element j) v`, and every other top-level key
   unchanged.

   Command:
   `heavy.sh why3 prove -P z3 -t 20 -a split_vc r2c_writeback.mlw`. Result: **37 Valid**, total
   1.54 s, max 1.42 s:
   * all variants and lemmas;
   * 14 goals of `rewrite_all`;
   * 4 of `caller_ok`: the caller reads back `symbol_table = v` and `name` unchanged.

   `caller_twin` (claims the OLD table) times out at 20 s. That is the expected non-proof; a Z3
   `Unknown (sat)` would be stronger evidence and was not chased.
3. **The same spike exhibits the unsoundness.** `alias_hole` holds `funcs = HArr [f0]`, stores it in
   `ir`, calls `rewrite_all ir v`, then asserts `funcs`' element still has `st0`. It **PROVES (Valid,
   1.42 s)**, and CPython disagrees whenever `funcs` and `ir["functions"]` are the same list object.
   This is the #283/#288/#295 hole one level deeper. A write-back lowering is sound only with a
   **no-sharing obligation** between the written root (and the loop-element names bound into it) and
   every other live name the proof can read afterwards.
4. **The live code relies on sharing in at least one marker.**
   * `_inline_calls`: shown in §3 row 2. In Python the caller's `funcs` sees the rewritten bodies. In
     the value model it would not. Inside the callee, `_Inliner(funcs, ..)` reads callee bodies that
     the loop already rewrote through `rewrite_funcs`, so the result depends on that sharing.
   * `_emit_specializations` + `monomorphize()`: after es, `generics` (built by cgd from the same
     dicts) is mutated too. `_record_classification(ir_data, generics, instantiations)` reads it
     afterwards (`monomorphize.py:93`).

   A value model has no name for "the object behind both". Faithful verification needs object
   identity: route (b), or an ownership/uniqueness discipline that is proven, not assumed.
5. **Under the fixed contract shape the harm is narrower but real.** With `ensures True`, a caller
   learns nothing about content. It only learns that roots outside the frame are UNCHANGED. So the
   alias hole becomes a frame hole: `assigns rewrite_funcs` would certify `funcs` unchanged, which is
   false in Python. Inside a converted body, a stale read through the other name can discharge a
   no-exception or type-safety VC that Python would fail (for example, a key present in the stale copy
   but absent from the live object).

So a value verifier can carry caller-tree mutation if it **refuses or proves away** sharing. That is
a static obligation, not a memory model. It cannot carry a program whose meaning *depends* on
sharing.

---

## 5. Candidate routes, costed

Unit costs are the base loop's own:
* an emitter build: hours;
* each mirror file a build moves: a whole-file LOW proof, up to about 12 h for the big mixins
  (`dict-value-wall-impl.md` "Cost");
* a certificate extension: Rocq + Lean lemmas in `Phase2f_PyVal`.

"Complete chains" means markers whose EVERY blocker is cleared, given the other routes already
landed.

### (a) Functional write-back along the access path (`d := hval_set_path d [k1; i; k2] v`)

**What it is.**
* Recognize a store `x[k] = v`, `x[k].append(e)`, `x.setdefault(k, []).append(e)`,
  `x.pop(k, dflt)` or `x.update(m)` whose receiver is an **hval access path**: a root `r` (a `ref`
  parameter in `assigns`, a self field, or a local) followed by string keys and loop indices.
* Lower it to a rebuild of `r` with definitional `pairs_set`, `pairs_del` (for `pop`),
  `hval_list_set` and `hval_list_snoc`, and **also** rebuild every live local that aliases a prefix
  of the path. The R2b loop element `func` is today an immutable `let` (`probes/q7…mlw:108`). It
  becomes a `ref` updated together with the root, so `func[..]` read after the store sees it.
* Default-producing reads cut the path:
  * `.get(k, [])` / `or {}` yield a FRESH object when the key is missing or falsy, and a store through
    it is lost. The write-back must be conditional on presence and truthiness (sf's `contracts` shows
    this is live).
  * A non-`HArr`/non-`HMap` node at a path step is a Python `TypeError`/`AttributeError`. The
    lowering must refuse or assert, never silently skip.

**Contract shape.** The frame names the root parameter (`#@ assigns ir_data`), which already lowers
to `ref` + `writes` (q1/q2). No new clause is needed: assigns-through-path is expressible as
"assigns the root". That answers the impl plan's "no contract shape for assigns-through-path". It is
coarse: the caller loses all knowledge of `ir_data`, which is exactly what `ensures True` gives it
anyway.

**Aliasing obligation (PARAM-DISJOINT + LOCAL-PARTNERS).** Sound only if no other name readable
after the store can share a mutable sub-object of the root. A fail-closed static rule, modelled on
#283/#295:

* **(i) Parameters.** Every other parameter whose type can contain a mutable dict/list (`PyVal`,
  `Dict`, `List`, `Set`, records) must be **in the frame too** (the havoc covers the caller), or be
  type-disjoint. ra's `rename_map: Dict[Tuple[str, str], str]` has only immutable leaves, so it is
  disjoint. ic's `funcs` vs `rewrite_funcs` is not, so ic is refused. This makes the caller sound.
* **(ii) Inside the body.** After a path store, any read through a name in the partner set of a path
  prefix must be refused unless the write-back updates that name too (the #279/#283 flow-sensitive
  walk, extended to hval paths).
* **(iii) Self fields.** A self field's tree must not be aliased by a parameter. For a `-> None`
  method that stores a fresh literal into `self.program_ir[..]`, this holds by construction.
* **(iv) Values stored into a tree.** A parameter element stored INTO a tree (cgd stores the
  caller's `func` into `generics`) makes the tree a partner of the caller's root for every later
  writer. That is the es/`generics` case. Track it, or refuse writes to roots that received such
  values in the same function.

**Certificate.** Four structural functions and three lemmas, of the same kind as `pairs_get`. Cert
work: extend `Phase2f_PyVal` with `pairs_set` / `pairs_del` / `hval_list_set` / `hval_list_snoc`
and their get/len lemmas. Ledger stays 3, because the only spec `val` is the already-landed
`hpairs_key_eq`.

**Cost (estimates).**
* Spike already done for the core (§4.2).
* Emitter build: path recognizer + write-back + partner extension + the four ops, gated on
  `_uses_pyval` so the corpus is byte-inert. Roughly the size of the R2b build (ch29) plus the
  #283 walk.
* Per marker, the store itself is about 0 marginal once built. The other blockers dominate.

**Markers unlocked, complete chains only: 0 now.**
* ra still needs 4 read-side seams (§3 row 1): prescan seeding, `.items()` over an hval local,
  `isinstance(<hval>, str)` → `match HStr`, and a `Dict[str, str]` local built by stores that must
  BE an hval (`HMap`) when stored back, since a `map` cannot be converted.
* The S pair still needs dict-literal → hval and AST getattr.
* es needs tuple-keyed maps and a `seq hval` → `HArr` conversion.
* ic is refused by the obligation, as it must be.

**Soundness risks.**
1. The alias hole (§4.3) if the partner rule is incomplete. `alias_hole` is the regression witness
   to keep.
2. Default-object loss through `.get(k, default)` / `or {}`.
3. Insertion order (`pairs_set` must append, not prepend).
4. A vacuous frame if the root is not named.
5. The loop-element `let` not being rebuilt.

**Make-or-break question for a spike.** Can the partner walk be made **complete** for hval paths,
so that every name that can reach a written sub-object is either in the frame or refused? Test it on
the live shape `body_funcs = [f for f in funcs if …]; g(funcs, body_funcs)`. The spike must REFUSE
ic, ACCEPT ra (with `rename_map` type-disjoint), and turn `alias_hole` into a rejection at emit time,
not a proof.

### (b) A heap model for IR dicts (regions / object identity)

**What it is.**
* IR dicts and lists become locations: `type obj = int`, a global `heap: map obj cell` with
  `cell = CMap hpairs_ref | CList list_ref`, and values `HRef obj | HStr .. | HInt ..`.
* A store writes `heap`. Frames become `writes { heap }`, or regions (`heap` split per IR kind or per
  root), with `\separated`-style preconditions.

**What it buys.** The only route that verifies ic and es faithfully, because sharing is the
semantics, not a hazard.

**Cost.**
* A new value carrier for every hval site: R2a/R2b/ch30/ch31 lowerings re-done over `heap`.
* A new certificate (a heap with identity; Phase2f covers only the pure ADT).
* Every mirror file that uses hval moves: 6 files, 31 `PyVal` sites (`errors.py`, `pycsl.py`,
  `module6_whyml/{functions,stmt_control_flow,expressions}.py`, `frontend/Module5_IREmitter.py`).
  Four of them are among the slowest whole-file proofs.
* Read proofs get harder: every read needs heap framing, and the existing `typed`/`store` heap models
  have a recorded history of erasing to `true` (`pycsl.py:2345-2362`, witnesses 1004-1008).
* Under `requires True`, the caller cannot state the separation it needs. That is the forbidden
  precondition the dict-value-wall review flagged. So converted callers would mostly prove
  "something in the heap changed", which is weaker than (a)'s per-root havoc.

**Markers unlocked: 0 complete.** ic/es carry the same read-side gaps as ra, plus generators and
inliner state.

**Soundness risks.** Biggest certificate delta in the project. Frame imprecision (`writes { heap }`
on every method destroys the frame plane's value). Regression of 1000+ verified methods if the
carrier changes globally. It must be per-file gated, which creates two coexisting models.

**Make-or-break question.** Can a heap carrier be **gated to one file / one root**, and coexist
with the value hval in the same scope as the earlier `pyval`/`hval` pair did, with a certificate no
larger than a Phase2f sibling? And does ANY ic/es chain become complete with it? If ic's other
blockers (generator `_walk_dicts`, `_Inliner` object, `_cb` set) are each also ≥1 build, the answer
is "no marker", and (b) is not worth its certificate.

### (c) R2c-local: restrict to locally built trees

**What it is.** Route (a)'s machinery with the root limited to a local bound to a FRESH constructor
(dict/list literal, comprehension, `copy.deepcopy(..)`, `dict(..)`) that has not escaped
(not returned, passed or stored) before the store. There are no parameter partners, so obligation
(i) is empty and (ii) is a local walk. This is the `dict-value-wall-response.md` §R2c carve-out and
impl Step 3, never run.

**Markers in scope:** cgd, sd, sf, scc (and es's local `by_generic`/`new_*`).

**Hazards still present.**
* cgd stores the CALLER's `func` into the local tree. The local tree then aliases caller elements.
  Writes into those elements later (via `generics[..]["methods"][j][..]`) would be caller-visible.
  cgd only appends, so it is fine, but the rule must forbid a store *below* a stored parameter value.
* sf's `contracts = spec.get("contracts") or {}` is a CONDITIONAL alias. The write reaches `spec`
  only when the value is truthy. Model it as `if truthy then write-back else fresh`, or refuse.
* `copy.deepcopy` must be modelled as identity on hval. That is faithful for a pure ADT, and the
  point of the value model.
* **A known false proof is adjacent and must be fixed first.** ch29: an annotated dict local whose
  first assignment is not a literal is emitted as the EMPTY map (`statements.py` `_emit_first_assign`,
  "SOUNDNESS — CONFIRMED false proof", `getting-better/dict-value-wall/ch29/false_proof_*.py`).
  `spec = copy.deepcopy(decl)` / `dict(func)` is exactly that shape. Any R2c-local build on top of
  it would certify stores into an empty map.

**Cost.** The cheapest of the four. It reuses spike §4.2 (drop the `ref` parameter), with no
contract-shape question. Per marker the store is about 0. The blockers are:
* deepcopy;
* comprehensions over hval (opaque today);
* dict-literal → hval (`any_map ()`);
* prescan seeding;
* `.pop`;
* the `_emit_first_assign` fix.

**Markers unlocked: 0 complete.** The closest is cgd at ≥3 (ch29). sd and sf are ≥4 each. scc's
blocker is a #283 partner of a comprehension, measured at ch29 only.

**Soundness risk.** Low if the fresh-root test is syntactic and fail-closed. The deepcopy, conditional
alias and `_emit_first_assign` items above are the known traps.

**Make-or-break question.** With `_emit_first_assign` fixed and dict-literal → hval in place, does
cgd's loop `generics[t]["methods"].append(func)` lower to a write-back whose witness reads the
appended element back (and whose twin fails), and does cgd then reach L3-tc clean? If cgd is still
≥2 after that, R2c-local is an enabler with no consumer, as R2a/R2b were.

### (d) Leave trusted: CERTIFIED-BOUNDARY with a reopening condition

**What it is.** Record ic (and es while `generics` sharing exists) as a boundary.

*Reason:* the code's meaning depends on two names for one object, which a value model cannot express
without a heap.

*Reopening condition:* either (b) lands for that file, or the live code is refactored (outside the
mirror loop) to make sharing explicit. For example, `_inline_calls` could return the rewritten bodies
and the caller could write them back by name. That is a live-source change, which needs
authorization.

ra, the S pair and the L four would stay **pending**, not boundary: their obstacles are value-model
seams (§3), not sharing.

**Preconditions before declaring it** (dict-value-wall-response.md §9.5, R6):
* The three trusted `assigns \nothing`-but-appends frames must be corrected first.
* So must the ch22 `_attach_loop_contracts` vacuous-append suspicion.

Otherwise the boundary hides a false trusted frame. Cost: one ledger and doc update. Markers: 0
(by definition).

**Make-or-break question.** Is every trusted frame in the boundary set honest, i.e. does each name
every root its live body writes **through an alias**? Checked by porting the bodies into scratch and
running the underdeclaration arms of the frame plane. If any trusted frame under-declares, (d) is
not allowed until it is fixed.

### Comparison

| route | markers in scope | complete chains now | new cert | ledger | main risk | spike cost |
|---|---|---|---|---|---|---|
| (a) path write-back, ref root | ra, es (top level), S pair; ic refused | 0 | 4 structural ops (Phase2f extension) | 3 | incomplete partner walk = §4.3 hole | core done (37 Valid); the partner walk on the live ic/ra shapes ≈ hours |
| (b) heap / regions | all C + S, incl. ic | 0 | new heap cert | 3 (if realizable) | frame-plane collapse, two models, re-proof of 6 files | days |
| (c) R2c-local | cgd, sd, sf, scc | 0 (cgd closest, ≥3) | same 4 ops | 3 | `_emit_first_assign` false proof underneath, deepcopy, conditional alias | ≈1 h after the first-assign fix |
| (d) boundary | ic (+es) | n/a | none | 3 | hides an under-declared trusted frame | frame audit ≈1 h |

---

## 6. What the reviewer should decide (Gate R questions)

1. **CONFIRM or REFUTE §3's reclassification.** Of the 11, only ra/ic/es store into a
   parameter-owned tree. The S pair, the L four and the X two are other problems. Recount from the
   live lines.
2. **CONFIRM or REFUTE §4.** Is caller-tree mutation a modelling choice for alias-free roots (the
   q1/q2/q8 lowerings + spike 37/37 + twin) and fundamental only where code depends on sharing
   (`alias_hole` proves; ic)? Is the fixed `assigns <root>` frame a sufficient contract shape for (a),
   given `ensures True`?
3. **Is the partner obligation of route (a) decidable fail-closed** with the existing #279/#283/#295
   walk, extended to hval access paths and to "parameter value stored into a local tree" (cgd → es)?
   Or does it need ownership types?
4. **Ordering.** Must the ch29 `_emit_first_assign` false proof be fixed before any R2c work? This
   report says yes for (c) and (a): both rely on locals holding their RHS.
5. **Is there ANY marker whose chain completes with ≤2 builds** among (a)/(c) plus the read seams in
   §3? This report found none. ra is the best candidate at 1 store + 4 read seams.

---

## 7. Artifacts and reproduction

All under `getting-better/r2c-wall/`. PATH must include `/home/fabrice/.opam/framac-coq8/bin`
(without it the pycsl type-check fails closed: "why3 not found on PATH").

* `probes/q1_param_store.{py,mlw,out}`: hval param in `assigns` → `ref` + `writes`. The L3-tc error is
  the scalar `v: PyVal` → `int`.
* `probes/q2_int_map_caller.{py,mlw,out}`: dict param write visible to the caller. L3-tc ✓.
* `probes/q3_loop_elem_store`, `q4_nested_path`, `q6_ra`: refused by #289. `q5_local_tree`: refused by
  #280.
* `probes/q7_ra_noloopstore.{py,mlw,out}`: ra's read side with the stores removed. The first L3-tc
  error is `st` = `ref 0` (mlw:97,109). Then the `st_items_0 ()` facade (mlw:111-118) and
  `isinstance` → `any bool` (mlw:123).
* `probes/q8_self_tree.{py,mlw,out}`: top-level store into the `Dict[str, PyVal]` self field. L3-tc ✓.
* `spike/r2c_writeback.mlw` + `spike/r2c_writeback.z3.out`: the path write-back.
  * 37 Valid.
  * `caller_twin` Timeout (expected).
  * `alias_hole` Valid (the hole).
* Command form:
  `scratchpad/heavy/heavy.sh .venv/bin/python src/pycsl/pycsl.py <f>.py --import-path src/pycsl --no-proof --keep-mlw`
  and `scratchpad/heavy/heavy.sh why3 prove -P z3 -t 20 -a split_vc spike/r2c_writeback.mlw`.

Prior walls cited:
* `getting-better/20260718-0633-stmt-list-append-mutation-wall{,-response,-impl,-STATUS}.md`: the
  `ref (seq τ)` + `writes` convention, BREAKABLE, built.
* `getting-better/20260718-ast-node-list-walker-wall{,-response}.md`: BREAKABLE via a compaction
  function. Relevant to sd/sf comprehensions over IR lists.
* `getting-better/dict-value-wall/dict-value-wall{,-response,-impl}.md`: §R2c local/caller split,
  §9.2, R6 precondition.
* `getting-better/chain-plan-g36/chain-plan-g36.md`: ch22 (vacuous append on an int-erased param),
  ch29 (ranking, false proof), ch30, ch31.
