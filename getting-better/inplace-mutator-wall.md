# W-IPM: the in-place collection mutator wall (census and routes)

*A state-of-the-art report for an independent reviewer. Dated 2026-10-12, branch `ghost-assign-bc6`,
HEAD `b05638d9`. The report is self-contained: every number below comes from a command that was run
on this tree. The instrument logic is in Appendix A and the probe sources are reproduced inline.
Nothing under `src/`, `bin/` or `test-suite/` was modified to produce it. The census harnesses edit
mirror files inside eight throw-away copies of `src/`+`bin/`+`config/`, and they edit LIVE files only
as scratch copies outside the tree. `git status` after the run shows only the pre-existing `.aux`
noise.*

**Short version.**
1. **Census.** The in-place mutator refusal family is the **first** blocker of **86 of the 435**
   `\trusted` stubs (19.8%). That makes it the largest refusal class. The next refusal classes are
   nested-closure (24) and `with … as` (12). The 229 located Why3 type errors are not a single class.
   The 86 split by refusal site as follows: 77 `expressions.py` receiver-mutator guard, 7
   `statements.py` self-field `append`, 2 list-parameter `append`. By receiver kind: **44 LOCAL** ·
   29 self field · 11 parameter · 2 other. By mutator: `pop` 23 · `setdefault` 22 · `extend` 10 ·
   `append` 9 · `add` 6 · `update` 5 · `clear` 4 · `insert` 3 · `sort` 3 · `reverse` 1. All 27 rows
   that the out-of-band ledger (`trusted-reasons.tsv`) classes as `in-place-mutator` are in this set.
   The other 59 are ledger-`unclassified`.
2. **Second blocker (measured on all 86, not a sample).** I erased every refused mutator site
   iteratively in a scratch copy of the live body and re-emitted. **Only 8 of the 86 then type-check.**
   The other 78 stop at:
   * 23 `string`↔`int` seam errors,
   * 28 other type errors,
   * 6 errors at `emit_ir`/`hval` boundaries,
   * 4 unbound symbols,
   * 4 unlocated type errors,
   * 12 other refusals (nested-closure 5, `except` model 2, `X is True` 2, …),
   * 1 run where the harness gave up (more than 15 sites).

   **Modelling the mutators is necessary for a fifth of the TCB, but it is enough for at most 8
   stubs, and realistically 1–4** (§3.5). The int-erasure seam sits behind it, as it did behind W-SB.
3. **This wall is a modelling choice, not a fundamental limit.** A hand-written Why3 spike (§4.3)
   models dict-field `setdefault`/`pop`/`clear` and list-field `append`/`extend` with a receiver
   plus a `writes` clause. The list field is **rebound to a fresh, exact-length array**, so the length
   is the array's own `length` and needs no shadow `_len`. Results:
   * **16/16** positive goals are Valid under the Z3+Alt-Ergo portfolio.
   * **3/3** non-vacuity witnesses (claims that are false of Python) are **not** proved.
   * There is no axiom.
   * Why3's region discipline **rejects** a stale alias of a rebound array field at type-check time
     (fail-closed). Dict fields are pure maps and get no such protection, so the existing alias guards
     must be extended in lock-step with any new mutator lowering.
4. **Top route (§5): R-C, the list SELF-FIELD mutator by fresh-array rebind.**
   * First-blocker payoff: 8 stubs.
   * Type-checks after erasure: 3.
   * Clean today: 1, `audit_proof.AuditReport.extend`. Its fields are already `array string`. The
     other two append a record into an `array int` field, which is a third blocker.
   * **Make-or-break spike:** emit `self.passes <- Array.append self.passes other.passes` with
     `writes { self.passes, … }`. Then:
     * prove the whole `audit_proof.py` mirror (578 lines; cheap);
     * show that corpus witness `0981` flips from REFUSED to *emitted but its false `\length` claim
       NOT proved*;
     * show a byte-diff of 0 elsewhere on both corpora.
   * The biggest first-blocker population is R-A (LOCAL mutators, 44), but only 2 of the 44 type-check
     after erasure.

---

## 1. Global picture

### 1.1 PyCSL and the mirror
PyCSL is a deductive verifier for Python annotated with `#@` contracts (`requires`, `ensures`,
`assigns`, loop invariants and variants, class invariants). The pipeline is Module 1 (ingest) →
Module 2 (contract parser) → Module 3 (weaver) → Module 4 (semantic checks) → Module 5 (JSON IR) →
Module 6 (WhyML emission, `src/pycsl/module6_whyml/`). Why3 1.8.2 then discharges the VCs with
Alt-Ergo 2.6.3 and Z3 4.13.3. Every command below assumes `. scratchpad/g29/env.sh`, which puts
the opam `framac-coq8` switch on `PATH` and sets `PYTHONHASHSEED=0`.

The self-annotation campaign keeps a **mirror** of PyCSL's own source under
`src/self-annotate/src/**`. It has the same layout as `src/pycsl/`, and it is emitted with
`--import-path src/pycsl`. A mirror function is either:
* **un-trusted**: a verbatim copy of the live body, verified by PyCSL; or
* **`\trusted`**: a stub whose contract is assumed. These stubs are the TCB being shrunk.

```
$ for f in $(find src/self-annotate/src -name '*.py'); do grep -cF '#@ \trusted' "$f"; done | paste -sd+ | bc
477          # lines mentioning the marker
$ grep -rhE '^\s*#@\s*\\trusted\b' src/self-annotate/src --include='*.py' | wc -l
449          # directive lines
```
The porting instrument `bin/probe-conversion-candidates.py` (`all_trusted`) enumerates **435** stub
functions in 44 mirror files. 411 have a live counterpart; 24 report `NO-LIVE-SOURCE`. **The census
unit is these 435.**

### 1.2 Oracle planes (lower bounds) and the ledger
| plane | command | measured now |
|---|---|---|
| fidelity | `bash bin/check-self-annotate-sync.sh` | `OK: all 897 un-trusted self-annotate mirror functions … are verbatim copies of the live source; 37 class-level constants are subsets of live` (7.3 s) |
| whole-file proof | `.venv/bin/python3 src/pycsl/pycsl.py <mirror> --import-path src/pycsl` | not re-run (report only). Cost scales with file size. Recorded: `statements.py` 2h19m and `expressions.py` 2h21m (`driver-backlog.md:635,639`); `pure_ast.py` 2798 goals in ~55 min (`wall-lessons.md:4885`) |
| corpus inertness | `bin/byte-diff-sweep.sh <dir>` then `bin/byte-diff-compare.py BASE CAND` and `… BASE/pyref CAND/pyref --min-files 2000` | not re-run. §3.6 gives the static corpus exposure and the per-file status of every corpus file that calls a mutator |
| fast planes | `bin/run-soundness-planes.sh` | not re-run |

