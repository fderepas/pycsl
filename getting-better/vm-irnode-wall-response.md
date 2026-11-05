# Independent review of `vm-irnode-wall.md` (run #5, commit `1da0da1d3`)

**Reviewer:** independent, fresh context. Read the report, then the live sources, the census data (`scratchpad/cv9/merged.json`) and the oracle (pycsl + Why3). No other narrative was used.
**Base:** HEAD `8783ece50` at review time (the report was written at `0e504dc78`; the files it cites are unchanged between the two for everything checked here).
**Scratch:** `scratchpad/vmF/` (tree `st/` = `git archive HEAD src/pycsl src/self-annotate bin`). Nothing in `src/` was edited; the one live-file retype (p14) was applied to the scratch copy and restored (`diff -q` verified, `batchA.sh` last line).
**Every oracle run** went through `scratchpad/heavy/heavy.sh` (`HEAVY_QUICK=1` for `--no-proof --keep-mlw`; NORMAL class for `why3 prove` and full proofs). Artifacts: `scratchpad/vmF/probe/<tag>.{log,mlw,src.py,patchlog}`, `scratchpad/vmF/toy/<t>.{py,tc.log,mlw,proof.log}`, `scratchpad/vmF/spike/dictview_tag.mlw`.

**Evidence tags:** **[M]** measured here (command + output lines quoted); **[C]** read from a repo file; **[I]** inference.

---

## 0. Verdict in six lines

1. The report's named emission facts are **accurate** (p01, p02, p06, p13, p14 reproduced byte-for-byte at the cited lines; t1/t2/t5/t6 reproduced). Its census arithmetic is slightly over-read (§2.1).
2. One factual claim is **refuted**: "`materialize` exists only for int sequences". The emission p02 already declares `val materialize_ir (s: Seq.seq emit_ir) : array emit_ir` (mlw line 901). The list half of R2 is a *recognizer* gap, not a model gap, and is cheaper than costed.
3. The report's central framing — "fail-closed by design, so the stubs are stuck rather than unsound" — is **wrong for two of its own findings**. Both named hazards are **real, reachable-today soundness holes** in corpus-style programs, not latent mirror-only risks:
   - **H1** `dv.kind` → `kind_of`: `toy/f1_kind_misproj.py` is a 20-line program that returns 1 in CPython and whose contract `ensures \result == 0` type-checks and is sent to Why3 as `result = 0` over `str_eq_op (kind_of !dv) "keys"`, where `str_eq_op` carries `ensures { result <-> (a = b) }` and no `kind_of` arm yields `"keys"` — valid in the model, false of the program. At the oracle the 110-arm case split timed out (30 s default, 120 s Z3), so H1 is confirmed at the model level and solver-bound at the proof level (§1.6, §3.1).
   - **H2** `<emit_ir>[k] = v` → `()`: the branch in `statements.py:2694-2706` returns `"()"` **without lowering `rest`**, so every statement after the store in the same block is deleted from the model. `toy/f2o_dropped_tail_precond.py` loses a callee-precondition VC that its control keeps (§3.2). The report under-scopes this as "a silently dropped mutation"; it is a dropped *continuation*.
4. Neither existing gate covers H2: `bin/check-dropped-mutation.py` counts Module 5 statements that produce no IR, `bin/check-param-mutator-visibility.py` counts mutations through *parameters*; H2 is a Module 6 lowering of an IR statement on a *local*. Gate hole, as the report suspected (Q3).
5. The wall itself is a **cost/scale wall with two correctness defects riding on it**, not a certified boundary. The only candidate for a genuine boundary is the reflection residue (`type(node)` dispatch, `getattr(c, "act_name", None)`, class objects as values) and it is a modelling choice too (§6).
6. Recommended 60 h: fix H1/H2 first (≈ 3 h, no stub moved, mandatory), then wire `materialize_ir` into the `List["ExprIR"]` return path with a byte-diff gate, then the R3 `FunctionView` slice on `core_ir_semantic`. Make-or-break spike and refutation exit in §5.

---

## 1. What I ran (the oracle)

