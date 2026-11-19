# The untyped `Dict[str, Any]` value model: a state-of-the-art report for independent review

*Driver run #3, wall cycle step 3 (report). Written 2026-10-28 against `ghost-assign-bc6` HEAD
`59985d6e9`. `src/`, `bin/` and `json/` are byte-identical to `3e834fa79`, the commit the cv4
re-census ran on (`git diff --stat 3e834fa79 HEAD -- src bin json` is empty). The document assumes
no knowledge of the project. Every number is either measured here, with the script and command
given in §10, or quoted from a cited file and line. Scratch evidence is under
`scratchpad/wall-dict/` (untracked). No source file was edited.*

---

## 0. The question in one paragraph

PyCSL verifies annotated Python by translating it to WhyML for Why3. It also verifies its own
emitter, and that emitter is written over a JSON-shaped intermediate representation: IR nodes are
`Dict[str, Any]`. Two independent campaigns have now stopped at the same root. The first is
**conversion**: replacing a trusted, unproved emitter function with its proved verbatim body. The
cv4 re-census on 2026-10-28 found **0** newly convertible stubs among 414. The second is
**soundness**: the last open family of false proofs about hashing (`{x}`, `d[x]`, `x in s` on an
unhashable `x`) can only be closed by refusing every hashed value whose class cannot be derived.
That refusal costs **27 of 53** mirror files at **679** sites, mostly reads like `node.get('name')`.
For the reviewer, this report:
- measures how much of each campaign actually hits a `Dict[str, Any]` read first;
- describes the five value models that coexist in the emitter today;
- costs four routes.

The headline measurement is that the wall is **narrower than its name suggests at the first
blocker, and wider than its name suggests behind it**:
- Conversions: a `Dict[str, Any]` read is the first blocker of 19 of the 370 live-bodied stubs
  (9 of the 94 type clashes, 10 of the 276 refusals). It appears somewhere in the body of 155.
- Hashing: making every dict read derivable would clear only **5** of the 27 refused mirrors,
  because 22 of them also have non-dict underivable sites (170 sites in all).

---

## 1. The system

### 1.1 PyCSL

PyCSL is a contract language plus a verifier for a statically analysable subset of Python
(`README.md`). Contracts are `#@` comments: `requires`, `ensures`, `assigns`, loop invariants,
variants, `no_exception`, `\trusted`.

The pipeline is a six-module compiler in `src/pycsl/`:
1. ingest;
2. a Lark parser for `#@`;
3. weaver;
4. semantic checks;
5. a JSON IR emitter (`frontend/Module5_IREmitter.py`);
6. the WhyML transpiler (`Module6_WhyMLTranspiler.py` + `module6_whyml/`).

Why3 1.8.2 generates verification conditions, and Alt-Ergo, Z3 or CVC5 discharge them. The
emitter's own source uses `Dict[str, Any]` **1,833** times
(`grep -rho 'Dict\[str, Any\]' --include=*.py src/pycsl | wc -l`).

### 1.2 The self-annotation mirror and `\trusted`

`src/self-annotate/src/` (53 files) mirrors the emitter. Each mirror function is one of two things:
- **Converted.** Its body is the live emitter body **verbatim**, under a fixed contract shape:
  `requires True / ensures True / assigns <tight frame>`. That shape states type safety plus frame.
  It is never value-faithful and never vacuous (`config/skills/self-tcb-reduction/SKILL.md:44-50`).
- **A `\trusted` stub.** Its signature and contract are assumed without proof.

Today there are **442** `#@ \trusted` lines
(`grep -rhF '#@ \trusted' src/self-annotate/src --include=*.py | wc -l`). Of these, **414** are
strict markers, one row each in `getting-better/trusted-reasons.tsv`.

The mirror's *annotations* may differ from the live ones, because they are the modelling layer. The
fidelity checker strips them before it compares bodies. So a mirror may write
`rec: Dict[str, PyVal]` where the live code writes `rec: dict`. That freedom is used in §4.5.

### 1.3 The three lower-bound planes

A conversion counts only if three disjoint executable planes pass
(`config/skills/self-tcb-reduction/SKILL.md:51-58`):
- **L1, fidelity.** `bin/check-self-annotate-sync.sh` and `bin/self-annotate-mirror-check.sh`
  confirm that the mirror body equals the live body, modulo `#@` lines and annotations.
- **L2, whole-file proof.** `pycsl.py <mirror>` proves the whole home file with 0 non-Valid goals,
  and `--fun <name>` proves the function itself.
- **L3, corpus byte-diff.** `bin/byte-diff-sweep.sh` gives a byte-identical `.mlw` for every
  reference program, in both corpus trees, against a baseline at the base commit. Every moved file
  is inspected and re-proved, and a baseline is never re-taken to make a diff disappear.

Further oracles also gate a conversion:
- non-vacuity (`check-emitted-vacuity.py`): no input-blind 0-ary `*_0 ()` facades and no
  `pycsl_getattr_default_*`;
- `check-yield-erasure`, `check-shadowed-selfcalls` and `check-untrusted-emitted`;
- 61 soundness planes (`bin/run-soundness-planes.sh`).

### 1.4 The ledger is 3: no new axioms

The soundness story has three links, mechanised in Rocq and Lean (`src/formal-semantics/`):
- **LINK-1:** weakest-precondition soundness;
- **LINK-2:** faithfulness of the Python-to-WhyML encoding;
- **LINK-3:** the emitter's self-verification. This wall sits on LINK-3.

The only axioms accepted are the kernel ones in `src/pycsl/proof_axiom_allowlist.py`:
- Lean: `propext`, `Classical.choice`, `Quot.sound`;
- Rocq: propositional and functional extensionality.

No change may add an axiom. The **coupling rule** says that a new WhyML value shape lands together
with an axiom-free Rocq/Lean certificate (`config/skills/self-tcb-reduction/SKILL.md:443`, `:482`).

### 1.5 Hard rules any route must respect

1. No new axiom, and no cited lemma standing in for a missing model.
2. Verbatim bodies. Only annotations may differ.
3. No vacuous facades. A body must read real modelled structure.
4. Corpus inertness, or every moved file inspected and re-proved.
5. The fixed contract shape: `requires True`, so there is no well-formedness precondition on the
   input.

---

## 2. Two campaigns, one root

### 2.1 Conversion (the cv4 re-census)