**Axiom ledger:** the Rocq/Lean certificates under `src/formal-semantics/` keep **3** axioms. This
report adds nothing to them, and the spike in §4.3 uses no `axiom`.

### 1.3 How collection-typed `self` fields and locals are modelled (measured)
**Plain record fields.** I emitted a mirror-shaped class
(`scratchpad/ipm/p_ms_dstore.py`: `@mutable_state @dataclass class C` with
`d: Dict[str,str]`, `di: Dict[str,int]`, `xs: List[str]`, `ns: List[int]`, `s: Set[str]`). The
emitted record is:
```
type c = { mutable d: map string (option string); mutable di: map string (option int);
           mutable xs: array string; mutable ns: array int; mutable s: map string (option int) }
```
The plain (non-`@mutable_state`) twin `p_pl_dstore.py` emits the **same** record.

**Real mirror classes** (each mirror file emitted with `--no-proof --keep-mlw` and its `type … = {…}`
read off):
| Python field | WhyML field | example |
|---|---|---|
| `Dict[str, str]` / `Dict[str, int]` | `map string (option string)` / `map string (option int)` | `ExpressionEmissionMixin._abstract_ops`, `TypeInferenceMixin._known_collection_sizes` |
| `Dict[str, PyVal]` | `map string (option hval)` (the `pyval` carrier) | `PyCSLToJSONEmitter.program_ir` |
| `List[str]` | `array string` (all modules; `preamble.py:8950` "I-E, WIDENED") | `AuditReport.passes`, `_Harvester._module_header` |
| `List[<record>]`, `List[tuple]` | **`array int`** (element erased) | `_Harvester._out: List[PyCSLContract]`, `ConcurrencyChecker.warnings`, `_Harvester._dec_ranges` |
| `List[PyVal]` (under `@mutable_state` or an IR-node param) | `seq hval` (`preamble.py:8930`, "K1") | probe `p_ms_pyvalappend.py`: `type c = { mutable ws: seq hval }` |
| `Set[str]` field | `map string (option int)` (membership = `Some 0`) | probe |
| field not declared in the mirror class | **absent from the record** | `pure_ast._Unparser`: `type _unparser = {  }` |

**Locals and parameters.**
* A list local that is appended to is `ref (seq T)`: `xs := Seq.snoc !xs v` (`f_local_append.mlw`).
* A literal-initialised list local is `ref (Seq.cons …)` with a dead `_len` (`f_lit_local_pop.mlw`).
* A dict local is `ref (map k (option v))`.
* A set local is `StrSet` (a `set.SetApp` clone over `string`).
* A dict or set **parameter** is `ref (map …)` with `writes { s }`.
* A list parameter is `array T`.

The two set models do not meet. `f_param_sadd_vis.py` (a caller passes a `set()` local to a
`Set[str]` parameter) fails L3-tc: `unbound function or predicate symbol 'map_update_some'`, which
is a `StrSet.set` vs `ref (map …)` mismatch. This fails closed.

**`@mutable_state`** is a class decorator (`def mutable_state(cls): return cls`) that sets the IR
flag `type_decls[].mutable_state` (`docs/ir.md:208`). It authorises the caller-visible
mutable-`self` model, and recognisers across Module 5/6 are gated on it (409 source lines under `src/pycsl` mention it). Every mirror emitter mixin
carries it (for example, `src/self-annotate/src/module6_whyml/expressions.py:16`). For the mutators
measured here, its only effect is that `self.s.add(x)` and `self.s.discard(x)` on a set field are
lowered (`self.s <- map_update_some self.s v 0`, `writes { self.s }`) instead of refused (§2.2).

---

## 2. The wall as first seen