Harness: `scratchpad/vmF/probe.sh` (same recipe as the report's: restore mirror from HEAD, `bin/port-one-mirror-body.py --convert`, optional patch, `pycsl.py --import-path st/src/pycsl --no-proof --keep-mlw`, restore). Batches `batchA.sh` (p01, p02, p13, p14, p14b), `batchF.sh` (p06, p03), `batchG.sh` (p11); toys `batchB/C/D/E.sh`.

```
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchA.sh
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchB.sh   # t1 t2 t5 t6 f1 f1p f1h f2 f2p f2a
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchC.sh   # f2l f2m
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchD.sh   # f2n f1h
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchE.sh   # f2o f2o_control
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchF.sh   # p06 p03 (p11 first attempt, patch failed)
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchG.sh   # p11 (mirror-only retype)
scratchpad/heavy/heavy.sh why3 prove -P alt-ergo -t 10 scratchpad/vmF/spike/dictview_tag.mlw
scratchpad/heavy/heavy.sh python3 src/pycsl/pycsl.py scratchpad/vmF/toy/f1_kind_misproj.py --keep-mlw
scratchpad/heavy/heavy.sh scratchpad/vmF/proofF2.sh                 # full proofs of f2o and f2o_control
```

### 1.1 Mirror ports, per named claim [M]

| tag | claim in report | my result | cite |
|---|---|---|---|
| p01 `_csl_in` port-as-is | L3-tc ✗, line 3614 chars 53-71 int vs emit_ir; `type cslin` int fields; `"range"` → `1974220728`; `"keys"` → `915441578`; `IrOther "MapValueIs"` | **CONFIRMED, same lines.** `probe/p01_csl_in.log:176` `This expression has type int, but is expected to have type PyCSL_Program.emit_ir` at `line 3614, characters 53-71`; `p01_csl_in.mlw:1170 type cslin = { mutable cslin_element: int; mutable cslin_collection: int }`; `:3612 … (get_func node.cslin_collection) = 1974220728`; `:3628 (get_kind !dv) = 915441578`; `:3633 IrExists !kv (IrOther "MapValueIs") IrSNone IrONone` | §2.2 |
| p02 `_csl_list_to_ir` port-as-is | `csl_list: array int`; `getattr` → `pycsl_getattr_unknown_539951548`; store → `()` | **CONFIRMED.** `p02_csl_list.mlw:3950 … (csl_list: array int) : array int`; `:3970 an := (pycsl_getattr_unknown_539951548 !_pyobj_state !c)`; `:3971-3973 if ((if (not (!an = pycsl_none)) && true then 1 else 0) <> 0) then begin () end`. Note `isinstance(d, dict)` lowered to the literal `true`. | §2.2 |
| p06 `_desugar_acts` | `contracts: array int`; `py_isinstance_Act_int_op`; `binop_left = !a` type error line 1428 chars 69-71 | **CONFIRMED.** `p06_desugar_acts.mlw:1395 (contracts: array int)`, `:1421 py_isinstance_Act_int_op !c`, `:1428 … { binop_left = !a; …}`; log:180 `line 1428, characters 69-71`. | §2.2 |
| p03 `_collect_instantiations` | REFUSED, erased-iterable variant | **CONFIRMED.** log:8 `a \`for\` loop over an iterable whose length term contains an unconstrained value (\`any\`) has no legal termination \`variant\``. | §2.1 |
| p11 mirror-only `CSLIn` retype | "changes nothing": `type cslin` stays int | **CONFIRMED** (`batchG.sh`; the first attempt in `batchF.sh` failed its patch assertion on the mirror's single-quoted docstring and silently became a port-as-is, hence the re-run). `p11_csl_in_mirror_retype.patchlog`: `retyped MIRROR Module2 CSLIn.element/collection -> "ExprIR" (live untouched)`; `p11…mlw:1170 type cslin = { mutable cslin_element: int; mutable cslin_collection: int }`; log:175-176 same `line 3614, characters 53-71 … int … emit_ir` as p01. Records are read from the **live** class bodies. | §2.3 |
| p13 `csl_list: List["ExprIR"]` + `-> List["ExprIR"]` | param becomes `array emit_ir`, **return stays `array int`**, `materialize !out` seq emit_ir vs seq int | **CONFIRMED.** `p13_csl_list_ret.mlw:3950 (csl_list: array emit_ir) : array int`; log:188 `This expression has type seq.Seq.seq PyCSL_Program.emit_ir, but is expected …seq int` at `:3977 (materialize !out)`. | §2.3 |
| p14 live `CSLIn` retype (scratch copy) | `range` branch faithful; new error 3624 chars 27-42 emit_ir vs string; `.kind` → `kind_of`, `.coll` → `svalue_of`; `py_isinstance_*_emit_ir_op` specless | **CONFIRMED.** `p14_csl_in_live.mlw:1170 … cslin_element: emit_ir …`; `:3609 str_eq_op (func_of node.cslin_collection) "range"`; `:3624 coll_var := (IrVar (svalue_of !dv))`; `:3625 if (str_eq_op (kind_of !dv) "keys")`; `:1623/:1626 val py_isinstance_CallExpr_emit_ir_op (x: emit_ir) : bool` / `…DictView…` with no contract; log:176 `line 3624, characters 27-42 … emit_ir, but is expected to have type string`. | §2.3 |
| **p14b** (report Q1: patch past 3624) | "the reviewer should confirm `kind_of` stays" | **CONFIRMED.** With `dv.coll` replaced by a literal (`x_p14b.py`, scratch only): `p14b…mlw:3624 coll_var := (IrVar "dcoll")`, `:3625 if (str_eq_op (kind_of !dv) "keys")`, `:3628 … "values"`. The DictView branch then type-checks; the next L3 error is **elsewhere**: `line 3117 … this expression depends on variable _pyobj_state, which is left out in the specification` (the `getattr(node.collection, "name", None)` tail, `p14b…mlw:3636 _coll_nm := (pycsl_getattr_unknown_90083744 !_pyobj_state …)`). The report's "unprobed tail" (§6 R1) is real: `:3637 if ((if (not (!_coll_nm = pycsl_none)) && (!_coll_nm = pycsl_none) …` is the constant-false vararg guard, and the symtab compare at `:3640` is int-hashed (`1207271756 || 39869774 || …`). | §2.3, §6 |

### 1.2 Toys: the int erasure [M]

| toy | report says | my result |
|---|---|---|
| t1 `def kind(ir: Any) -> str: return ir.get("type")` | REFUSED #252 | **CONFIRMED** `t1_any.tc.log`: `an erased (\`Any\`/\`object\`/unannotated/TypeVar) value flows into a slot declared as a builtin type: the \`return\` of a function declared \`-> str\`` |
| t2 `Dict[str, Any]` → `-> str` | REFUSED #252 | **CONFIRMED** (same text, function `name_of`) |
| t5 heterogeneous `Dict[str, Any]` literal | L3 ✗, int-hashed literal | **CONFIRMED** `t5…mlw:21 map_update_some (… (const (None: option int)) "pattern" 2193169) "ctor" ctor) "n" 3`; log: `This expression has type string, but is expected to have type int` |
| t6 `for f in ir.get("functions", [])` | TC ✓, input-blind | **CONFIRMED** `t6…mlw:13 val iter_length (x: int) : int`; `:15 let count_funcs (ir: map string (option int))`; `:22 iter_length (match Map.get ir "functions" with Some v_ -> v_ \| None -> 0 end)` |

### 1.3 The `.mlw` spike (`scratchpad/vmF/spike/dictview_tag.mlw`) [M]

Three modules:
- `DictViewTag`: a tagged-union `node = IrVar string | IrCall string | IrDictView string string`, with the node-tag projector `kind_of` and a per-class projector `dv_kind`. `is_keys_faithful` carries the honest contract; `is_keys_misproj` is the lowering as emitted at p14:3625 with `ensures { result = 0 }`. Two goals: `false_claim_faithful: forall e. is_dictview e -> dv_kind e <> "keys"` (must **fail**) and `misproj_claim: forall e. is_dictview e -> kind_of e <> "keys"` (expected to **prove** — the misprojection makes a false CPython statement a theorem).
- `HNodeBridge` (report Q5): `node` and `hval` **mutually** recursive (`IrHVal hval` / `HNode node`), `pairs_get`, `to_node`; round-trip lemmas plus a false goal `forall n m. to_node (HNode n) = m` that must fail.
- `DroppedTail`: `bump_as_emitted = ()` vs `bump_faithful = need_empty an` with `requires { an = 0 }` (the VC must fail for the faithful one and vanish for the emitted one).

**Result (Z3, 10 s; full table in §1.6):** `is_keys_misproj'vc` **Valid** and `misproj_claim` **Valid** (the false CPython claim is a theorem of the lowering as emitted), `false_claim_faithful` **Unknown** (not provable through the faithful projector), the mutual `node`/`hval` sum type-checks and its round-trip lemmas prove, `false_bridge` not provable, `bump_faithful'vc` **Unknown (sat)** while `bump_as_emitted` generates no VC.

### 1.4 Corpus-style programs for the two hazards [M]

All live in `scratchpad/vmF/toy/`. They use only what any user program may use: the identity decorator `def mutable_state(cls): return cls` (5 reference-corpus programs declare it, e.g. `test-suite/corpus/pycsl-reference/5249_gen37_r384_field_alias_pop.py`), `@dataclass`, and the forward-ref annotation `"ExprIR"` (the report's own t3 shows it is accepted in a plain program).

| toy | shape | L3 | emission (the load-bearing lines) |
|---|---|---|---|
| **f1_kind_misproj** | `@mutable_state class Em: def is_keys_view(self, node: "ExprIR") -> int: if isinstance(node, DictView): dv = node; if dv.kind == "keys": return 1; return 0` with `ensures \result == 0` | **✓** | `f1…mlw:298-311`: `ensures { (result = 0) }` … `if (py_isinstance_DictView_emit_ir_op node) then begin dv := node; if (str_eq_op (kind_of !dv) "keys") then begin raise (Return 1) end end; raise (Return 0)`. No `kind_of` arm returns `"keys"` (grep of the 110-arm match: the only `"keys"` in the file is line 307), so `result = 0` is a theorem of the model and **false of CPython** (`Em().is_keys_view(DictView("d","keys")) == 1`). |
| f1p (same, plain function) | — | ✗ | `dv` is declared `ref 0` (int) and `dv := node` fails L3 (`f1p…mlw:300-301`). Fail-closed **by accident** (the projector path is `@mutable_state`-gated, the local's type is not). |
| f1h (honest `ensures \result >= 0 and \result <= 1`) | — | ✓ | identical body |
| f2 / f2p / f2a (store through a **parameter** typed `"ExprIR"`) | — | REFUSED | `core_ir_semantic.py:616` `Subscript assignment to non-list/dict variable 'd' (type 'ExprIR')` (`PYCSL-SEM-SUBSCRIPT`). Good: the parameter case is closed. |
| f2l / f2m (store on a **local** `d = self.mk(k)` with `mk -> "ExprIR"`, then a read and a `return`) | — | ✗ | `f2l…mlw`: `d := (self_mk_1 k); k0 := (kind_of !d); ()` — `k1 = …`, the `if`, and both `return`s are **gone**; L3 fails only because the function is `int`-typed and the tail is now `()` (`This expression has type int, but is expected to have type ()`). |
| f2n (store, then `self.count = self.count + 1`, `assigns self.count`, false `ensures self.count == \old(self.count)`) | — | ✗ | Why3 L3: `this write effect does not happen in the expression` — the field write after the store was dropped; the `writes` check catches it by luck. |
| **f2o_dropped_tail_precond** (store, then `self.need_empty(an)` whose contract is `requires an == ""`; outer `assigns \nothing`, `ensures True`) | — | **✓** | `f2o…mlw` `em__bump`: `let d = ref (IrOther "") in d := (self_mk_1 an); ()`. **No callee-precondition obligation.** |
| f2o_control (identical minus the store) | — | ✓ | `em__bump`: `… let _ = begin assert { [@expl:PyCSL-R167 callee precondition at a stubbed method call] (((an) = "")) }; (self_need_empty_1 an) end in ()` — the VC is present and unprovable for `an <> ""`. |

Full-proof runs of f1 and f2o/f2o_control were queued (`heavy.sh`, NORMAL class) and were still waiting for a slot at time of writing (§1.6). The emission-level evidence above is already decisive for f2o: the proof obligation does not exist in the WhyML, so Why3 cannot fail it.

### 1.5 Census arithmetic [M]

`python3 -I` over `scratchpad/cv9/merged.json`: 245 chains; **42** contain `cap-vm-unerase-irnode` in `need` (matches). Split by `src`: cv9 37, lvB 2, lvC 3. Chains whose `finals` list contains the capability: 37; chains whose **last** `finals` entry is it: **29**. Chains where it is the only entry of `need`: **2** (`_csl_in`, `_csl_list_to_ir`); `_desugar_acts` has `need = ['LIVE-REFACTOR', 'cap-vm-unerase-irnode']`. File counts (ir_resolve 8, monomorphize 8, Module2 6, preamble 5, Module3 4, Module5 4, core_ir_semantic 2, expr_ghost_spec_ops 2, ir_inline 1, scc 1, pycsl 1) match the report.

### 1.6 Proof verdicts [M]

All four heavy slots were held by other agents' batch jobs for the first hour of the review (my `why3 prove` entry queued at 10:51 UTC never got a slot; the f1 entry died on its own 50-min `timeout` while waiting). The driver agent then authorised `HEAVY_PRIO=1` for this gate; the runs below are `HEAVY_PRIO=1 scratchpad/heavy/heavy.sh scratchpad/vmF/proofPrio.sh` and `…/proofPrio2.sh` (one queue entry each, still inside heavy.sh's memory-capped scope).

**H2, the dropped continuation — the full-proof differential is decisive:**

| program | pycsl verdict | the load-bearing lines |
|---|---|---|
| `toy/f2o_dropped_tail_precond.py` (store, then a call whose `requires an == ""` is violated) | **`[+] Verification SUCCESS! All contracts formally proven.`** (`toy/f2o_dropped_tail_precond.proof.log:472`, 115 sub-goals Valid, `rc=0`) | there is no R167 sub-goal in the log: the call is not in the model |
| `toy/f2o_control.py` (identical minus the store) | **`[-] Verification FAILED or INCOMPLETE`** (`toy/f2o_control.proof.log:483`, `rc=1`) | `:455 Sub-goal PyCSL-R167 callee precondition at a stubbed method call of goal em__bump'vc.` `:456 Prover result is: Timeout (30.00s, 74847954 steps).` — the one sub-goal that is false of the program is the one that does not prove |

A program that violates a callee's precondition in CPython is reported *fully proven* by the verifier at HEAD, and removing one statement that lowers to `()` turns the verdict into the correct failure. This is a reachable fail-OPEN today.

**H1, the `.kind` misprojection — the model entails the false claim; the 110-arm instance is solver-bound:**

| run | verdict |
|---|---|
| `toy/f1_kind_misproj.py`, pycsl default provers (30 s) | `[-] Verification FAILED or INCOMPLETE`; 114 sub-goals Valid; the one Timeout is **the postcondition itself**: `Sub-goal postcondition of goal em__is_keys_view'vc. Prover result is: Timeout (26.90s, 17012145 steps)` (`toy/f1_kind_misproj.proof.log:453-456`). The prover did not refute `result = 0`; it ran out of time case-splitting the 110-constructor `kind_of`. |
| same goal, `why3 prove -a split_vc -P z3 -t 120` on the emitted `toy/f1_kind_misproj.mlw` | two of the three path sub-goals Valid; the `return 1` path `Timeout (120.00s, 95071616 steps)` (details below) |
| spike `DictViewTag.misproj_claim` (3-arm model of the same lowering) and `is_keys_misproj`'s `ensures { result = 0 }` | **both Valid with Z3 in under 0.01 s** (table below) |

Reading: the emitted VC `forall node. py_isinstance_DictView_emit_ir_op node -> str_eq_op (kind_of node) "keys" = false -> result = 0` is valid in the model because `kind_of` is a total function whose 110 arms are all constants other than `"keys"`; whether a 30-second SMT call finds the case split is a scale question (the report's §4.4 point), not a soundness one. The soundness defect is that the VC *is* valid of a program for which the claim is false. H1 is therefore **confirmed at the model level and solver-bound at the oracle level**; H2 is confirmed outright.

**f1 at 120 s** (`why3 prove -a split_vc -P z3 -t 120 toy/f1_kind_misproj.mlw`, `toy/f1_kind_misproj.z3-120.out:448-460`): the postcondition splits into three path sub-goals; the two `return 0` paths are `Valid (0.01s, 6942 steps)` / `Valid (0.00s, 4046 steps)`, the `return 1` path (which needs `kind_of node <> "keys"` across the 110 arms) is `Timeout (120.00s, 95071616 steps)`. Alt-Ergo at 120 s gave `High failure (unrecognized prover answer)` on the string goals and was cut by my outer 600 s timeout (`ae-120.out`), so it adds nothing. The emitted `str_eq_op` carries `ensures { result <-> (a = b) }` (`f1…mlw:295-296`, and the same in the mirror emission `p14…mlw:1669-1670`), so the VC is valid in the model; the solver, not the model, is what stands between the program and a false SUCCESS.

**Spike** (`scratchpad/vmF/spike/dictview_tag.mlw`, `why3 prove -P z3 -t 10`, `spike/dictview_tag.z3.out`; Alt-Ergo agrees on every goal it does not time out on — its string reasoning is weaker, `spike/dictview_tag.altergo.out`):

| goal | meaning | Z3 |
|---|---|---|
| `tag_of_dictview`, `kind_roundtrip` | honest tag/field facts | Valid |
| `is_keys_faithful'vc` | the faithful lowering meets its two-clause contract | Valid |
| **`is_keys_misproj'vc`** | `ensures { result = 0 }` on the lowering **as emitted today** (`.kind` → `kind_of`), false of CPython | **Valid (0.00s, 672 steps)** |
| `false_claim_faithful` | the same false claim through the faithful projector `dv_kind` | **Unknown** (not provable, as it must be) |
| **`misproj_claim`** | `forall e. is_dictview e -> kind_of e <> "keys"` | **Valid (0.00s, 652 steps)** |
| `roundtrip_node`, `get_stored_node` (`HNodeBridge`, mutual `node`/`hval`/`hpairs` sum) | Why3 accepts the mutual sum (report Q5: positivity is not the obstacle) and the coercion round-trips | Valid |
| `false_bridge` | a stored node is not an arbitrary other node | Timeout (not provable, as it must be) |
| `bump_faithful'vc` (`DroppedTail`) | the callee precondition after the store, as the program reads | **Unknown (sat)** — the VC fails |
| `bump_as_emitted` | the same with the continuation dropped, as emitted | no VC generated at all |

So the spike isolates both defects in a model small enough for a 10-second prover: the misprojection turns a false CPython statement into a theorem (`misproj_claim`, `is_keys_misproj`), the faithful projector does not (`false_claim_faithful`), and the dropped continuation removes the obligation rather than weakening it (`bump_as_emitted` vs `bump_faithful`). The f1 emission is the same theorem over 110 arms; only the solver budget differs.

Spike harness notes (so the next reviewer does not lose the 3 iterations I did): in WhyML *program* code a bare `=` on strings resolves to `int` equality once `int.Int` is in scope — the emitter's `str_eq_op` val-with-law shape is the right one in spikes too; a recursive helper used only in formulas should be a logic `function`, not a `let function`.

---

## 2. Claims: wrong, over-scoped, under-scoped

### 2.1 Over-read or imprecise (minor)

- **"the terminal wall on 37 of them"** (§0.1). The census table column that reads 37 is the `cv9` source column (`run5-chain-census.md:212` header `| capability | family | stubs | cv9 | lvA | lvB | lvC | lvE |`). By the data, 37 chains *list* the capability among their finals and 29 have it as the last link. Over-read by 8 on the strict definition; the conclusion ("largest single capability") stands either way.
- **"On only 3 chains is it the only non-free capability"** (§0.1). Two, plus `_desugar_acts` if `LIVE-REFACTOR` is counted as free (the census does; the report should say so, because a live refactor is a sanctioned emission change with its own sweep).
- **"`\trusted` count 413 vs my 385 marker lines"** (§8). My `grep -c '^\s*#@ \\trusted'` over `src/self-annotate/src` also gives **385**. The 413 in log 490 is the driver's rule; the report is right to flag the unreconciled gap, and it should be reconciled by the driver, not by either of us.
- **Sub-seam C** (§3.1): the ADT **does** declare `IrProj emit_ir int` (`p01_csl_in.mlw:195`, `kind_of` arm `:244 | IrProj _ _ -> "ProjExpr"`). The census wording "carries the Proj index as an emit_ir child" is stale; the report already suspected this. Both C stubs stop first at R563 (`p04`), which I did not re-run.

### 2.2 Refuted

- **"`materialize` exists only for int sequences"** (§2.3, R2). `probe/p02_csl_list.mlw:901`: `val materialize_ir (s: Seq.seq emit_ir) : array emit_ir`, with the preamble comment at `:888` ("the emit_ir analogue of `materialize_str` … Gated on `_uses_synthesize_overload_guard`"). The *theory* for a `seq emit_ir → array emit_ir` return already exists in this very file; what is missing is the return-type lowering choosing it when the mirror return annotation is `List["ExprIR"]` (p13 shows the function is still emitted `: array int`). That is a recognizer change in `functions.py` (hot twin, ≈ 6 h proof) — but not a new instance, not a theory change, and not a cert touch. R2's "give `materialize` an `emit_ir` instance" is already done.

### 2.3 Wrong framing (the important one)

- **"The erasure is fail-closed by design, and that is why the stubs are stuck rather than unsound"** (§0.3) and **"[H1] does not break the type-safety contract `ensures True`"** (§2.3), **"[H2] a sound no-op for the type-safety+frame contract"** (quoting `statements.py:2698-2703`).

  Both statements are true *of the mirror conversion contract* and false *of the verifier*. The two lowerings are not gated on the mirror; they are gated on `_current_self_type in _mutable_state_classes` (`statements.py:2704`, `expressions.py:5400-5403`), and `mutable_state` is an identity decorator any program may declare. A user program with a `@mutable_state` class and an `"ExprIR"`-typed value reaches both paths today (f1, f2o). Under a *value* contract (`ensures \result == 0`, a callee `requires`), they produce a false proof (f1) and a vanished obligation (f2o). The report's §7.1(c) says "latent"; it is live.

### 2.4 Under-scoped

- **H2 is a dropped continuation, not a dropped mutation.** `_handle_array_set_stmt` (statements.py:2694) is a CPS handler: every handler lowers `rest` itself (`:5085-5115` dispatch; the handler's normal exit at `:2694+338` does `code += ";\n" + self._stmts_to_whyml(rest, …)`). The emit_ir branch `return f"{indent}()"` at `:2706` exits before that line. f2l shows the loss directly (`k1`, `if`, `return` absent). In the mirror the only verified body with such a store, `stmt_control_flow.py:1134 c["pattern"] = new_pat` in `_handle_match_stmt`, has the store as the *last* statement of its block, which is why nothing was ever noticed. In p02 the store is also last in its `if`. The hazard the report names (`act_name` never attached) is the benign half.
- **Q3 (dropped-mutation gate).** Neither gate can see H2 by construction: `bin/check-dropped-mutation.py` says its population is "Module 5's ASSIGNMENT-family statements (a statement that produces no IR at all)"; `bin/check-param-mutator-visibility.py` says it is keyed on "a collection **PARAMETER**" and that "the two planes are disjoint by construction". H2 is an IR statement (`ArraySet`) on a **local**, lowered by Module 6 to `()`. Gate hole confirmed.
- **R1 step 2 (narrowing) is scoped as a feature; it is also the fix for H1.** The shared table `_EMIT_IR_STR_ATTRS` (`expressions.py:185`) is keyed by attribute name only, and `_is_string_expr` applies it whenever `ft is None` and the receiver `_is_emit_ir_expr` (`:5398-5403`). Any `.kind/.name/.op/.func/.var/.label/.base/.arr/.ctor/.id/.attr` read on a non-IR object held as emit_ir is misprojected. The 5-line fail-closed version (refuse a `_EMIT_IR_STR_ATTRS` read on a local that was bound inside an `isinstance(x, C)` branch where `C` is a record-modelled class that is not an IR node) costs no cert and no proof-hour beyond the `expressions.py` re-port, and it is what makes H1 go away *before* the narrowing exists.

### 2.5 Confirmed as stated

The four-sub-seam split (A verified on p01/p02/p06; B/C/D taken from census text, not re-probed); the five non-interoperating value models (I checked `HNode hval` in the report's citation, not the pydict side); records read from the **live** class bodies (p14 vs p11, with the p11 caveat in §1.1); the specless `py_isinstance_*_emit_ir_op` vals; the int-hashed string compares; the `IrOther "MapValueIs"` field drop; the constant-false vararg guard and int-hashed symtab compares in `_csl_in`'s tail (p14b); the "recognizer is the bottleneck" reading (lesson (q), `wall-lessons.md:1286-1292`, and the `materialize_ir` finding is one more instance of it).

---

## 3. Are the two hazards real soundness bugs reachable today?

### 3.1 H1 — `.kind` misprojection after `isinstance(x, DictView)`: **YES** (value-level)

`scratchpad/vmF/toy/f1_kind_misproj.py`:

```python
def mutable_state(cls): return cls

@dataclass
class DictView:
    coll: str
    kind: str

@mutable_state
class Em:
    #@ requires True
    #@ ensures \result == 0
    #@ assigns \nothing
    def is_keys_view(self, node: "ExprIR") -> int:
        if isinstance(node, DictView):
            dv = node
            if dv.kind == "keys":
                return 1
        return 0
```

CPython: `Em().is_keys_view(DictView("d", "keys")) == 1`. Emitted (`f1_kind_misproj.mlw:298-311`): `ensures { (result = 0) }` over `if (str_eq_op (kind_of !dv) "keys") then raise (Return 1)`. `kind_of` is a total `let function` over the 110 constructors, none of whose tags is `"keys"`, so `result = 0` is provable by case split (Why3 verdict in §1.6 when the slot frees; the spike's `misproj_claim` goal is the same statement in a 3-arm model).

Reachability conditions: a `@mutable_state` class (user-declarable), an `"ExprIR"`-typed value (user-annotatable), a user class with a field named like a table key (`kind`, `name`, `op`, `func`, `var`, `label`, `base`, `arr`, `ctor`, `id`, `attr`), an `isinstance` to it, and a value contract. None of these needs the mirror.

Why it type-checks only inside `@mutable_state`: outside, `dv` is declared int (`f1p…mlw:300`) and fails L3 — the fail-closed outcome is an artefact of two gates disagreeing, not a design.

### 3.2 H2 — `<emit_ir>[k] = v` → `()`: **YES** (contract-level, independent of the value model)

`scratchpad/vmF/toy/f2o_dropped_tail_precond.py`:

```python
@mutable_state
class Em:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def mk(self, k: str) -> "ExprIR":
        return {"type": "Var", "name": k}

    #@ requires an == ""
    #@ ensures True
    #@ assigns \nothing
    def need_empty(self, an: str) -> None:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def bump(self, an: str) -> None:
        d = self.mk(an)
        d["act_name"] = an
        self.need_empty(an)
```

CPython: `Em().bump("x")` violates `need_empty`'s precondition. Emitted `em__bump` = `let d = ref (IrOther "") in d := (self_mk_1 an); ()`. The control without the store emits `assert { [@expl:PyCSL-R167 callee precondition …] ((an) = "") }; (self_need_empty_1 an)`. The obligation is not weakened; it is **absent**. Any statement after the store in the same block is absent: a `raise` (so a `raises`/`no_exception` claim), a field write (caught by Why3's `writes` check only if declared, f2n), a `return` (caught by L3 only if the function is non-unit, f2l).

Reachability: `@mutable_state` class + an emit_ir-typed **local** (a parameter is refused by `core_ir_semantic.py:616`) + a store. The fix is a one-line refusal (raise `PyCSLSemanticError` in the emit_ir branch of `_handle_array_set_stmt`, the same family as `PYCSL-WHYML-PARAM-COLLECTION-MUT` at `:2681`) or, at minimum, falling through to the `rest` lowering. Byte-diff exposure: every verified mirror body with such a store (`stmt_control_flow.py:1134` is the one I found by grep; a refusal there would un-verify `_handle_match_stmt`, so the `rest`-lowering variant is the byte-safe one, and a refusal keyed on "non-empty `rest`" is the safe-and-sound one).

### 3.3 What the two have in common

Both are gated on `@mutable_state`, i.e. the mirror's own convenience gates leaked into the user-facing semantics. Neither is a value-model limitation. They are the "coherent-and-wrong" class SKILL.md §0 warns about, and they would pass every current plane: L3, the whole-file proof under `ensures True`, byte-diff 0, and both mutation gates.

---

## 4. The four questions in the report's §9

1. **R1 / `kind_of` stays:** yes (p14b, §1.1). A narrowing to the `dictview` record without a new arm is possible as `val function view_dictview (e: emit_ir) : dictview` with no law — honest about type, blind about value (the report says this correctly). Non-vacuity would need a law tying `py_isinstance_DictView_emit_ir_op e` to the view, which is an `IrDictView string string` arm in all but name. So: refuse now (§2.4), narrow with the arm later.
2. **Do verified mirror bodies already contain a misprojected `_EMIT_IR_STR_ATTRS` read?** Bounded by grep: every `.kind` read in non-trusted mirror bodies is on a real IR node (`expressions.py:1438/1461/1607`, `expr_ghost_collections.py:163 s_ir.kind` with `s_ir = node.set`, `node: "ExprIR"`), where `kind` **is** the tag field of the `ir_schema` dataclass; `pure_ast.py:4953 node.kind == "u"` is on an unannotated (int-erased) `node`, so it goes through `get_kind` + hash, not `kind_of`. I found **no** misprojection in a verified body. The exposure is in future conversions (`_csl_in`, `_region_bound_str`) and in user programs.
3. **Gate:** hole, see §2.4.
4. **R3 s013:** not probed (budget); the census row (`merged.json` s013) lists `cap-R325-call-set-ctor` as the first link before the IR-dict read, so the report's "set() ctor first" ordering is right.
5. **`HNode` ↔ `emit_ir` positivity:** the spike's `HNodeBridge` module defines `node`/`hval`/`hpairs` as one mutual strictly-positive block (`IrHVal hval` inside `node`, `HNode node` inside `hval`). Why3 accepts it and proves `roundtrip_node` / `get_stored_node` (Valid, Z3 and Alt-Ergo), while the false `false_bridge` stays unprovable (§1.6). Positivity is not the obstacle. The real cost is the certificate side (`Phase2f_PyVal` would become mutual with the TermIR cert) and the emitter coercions.

---

## 5. The route I would take (≈ 60 h wall clock)

Guiding fact from this review: the model already has every piece the first three links need (`emit_ir`, `func_of/args_of`, `str_eq_op`, `materialize_ir`, record types for every CSL class, `cslx_view`); every blocker I touched was a recognizer/gate, and two of them are unsound. So spend proof-hours on *wiring and gates*, not on new sums or certs.

**Step 0 (3 h, mandatory, converts 0): close H1 and H2.**
- `statements.py` emit_ir `ArraySet` branch: refuse when `rest` is non-empty or the stored value is later read; otherwise fall through to the `rest` lowering. Re-emit the 52 mirrors (`bin/mirror-emit-sweep.sh`), expect byte-diff 0 except `stmt_control_flow` (unchanged if the fall-through is taken).
- `expressions.py` `_is_string_expr`/`_handle_attribute_expr`: refuse a `_EMIT_IR_STR_ATTRS` read on a local bound in an `isinstance(x, C)` branch where `C` is a record-modelled non-IR class. Corpus sweep expected 0 (no corpus program holds an emit_ir var: `expressions.py:3347` comment).
- Owes: `expressions.py` + `statements.py` whole-file proofs (≈ 6 h + 5.3 h, sequential per RULES.md rule 10). Run them as the background of steps 1-2.
- Add two corpus programs (f1-shaped expected REFUSED, f2o-shaped expected REFUSED) so the planes see the class.

**Step 1 (make-or-break spike, 2 h QUICK, 0 proof-hours): `List["ExprIR"]` return wiring.** In a scratch copy, make the return-type lowering in `functions.py` select `array emit_ir` + `materialize_ir` when the (mirror) return annotation is `List["ExprIR"|"StmtIR"|…]`, gated on that annotation so int lists are untouched. Gate: p13 re-run must give L3 ✓ for `_csl_list_to_ir` **and** `bin/byte-diff-sweep.sh` 0 **and** `mirror-emit-sweep` moves only Module5. **Refutation exit:** if the materialized `array emit_ir` cannot be consumed by the callers' `array int` interface without touching `_py_stmts_to_ir`-style dispatchers (the "RETURN-type retype rewrites the interface every caller was verified against" lesson from `15a134ced`), stop the list track and report the blocking caller.

**Step 2 (R1 step 1 + R2 landing, ≈ 8 h incl. one Module5 proof ≈ 1 h and the pycsl mirror):** live `CSLIn` retype (precedented, `ef94162f`), wire step 1, convert `_csl_list_to_ir` with the `act_name` store **refused by step 0 → so it does not convert verbatim**. Honest yield: `_csl_list_to_ir` needs the `act_name` decision (an `IrActTag string emit_ir` wrapper arm, cert touch) — if the user wants a count, that is the cheapest new arm in this family and it also closes the `IrOther "MapValueIs"` field drop by the same mechanism (one construction-only leaf, lever (3) at `driver-backlog.md:4888`). Yield: 1-2 stubs (`_csl_list_to_ir`, `_parse_expr_list` link).

**Step 3 (R3 slice, remaining ≈ 40 h):** `FunctionView` TypedDict for the function-entry record, optional keys as `option`, consumed first by `core_ir_semantic` (s013/s016; proof ≈ 1.7 h). Spike gate before building: port s013 verbatim with the view declared in scratch; if the next wall is non-VM (`set()` ctor R325 is first per the census), build that one-line ctor model first, re-probe; if the second wall after the view is `elem-store-nonlist` or closure-lift, stop R3 for that file and move to `preamble` s137/s127 or `scc` s140. Expected closed: 3-5.

**Not** in 60 h: R4, any new sum type, any new cert. The `DictView` arm (R1 step 2) only if `_region_bound_str` turns out to need it too; otherwise the step-0 refusal is the sound answer.

**Per proof-hour estimate:** step 0 ≈ 11 h of proof for 0 stubs but it removes two false-proof classes; steps 1-3 ≈ 5-7 h of proof for 4-7 stubs. The report's R-ranking has R3 second; I would put it third behind the list wiring only because `materialize_ir` exists and p13 is already one link from L3 ✓.

---

## 6. Certified boundary or cost wall?

**Cost/scale wall**, with this precise statement of what would make part of it a certified boundary:

- A **certified boundary** would be a theorem-shaped statement that some Python value or operation reachable in the mirror has *no* definitional model under the ledger (3 axioms, strictly positive sums, no uninterpreted laws). Nothing in this wall is of that shape. `Any` as a sum is definable (three certified instances exist); the fragmentation between them is a coercion problem (`HNodeBridge` shows the mutual sum is well-formed); open-world dicts are `option` fields plus a dynamic tail (`K_dyn string` already exists in `irkey`); reflection (`type(node)` dispatch, `getattr(c, "act_name", None)`, class objects as values) needs a finite class-tag universe with per-class attribute tables — finite, enumerable from the source, definitional. Nagini's axiomatic route is barred, the definitional route is not.
- What **is** a limit today, and should be written down as one, is **scale**: a 110-arm `kind_of` in every string compare, 23 k goals in `expressions`, and no measurement of what a sum-typed `Any` does to the 2-6 h per-file envelope. That is a budget statement, not a correctness one, and the report says so (§4.4).
- Two **correctness defects** ride on the wall (H1, H2). They are not boundaries either; they are gates that the mirror's convenience leaked through. Until step 0 lands, every "TC ✓ facade" in sub-seam A is at risk of being coherent-and-wrong in exactly the way the report predicts and SKILL.md §0 names.

**Bottom line for the driver:** keep the capability label, drop the "fail-closed by design" sentence, land the two refusals before any further sub-seam-A conversion, and cost R2's list half as wiring (the model is there).

---

## 7. Limits of this review

- Everything in §1 is `--no-proof` (L3) except the three queued proof jobs (§1.6). "L3 ✓" never means proved.
- I re-ran p01, p02, p03, p06, p11, p13, p14 and added p14b; I did not re-run p04, p05, p07, p12 or the sub-seam B/C/D stubs.
- The p11 first attempt (`batchF.sh`) silently degraded to a port-as-is (patch assertion on the mirror's `'…'` docstring); the corrected run is `batchG.sh` (§1.1). Lesson for the harness: `probe.sh` should fail the probe when the extra patch exits non-zero instead of logging and continuing.
- The `.kind` grep (Q2) covers `kind` only; the other ten table keys were not grepped.
- No whole-file mirror proof was run; proof-hour figures are the report's recorded ones.

## 8. Reproduce

```
cd /home/fabrice/git/pycsl
mkdir -p scratchpad/vmF/st && git archive HEAD src/pycsl src/self-annotate bin | tar -x -C scratchpad/vmF/st
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchA.sh     # p01 p02 p13 p14 p14b
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchB.sh     # toys t1 t2 t5 t6 f1 f1p f1h f2 f2p f2a
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchC.sh     # f2l f2m
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchD.sh     # f2n f1h
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchE.sh     # f2o f2o_control
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchF.sh     # p06 p03
HEAVY_QUICK=1 scratchpad/heavy/heavy.sh scratchpad/vmF/batchG.sh     # p11
source scratchpad/g29/env.sh
scratchpad/heavy/heavy.sh why3 prove -P alt-ergo -t 10 scratchpad/vmF/spike/dictview_tag.mlw
scratchpad/heavy/heavy.sh python3 src/pycsl/pycsl.py scratchpad/vmF/toy/f1_kind_misproj.py
scratchpad/heavy/heavy.sh scratchpad/vmF/proofF2.sh
```