The cv4 re-census is commit `cf38e06f9`, section "Re-census (cv4)" of
`getting-better/conversion-census-r3.md`. That commit is not yet on this branch; read it with
`git show cf38e06f9:getting-better/conversion-census-r3.md | sed -n 624,800p`.

Method: each of the 414 rows had its live body ported verbatim, its marker deleted, and was
type-checked with `--no-proof`. Results:

| verdict | stubs |
|---|---|
| TC-OK (all known-blocked by the phase-B oracles) | 20 |
| REFUSED (a pipeline guard) | 276 |
| L3-TC (a Why3 type clash) | 94 |
| ABORT (no live body) | 24 |

**Newly TC-OK: 0** of the 413 rows that also existed at phase A.

The earlier census already showed that no refusal guard is the binding constraint: neutralising
all seven guards unlocks 2 of 153 (`conversion-census-r3.md:66-80`). The binding constraint is the
**int-erasure seam**: an `Any`, unannotated or dict value is lowered to an opaque WhyML `int`, and
meets a typed site. That analysis is `getting-better/int-erasure-seam-r3.md`.

The route the response picked was R5-str, a typed model for `str` methods. It converted **1** stub
and moved 3 chains by one link each (`int-erasure-seam-r3-impl.md` §8). The levers ledger
re-confirmed that "no lever found here unlocks more than one stub"
(`getting-better/levers-r3.md`, "Why the yields are 1, not tens").

### 2.2 Soundness (hashing)

Routes #381, #382, #383, #394 and #421 repaired the hashing false proofs one source family at a
time. Each repair adds a rule that derives the class of a hashed value; a class that may lack a
hash is refused.