### 2.1 Refusal sites in the live emitter
| site | trigger | message head |
|---|---|---|
| `src/pycsl/module6_whyml/expressions.py:36` | `_SELF_FIELD_MUTATORS = {append, extend, insert, remove, pop, clear, sort, reverse, update, popitem, setdefault, add, discard, intersection_update, difference_update, symmetric_difference_update}` | (the set) |
| `expressions.py:7818–7829` (routes #13/#14) | the generic abstract-op fallback is reached with `not receiver_param and not writes_clause` and the method name is in the set. **Any receiver**: self field, local, parameter | ``"`X.m(...)` MUTATES its receiver in place, and no certified lowering models it: the call becomes an abstract operation that takes NEITHER the receiver NOR a `writes` clause, so the mutation would be SILENTLY ABSENT …"`` |
| `expressions.py:7781–7816` (route #162) | `_R162_ARG_MUTATORS` (`heapq.*`, `random.shuffle`, `bisect.insort*`, `struct.pack_into`, `operator.setitem/delitem/iadd/iconcat`) with a collection argument | ``"`f(...)` MUTATES an ARGUMENT in place …"`` |
| `module6_whyml/statements.py:2852–2866` (code `PYCSL-WHYML-PARAM-LIST-APPEND`) | `.append` on a formal list parameter (outside `_stmt_seq_mut_params`) | `"in-place `append` to list parameter 'a' is out of scope: Python passes a list argument BY REFERENCE …"` |
| `statements.py:3034–3047` (route #13b) | `self.<f>.append(x)` reaches the array-local arm (`Array.make 1024 0` shadow, no write-back) | ``"`self.xs.append(...)` appends to the collection in the field `xs`, and no certified lowering models it …"`` |
| `statements.py:538–560` (alias guard) | `ys = xs` followed by an `.append` through either name. Its comment: "WHY ONLY `append`: every other length-changing list mutator on an aliased list is ALREADY a pipeline refusal" | `aliasing a list that is later APPENDED to is out of scope` |
| `statements.py:1020–1068` (alias guard) | `e = d` (or `= self.<dict field>`) followed by a store (`ArraySet`, `FieldAssign`, …) through either name | `aliasing a mutated dict is out of scope` |

The guard at `expressions.py:7818` keys on the **lowering** (an abstract op with neither receiver
nor `writes`), not on the receiver. Its own comment records why: the narrower `self.`-only version
was exploited through locals and parameters (corpus witnesses 0980–0983).

### 2.2 What the language allows today (probe matrix)
Probes are in `scratchpad/ipm/`, generated by `gen.py` (Appendix A.1). Each one is a single-method
class `C` with the fields listed in §1.3 and `#@ assigns <field>`, or a single function. Each was run
with `pycsl.py <probe> --import-path src/pycsl --keep-mlw`.

| construct | plain `@dataclass` | `@mutable_state` | local | parameter |
|---|---|---|---|---|
| `d[k] = v` (dict store) | **lowered, proved**: `self.d <- map_update_some self.d k v` | same, plus `writes { self.d }` | **lowered, proved** (`d := map_update_some !d k 1`; `ensures \result == 1` Valid) | **lowered, proved** (`d: ref (map …)`, `writes { d }`) |
| `d.setdefault(k, v)` | REFUSED (7820) | REFUSED (7820) | REFUSED (7820) | REFUSED (7820) |
| `d.update({k: v})` | REFUSED | REFUSED | REFUSED | – |
| `d.pop(k, None)` / `d.clear()` | REFUSED | REFUSED | – | – |
| `xs.append(v)` | REFUSED (13b, 3035) | **REFUSED (13b)** for `List[str]`/`List[int]` | **lowered, proved**: `xs := Seq.snoc !xs v` | REFUSED (2855) |
| `ws.append(v)`, `ws: List[PyVal]` | – | **lowered**: `self.ws <- Seq.snoc self.ws (HStr v)` | – | – |
| `xs.extend(..)` / `xs.pop()` / `xs.insert(0, v)` / `xs.sort()` | REFUSED (7820) | REFUSED (7820) | REFUSED (7820) | REFUSED (7820) |
| `s.add(x)` / `s.discard(x)` | **REFUSED** (7820) | **lowered, proved**: `self.s <- map_update_some self.s v 0` | **lowered, proved**: `s := StrSet.add k !s` | lowered (`s: ref (map …)`) |
| `heapq.heapify(xs)` | – | – | – | REFUSED (#162, 7810) |
| alias `ys = xs; xs.append(1)` | – | – | REFUSED (alias guard 558) | – |
| alias `e = d; d["a"] = 1` | – | – | REFUSED (alias guard 1063) | – |

**Lowered unsoundly: none found.** Every refused form fails closed. I also re-checked three lowered
forms with a claim that is false of CPython, and none was proved:
* `self.m("a"); return "a" in self.s` under `ensures \result == False` (`@mutable_state`): **Timeout**,
  not proved (`p_ms_sadd_vis.py`; Python prints `True`).
* `d: Dict[str,int] = {}; d["b"] = 1; return d["a"]` under `#@ no_exception KeyError`: the emitter
  inserts `assert { Map.get !d "a" <> None }`, which times out, so the run reports FAILED
  (`f_keyerror.py`; Python raises `KeyError`). Without `no_exception`, the `None -> 0` arm is the
  usual partial-correctness reading of a raising read.
* The parameter set-add through a caller fails L3-tc (§1.3 seam). This is fail-closed, not a lie.

Two measured gaps on lowered forms (not mutator refusals):
* `\length(self.ws)` on the `seq hval` field lowers to `Array.length self.ws`, which is ill-typed
  (`This term has type seq … hval, but is expected to have type array 'xi`). The faithful K1 append
  therefore cannot yet carry a length postcondition.
* `len(self.ws)` in a contract hits `unbound function or predicate symbol 'iter_length'`.

---

## 3. CENSUS

### 3.1 Method
**A.2 `firsterr.py` (first blocker).**
* For each of the 435 stubs, port the live body *signature-preservingly* using
  `probe-conversion-candidates.py`'s own `probe()`, with only its emit step replaced.
* Run `pycsl.py <mirror> --import-path src/pycsl --no-proof --keep-mlw` and record the first Why3
  error (with the emitted fragment it points at), or the pipeline refusal text.
* Restore the mirror after every candidate.
* Execution: 8 isolated root copies, rsync-restored from the real mirror before each wave, 2 resumable
  waves of at most 570 s. `pure_ast.py` was split 0:29/29:58.
* Result: 435/435 records, no duplicates.

**A.3 `static.py` (receiver classification).**
* For each IPM stub, parse the refusal text to get the receiver and the method.
* Classify the receiver on the **live** AST:
  * a self field gets its annotation from the mirror class, else from the live class;
  * otherwise the receiver is a parameter, a local (annotation or initialiser), a module global, or
    other.
* Read the WhyML field type off a `--no-proof --keep-mlw` emission of the unmodified mirror file
  (11 files, all `L3-tc ✓`).
* Count every in-place mutator call in the live body, nested defs included.

**A.4 `second.py` (second blocker).**
* Same port. While the first blocker is an IPM refusal, rewrite the refused (receiver, method) sites
  in a **scratch copy of the live file**:
  * a statement-position call becomes `None`;
  * `X.pop()` becomes `X[len(X) - 1]`;
  * `X.pop(i)` becomes `X[i]`;
  * `X.pop(k, d)` and `X.setdefault(k, d)` with the value used become `X.get(k, d)`;
  * any other used value becomes `X`.
* Re-emit, up to 15 times. Record the chain of erased sites and the first non-IPM outcome.
* This is **erasure, not modelling**. It answers "what is the next thing that breaks if every mutator
  type-checked as a no-op of the right type", not "would the stub prove".

### 3.2 Whole-population first blocker (435 stubs, this HEAD)
```
L3TC-FAIL 394 = 229 located Why3 errors + 165 pipeline refusals
  refusals: IN-PLACE MUTATOR 86 (77 receiver-guard · 7 self-field append · 2 param append)
            nested-closure lift 24 · with-as 12 · name-rebinding 9 · heterogeneous-list 5 ·
            array-local-reassign 4 · dict-alias 1 · other 24
L3TC-OK   17
NO-LIVE   24
```
`other` contains a few collection-adjacent refusals that are **not** in the 86 and that no mutator
route would retire:
* 4 × `Subscript assignment to non-list/dict variable '<x>' (type 'int')` (an int-erased dict);
* 1 × `del <seq>[i:j]` slice delete;
* 1 × `deque(<iterable>)`.

**Ledger cross-check.** `getting-better/trusted-reasons.tsv` has 27 rows with reason
`cost-scale:in-place-mutator`. All 27 are among today's 86. The other 59 of the 86 are
`unclassified` there.

### 3.3 Breakdown by mutator and by receiver
| mutator | total | self field | param | local | module global | other |
|---|---|---|---|---|---|---|
| `.pop` | 23 | 3 | 2 | 17 | 0 | 1 |
| `.setdefault` | 22 | 9 | 4 | 8 | 1 | 0 |
| `.extend` | 10 | 2 | 1 | 7 | 0 | 0 |
| `.append` | 9 | 7 | 2 | 0 | 0 | 0 |
| `.add` | 6 | 3 | 1 | 2 | 0 | 0 |
| `.update` | 5 | 0 | 0 | 5 | 0 | 0 |
| `.clear` | 4 | 4 | 0 | 0 | 0 | 0 |
| `.insert` | 3 | 0 | 1 | 2 | 0 | 0 |
| `.sort` | 3 | 1 | 0 | 2 | 0 | 0 |
| `.reverse` | 1 | 0 | 0 | 1 | 0 | 0 |
| **total** | **86** | **29** | **11** | **44** | **1** | **1** |

By collection kind:
* **dict 33**: self field 16, param 5, local 11, global 1.
* **list 38**: self field 9, param 5, local 24.
* **set 10**: self field 3, param 1, local 6.
* **unknown 5**: `hashlib.sha256().update`, two `copy.deepcopy(...).pop`, an unannotated `f.pop`, and
  the undeclared `_module_global_classes.pop`.

**Call shapes of the triggering site:**
* `pop`: 14 × `x = stack.pop()` (worklist), 8 × `d.pop(k, None)` as a statement, 1 × `tokens.pop(0)`.
* `setdefault`: 11 as a statement, **6 chained** (`d.setdefault(k, []).append(x)` ×4, `.extend` ×2;
  these need a *nested* in-place update of the map's value), 3 assigned, 2 subscripted.
* Every other mutator is in statement position.

**Self-field receivers and their record model** (29):
| model | stubs | receivers |
|---|---|---|
| `map string (option hval)` | 8 | `PyCSLToJSONEmitter.program_ir.setdefault` (`_emit_typeddict_record`, `_synthesize_typeddict_functional`, `_emit_namedtuple_record`, `_synthesize_namedtuple_functional`, `_emit_protocol_interface`, `_populate_protocol_conformance`, `visit_ClassDef`, `_normalize_union_annotation`) |
| `map string (option string)` | 4 | `ExpressionEmissionMixin._abstract_ops.clear` ×3 (`_handle_call_expr`, `_handle_isinstance`, `_expr_to_whyml`), `_quant_record_binders.pop` |
| `map string (option int)` | 1 | `TypeInferenceMixin._known_collection_sizes.pop` |
| `array string` | 2 | `AuditReport.passes.extend` (and `.failures`, `.skips`), `_Harvester._module_header.append` |
| `array int` (record or tuple element erased) | 6 | `_Harvester._dec_ranges.append`, `_flat.append`, `_flat.sort`, `_out.append`; `ConcurrencyChecker.warnings.append` ×2 |
| **not declared in the mirror record** | 8 | `_Unparser._source.extend`, `_Unparser._type_ignores.clear` (record `_unparser = { }`), `PyCSLToJSONEmitter._cur_literal_ensures.append`, `PyCSLWeaver._csl_bound_names.add`, `PreambleEmissionMixin._axiom_logic_funcs.add`, `._module_global_classes.pop`, `AbstractOpsMixin._abstract_ops.setdefault`, `FunctionEmissionMixin._record_locals.add` |

**Parameter receivers** (11):
* `ir_data.setdefault`, `Dict[str, Any]`, ×4: `ir_resolve._resolve_direct_imports`,
  `_resolve_imported_classes`, `_resolve_imported_base_classes`, `monomorphize._record_classification`.
* `expr.pop('receiver', None)` (`Dict[str,Any]`).
* `tokens.pop(0)` (`List[str]`).
* `pre.extend` (`List[Any]`).
* `out.append` (`List[tuple]`) ×2, in Weaver `_collect_*_sites`.
* `out.insert` (`List[str]`).
* `declared_types.add` (`Set[str]`).

**Local receivers** (44):
* Mostly worklist `pop()`: list literal 5, `List[Any]` 4, `list()` 3, plus `List[Optional[str]]`,
  `List[Tuple[Any,int]]`.
* `extend` on `List[str]`/`List[Any]`/`List[HappyProperty]`.
* `set().update` ×3.
* Dict `setdefault` ×8.
* One each of `sort` (literal and `quote_types`), `reverse`, `insert(0, ·)`.

### 3.4 By mirror file (whole-file proof cost scales with size)
| mirror file | IPM first-blocked | all `\trusted` stubs | mirror lines | live lines |
|---|---|---|---|---|
| `frontend/Module5_IREmitter.py` | **14** | 28 | 3530 | 7201 |
| `module6_whyml/expressions.py` | 8 | 37 | 1924 | 19116 |
| `frontend/Module3_Weaver.py` | 8 | 27 | 521 | 3619 |
| `frontend/Module1_Ingestor.py` | 6 | 12 | 173 | 398 |
| `audit_proof.py` | 5 | 11 | 578 | 577 |
| `frontend/pure_ast.py` | 5 | 58 | 5487 | 3878 |
| `frontend/ir_inline.py` | 5 | 6 | 228 | 545 |
| `frontend/ir_resolve.py` | 5 | 15 | 252 | 3223 |
| `module6_whyml/preamble.py` | 4 | 18 | 408 | 9698 |
| `frontend/monomorphize.py` | 3 | 13 | 350 | 715 |
| `Module6_WhyMLTranspiler.py` | 3 | 11 | 1097 | 1776 |
| `module6_whyml/statements.py` | 3 | 24 | 2032 | 7412 |
| `module6_whyml/functions.py` | 3 | 10 | 1898 | 9880 |
| `pycsl.py` | 2 | 27 | 1490 | 3769 |
| `frontend/ConcurrencyChecker.py` | 2 | 5 | 90 | 165 |
| `module6_whyml/abstract_ops.py` | 2 | 4 | 34 | 559 |
| 8 more files with 1 each | 8 | – | – | – |

**Live function sizes** of the 86:
* median 60 lines;
* 19 are ≤20 lines, 25 are 21–60, 21 are 61–200, and **21 are over 200** (`pycsl._run_pipeline`
  2485, `functions._reset_function_state` 1921, `Module3_Weaver.process` 1740,
  `expressions._handle_binop` 1600, …).

**Mutator sites per body:** 19 bodies have exactly one site. 67 have two or more. The 86 bodies
contain **956** mutator calls in all (append 358, add 211, extend 150, pop 115, setdefault 69, …),
most of them on forms that are already modelled (local `append`/`add`).

### 3.5 Second blocker (what remains if every IPM site were modelled), all 86
| route group (§5) | n | IPM sites erased: 1 / ≥2 | then L3TC-OK | seam `string`↔`int` | other type error | refusal |
|---|---|---|---|---|---|---|
| R-A local | 44 | 22 / 22 | **2** | 11 | 18 | 13 |
| R-B dict self field (declared) | 13 | 8 / 5 | **0** | 4 | 7 | 2 |
| R-C list self field (declared) | 8 | 4 / 4 | **3** | 2 | 2 | 1 |
| R-D self field NOT declared | 8 | 7 / 1 | **2** | 2 | 3 | 1 |
| R-E parameter | 11 | 7 / 4 | **1** | 3 | 7 | 0 |
| R-F global / other | 2 | 2 / 0 | 0 | 1 | 1 | 0 |
| **total** | **86** | 50 / 36 | **8** | 23 | 38 | 17 |

(The "other type error" column covers every *located* Why3 error that is not a `string`↔`int`
seam. That includes `emit_ir`/`hval`/`pyval` boundary errors (6), unbound symbols (4) and two WhyML
syntax errors in emitter output. The "refusal" column covers every *unlocated* outcome:
* nested-closure lift 5,
* `X is True` identity 2,
* `except` model 2,
* heterogeneous list 1,
* array-local reassign 1,
* dict/set-parameter subscript store 1,
* unlocated Why3 type errors 4,
* the 15-site give-up 1, which is `Module3_Weaver.process`.)

**The 8 that type-check after erasure**, and what a real lowering still needs for each:
| stub | erased sites | what a faithful lowering still needs |
|---|---|---|
| `audit_proof.AuditReport.extend` | `self.passes/failures/skips.extend` | **nothing beyond R-C**: the fields are already `array string`, and `other` is the same record type |
| `frontend/Module1_Ingestor._Harvester._emit_block_footer` | `self._out.append(PyCSLContract(…))` | R-C, **plus** the field must become `array pycslcontract` (today it is `array int`) |
| `frontend/ConcurrencyChecker._warn_if_unprotected` | `self.warnings.append(ConcurrencyWarning(…))` | R-C, plus the record element type (today `array int`) |
| `frontend/Module1_Ingestor._Harvester._emit_target` | `contracts.extend` ×2 (local), `self._out.append` | R-A plus R-C plus the element type |
| `proof2why3/from_lean_json._linearize_app` | `args.insert(0, cur["arg"])` on `List[Dict[str, Any]]` | R-A `insert` on a `seq` local with a `Dict[str, Any]` element (the `pyval` carrier) |
| `frontend/pure_ast._Unparser.write` | `self._source.extend(text)` (`*text` varargs) | R-D (declare `_source`; the `_unparser` record is empty), plus a varargs-tuple `extend` |
| `frontend/pure_ast._Unparser.visit_Module` | `self._type_ignores.clear()` | R-D (declare `_type_ignores: Dict[int, str]`), plus dict `clear` → `const None`, plus the dict-comprehension field store |
| `frontend/Module3_Weaver._collect_self_call_sites` | `out.append((cur_stmt, cur_func))` on a `List[tuple]` param | R-E (caller-visible list-parameter model), plus a tuple element |

**Realistic direct yield of modelling the whole IPM family: 1 stub (`AuditReport.extend`) at R-C
cost, up to about 4 with element typing and field declarations. The ceiling is 8 at L3-tc, and none
of them has been proved.** This matches the prior on this campaign:
* backlog #64: three seam repairs moved 11 markers and lowered 0;
* `self-field-append-wall-impl.md` §K4–§L3: K1 built the `seq hval` self-field append, and each
  following increment uncovered another missing piece and was reverted.

### 3.6 Corpus exposure (M1 discipline)
I statically scanned both corpora for calls `.<mutator>(...)`:
* **56 files** in all, 53 in `pycsl-reference` and 3 in `python-reference`;
* by call: `append@name` 27, `add@name` 15, `extend@name` 4, `update@name` 3, `reverse@name` 2,
  `remove@name` 2, `pop@name` 2, `add@self` 2, `reverse@self` 1, `discard@name` 1, `append@self` 1.

I emitted all 56 (`--no-proof --no-typecheck --keep-mlw` on scratch copies): **37 emit and 19 are
refused.**

Refused **by an IPM site** (these are the corpus's soundness witnesses for this wall):
* `0980_self_field_mutator_refused` (`self.xs.reverse()`)
* `0981_self_field_append_refused`
* `0982_local_list_mutator_refused` (`xs.reverse()`)
* `0983_param_list_mutator_refused`
* `1080_route49_append_param_dropped`
* `1081_route49_append_param_frame_lie`

Each one carries a contract that is **false of Python**. A faithful lowering must turn REFUSED into
"emitted, false claim NOT proved". `byte-diff-compare.py` flags REFUSED→EMITTED as a soundness loss,
so every such flip needs an explicit justification row plus a proof run showing the witness fails.

Refused for neighbouring reasons that must stay refused:
* alias guards `1019`, `1200`;
* contract-named parameter mutation `0988`, `1145`, `1147`;
* `no_exception` `.remove` `1171`;
* namespace-dict `.update` `1401`, `1421`, `1423`;
* `0404`, `0405`, `1830`, `pyref 0166` (other reasons).

Emitted today:
* user-defined methods named `pop` (`0192`);
* recogniser-folded `extend` (`0943`, `0944`, `0948`, `0949`, pyval list walkers);
* `1172` (`.remove`, no-op boundary);
* `add@self` under `@mutable_state` (`0775`, `0941`);
* local `append`/`add` everywhere else.

**Every non-witness corpus file that calls a refused mutator is a recogniser or a refusal, so a
route that only lowers what is refused today should move no emitted `.mlw`.** The sentinels are the
6 witnesses and the 7 emitted non-append files listed above.

---

## 4. Deeper truth: fundamental, or a modelling choice?

**It is a modelling choice.** The refusals exist because the generic fallback lowers an unrecognised
method call to an abstract `val` that neither takes the receiver nor declares `writes`. That
deletes the effect (corpus 0980–0983 measured exactly this before the guard). Nothing in the logic
prevents a faithful model. What is missing is **emission**: a lowering per (mutator × carrier),
where the carriers are `map`, `array`, `seq`, `StrSet`, and `ref` parameters.

### 4.1 What Why3 1.8.2 offers (`why3 --print-datadir`/stdlib)
* `map.Map`/`map.Const`: total maps. PyCSL's `map k (option v)` dict model is a **pure value**, so
  `setdefault`/`pop`/`clear`/`update` are all pure map functions followed by a field (or `ref`) write.
* `fmap.Fmap`: finite maps with `size` (useful only if `len(dict)` is wanted; PyCSL does not use it).
* `array.Array`: the array carries its own `length`; `append` (`array.mlw:127`) and `sub`/`copy`
  are proved stdlib functions.
* `seq.Seq`: `snoc`, `[..]` slice, `length`.
* `python.mlw` (`module Python`): Why3's own model of a Python list, a record
  `{ mutable elts: seq 'a; mutable len: int } invariant { len = length elts }`, with `val append`
  (`writes { l }`), `pop`, `clear`, `sort` (`writes { l.elts }`, permutation plus sortedness),
  `reverse`. This is the reference design for **caller-visible** list mutation through a parameter.
* A `writes { … }` clause on a `val`, ghost fields, and `old`.

### 4.2 What PyCSL already certifies or emits
* `map_update_some (m) (k) (v) : … ensures { result = Map.set m k (Some v) }` serves dict stores on
  fields, locals and parameters (`statements.py:128,162`).
* `self.f <- Seq.snoc self.f (<pyval-wrap x>)` is the K1 self-field append, gated on `List[PyVal]`
  (`statements.py:2883`, `preamble.py:8930`).
* `StrSet` (`set.SetApp` clone) serves local sets.
* A **pinned `__setdefault`** exists inside one recogniser (`generic_fold.py:18790`, auto_trust
  `_extract_array_lengths`). It is `val __setdefault` with
  `ensures { result = Map.set m k (match Map.get m k with None -> Some n | Some x -> Some x end) }`.
  Its comment records the important cost fact: the **inline** union-unwrap form blew E-matching up
  to *132M/369M steps*, and pinning it inside one opaque `val` avoided that. **A general setdefault
  lowering should emit the pinned `val`, not an inline `if mem …`.**
* There is no `Array.append`/resize lowering anywhere in `module6_whyml/`
  (`grep -c 'Array.append\|array_append\|resize'` gives 0).

### 4.3 Feasibility spike (hand-written WhyML, not emitter output)
`scratchpad/ipm/spike.mlw`, abridged to the load-bearing parts:
```why3
type c = { mutable d: map string (option string); mutable xs: array string; mutable n: int }
function setdefault_map (m: map 'k (option 'v)) (k: 'k) (v: 'v) : map 'k (option 'v) =
  match m k with None -> Map.set m k (Some v) | Some _ -> m end
function setdefault_val (m: map 'k (option 'v)) (k: 'k) (v: 'v) : 'v =
  match m k with None -> v | Some x -> x end
val dict_setdefault (self: c) (k: string) (v: string) : string
  writes { self.d }
  ensures { self.d = setdefault_map (old self.d) k v }
  ensures { result = setdefault_val (old self.d) k v }
val dict_clear (self: c) : unit  writes { self.d }  ensures { self.d = const None }
val dict_pop_default (self: c) (k: string) (dflt: string) : string  writes { self.d }
  ensures { self.d = Map.set (old self.d) k None }
  ensures { result = match (old self.d) k with None -> dflt | Some x -> x end }
let list_append (self: c) (v: string) : unit  writes { self.xs }
  ensures { length self.xs = length (old self.xs) + 1 }
  ensures { self.xs[length (old self.xs)] = v }
  ensures { forall i. 0 <= i < length (old self.xs) -> self.xs[i] = (old self.xs)[i] }
= self.xs <- Array.append self.xs (Array.make 1 v)              (* REBIND: exact length *)
let list_extend (self: c) (ys: array string) : unit  writes { self.xs }  (* + 3 ensures *)
= self.xs <- Array.append self.xs ys
type report = { mutable passes: array string; mutable failures: array string }
let report_extend (self: report) (other: report) : unit         (* AuditReport.extend shape *)
  writes { self.passes, self.failures }
  ensures { length self.passes = length (old self.passes) + length other.passes } (* ×2 *)
= self.passes <- Array.append self.passes other.passes;
  self.failures <- Array.append self.failures other.failures
let local_pop () : int ensures { result = 7 }                    (* seq-local worklist pop *)
= let xs = ref (S.snoc (S.snoc S.empty 0) 7) in
  let r = S.get !xs (S.length !xs - 1) in xs := S.([..]) !xs 0 (S.length !xs - 1);
  assert { S.length !xs = 1 }; r
(* callers: caller_setdefault (absent key ⇒ result="dflt" ∧ d k = Some "dflt"),
   caller_setdefault_present (present ⇒ result="x" ∧ d unchanged), caller_append (len+1) *)
(* NON-VACUITY, each FALSE of Python: *)
let bad_setdefault_noop (self: c) (k: string) : unit
  requires { self.d k = None }  ensures { self.d = old self.d } = let _ = dict_setdefault self k "dflt" in ()
let bad_append_len (self: c) : unit ensures { length self.xs = length (old self.xs) } = list_append self "a"
let bad_clear (self: c) (k: string) : unit
  requires { self.d k = Some "x" } ensures { self.d k = Some "x" } = dict_clear self
```
`why3 prove -a split_vc -P z3 -t 10` and then `-P alt-ergo -t 30`, goal by goal:
```
z3:       L41 V  L38 V  L39 Unknown  L40 V  L44 V  L45 V  L46 V  L52 V  L53 V  L58 V  L62 V
          L69 V  L70 V  L79 V  L80 V  L76 V | L86 Unknown  L89 Unknown  L93 Timeout
alt-ergo: L41 V  L38 V  L39 V        L40 V  ... all 16 positive V      | L86 Timeout  L89 Timeout  L93 Timeout
```
**All 16 positive goals are Valid under the portfolio.** L39 (`self.xs[length old] = v`) needs
Alt-Ergo. All 3 false claims are **not proved**. No `axiom` is used.

**Aliasing, measured** (`scratchpad/ipm/alias.mlw`): `let ys = self.xs in list_append self "a"; length ys`
fails at type-check with `This expression prohibits further usage of the variable ys or any function
that depends on it`. Why3's reset discipline therefore makes the rebind model **fail closed** for a
stale *array* alias. Pure-map dict fields have no regions, so `e = self.d; self.d.setdefault(…)`
would silently copy. The dict alias guard (`statements.py:1020`) recognises only *store statements*
(`ArraySet`, `FieldAssign`, …), and the list alias guard (`statements.py:538`) recognises only
`.append`. Its comment rests on the premise that every other list mutator is refused. **Any new
mutator lowering must extend both guards' trigger sets in the same commit**, or it reopens route
#59/#81's alias exploit.

### 4.4 Answers to the specific questions
* **Is `self.d <- (if mem k self.d then self.d else set self.d k (Some v))` with `writes {self.d}`
  enough for dict fields?** For the field effect, yes: §4.3 proves it and the frame is visible to
  callers. Three things are still needed:
  1. **Return value**: `setdefault` returns the stored value. 5 of the 22 use it, and 6 more chain a
     mutation onto it (`d.setdefault(k, []).append(x)`), which needs a nested pure update
     `Map.set d k (Some (HList (snoc …)))` through the `pyval` carrier.
  2. **Cost**: emit the pinned-`val` form (§4.2), not the inline match.
  3. **Alias guard** extension (§4.3).
* **What does list `append` need?** For a **field**, the fresh-array rebind above suffices. The
  length is `Array.length` of the new array, so the "carry the LENGTH in the field model" phrase of
  backlog #61a does not require a new length field; it requires abandoning the
  `Array.make 1024 0` + `_len` *shadow-local* idiom for fields. The remaining cost is the
  **element type**: 6 of the 9 list-field receivers are `array int` holding erased records or
  tuples. For a **parameter**, rebinding is impossible: the caller's binding cannot be reassigned.
  You need a mutable container (a `ref`, as dict and set parameters already use, or Why3's `Python.list`
  record). That changes the parameter model of every corpus list-parameter driver, which is the
  high-risk part.

---

## 5. Routes, honestly costed

Payoff is measured by the §3.5 harness: first blocker cleared, then what the erasure run says is
next. "Clean" means L3TC-OK after erasure **and** no other model change needed (the §3.5 table).
Corpus risk follows M1: a corpus diff must be exactly the intended correction **and** everything
affected must still prove, or the witness must still fail.

| # | route | first-blocker payoff | type-check after erasure (clean) | corpus risk | make-or-break spike | cost |
|---|---|---|---|---|---|---|
| **R-C** | **List SELF-field `append`/`extend`/`sort` by fresh-array rebind with `writes {self.f}`** (replace the 13b refusal and the 7820 refusal for `array`-typed fields) | 8 | 3 (**1**: `AuditReport.extend`) | Sentinels `0980` (`reverse@self`) and `0981` (must become *emitted, `\length == 2` NOT proved*). `add@self` files `0775`/`0941` must stay byte-identical | Lower `AuditReport.extend`: whole-file proof of the `audit_proof.py` mirror (578 lines); `0981` flip plus failed proof; byte-diff 0 on both corpora. Refuted if Why3's reset rule rejects callers in the mirror that hold the field (`prohibits further usage`), so measure the callers of `extend` | small to medium: one Module 6 arm per method, ensures as in §4.3, `sort` as an opaque permutation `val` |
| **R-A** | **LOCAL mutators** as pure `ref` updates: `pop()`/`pop(0)` on `seq` (slice), `extend` (`++`), `insert`, `reverse`, dict `setdefault`/`pop`/`update`, set `update` | **44** (largest) | 2 (0 clean: `_linearize_app` needs a pyval element; `_emit_target` also needs R-C) | `0982` witness flips. Alias guards **must** be widened (list: any length-changing mutator, not only `append`; dict: method-call stores). No other refused corpus local | Lower `xs.pop()` on a seq local; `0982` (`reverse`) emitted and its false `\result == 0` NOT proved; corpus `1019`/`1200` still refused once `pop`/`extend` are added to the alias trigger | medium: about 7 methods × 4 local carriers (seq, array+len, map, StrSet); `IndexError`/`KeyError` `no_exception` triggers per `pycsl-exception-model` |
| **R-B** | **Dict SELF-field `setdefault`/`pop`/`clear`/`update`** via a pinned `val` with receiver and `writes` (§4.3) | 13 | **0** (4 seam, 7 type, 2 refusal) | No corpus file calls these on a dict field, so it should be inert. The dict alias guard must cover method calls | Lower `_pop_quant_binder` (16 lines, `map string (option string)`). Its next error is already known (`_tu_kind, _tu_prev` tuple pattern vs `int`), so the spike tests the lowering, not the yield | small. **Low direct yield**; needed eventually for the 8 `program_ir.setdefault` Module5 stubs, all of which then hit `py_classdef_node`/seam errors |
| **R-D** | **Declare the missing mirror self fields** (8 receivers not in the record, e.g. `_unparser = { }`) | 8 (it is also a prerequisite for R-B/R-C on them) | 2 (`_Unparser.write`, `.visit_Module`; both need a whole-class field model first) | Mirror-only, so corpus-inert | Declare `_Unparser` fields in the mirror and re-emit `pure_ast.py` (L3-tc ~15 s; proof ~55 min) | small per field, but `_unparser` is a class-scale job |
| **R-E** | **List/dict/set PARAMETER mutators** as a caller-visible container (`ref (seq T)`, or Why3's `Python.list`) | 11 | 1 (`_collect_self_call_sites`, tuple element) | **High**: changes the lowering of every list parameter; `1080`/`1081`/`0983` witnesses; every proved corpus list-parameter driver moves | Model `g(a: list): a.append(1)` plus caller `f([])` (`1080`): emitted, false `\result == 0` NOT proved, and `python-reference` byte-diff measured | large |
| R-F | module global `_STRUCT_FMT_FOLDS.setdefault`, `copy.deepcopy(…).pop`, `hashlib…update` | 2 (+3 unknown) | 0 | – | – | not worth a route |

**Ranking** by (stubs unblocked × landing confidence) ÷ cost, using the clean column as "unblocked":
1. **R-C.** Highest confidence (model proven §4.3, Why3 fails closed on aliases, field types already
   right for the pilot) and smallest cost. Payoff: 1 sure, about 3 with element typing. Run it as a
   **chain probe on `AuditReport.extend`**, the way #64 and W-SB recommend, not as a class sweep.
2. **R-A.** The largest first-blocker population, so landing it moves 44 stubs onto their *next*
   wall (a census gain more than a TCB cut: 2 type-check, 0 clean). The cost is dominated by the
   alias-guard and exception-trigger coupling, not by the logic.
3. **R-D.** A cheap mirror-only prerequisite. Do it on demand when an R-B/R-C chain reaches an
   undeclared field.
4. **R-B.** Cheap and probably sound, but 0 of 13 type-check after it. Schedule it after the seam
   work that its stubs hit next (`py_classdef_node`, `string`↔`int`).
5. **R-E.** Large cost and corpus risk for 1 stub. Park it.

**Expected effect on the `\trusted` count from W-IPM alone: small (1 to about 4).** W-IPM is the
**largest first blocker** but not the binding constraint. Behind it, 23 of 86 stop at the same
`string`↔`int` seam W-SB found, and 38 more stop at other type errors. Retiring markers at scale
needs W-IPM **together with** the int-erasure seam work (backlog #62/#64) and, for the 6 `array int`
list fields, record-element typing.

---

## 6. Honest limits
1. **The second blocker is an erasure measurement, not modelling.** The A.4 rewrites (`None`,
   `X[len(X)-1]`, `X.get(k,d)`) are type-plausible stand-ins. A real lowering can add its own type
   errors, such as an element-type mismatch when a record is appended to an `array int`. Three of the
   8 type-checking stubs are known to need exactly that (§3.5). Conversely, a stand-in can create an
   error the real lowering would not have. For example, `X[len(X)-1]` on an erased iterable may be the
   cause of some "other type error" rows. I did not audit all 78 non-OK rows for stand-in artefacts.
2. **L3TC-OK is not proved.** None of the 8 was taken through a whole-file proof. Loop invariants,
   variants and frame clauses for the converted bodies are not written. The 17 L3TC-OK stubs in §3.2
   are also unproved and outside this wall.
3. **The receiver classification is syntactic.**
   * It reads annotations from the mirror class, then the live class, then the initialiser.
   * The WhyML field model comes from emitting the *unmodified* mirror file.
   * 5 receivers have an unknown collection kind (§3.3).
   * A receiver that is a local alias of a self field (`d = self.x; d.setdefault(...)`) is counted as
     *local*.
4. **The refusal text identifies one site.** Bodies with several refused sites (36 of 86 needed two
   or more erasure rounds; `Module3_Weaver.process` needed more than 15) are attributed to whichever
   site the emitter met first.
5. **The spike (§4.3) is hand-written WhyML.** It shows the model is expressible, dischargeable,
   axiom-free and non-vacuous. It does not show that the emitter can produce it at every site, or that
   the mirror's callers survive Why3's reset rule.
6. **The corpus status (§3.6) is an emission run on 56 statically selected files**, not the full
   `byte-diff-sweep` of both corpora. The static selector matches attribute calls named like a
   mutator, so it includes user methods (`0192`'s `Buffer.pop`).
7. **Planes not re-run:** whole-file proofs, `run-soundness-planes.sh`, the full byte-diff.
   Fidelity was re-run (OK, 897). Nothing was changed, so the ledger is 3 by construction.
8. Snapshot: HEAD `b05638d9`. The first-blocker census agrees with the W-SB census taken at
   `11834d83` on the receiver-guard count (77). W-SB folded the 9 `statements.py` refusals
   elsewhere; this report counts them in the family (86).

---

## Appendix A: instruments (scratch copies under `$SCRATCH/ipm/`, `$SCRATCH` = this session's scratchpad)

Reproduce:
```
. scratchpad/g29/env.sh
python3 gen.py                                          # §2.2 probes p_*.py / f_*.py
for f in p_*.py f_*.py; do .venv/bin/python3 src/pycsl/pycsl.py $f --import-path src/pycsl --keep-mlw; done
# 8 roots: rsync -a --exclude formal-semantics --exclude __pycache__ src/ roots/rN/src/; rsync bin config roots/rN/
./run_group.sh N   (N=1..8, resumable)  -> fe_N.jsonl   # §3.2 first blocker (A.2)
.venv/bin/python3 static.py                              # §3.3 receivers (A.3)
.venv/bin/python3 shape.py                               # §3.3 call shapes
./run_second.sh N  (N=1..8, resumable)  -> se_N.jsonl    # §3.5 second blocker (A.4)
python3 xtab.py                                          # §3.3/§3.4 tables
why3 prove -a split_vc -P z3 -t 10 spike.mlw; why3 prove -a split_vc -P alt-ergo -t 30 spike.mlw   # §4.3
why3 prove -P z3 -t 5 alias.mlw                          # §4.3 alias
```
Wall-clock: first-blocker census about 10–15 min on 8 roots (2 waves); second-blocker about 9 min on
8 roots; the per-file mirror emissions took 1.6–19.6 s each.

### A.1 Probe generator (core)
```python
HDR = '''from dataclasses import dataclass
from typing import Dict, List, Set, Any
def mutable_state(cls): return cls          # omitted (and the decorator) for the plain variant
@mutable_state
@dataclass
class C:
    d: Dict[str, str] = None
    di: Dict[str, int] = None
    xs: List[str] = None
    ns: List[int] = None
    s: Set[str] = None
'''
BODIES = {"setdefault": ("self.d", "self.d.setdefault(k, v)"), "update": ("self.d", "self.d.update({k: v})"),
 "dstore": ("self.d", "self.d[k] = v"), "dpop": ("self.d", "self.d.pop(k, None)"),
 "append": ("self.xs", "self.xs.append(v)"), "nappend": ("self.ns", "self.ns.append(3)"),
 "extend": ("self.xs", "self.xs.extend([v])"), "pop": ("self.xs", "self.xs.pop()"),
 "insert": ("self.xs", "self.xs.insert(0, v)"), "sadd": ("self.s", "self.s.add(v)"),
 "sdiscard": ("self.s", "self.s.discard(v)"), "clear": ("self.d", "self.d.clear()"),
 "sort": ("self.xs", "self.xs.sort()")}
# each: HDR + f"    #@ assigns {fld}\n    def m(self, k: str, v: str) -> None:\n        {body}\n"
# function probes: local append/sort/setdefault/add/pop/extend/update/store, param append/sort/
# setdefault/store/add, heapq.heapify, list/dict alias, KeyError read, caller-visibility (§2.2)
```

### A.2 `firsterr.py`: the same harness as `string-builder-wall.md` A.2, made resumable
It skips (file, cls, name) keys already present in the output, and refusal messages are kept to 700
characters. It monkey-patches `pcc._probe_emit`, writes the ported mirror, runs
`pycsl.py --no-proof --keep-mlw`, records the first `File "...mlw", line L, characters a-b` error
(fragment and line) or the line after `[!] PIPELINE ERROR`, and **restores the mirror in a
`finally`**.

### A.3 Receiver classification (core of `static.py`)
```python
MUT = {"append","extend","insert","remove","pop","clear","sort","reverse","update","popitem",
       "setdefault","add","discard","intersection_update","difference_update","symmetric_difference_update"}
# refusal text -> (receiver, method):
#  r"`([\w\.\[\]]+)\.(\w+)\(\.\.\.\)` MUTATES its receiver"   (expressions.py:7820)
#  r"`([\w\.]+)\.(\w+)\(\.\.\.\)` appends to the collection"  (statements.py:3035)
#  r"to list parameter '(\w+)'"                                (statements.py:2855)
# receiver kind: 'self.<f>' -> self-field (type: mirror class AnnAssign, else live `self.f: T`/initialiser);
#   Name in fn.args -> param; Name assigned in fn -> local; module-level Assign -> module-global; else other.
# WhyML field model: re.findall(r"mutable\s+<f>\s*:\s*([^;}]+)", <unmodified mirror>.mlw)
```

### A.4 Second-blocker loop (core of `second.py`)
```python
for k in range(15):
    pcc.LIVE = neut                       # a SCRATCH copy of the live file, never src/pycsl/
    pcc.probe(name, cls)                  # signature-preserving port + emit + restore
    ip = None if rec.get("frag") is not None else ipm_of(rec.get("msg"))
    if ip is None: break                  # first NON-IPM outcome = the second blocker
    neutralise(neut, name, cls, *ip)      # rewrite every (receiver, method) call in that function:
    #   Expr-statement call -> None ; X.pop() -> X[len(X) - 1] ; X.pop(i) -> X[i]
    #   X.pop(k,d) / X.setdefault(k,d) (value used) -> X.get(k, d) ; other used value -> X
```