What remains is the **`#UND` residual**: a value whose class *cannot be derived* is **admitted**.
`pycsl.py:6231-6234` gives the rule. `pycsl.py:8222-8226` adds that "an `Any` / `object` / TypeVar
reached THROUGH a container (`Dict[str, Any]`'s `m[k]` / `.get(k)` / element) is underivable
('#UND')". The residual is documented in:
- `open-routes/route383-hash-element-class-sources.md:95` ("Residuals (1)");
- `open-routes/route421-global-initializer-derivation.md:45-47` ("The LOCAL derivation's #UND
  residual (Dict[str, Any] reads, un-annotated callees) is untouched by design (the full flip
  costs 27/53 mirrors)").

The flip ("refuse `#UND` too") was built and measured, then **not landed**
(`open-routes/route394-hash-allowlist-missing-sources.md:26`). It refuses:
- **27 / 53 mirrors, at 679 sites** (`systematic-soundness-r3/e1-r392-395/mirflipA.tsv`);
- 7 root/pyref corpus PASS files;
- `pycsl_lib/syscfg`.

A refused mirror loses a proved file, so the polarity stays a deny-list.

The two campaigns meet in the census itself. **`route#349` (the hashing refusal) is now the first
blocker of 10 stubs**, up from 2 at phase A (cv4 "First-blocker counts that moved"). Each hashing
repair that refines the derivation also reaches the mirror stubs it is ported into.

---

## 3. How `Dict[str, Any]`, `pyval` and `hval` are modelled today

### 3.1 Five value models coexist in one emitter

| model | selected by | WhyML | where |
|---|---|---|---|
| **erased dict** (default) | `Dict[str, Any]`, bare `dict`, `Dict` | `map string (option int)` for a str-keyed param, `map int (option int)` otherwise; a value read is `match Map.get m k with Some v_ -> v_ \| None -> <absent> end : int` | `frontend/Module5_IREmitter.py:6142-6186` (`_m5_get_dict_value_type`: only a `str`, `PyVal`, nested-dict or `List[..]` value type is recognised; `Any` returns `None`, which means `int`); `module6_whyml/functions.py:11738-11779` (`_dict_param_whyml_type`, default `map int (option int)`); `module6_whyml/functions.py:11705-11736` (`_symtype_to_whyml`: `"dict"` becomes `map int (option int)`, anything unknown becomes `int`); `.get` lowering `module6_whyml/expressions.py:14040` (`_lower_dict_get_call`), template at `:14594-14596`; one-argument absent default = the opaque `pycsl_none` (route #57, `expressions.py:1289-1301`) |
| **erased receiver facade** | a `.get` on a value the emitter does not know is a dict (an element of `List[Dict[str, Any]]`, an `int`-placeholder parameter) | `val f_get_1 (x0: int) : int`, **receiver dropped**, key hashed to an int | `module6_whyml/expressions.py:8175` (`_handle_dotted_call`), `:7971` (`_resolve_dotted_signature`) |
| **`hval`** (certified tagged value) | `Dict[str, PyVal]` on a parameter or local (`PyVal` is a corpus-absent sentinel name, `= Any` at run time) | `type hval = HStr string \| HInt int \| HArr hval_list \| HMap hpairs \| HNode hval`; reads are `pairs_get` (a terminating lookup fold); projections `hstr_of` / `hint_of` are total, and a wrong tag projects to the uninterpreted `hval_opaque_str h` | `Module5_IREmitter.py:6160-6161`; `module6_whyml/preamble.py:8005-8130` (`_emit_pyval_theory`); certificate `src/formal-semantics/rocq/Phase2f_PyVal.v`, `src/formal-semantics/lean/PyCSL/PyVal.lean` |
| **`pyval` / `irkey`** (generic-fold model) | the D1/R-A fold recognisers | `type pyval = PInt \| PStr \| PBool \| PNone \| PList \| PDict pydict` keyed by an interned `irkey` (`K_type \| K_name \| … \| K_dyn string`) | `module6_whyml/preamble.py:4318-4345` (`_pydict_theory_lines`); certificate `Phase2c_PyValDict.v`; per-key typing predicate `wf_val` generated from the schema (`module6_whyml/wf_ir_gen.py:1-17`) |
| **typed records** | `TypedDict` classes; `ExprIR`/`StmtIR` annotations | `type varir = { mutable py_type: string; mutable name: string }`; `ExprIR`-annotated values become the IR sum `emit_ir` (`preamble.py:5179`) | `functions.py:11729-11735`; `module6_whyml/expressions.py:16919` (`_typeddict_field_access`), `:16959` (`_typeddict_record_literal`) |

The soundness guards on the erased model are:
- **Route #325**: an opaque int may only be bound, passed, returned or compared for (in)equality
  (`pycsl.py:18138-18147`).
- **Route #252**: an erased value may not flow into a builtin-typed slot (`functions.py:2638`,
  message at `:2883`).
- **Route #398**: a TypedDict key is read only when it is positively required.
- **Rule TC**: a `TypedDict` may appear only in an annotation, base or cast position, never as a
  value (`systematic-soundness-r3.md:146`).

### 3.2 Probes: what a user program gets today

Each probe was run with
`heavy.sh python3 src/pycsl/pycsl.py scratchpad/wall-dict/probes/<p>.py --no-proof --keep-mlw`.

**q1b: a `Dict[str, Any]` read compared with a string.** rc 0, type-checks.
(`probes/q1b_any_get.mlw:15`)
```
let kind_is_var (node: map string (option int)) : int
  =
    let t = ref 0 in
    t := (match Map.get node "type" with | Some v_ -> v_ | None -> pycsl_none end);
    (if (pycsl_py_eq !t "Var") then 1 else 0)
```
- The value is an opaque `int`.
- The `==` becomes the uninterpreted polymorphic `pycsl_py_eq`, so nothing about the string
  survives.
- An absent key gives `pycsl_none : int`, which shares a sort with every present value.

**q1: the same read returned as `str`.** **REFUSED**, route #252: "an erased (`Any`/...) value flows
into a slot declared as a builtin type: the `return` of a function declared `-> str`". Fail-closed.

**q2: the same read under `Dict[str, PyVal]`.** rc 0. (`probes/q2_pyval.mlw:64-75`)
```
let name_len (node: map string (option hval)) : int =
  let n = (match Map.get node "name" with | Some v_ -> v_ | None -> (HInt pycsl_none) end) in
  if (match n with HStr _ -> true | HInt _ -> (any bool) | HArr _ -> false | HMap _ -> false | HNode _ -> false end) then
    raise (Return (match n with HArr _ -> (hval_len n) | _ -> (hval_len_other n) end))
```
- The tag is real, and `isinstance(n, str)` becomes a match on it.
- The absent key is `HInt pycsl_none`. Because of that, the `HInt` arm of an `isinstance(_, str)`
  test must be `(any bool)`: an absent value and a real int cannot be told apart.

**q3b / q3c: a TypedDict view.**
```
type varir = { mutable py_type: string; mutable name: string }
let function name_of (node: varir) : string  ensures { result = node.name } = node.name    (* q3b: faithful *)
let function is_var (node: varir) : int = (if (node.py_type = 1734671427) then 1 else 0)   (* q3b: node["type"] == "Var" *)
let function is_var (node: varir) : int = (if (str_eq_op node.py_type "Var") then 1 else 0) (* q3c: node.get("type") == "Var" *)
```
- The read is a faithful record projection.
- But q3b, `node["type"] == "Var"`, compares a `string` field with the **hashed literal**
  `1734671427`. That is an L3 type clash (`probes/q3b_typeddict.out`: "This expression has type
  string, but is expected to have type int").
- q3c spells the same test with `.get`, routes it through `str_eq_op`, and type-checks. So the
  record view exists, but its consumer lowering depends on whether the read is spelled `.get(k)` or
  `[k]`.
- q3, `len(node["name"])` in an `ensures`, also clashes: `iter_length` is int-typed.

**q4 / q5 / q6: hashing a `Dict[str, Any]` value under `#@ no_exception \all`.** CPython raises
`TypeError: cannot use 'list' as a set element` on each `__main__` driver (`python3 <probe>`).

| probe | Python | pipeline | emitted |
|---|---|---|---|
| q5 | `v = m["a"]; s = {v}` | **REFUSED**, `PYCSL-R349-UNHASHABLE-RECORD` (route #383 addendum: a `Dict[str, Any]` *subscript* value is `#UNK`) | — |
| q4 `g` | `s = {m.get("a")}` | **admitted**, rc 0 | `let s = ref (any int) in 1` (no hashing obligation) |
| q4 `h` | `v = m.get("a"); s = {v}` | **admitted**, rc 0 | `v := (match Map.get m "a" with … None -> pycsl_none end); let s = ref (any int) in 1` |
| q6 | `for f in funcs: seen.add(f.get("name"))`, `funcs: List[Dict[str, Any]]` | **admitted**, rc 0 | `funcs: array int`; `seen := map_update_some !seen (f_get_1 1878939832) 0`: the element is erased to `int`, so `.get` becomes a **receiver-less** facade |

The only goal left in q4 and q6 is `result = 1`, with a body that returns `1`. So these are the
documented `#UND` false-proof shape: a `.get` is admitted where a `[k]` subscript is refused. The
full proof was **not** run here, because the heavy-job slots were occupied by other executors' long
mirror proofs; see §9.

### 3.3 Two mirror functions, emitted

**A live `Dict[str, Any]` reader as the mirror sees it.** This is
`module6_whyml/functions.py::_mixin_dep_pseudo_functions`, ported verbatim (cv4 row 282,
`scratchpad/wall-dict/tc/282.mlw:2504-2531`). The mirror signature is `functions: List[int]`; the live
one is `List[Dict[str, Any]]`.
```
let functionemissionmixin___mixin_dep_pseudo_functions (self: functionemissionmixin) (functions: array int) : array int
  ...
      let func = ref (functions[!_idx_func]) in
      deps := (let __or_l = (func_get_1 132784272) in if __or_l <> 0 then __or_l else (Array.make 1024 0));
      ...
      name := (func_get_2 1878939832 313406155);
```
The Python is `deps = func.get("method_deps") or []` and `name = func.get("name", "")`. The
emission is `val func_get_1 (x0: int) : int`: it never receives `func`, so the read is
**input-blind**. The type clash is `array int` versus `int` at `or []`.

**The certified `hval` reader, in a proved mirror.** This is
`module6_whyml/types.py::_field_type_for`, converted. The mirror declares
`_record_types: Dict[str, Any]` (`src/self-annotate/src/module6_whyml/types.py:34`), but the field is
retyped to `hval` by name (`hval-record-view`, `driver-backlog.md:3614-3621`). It is emitted as
`map string (option hval)` (`scratchpad/wall-dict/types.mlw:522`, `:1368-1374`).
```
while !_idx_info < (hval_values_len self._record_types) do
  let info = ((hval_values_get self._record_types !_idx_info)) in
  if (str_eq_op (hstr_of (match info with HMap m_k7 -> (match pairs_get m_k7 "whyml_name" with Some v_ -> v_
       | None -> (HInt pycsl_none) end) | _ -> (HInt pycsl_none) end)) !cls) then begin
    raise (Return__union__field_type_for_0 (match (match (match info with HMap m_k7 -> (match pairs_get m_k7 "field_types" ...
```
This is the existence proof that a faithful, non-vacuous, axiom-free `Dict[str, Any]` read is
expressible today. The cost history, from `driver-backlog.md`:
- retyping **one** shared field to `hval` pushed the `stmt_control_flow.py` whole-file proof to
  about 2,400 s (`:3619-3623`);
- a size "PIN" lemma pack recovered about 2 % (`:3698-3703`, "REFUTED");
- the `typed-record-view` spike was judged FULL-REWORK-NEEDED: about 97 read sites in 6 files for a
  yield of about 2-3 stubs (`:3583-3595`).

---

## 4. Measurements: the joint population

### 4.1 The 94 type-clash stubs: what is the first clash?

All 94 L3-TC stubs of cv4 were re-ported one at a time and emitted with `--no-proof --keep-mlw`
(`scratchpad/wall-dict/tc.sh`). The census tree was copied to `scratchpad/wall-dict/tree`, and the
file was restored after each stub. All 94 reproduce: rc 1 for every one, and 93 of 94 have the same
first message as cv4. The 94th, row 222, is the same error, which `clash.py` failed to extract.

`clash.py` slices the emitted `.mlw` at the line and characters Why3 reports
(`scratchpad/wall-dict/clash.json`). For ambiguous rows, `fsrc.py` locates the Python line. The
classification is in `scratchpad/wall-dict/l3-class.tsv`:

| first clash | stubs | rows |
|---|---|---|
| **A. a `Dict[str, Any]` / bare-`dict` value read** (`.get` / `[k]` / view on an Any-valued dict) is the clashing expression or its `int` origin | **9** | 034 `nt_arities[callee]` (`nt_arities: dict`); 143 `for entry in dep_ir.get("imports", [])`; 242 `_lir.get("args")` inside an `and` chain; 248 `expr.get("args", [{}])[0] if expr.get("args")`; 250 `known_sizes[vname]` (a dict from `getattr(self, …, {})`, int-keyed vs a string key); 282 `func.get("method_deps") or []` (receiver-less `func_get_1`); 298 `rec.get("init_ensures", []) or []` (`rec_get_2`); 398 / 400 `term.get("explanations") or []` (`term_get_1`) |
| **B. a whole `Dict[str, Any]` container crosses a typed slot** (dict model vs `int` / `emit_ir` / `hval`) | **6** | 024 / 392 `json.dumps(payload)` (stdlib stub `obj` unannotated, so `int`); 156 `ir_data: int` placeholder passed to a `Dict[str, PyVal]` callee (`int` vs `map string (option hval)`: **two dict models meeting**); 239 `ir: Dict` passed to an `ExprIR` callee (`map` vs `emit_ir`); 399 a `List[dict]` element (`int`) passed to `_record_key(rec: dict)`; 029 a heterogeneous dict literal (`report.compile_stdout : string` into `map … (option int)`) |
| C. a *typed* dict whose value or key type is unmodelled | 4 | 072 a dict comprehension read; 078 / 085 `Dict[int, List[CSLNode]]` values; 374 `_UNICODE_OPS.items()` keys |
| other (external calls, `re`/`subprocess`/`Path`, records and dataclasses, `None` for a typed return, tuples, generators, cross-file self-methods, list-literal defaults) | 75 | `l3-class.tsv` |

**So a `Dict[str, Any]` read is the first blocker of 9 / 94. Dict-model mismatches (A + B) cover
15 / 94.** The clash-pair statistics of the earlier census (int⇒string 31, int⇒array 22, …,
`conversion-census-r3.md:85-110`) are therefore not dominated by dict reads at the first link.

### 4.2 The 276 refused stubs: is the refused value a dict read?

The refusal messages are in `scratchpad/wall-dict/cv4-new.json`, copied from the cv4 scratch. For
route #252, the message names the slot and not the value. `r252.py` therefore lists every argument
passed into the named slot in the live body. The origin of each value was then read off the source
(`refused-class.tsv`).

| refused because of | stubs | rows |
|---|---|---|
| **A. a `Dict[str, Any]` read** | **10** | R325 opaque-int fallback whose origin is a dict field or `.get`: 001, 098 (values of a dict field), 007 (`self.ir`, a `Dict[str, Any]` field), 236 (`info.get(..)` → `info_get_2`); #252, a dict read flowing into `whyml_ident(name: str)`: 006 (`func['name']`), 325 (`a.get("base")`, `root.get("name")`); **#349 hashing**, where the hashed value is a dict read: 150 (`td["name"]`), 300 (`vtd['name']`), 336 (`_r2b_e.get("name")`), 391 (a loop variable over IR dicts) |
| a `Dict[str, Any]` *store* through an `int` placeholder parameter ("Subscript assignment to non-list/dict variable 'func_ir' (type 'int')") | 4 | 123, 124, 141, 159 |
| route #398: an optional TypedDict key (`ir_schema.py::validate_ir`; `ContractsIR`/`FunctionIR`/`ProgramIR` are `total=False`) | 1 | 225 |
| other: in-place mutators 36, R325 on non-dict origins 38, #252 on ast attributes / `Any` tuple elements 23, nested-closure lift 16, definite assignment 13, R327 12, … | 261 | `refused-class.tsv` |

The other 6 #349 refusals hash values that are not dict reads. They are:
- index expressions and fields whose class set includes "a list / dict / set" because of mirror
  `int` placeholders (045, 052, 224);
- a trusted call's result (324);
- a `self` field (254);
- `hash(ref)` on a dataclass (358).

**So a `Dict[str, Any]` read is the first blocker of 10 / 276 refused stubs, plus 4 dict stores
and 1 TypedDict optional-key refusal.**

### 4.3 Upper bound: how many stubs contain such a read anywhere?

`contains.py` counts stubs whose live body has a literal-key `x.get('k')` or `x['k']`:

| verdict | contain a literal-key read | live signature mentions `Dict`/`dict` | both |
|---|---|---|---|
| REFUSED (276) | 134 | 121 | 98 |
| L3-TC (94) | 21 | 31 | 17 |
| TC-OK (20) | 2 | 3 | 1 |

**155 of the 370 refused or type-clashing stubs contain a literal-key dict read.** Fewer than one
in eight of them (19) hits it first. A dict-read model is therefore at most an enabler for 155 and
the first link for 19.

The 19 stubs in §4.1 A and §4.2 A have these properties (`leaf19.py`):
- 8 are leaves (they call no other trusted stub): 001, 034, 098, 150, 250, 391, 398, 400;
- 5 are short, at 8 to 33 lines;
- 19 / 19 live in one of the 27 mirrors that the hashing flip refuses (§4.4). Converting any of
  them while the flip is in place is moot.

### 4.4 The 679 `#UND` hashing sites: what is hashed?

`flipclass.py` classifies every row of `mirflipA.tsv` by the source of the hashed expression. It
reads the mirror text at `3b2d2e763`, the flip's measurement base; line numbers were checked to
match. Classification is AST-based and follows local bindings for up to two hops.

| source of the hashed value | sites | % |
|---|---|---|
| **a dict read with a string-literal key** (`x.get('name')`, `x['k']`, directly or via ≤ 2 local bindings, incl. loop over such a read) | **399** | 59 |
| a dict read with a variable key | 38 | 6 |
| a loop variable over `.items()` / `.keys()` / `.values()` | 72 | 11 |
| **dict-related subtotal** | **509** | **75** |
| a call result (incl. loop over / unpack of one) | 93 | 14 |
| an attribute (`t.op`, `node.op.__class__.__name__`, …) | 52 | 8 |
| an unannotated / `Any` / `int`-placeholder parameter, literals, other | 25 | 4 |

Some further breakdowns:
- **Direct reads.** In 209 sites the hashed expression is itself the read. Their receivers
  (`flipclass2.py`) are:
  - an `Any`-annotated parameter: 73;
  - a loop variable over a list of IR dicts: 69;
  - the result of another dict read: 24;
  - a `Dict[str, Any]` / IR-annotated parameter: 15;
  - an unannotated parameter: 11;
  - other: 17.

  So most `#UND` dict receivers are **not even annotated `Dict[str, Any]`**. They are `Any` or loop
  variables.
- **Keys** (`schemakeys.py`). `name` 194, `target` 44, `func` 28, `var` 27, `object` 13,
  `formal_params` 13, `field` 8. The IR schema (`src/pycsl/ir_schema.py`, 117 classes, 114 field
  names) gives a single scalar type (`str` / `int` / `bool`) to 35 key names. **332 of the 399**
  string-key read sites use such a key; `name` is `str` in every schema class.
- **Per mirror.** **5** of the 27 refused mirrors contain only dict-related sites
  (`preamble.py`, `ir_resolve.py`, `audit_proof_reverify.py`, `audit_proof.py`, `ir_schema.py`).
  **22** also contain non-dict sites: 170 in all, made of call results, attributes and parameters.
  Making only the 332 schema-scalar-key reads derivable clears **1** mirror.

**Answer to "how many of the 679 are `Dict[str, Any]` reads": 509 (75 %) are dict-related, and 399
(59 %) are literal-key reads. But a dict-read model alone cannot remove the 27-mirror cost of the
flip: at best 5 mirrors stop being refused.**

### 4.5 A route-(a) spike on the emitter: re-annotate to `hval`, nothing else

The fidelity plane allows annotations to differ, and `Dict[str, PyVal]` already selects the
certified `hval` model. So route (a) can be tried today with no emitter change. Four leaf-ish stubs
from §4.1 A were ported, and only their parameter annotation was changed (`spike/edits.py`,
`spike/run.sh`):

| stub | edit | result | new first clash (`spike/<id>.mlw`) |
|---|---|---|---|
| 398 `pycsl._record_key` | `rec: dict` → `Dict[str, PyVal]` | L3-TC | the reads now descend faithfully (`match term with HMap m_k7 -> (match pairs_get m_k7 "goal_name" …`). The clash moves to `tuple(<hval>)`: the builtin is still int-typed |
| 400 `pycsl._synthesize_block` | same | L3-TC | `", ".join(<hval>)`: `join_1` is int-typed |
| 034 `core_ir_semantic._namedtuple_check_call` | `call`, `nt_arities` → `Dict[str, PyVal]` | L3-TC | `callee in nt_arities` with `callee : hval` used as a `map string` key: a projection is missing at the key position |
| 282 `functions._mixin_dep_pseudo_functions` | `functions: List[Dict[str, PyVal]]` | L3-TC | `self._parse_mixin_sig(dep.get("sig", ""))`: an `hval` passed to a `str` parameter of a trusted callee. A projection is missing at the call-argument boundary; `hstr_of` exists only in compare and return positions |

**0 / 4 reach TC-OK. In every case the dict read itself is repaired (faithful, receiver-reading,
tagged), and the chain advances by exactly one link.** The next links are hval consumers:
- builtins over `hval` (`tuple`, `join`, `len`);
- `hval` as a dict key;
- `hval` as an argument to a `str` slot.

This is the same "one link per capability" pattern as R5-str and the levers ledger.

---

## 5. The state-of-the-art lens

| technique | how it types a JSON-like value | what it would mean here |
|---|---|---|
| **TypedDict / PEP 589** (mypy, pyright) | A closed record type per dict shape. `d["k"]` gets the declared type; `.get` gets `Optional`. Totality and `NotRequired` mark optional keys. Unsound at the boundary: a `Dict[str, Any]` is accepted where a TypedDict is expected only via `cast`. | The emitter already lowers TypedDicts to records (q3b/q3c), and the mirror already uses three closed-key views (`ValIRBoolView`, `BoolWrapIRView`, `LogicSymbolView`). The boundary is the problem. Probe q7 passes a `Dict[str, Any]` into a `VarIR` parameter: an L3 clash (`map string (option int)` vs `varir`), so it fails closed, and **no modelled cast exists**. |
| **Record views over JSON** (JSON Schema → types; F# type providers; Typed Racket `jsexpr`) | A schema-derived static type, validated once at ingestion | `ir_schema.py` is that schema: 117 classes, and `wf_ir_gen.py` derives a per-key `wf_val` predicate. But `validate_ir` checks only required top-level keys, not the type of every node (`ir_schema.py:1-10`, `:158-172`), and a proof could rely on the schema only through a `requires wf_ir`. Rule 5 forbids that precondition. |
| **Tagged unions / variants** (ML / Why3 algebraic types; CompCert `val`; Dafny `Box`) | One sum with a constructor per runtime kind; projections are pattern matches | `hval` and `pyval` exist and are certified. Their limit (§4.5) is the number of **consumers** that must accept `hval`. Each builtin, each key position and each call boundary needs a projection or an hval-polymorphic version. |
| **Occurrence typing** (Typed Racket, Tobin-Hochstadt & Felleisen, ICFP 2010; mypy/pyright `isinstance` narrowing) | Flow-sensitive narrowing after `isinstance` or key tests | The emitter's own code is full of `isinstance(x, dict) and x.get("type") == "Call"` guards (e.g. `_emit_membership`, row 242). Narrowing would turn an `hval` read into a typed one exactly where the live code checks. The hval lowering already turns `isinstance(v, str)` into a tag match (q2), but the narrowed type is not propagated to later uses. |
| **Gradual typing with runtime tags** (Siek & Taha 2006; Reticulated Python's transient checks, Vitousek et al. 2014/2017) | Statically unknown values carry tags; a check is inserted at each typed use, and a failure is a blame error | A check is a proof obligation here. Under `requires True` the obligation "this `.get` is a `str`" is not provable for an arbitrary input, so every such use becomes a failing VC. That is the same refusal set as the hashing flip, moved from the pre-pass to Why3. |
| **Why3 algebraic types** | Strictly positive sums; no subtyping; polymorphism encoded soundly to many-sorted SMT (Bobot & Paskevich, FroCoS 2011) | `HArr` must recurse through a bespoke `hval_list`, and `HMap` through `hpairs` (`preamble.py:8022-8030`, "Why3 rejects `seq` recursion as non-strictly-positive"). Polymorphic results may not instantiate a mutable type (`int-erasure-seam-r3.md` §3.7). Proof cost is E-matching on `pairs_get` folds (§3.3). |
| **Nagini / Viper** (Eilers & Müller, CAV 2018) | Every value is a `Ref` with `typeof(r)` into a `PyType` domain. **Requires mypy-clean PEP 484 types** and rejects what mypy cannot type. `Dict[str, Any]` values are `Ref`s whose `typeof` is unconstrained. | Nagini would not accept the emitter: 62 % of the live trusted signatures are imprecise (`int-erasure-seam-r3.md` §3.4). Its answer to a JSON IR is "declare the classes", which in Python means TypedDict or dataclass IR (the live emitter is partly there: `node.to_dict()`, `ExprIR` dataclasses in `ir_schema.py`). |
| **Gillian-JS / JaVerT** (Santos et al., POPL 2018) | JS values are a tagged union in the logic, and every operation dispatches on the tag | The faithful version of route (a). The cost is VC volume on dispatch-heavy code: the emitter's handlers are exactly that. |

---

## 6. Routes, costed

Pricing basis:
- **"Unlocks"** counts stubs whose *first* blocker the route removes (§4.1 A/B, §4.2 A), and #UND
  sites it makes derivable (§4.4).
- **"Converts"** would need the whole chain. §4.5 measures that one link is all a dict-read route
  removes.
- **Mirror re-proof** is the whole-file proof of each touched mirror. Measured times:
  - `preamble.py` 1,074 s and `Module2_Parser.py` 801 s
    (`/home/fabrice/git/pycsl-u411/getting-better/systematic-soundness-r3/u411-r411/mirror-wholefile-proofs.txt`);
  - `stmt_control_flow.py` about 2,400 s with one hval field (`driver-backlog.md:3619`);
  - `core_ir_semantic.py` over 70 min (`getting-better/driver-frontier-floor.md:167`);
  - `pure_ast.py` 8,582 s including queue (`conversion-census-r3.md`, phase C);
  - the big mixins (`expressions`, `statements`, `functions`) at 2–3 h each
    (`int-erasure-seam-r3-impl.md` §4).

### (a) A tagged `pyval`/`hval` sum with a constructor per JSON kind and proven projections

- **What exists:**
  - `hval` and its certificate (`Phase2f_PyVal.v`, `PyVal.lean`);
  - its selection by `Dict[str, PyVal]` on a parameter or local (but **not** on a return: backlog
    #69, `driver-backlog.md:157-192`, probe p3 of `int-erasure-seam-r3.md` §3.6);
  - total projections `hstr_of` / `hint_of`, where a wrong tag projects to an uninterpreted value
    with no axiom.
- **What is missing:**
  - hval-accepting consumers: `tuple` / `join` / `len` / `sorted` over `hval`, `hval` as a map key,
    and `hval` passed to a typed parameter (with an `hstr_of`-style projection at the argument);
  - return-annotation selection (#69);
  - an absent-key sentinel distinct from `HInt` (q2's `(any bool)` arm).
- **Unlocks (first link):** at most the 9 A-clashes + 10 A-refusals + 4 stores = **23 stubs**,
  re-annotated in the mirror only. **Measured: 0 / 4 reach TC-OK** (§4.5).
- **#UND sites:** **none**. The hashing check is a static pre-pass over Python source
  (`pycsl.py:7490-7510`), not a WhyML property. An `hval` may be `HArr` (a list), so a hashed `hval`
  is not positively hashable.
- **New certificate?** No for the type itself. The coupling rule applies to each new consumer
  shape, for example hval-polymorphic builtins.
- **Mirror re-proof:** every file whose functions are re-annotated. 19 / 19 A-stubs live in big
  mirrors (§4.3), so each step costs 1–3 h of proof per file, with the E-matching risk of §3.3.
- **Corpus:** none (`PyVal` is a corpus-absent sentinel, `Module5_IREmitter.py:6156-6158`).

### (b) TypedDict declarations for the mirror's IR node shapes, read through typed projections

- **What exists:**
  - TypedDict → record lowering (q3b `name_of`);
  - three closed-key views in the mirror (`module6_whyml/types.py:8-16`, `statements.py:25`,
    `stmt_control_flow.py:10`, `scc.py:5`);
  - route #398 (a key is read only when positively required);
  - the schema: 117 classes.
- **What is missing:**
  1. **A modelled boundary.** Probe q7 shows that a `Dict[str, Any]` value reaching a TypedDict
     parameter is a Why3 clash, and TC refuses a TypedDict used as a value. A sound `cast` would
     need either a proof (impossible under `requires True`) or an explicit trusted conversion,
     which is a new `\trusted` site.
  2. **A union of node shapes.** A handler receives `node` and dispatches on `node["type"]`. Its
     static type is the union of up to 117 TypedDicts, and a Why3 record cannot express that. It
     needs a sum, which is route (a) or `emit_ir`.
  3. **Consumer fixes.** `node["type"] == "Var"` lowers to a hashed-int compare (q3b clash);
     `len(node["name"])` lowers to an int-typed `iter_length` (q3).
  4. **Closed views over-claim.** A required `op: str` in a view asserts presence for nodes that have
     no `op`. Only 5 of the 117 schema classes declare an `op` field (an AST count over the
     class bodies of `src/pycsl/ir_schema.py`; script in §10 step 5).
     The existing views are sound only as far as their reads are `.get` and their consumers are
     insensitive to the missing-key value. That has not been audited.
- **Unlocks (first link):** the same population as (a), at most 23, for stubs whose receiver has a
  single shape. Most do not: 242 and 248 read `expr` of any expression kind.
- **#UND sites:** a value read from a TypedDict field is derivable today; the q7 `key_of` hash is
  admitted. At most the 209 direct reads, and only where the receiver can be retyped. 73 of their
  receivers are `Any` parameters and 69 are loop variables over lists of dicts.
- **New certificate?** No (records are already certified shapes).
- **Mirror re-proof:** per retyped file, as in (a).
- **Corpus:** none if only mirror annotations change. The q3b consumer fix is a corpus change
  (TypedDict programs exist in the corpus, e.g. `1865`, `3806`, `5444`).

### (c) A key-indexed typed view for literal-key reads (schema-directed)

- **Idea:** derive the type of `x.get("name")` / `x["name"]` from the key alone, using the
  schema's single-shape keys (35 scalar keys; `name` is `str` in all of them). Apply it in the
  hashing derivation (no emission change), and optionally as an `hval` projection in emission.
- **Unlocks, hashing:** **332** of the 679 `#UND` sites, but **1** of the 27 refused mirrors
  (§4.4). Even with all 509 dict-related sites, only 5 / 27.
- **Unlocks, conversions:** in emission it is (a) plus a key-directed projection, so at most the
  same 23 first links.
- **Soundness:** this is the route's real cost. Keying a type off a key *name* is sound only if the
  receiver **is** a schema-conforming IR node. The mirror's `#UND` receivers include why3 JSON
  records (`_record_key`: `loc.get("file-name")`), symbol tables and registries. Without
  provenance (the receiver typed `ExprIR`/`StmtIR`, or produced by an IR traversal), the view is
  an unproved typing assumption about the input. That is an assumption not on the ledger, and the
  rules forbid it.
- **New certificate?** For the hashing use, none (no WhyML change). For emission, the per-key
  projection is the existing `wf_val` table (`wf_ir_gen.py`), whose discharge needs `requires
  wf_ir node`, which rule 5 forbids.
- **Mirror re-proof:** none for the hashing use. As (a) for emission.
- **Corpus:** a refusal-set change only. A corpus program reading `d.get("name")` from a non-IR
  dict would become admitted when hashed. That is an **unsound widening unless provenance-gated**,
  so it must be gated on IR-typed receivers.

### (d) Leaf-first conversion

- **Population:** 8 of the 19 A-stubs are leaves, and 5 are at most 33 lines (§4.3).
  `int-erasure-seam-r3.md` §3.8 measured that conversion order does not change a callee's `val`
  type, so ordering has **zero** type leverage.
- **Unlocks:** nothing by itself. It decides the spike set for (a)/(b): 398, 400, 034, 001 and 250,
  all small leaves.
- **#UND sites:** none.
- **New certificate?** No.
- **Mirror re-proof:** it minimises it. One home file per conversion, and no caller's `val`
  changes.
- **Honest catch:** all 19 live in mirrors the hashing flip would refuse (§4.3). If the flip ever
  lands, each conversion there is lost unless that mirror's non-dict `#UND` sites are fixed too.

### What the measurements say about the combination

- **For hashing**, the dict model is **not** the binding constraint on the 27-mirror cost. 22
  mirrors carry 170 non-dict `#UND` sites: call results 93, attributes 52, parameters. Any route
  that only types dict reads leaves the flip at **≥ 22 / 53** mirrors refused. Two further pieces
  are needed:
  - an allow-list derivation for call results: the `-> T` of trusted mirror stubs, whose mirror
    annotations are often `int` placeholders (`int-erasure-seam-r3.md` §3.4: 100 / 142 drifted
    signatures);
  - attribute classes of `ast` nodes.
- **For conversions**, the dict read is the first link of 19 stubs. Behind it sit the
  hval-consumer links (§4.5) and the 75 + 261 non-dict first blockers.

---

## 7. Honest limits

- **The classifications in §4.1 and §4.2 were made by reading.** Each row cites the emitted slice
  (`clash.json`) or the message (`cv4-new.json`), with the Python source located by `fsrc.py` and
  `r252.py`. Borderline calls:
  - 250 (a dict obtained by `getattr`) was counted as A;
  - 072 (a dict comprehension) was counted as C;
  - 235 (`node.tuple` on an `int`-placeholder parameter, an IR object attribute) was counted as
    other.

  Counted the other way, A moves by ±2.
- **`flipclass.py` is syntactic.** It follows at most two local binding hops and picks the "most
  dict-like" source when a name has several bindings. That choice biases towards "dict-related",
  so 509 is an upper estimate for that row. Its schema-key test checks the key *name* only, not the
  receiver's provenance.
- **`mirflipA.tsv` was measured at `3b2d2e763`, before routes #398-#428 landed.** Some of its 679
  sites may have changed since. Re-measuring the flip needs the e1 log-mode patch, which was not
  re-run here.
- **The hashing probes q4 / q6 were screened, not proved.** `--no-proof` rc 0 shows that they pass
  every refusal and emit no hashing obligation. The only remaining goal is `result = 1` over a body
  returning `1`. A full proof was queued but cancelled unrun, because both NORMAL heavy slots were
  held by other executors' multi-hour mirror proofs.
- **The §4.5 spike is 4 stubs and annotation-only.** It shows the next link, not the chain length.
- **"Contains" (§4.3) is an upper bound**, counted over literal-key reads only.
- **Proof-time figures** in §6 are quoted from other executors' logs, not re-measured.
- **The SOTA characterisations** in §5 are from the literature, except where a probe is cited.
- **Nothing was committed, and `src/` was not edited.** All experiments ran in
  `scratchpad/wall-dict/tree`, a copy of the cv4 census tree, which equals `src/` at HEAD.

---

## 8. Questions for the reviewer

1. Given that 22 of the 27 flip-refused mirrors also have non-dict underivable sites, is the right
   object a **dict value model** at all? Or is it a **positive derivation for every value source**
   (call results through mirror signatures, `ast` attributes, dict reads), with the dict model as
   one row?
2. Under a fixed `requires True`, can a schema-keyed view (route c) be made sound **without** a
   `wf_ir` precondition? For example, provenance typing: a value produced by an IR traversal or
   annotated `ExprIR` is an IR node. Or a modelled `validate_ir` at the Module5→Module6 boundary
   whose postcondition the mirror may assume?
3. For route (a), the measured residuals are hval consumers. Is a small closed set of
   hval-polymorphic builtins plus an argument-boundary projection likely to be the whole chain? Or
   does §4.5's one-link pattern predict another layer behind it (R5-str's experience)?
4. Is there a principled way to type `node["k"]` for a node whose kind is decided by
   `node["type"]` (a discriminated union over 117 shapes) in Why3, without the E-matching cost
   measured for `pairs_get` (§3.3)? For example, one record type with all 114 keys as `option`
   fields.
5. Should the `.get` / `[k]` asymmetry in hashing (q4 admitted, q5 refused) be closed by refusing
   `.get` of a declared `Dict[str, Any]` too, as the route-#383 addendum did for `[k]`? What is that
   rule's mirror cost, as opposed to the full `#UND` flip?

---

## 9. Measured facts, in one place

| fact | value | source |
|---|---|---|
| L3-TC stubs whose first clash is a `Dict[str, Any]` read | 9 / 94 | §4.1, `l3-class.tsv` |
| … plus whole-dict model mismatches | 15 / 94 | §4.1 |
| REFUSED stubs whose refused value is a `Dict[str, Any]` read | 10 / 276 (+4 stores, +1 TypedDict optional key) | §4.2, `refused-class.tsv` |
| `route#349` (hashing) first blockers in the conversion census | 10 (2 at phase A); 4 of them dict reads | §2.2, §4.2 |
| stubs whose live body contains a literal-key dict read | 155 / 370 | §4.3, `contains.py` |
| dict-read-first stubs in a flip-refused mirror | 19 / 19 | §4.3 |
| `#UND` hashing sites that are dict-related / literal-key dict reads | 509 / 679 (75 %) / 399 (59 %) | §4.4, `flipclass.py` |
| … with a key that has one scalar type in `ir_schema.py` | 332 | `schemakeys.py` |
| refused mirrors cleared if every dict read were derivable | 5 / 27 (22 keep 170 non-dict sites) | `schemakeys.py` |
| route (a) annotation-only spike (`Dict[str, PyVal]`) | 0 / 4 TC-OK; chain advances one link in all 4 | §4.5 |
| `.get` vs `[k]` hashing asymmetry | `{m.get("a")}` admitted, `{m["a"]}` refused (`Dict[str, Any]`) | q4 / q5 |

---

## 10. Reproduction

Run everything from `/home/fabrice/git/pycsl`. First run
`export PATH=$HOME/.opam/framac-coq8/bin:$PATH`. Every pycsl run goes through
`scratchpad/heavy/heavy.sh`, and the QUICK class (`--no-proof`) is enough everywhere. Let
`W=scratchpad/wall-dict`.

1. **cv4 data.** `git show cf38e06f9:getting-better/conversion-census-r3.md | sed -n 624,800p`.
   Per-stub verdicts and messages: `$W/cv4-new.json`, copied from the cv4 executor's scratch
   `…/scratchpad/cv4census/new.json`. The census trees `$W/tree` and `$W/pristine` are copies of
   the cv4 `tree/` and `pristine/`.
2. **L3-TC re-run.** `$W/l3.tsv` lists the 94 rows. Run
   `scratchpad/heavy/heavy.sh bash $W/tc.sh --no-proof` repeatedly. It is resumable and stops after
   about 130 s per call. It writes `$W/tc/<id>.{out,mlw,ported.py}` and restores the mirror file
   after each stub. Then `python3 $W/clash.py` writes `clash.json` and prints the slices, and
   `python3 $W/fsrc.py <id> <substr…>` prints the Python lines.
3. **Classifications.** `$W/l3-class.tsv` and `$W/refused-class.tsv`. For the route #252 argument
   lists: `python3 $W/r252.py`.
4. **Contains census.** `python3 $W/contains.py`. **Leaf status:** `python3 $W/leaf19.py`.
5. **Hashing sites.** `python3 $W/flipclass.py` writes the source table and `flipclass.tsv`.
   `python3 $W/flipclass2.py` gives direct reads and receiver types. `python3 $W/schemakeys.py`
   gives schema keys and the mirror-clearing counts. The `op`-field count is a one-line AST count
   of `ClassDef`s in `src/pycsl/ir_schema.py` that have an `op: …` annotated field (5). `python3 $W/mirrorkeys.py` gives the
   whole-mirror key census (1,647 literal-key reads, 187 keys, top 10 = 60 %). The mirror text at
   the measurement base is in `$W/mir3b2/`, from `git show 3b2d2e763:<file>`.
6. **Probes.**
   `scratchpad/heavy/heavy.sh python3 src/pycsl/pycsl.py $W/probes/<p>.py --no-proof --keep-mlw`
   for `q1_any_get`, `q1b_any_get`, `q2_pyval`, `q3_typeddict`, `q3b_typeddict`,
   `q3c_typeddict_get`, `q4_hash_get`, `q5_hash_sub`, `q6_hash_ir` and `q7_td_boundary`. Outputs
   are `$W/probes/<p>.{out,mlw}`. CPython: `python3 $W/probes/q4_hash_get.py`, and likewise for
   q5, q6 and q7.
7. **Mirror emission.** `heavy.sh python3 src/pycsl/pycsl.py src/self-annotate/src/module6_whyml/types.py
   --import-path $PWD/src/pycsl --no-proof --keep-mlw`, run inside `$W/tree`, gives `$W/types.mlw`;
   `_field_type_for` is at lines 1331-1381 (the function ends at `with Return… end`). The row 282 emission is `$W/tc/282.mlw:2504-2531`.
8. **Route (a) spike.** `scratchpad/heavy/heavy.sh bash $W/spike/run.sh --no-proof`. It applies
   `$W/spike/edits.py` and writes `$W/spike/<id>.{out,mlw}`.
9. **Counts.** `grep -rhF '#@ \trusted' src/self-annotate/src --include=*.py | wc -l` gives 442;
   `grep -rho 'Dict\[str, Any\]' --include=*.py src/self-annotate/src | wc -l` gives 277; in
   `src/pycsl` it gives 1,833.
