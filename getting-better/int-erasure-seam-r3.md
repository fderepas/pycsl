# The int-erasure type seam: a state-of-the-art report for independent review

*Driver run #3, wall cycle step 3 (report). Written 2026-10-26 against `ghost-assign-bc6` HEAD
`afcadd6f6` (the census it builds on ran at `ba41be495`). This document assumes no knowledge of the
project. Every number is either measured here, with the command given in §11, or quoted from a cited
file and line.*

---

## 0. The question in one paragraph

PyCSL is a deductive verifier that translates annotated Python to WhyML for Why3. Its back end gives
any Python value whose type it cannot determine statically the WhyML type `int`, as an opaque token.
Values it can determine get faithful types such as `string`, `array τ`, `map k (option v)`, records,
or the IR sum type `emit_ir`. Both value models coexist in one emitted file, and Why3 has no subtyping
or coercion between them. A function therefore fails to type-check whenever a value crosses from one
model to the other.

PyCSL also verifies its own emitter, and that is where the cost shows. There are 446 emitter
functions still trusted without proof (`\trusted`). For **179** of them, the first obstacle to proving
them is a Why3 type clash at this seam. No refusal guard is the binding constraint: removing all seven
of them unlocks 2 of 153.

The questions for the reviewer:
- Is the seam a fixable modelling choice, or a consequence of verifying a dynamically typed language
  with a typed intermediate language?
- Which established technique fits the constraints in §1.4 best? Candidates include typed signatures,
  inference, a universal tagged value type, polymorphic opaque operations, and per-library typed
  models.
- What does each technique cost?

A rigorous "none of these can work under the constraints" is an equally useful answer.

---

## 1. The system

### 1.1 PyCSL

PyCSL is an annotation language and tool for a statically analysable subset of Python (`README.md:3`).
Contracts are written as `#@` comments: `requires`, `ensures`, `assigns`, loop invariants, variants and
`\trusted`. The pipeline is a six-module compiler (`src/pycsl/`, about 165 kLOC of Python):
1. ingest;
2. Lark parser for the `#@` language;
3. weaver;
4. semantic checks;
5. a JSON IR emitter (`frontend/Module5_IREmitter.py`);
6. the WhyML transpiler (`Module6_WhyMLTranspiler.py` and `module6_whyml/`, about 100 kLOC).

Why3 1.8.2 generates verification conditions by weakest precondition, and Alt-Ergo, Z3 or CVC5
discharge them. A reference corpus of 3,837 annotated `.py` programs (`test-suite/corpus/pycsl-reference/`)
pins the emitter's behaviour.

### 1.2 Self-verification: the mirror and `\trusted`

PyCSL verifies its own emitter through a **self-annotation mirror**, `src/self-annotate/src/`
(53 files, 31 kLOC). Each mirror function is one of two things:
- **Converted.** Its body is the live emitter body, **verbatim**, carrying a fixed contract shape:
  `requires True / ensures True / assigns <tight frame>`. This shape states type safety plus frame.
  It is deliberately **not** value-faithful (`config/skills/self-tcb-reduction/SKILL.md:44-50`).
- **A `\trusted` stub.** The emitter keeps its signature and contract and assumes them without proof.

Today there are 446 `#@ \trusted` lines: `grep -rhF '#@ \trusted' src/self-annotate/src --include=*.py | wc -l`.
`getting-better/trusted-reasons.tsv` classifies the stubs (418 rows).

**Converting** a stub means porting the live body verbatim, deleting the marker, and proving it. The
mirror's *annotations* (parameter, return and local types) are allowed to differ from the live
annotations, because they are the modelling layer. The fidelity checker strips them before it compares
bodies (`bin/check-self-annotate-mirror-sync.py:58-66`, `:78-92`). Statements, calls and literals must
not differ.

### 1.3 The oracles: three lower-bound planes and a three-axiom ledger

A conversion counts only if three disjoint executable planes all pass
(`config/skills/self-tcb-reduction/SKILL.md:51-58`):
- **L1, fidelity.** `bin/check-self-annotate-sync.sh` and `bin/self-annotate-mirror-check.sh` confirm
  that the mirror body equals the live body, modulo `#@` lines and annotations.
- **L2, Why3 proof.** The whole mirror file proves with 0 non-Valid goals (`pycsl.py <mirror>`), and
  `--fun <name>` proves the converted method.
- **L3, corpus inertness.** `bin/byte-diff-sweep.sh` gives a byte-identical `.mlw` for every corpus
  program, on both corpus trees, against a baseline at the base commit. Any emitter change that
  touches non-target programs has to be justified file by file.

Further oracles also gate a conversion: `check-emitted-vacuity.py` (no input-blind facades),
`check-yield-erasure.py`, `check-shadowed-selfcalls.py`, `check-untrusted-emitted.py` and
`run-soundness-planes.sh` (61 planes).

**The ledger is three axioms.** The soundness story has three links, all mechanised in Rocq 8.20 and
Lean 4.29 (`src/formal-semantics/`; `generic-dict-str-any-2.md:200-202`):
- **LINK-1:** weakest-precondition soundness against an operational semantics;
- **LINK-2:** faithfulness of the Python-to-WhyML encoding;
- **LINK-3:** the emitter's self-verification. This wall sits on LINK-3.

The only axioms these links rest on are the kernel axioms accepted in
`src/pycsl/proof_axiom_allowlist.py:14-40`: Lean `propext`, `Classical.choice` and `Quot.sound`, plus
propositional and functional extensionality on the Rocq side. The *ledger = 3* rule says that no
change may add an axiom.

The **coupling rule** (`SKILL.md:244-250`) adds that a new WhyML value shape must land together with
an axiom-free Rocq/Lean certificate of its soundness.

### 1.4 Hard rules any proposal must respect

1. **No new axiom.** The ledger stays at 3, and no `#@ proof`-cited lemma may stand in for a missing
   model.
2. **Verbatim bodies.** The converted mirror body *is* the live body. Annotations may differ;
   statements may not.
3. **No vacuous facades.** A converted body must read real modelled structure. Two things are
   forbidden:
   - an input-blind 0-ary `*_0 ()` operation or `pycsl_getattr_default_*` that stands in for a call
     on the input;
   - a contract weakened to make the proof go through.
4. **Corpus inertness.** An emitter change either moves no corpus `.mlw`, or each moved file is
   inspected and re-proved. A gate may never be re-baselined.
5. **Fixed contract shape.** The contract is type safety plus frame, never value-faithful. This scope
   cut is what keeps the problem bounded.

---

## 2. The wall as first seen

The seam has been named and re-measured several times. `getting-better/driver-backlog.md` holds the
history; earlier claims are listed here so the reviewer can see what was already refuted.

- **"Real #1 blocker" (2026-09-24, `driver-backlog.md:8412-8448`).** Six candidates were converted.
  Four failed on the **stub's own `int` placeholder annotation**: the mirror said `held: int` where
  the live code says `held: Set[str]`. Re-typing `held` only moved the error to the next expression:
  "a CHAIN of type repairs, not one".
- **#62 (2026-09-26, `driver-backlog.md:859-917`): "THE INT-ERASURE SEAM IS THE NUMBER-ONE WALL".**
  Of 116 markers that failed with a type error, 102 had exactly one side of the clash equal to `int`,
  in both directions in roughly equal numbers. The key sentence: "THE MIRROR IS EMITTED WITH TWO
  COEXISTING VALUE MODELS ... both directions appear, in roughly equal numbers, which is exactly what
  a seam looks like and is NOT what a missing coercion looks like."
- **#64 (`driver-backlog.md:833-857`): the unit of work is one marker's whole chain.** Three real
  repairs were made: the `or {}` falsy default, the `.get(k, {})` default and the f-string classifier.
  Over all 115 type-error markers they produced **11 moved, 0 lowered**. Every moved marker had a
  second blocker behind the first, and the shallowest chain had depth at least 3, with three distinct
  capabilities.
- **#70 and lesson (r4) (`driver-backlog.md:405-441`): a missing callee is typed `int -> int`.** An
  unresolved free call auto-synthesises `val f_1 (x0: int) : int`. A string-typed callee therefore
  fails at both ends. Typing it costs a new `\trusted` shim, so the net change in markers is zero.
- **#72 (`driver-backlog.md:526-575`): triage by callee closure.** 69 markers pass every
  method-call blocker test and are still int-erasure. The wall is shaped by types, not by calls.
- **Pyval wall I2 (`getting-better/pyval-value-model-wall-impl.md:87-104`).** A certified tagged value
  type exists and repairs a heterogeneous dict build. It converts **0 stubs on its own**, because each
  candidate is also gated by an opaque `stmts_of : emit_ir -> array int` read on the input side.
- **#69 (`driver-backlog.md:157-192`).** The faithful `hval` model is selected by a local or parameter
  annotation `Dict[str, PyVal]`, but **not** by a return annotation.
- **Census r3 (`getting-better/conversion-census-r3.md:66-110`), the measurement this report starts
  from.** It covers all 420 markers:
  - 89 fail type-checking at the first blocker; 179 fail it once guards are neutralised.
  - Lifting all seven refusal guards unlocks 2 of 153.
  - Clash pairs: int⇒string 31, int⇒array 22, string⇒int 15, int⇒record 14, array-int⇒int 13,
    array-string⇒int 9, dict⇒int 6, emit_ir⇒int 5, other 64.
  - Clashing expression: a variable or field read 88, a call result 40.
  - In 58 of the 179, the mirror signature differs from the live one.

---

## 3. Measured sub-populations: a re-measurement on 12 stubs

### 3.1 Method

12 stubs were chosen to cover every major clash pair in the census. They are **not a random sample.**

Each was ported verbatim into a scratch copy of the tree, one at a time, with the file restored after
each run. The port uses `bin/port-one-mirror-body.py <tree> <file> <qualname> --convert [--replace]`.
The ported file was then emitted with `pycsl.py <mirror> --no-proof --keep-mlw`, and the kept `.mlw` was
saved. The script is `scratchpad/wall-ies/tc.sh`; outputs are in `scratchpad/wall-ies/out/`.

**All 12 reproduce the census's first-clash class at `afcadd6f6`** (rc 1, L3 type-check failure).

### 3.2 The 12 clashes, verbatim

Each row gives the clash Why3 reports (*has* ⇒ *expected*), the emitted sub-expression that clashes,
the Python source it came from, and **where the `int` actually originates**.

| # | stub (`file::qualname`) | clash | clashing WhyML | Python source | origin of the `int` |
|---|---|---|---|---|---|
| 1 | `pycsl.py::_make_temp_mlw_path` | int ⇒ string (the function body) | `let path = ref 0 in … let (_tu_fd,_tu_path) = (tempfile_mkstemp_0 ()) in … !path` | `fd, path = tempfile.mkstemp(prefix=".pycsl_", suffix=".mlw"); …; return path` | external call synthesised as `val tempfile_mkstemp_0 () : (int, int)`; keyword args dropped; local pre-declared `ref 0` |
| 2 | `module6_whyml/struct_format.py::calcsize` | int ⇒ string | `Map.get (!sizes) (!char)` | `count_str, char = m.group(1), m.group(2)` … `elif char in sizes` | `re` match object: `m := (_TOKEN_RE_match_2 (str_hash_op fmt) !pos)` with `val m_group_1 (x0: int) : int`. The *string* `fmt` is **hashed to int** before the call. `sizes` (a str-keyed dict literal) is faithful `map string`. |
| 3 | `proof2why3/extract.py::_split_rocq_check_output` | string ⇒ int | `(strip_1 (subscript_get !lines !i)) = !qn` | `if lines[i].strip() == qn:` | `stdout.splitlines()` becomes **receiver-less** `val stdout_splitlines_0 () : int`; `.strip()` becomes `val strip_1 (x0: int) : int`; `qn` (from `List[str]`) is faithful `string` |
| 4 | `audit_proof_reverify.py::_coqc_version` | array string ⇒ int | `subprocess_run_1 (let _alit = Array.make 2 ("coqc") in …)` | `subprocess.run(["coqc", "--version"], capture_output=True, …)` | `val subprocess_run_1 (x0: int) : int`; the list literal is faithful `array string` |
| 5 | `pycsl.py::_find_coqc` | int ⇒ `_union__find_coqc_1` | `raise (Return__union__find_coqc_1 (_sh_which_1 1057863838))` | `import shutil as _sh; return _sh.which("coqc")` | `val _sh_which_1 (x0: int) : int`; literal `"coqc"` hashed to `1057863838`; return `Optional[str]` is a synthesised union type |
| 6 | `module6_whyml/identifiers.py::whyml_ident` | string ⇒ int | `if (!ascii_ch <> 0) then !ascii_ch else (str_concat_op "u" …)` | `ascii_ch = ''.join(c for c in decomp if ord(c) < 128)`; `ascii_ch if ascii_ch else f"u{ord(ch)}"` | generator expression becomes `(any int)`; `str.join` becomes `val join_1 (x: int) : int`; truthiness of the erased value is lowered as `<> 0`; `unicodedata.normalize('NFD', ch)` becomes `unicodedata_normalize_2 117123930 (str_hash_op !ch)` |
| 7 | `proof2why3/sertop.py::parse_sexp` | int ⇒ array string | `(_sexp_parse !tokens)` | `tokens = list(_sexp_tokens(s)); return _sexp_parse(tokens)` | **trusted callee's own signature.** `_sexp_tokens(s: str) -> Iterator[str]` (identical in mirror and live) lowers to `val _sexp_tokens (s: string) : int`, because the annotation mapper has no `Iterator`. `_sexp_parse(tokens: List[str])` is faithful `array string`. |
| 8 | `audit_proof_reverify.py::_cache_store` | `int -> option int` ⇒ int | `dumps payload 0 1 1 1 …` | `f.write_text(json.dumps(payload, indent=2))` | stdlib stub `src/pycsl_lib/json/__init__.py:191` `def dumps(obj, *, …)` has an unannotated `obj`, so it becomes `(obj: int)`. The `dict` parameter `payload` is `map int (option int)`. |
| 9 | `pycsl.py::_record_key` | array int ⇒ int | `let __or_l = (term_get_1 775185414) in if __or_l <> 0 then __or_l else (Array.make 1024 0)` | `tuple(term.get("explanations") or [])` | `.get` on an erased dict gives `int`; the `[]` literal defaults to `Array.make 1024 0` (array int) |
| 10 | `Module6_WhyMLTranspiler.py::…_shared_use_lines` | int ⇒ array int | `array_slice (self__emit_preamble_uses_1 !needs) 1 pycsl_none` | `self._emit_preamble_uses(needs, module_name="__tmp__")[1:]` | the callee is a mixin method defined in **another file** (`module6_whyml/preamble.py:3214`). In this file it is auto-synthesised as `val self__emit_preamble_uses_1 (x0: int) : int` (receiver and keyword argument dropped). Its mirror signature also drifts: `needs: int` in the mirror vs `Dict[str, Any]` live. |
| 11 | `module6_whyml/expressions.py::…_handle_ifexpr_expr` | emit_ir ⇒ int | `_is_arr_var_1 node.ifexprexpr_body` | nested `def _is_arr_var(_d: Any) -> bool` applied to `node.body` | the nested def is lifted, and its **`Any` parameter** becomes `(x0: int)`. The argument is a faithful `emit_ir` IR node. |
| 12 | `frontend/Module5_IREmitter.py::…_csl_in` | int ⇒ emit_ir | `pycsltojsonemitter___csl_to_ir self node.cslin_element` | `self._csl_to_ir(node.element)` | dataclass field `element: CSLNode` (`frontend/Module2_Parser.py:528`) becomes **record field** `cslin_element: int`, because the class name is unrecognised. The callee's mirror signature takes `'ExprIR'` (`emit_ir`). |

Sources: the `.out`, `.mlw` and `.ported.py` files under `scratchpad/wall-ies/out/` for each key.
`val` signatures come from `grep -n "val <name> "` on the kept `.mlw` (§11, step 2).

### 3.3 Where the `int` comes from, grouped (12 stubs)

| origin of the opaque `int` | stubs | examples |
|---|---|---|
| synthesised abstract op for an **external / stdlib / `str`-method** call (default result `int`, receiver often dropped, string args hashed) | 6 | 1, 2, 3, 4, 5, 6 |
| synthesised op for a **cross-scope self-method or lifted nested def** (`Any` param or unknown callee becomes `int`) | 2 | 10, 11 |
| a **declared signature lowered to `int`** (trusted callee `Iterator[str]`; unannotated `obj` in a stdlib stub) | 2 | 7, 8 |
| a **record field** of an unrecognised class type | 1 | 12 |
| a **container literal default** (`[]` becomes `Array.make 1024 0`) meeting an erased `.get` | 1 | 9 |

In this sample, **two value models meet inside one function**:
- `calcsize`: `sizes` is a faithful `map string`, but `char` is erased. `char in ("s","p")` is lowered
  as hashed-int comparisons (`!char = 256268151 || !char = 532054186`, polymorphic probe below), while
  the very next statement needs `char : string`.
- `whyml_ident`: the same split shows up as a string branch and an int-erased branch of one
  conditional expression.

### 3.4 Signature drift, measured over the whole population

`scratchpad/wall-ies/sigdrift.py` compares the mirror `def` with the live `def` for every row of
`trusted-reasons.tsv`:
- 394 have both a live and a mirror definition; 24 have no live counterpart.
- **252 signatures are identical; 142 differ.** This matches the census's 142/396.
- **100 of the 142 have an `int` placeholder in the mirror where the live slot is typed.**
- The drift is two-way. Some mirrors are *richer* than the live code: `'ExprIR'` where the live code
  is unannotated. That is the modelling layer working as designed.
- The existing drift oracle `bin/check-mirror-signature-drift.py` compares **parameter names only**:
  it reports "0 / ratchet 0 over 1265 pairs". By design it does not see annotation drift.

**The live code itself is weakly typed** (same script, live side, 394 stubs):

| live signature property | stubs |
|---|---|
| fully and precisely annotated (no `Any`, no bare `dict`/`list`/`tuple`/`object`, nothing unannotated) | **150** (38%) |
| at least one slot mentions `Any` | 135 |
| at least one slot unannotated | 99 |
| at least one bare `dict`/`list`/`object`/`tuple` slot | 12 |

The emitter's own IR is JSON-shaped `Dict[str, Any]`. That is why "take the types from the live
annotations" has a hard ceiling (§7, route R2).

### 3.5 Annotation-only repairs: does re-typing move the seam? (4 spikes)

Re-typing is allowed by the fidelity plane: parameter and return annotations, plus local `x: T = v`
(`check-self-annotate-mirror-sync.py:78-92`). Four ported stubs were re-typed that way and re-emitted
(`scratchpad/wall-ies/spike.sh`, outputs in `scratchpad/wall-ies/spike/`).

| spike | edit (annotations only) | result |
|---|---|---|
| `calcsize_ret` | return `int` → `Optional[int]` (the live type) | **no change**: same clash `Map.get (!sizes) (!char)` |
| `split_typed` | return → `Dict[str, str]` (live); `lines: List[str] = stdout.splitlines()` | **moved one link.** The consumer becomes `Array.length (!lines)`, but the producer is still `val stdout_splitlines_0 () : int` and the local is still `let lines = ref 0`. New clash: int ⇒ array. |
| `parse_typed` | `tokens: List[str] = list(_sexp_tokens(s))` | **no change**: `list_new (_sexp_tokens s)` is int |
| `ident_typed` | `ascii_ch: str = ''.join(…)` | **moved one link.** The consumer becomes `str_length_op !ascii_ch`, but the producer `join_1 (any int)` is still int. New clash: int ⇒ string. |

**Measured fact:** an annotation changes how the **consumer** is lowered, never the **producer**. A
synthesised op's result type, and the pre-declared local, stay `int`. The seam just moves one link
inward, as backlog #64 predicted. In 0 of 4 spikes did annotation-only re-typing make the stub
type-check.

### 3.6 The seam is a property of the core lowering, not of the mirror (4 user-level probes)

Four probes under `scratchpad/wall-ies/probes/` were run with
`pycsl.py <probe> --no-proof --keep-mlw`.

| probe | Python | result |
|---|---|---|
| `p1_unannotated` | `def ident(x): return x`, then `y = ident(s); return y` in a `-> str` function | **REFUSED** by route #252: "an erased (`Any`/`object`/unannotated/TypeVar) value flows into a slot declared as a builtin type". Fail-closed. |
| `p2_any_dict` | `d: Dict[str, Any]; v = d.get("name"); return v` in `-> str` | **REFUSED**, route #252 again |
| `p3_pyval` | `PyVal = Any`; `def mk(bound: str) -> Dict[str, PyVal]: return {"bound": bound}` | L3-tc ✗. Emitted `let function mk (bound: string) : map int (option int) = (map_update_some (const (None: option int)) 2119122976 bound)`: the return annotation does **not** select the tagged model, and the key `"bound"` is hashed. This reproduces backlog #69 (still open). |
| `p4_list_default` | `def first_or_empty(d: dict) -> List[str]: xs = d.get("xs") or []; return xs` | L3-tc ✗. **Four erasures in one line:** `d : map string (option int)`, `let xs = ref 0`, `[]` becomes `Array.make 1024 0`, and the return is `array string` |

### 3.7 A new route, probed: polymorphic opaque operations

Why3 is ML-polymorphic and encodes polymorphism into many-sorted SMT soundly. If the synthesised ops
returned a **type variable** instead of `int`, Why3's own unification would pick the type at each use
site. Three probes test this.

1. **Hand-written spikes.** `scratchpad/wall-ies/why3py/poly-seam-spike.mlw` (= `poly2.mlw`),
   `poly3.mlw` and `poly4.mlw`.
   - With `val stdout_splitlines_0 () : 'a`, `val strip_1 (x0: 'a) : 'b` and
     `val join_1 (x0: 'a) : 'b`, the `_split_rocq_check_output` and `whyml_ident` shapes **type-check
     and prove** (Alt-Ergo: `split_like'vc` Valid in 0.03 s; `split_arr'vc` Valid).
   - The `_make_temp_mlw_path` shape type-checks with `val tempfile_mkstemp_0 () : ('a, 'b)` and
     pre-declared locals `ref (any_v ())` (`poly3.mlw`, rc 0).
   - **Hard limit found:** a polymorphic *result* may not be instantiated with a mutable type.
     Why3 says: "This application instantiates pure type variable 'a with a mutable type array"
     (`poly.mlw:16`). PyCSL lowers `list` to the mutable `array`, so list-returning ops need a
     separate `array 'e` family. A polymorphic *argument* may receive an array (`poly4.mlw`, rc 0).
2. **On the real emitted files.** `scratchpad/wall-ies/polypatch.py` rewrites a kept `.mlw` textually.
   This is a probe of the route, not an emitter change. Inside the target function, every all-`int`
   abstract `val` it calls becomes type-variable typed, and every `ref 0` local becomes
   `ref (pyc_any ())`. Results of `why3 prove --type-only`, before → after:

   | stub | after | residual clash |
   |---|---|---|
   | `_make_temp_mlw_path` | **type-checks** | — |
   | `_find_coqc` | **type-checks** | — |
   | `_coqc_version` | **type-checks** | — |
   | `whyml_ident` | fails | `if (!ascii_ch <> 0)`: the *consumer* (truthiness) was already lowered as int `<> 0` |
   | `_split_rocq_check_output` | fails | `(strip_1 …) = !qn`: the emitter chose **int `=`** for the comparison |
   | `calcsize` | fails | `char in ("s","p")` was lowered as **int comparisons against hashed literals** |
   | `parse_sexp` | fails | `list_new` result instantiated with mutable `array string` |

   **3 of 7 type-check; 4 fail.** 3 of those 4 fail because the emitter had already chosen a
   monomorphic **operator** from its own erased type guess: int `=`, int truthiness, or hashed `in`.
   The fourth fails on the mutable-instantiation rule.
3. **What these results do not show.** Type-checking is not a conversion:
   - the three that type-check still contain the input-blind 0-ary ops `tempfile_mkstemp_0 ()` and
     `strip_0 ()`, so they would fail the non-vacuity oracle (hard rule 3);
   - none was proved;
   - none went through L1 or L3.

### 3.8 Leaf structure (approximate)

`scratchpad/wall-ies/leaf.py` matches names over each live stub body: **184** stubs call no other
trusted stub, **210** call at least one, and 24 have no live body. Conversion order would only matter
if converting a callee changed the type its callers see. It does not: the callee's `val` type comes
from its mirror annotation whether it is trusted or converted (stub 7: `_sexp_tokens` would still
lower to `: int`).

---

## 4. Where the `int` comes from in the emitter

All line numbers are at `afcadd6f6`. Paths are under `src/pycsl/`. Spot-checked lines are quoted in
§11 step 5.

| erasure | lowering | file:line |
|---|---|---|
| unannotated parameter tagged `"Any"` | Module5 symbol table | `frontend/Module5_IREmitter.py:6339-6340` |
| `Optional[non-Name]`, `Union`, other subscripts → `"Any"` / lower-cased head | `_m5_get_type_name_legacy` | `frontend/Module5_IREmitter.py:5622`, `:5633`, `:5645-5646` |
| all-`Any` union → `"int"` | `_normalize_union_annotation` | `frontend/Module5_IREmitter.py:5307-5309` |
| **parameter type default** (`Any`, `object`, unknown class, unannotated) → `int`; bare `list`/`tuple` → `array int`; bare `set` → `map _ (option int)` | `_param_type_str` | `module6_whyml/functions.py:264`, `:212`, `:174` |
| abstract-op parameter / return default `int` | `_symtype_to_whyml` | `module6_whyml/functions.py:11716` (also `:11690`, `:11705`) |
| **return type default** `int`; tuple → `(int,…,int)`; a `String` return → `int` | `IRScanner.find_return_type` | `module6_whyml/ir_scanner.py:799`, `:801`, `:812` |
| **unannotated local pre-declared** `let x = ref 0` | `_emit_body_code` | `module6_whyml/statements.py:9044-9045` (prefix `"0"` at `:8968`); try-block twin `module6_whyml/stmt_control_flow.py:2272` |
| **dotted / external call** → `val <recv>_<meth>_<arity>`, receiver folded into the *name* (not passed), result default `int`, missing params padded `int` | `_handle_dotted_call`, `_resolve_dotted_signature` | `module6_whyml/expressions.py:8088-8090`, `:7774-7775`, `:8169-8171`, `:9140-9141`, `:9153-9155` |
| **generic call fallback** → `val f_n (x0: int) … : int`, args coerced to int | `_handle_call_expr` | `module6_whyml/expressions.py:10594`, `:10618`, `:10804`, `:10836-10844` |
| **string → int by hashing** (literal → `stable_hash` constant; non-literal → `str_hash_op`) | `_coerce_to_int`, `_str_operand_to_int`, dotted-call args | `module6_whyml/expressions.py:1156-1157`, `:5175-5177`, `:8356-8361`, `:10639-10648`; hash `module6_whyml/identifiers.py:82` |
| `[]` → `Array.make 1024 0` (array int) | `_expr_to_whyml` `ArrayLitExpr` | `module6_whyml/expressions.py:22056` |
| `{}` → `const (None: option int)`; dict param → `map int (option int)`; dict keys `str` → hashed | `DictLitExpr`, `_dict_param_whyml_type` | `module6_whyml/expressions.py:22431`; `module6_whyml/functions.py:11722`; `frontend/Module5_IREmitter.py:6175-6178` ("the model's uniform `dict[str,_] ~ map int (option _)` convention") |
| generator expression → `(any int)`; list/set/dict comprehension → `list_comp 0` / `set_comp 0` / `dict_comp 0` | `_expr_to_whyml` | `module6_whyml/expressions.py:22270-22292`, `:22565-22566`, `:22624-22625`, `:22633-22634` |
| attribute of an opaque object → `getattr_N x <hash>` over `_pyobj_state`; `pycsl_getattr_unknown_*` | `_lower_getattr`, `_handle_field_get_expr` | `module6_whyml/expressions.py:14566-14568`, `:14933`, `:18468-18478`; `module6_whyml/abstract_ops.py:50-54` |
| **record field** of an unrecognised type → `int` | `_field_type_from_annotation`, `_emit_type_decls` | `frontend/Module5_IREmitter.py:2871-2872`, `:2879`, `:2886`, `:2888`; `module6_whyml/preamble.py:9209-9215` |

**The faithful models that coexist with the erasure:**
- `type pyval = PInt | PStr | PBool | PNone | PList | PDict`, emitted only when routed
  (`module6_whyml/preamble.py:4326-4335`);
- `hval = HStr | HInt | HArr | HMap | HNode`, selected by `Dict[str, PyVal]`
  (`frontend/Module5_IREmitter.py:6160-6161`; theory `module6_whyml/preamble.py:8000-8082`; certificate
  `src/formal-semantics/rocq/Phase2f_PyVal.v`);
- `emit_ir` (`module6_whyml/preamble.py:5174`);
- synthesised `_union_*` sum types for `Optional`/`Union` returns
  (`frontend/Module5_IREmitter.py:5327`);
- a schema-derived `wf_val` typing predicate for IR fields (`module6_whyml/wf_ir_gen.py:1-17`);
- a polymorphic-result getattr already exists: `val getattr_{_pst}_poly … : 'a`
  (`module6_whyml/expressions.py:14566`).

**The soundness guards on the erased model:**
- **Route #325** (`pycsl.py:13482-13503`, raised at `:15480-15492`) records why the `int` must be
  opaque. The comment says that before #325, "every claim true of ALL INTEGERS was proved of floats,
  strings, lists and modules: `F = 0.5; F % 1 == 0` … PROVED (CPython False)". An erased value may
  now only be bound, passed, returned, discarded, or compared `=`/`<>` against a different value.
- **Route #241** (`expressions.py:22280-22291`): the generator-expression placeholder used to be the
  literal `0` and proved `m() == 1` where CPython gives 0. It is now the fresh `(any int)`.
- **Route #252** (probes p1/p2) refuses an erased value flowing into a builtin-typed slot.

---

## 5. The deeper truth: modelling choice or fundamental?

**The `int` placeholder is a modelling choice, and a sound one.** It is a universal "opaque token"
sort. The guards make it an over-approximation: R325 takes away int theory, #241 replaced fixed
constants with fresh values, and #252 refuses flows into builtin slots. Nothing forces the token to be
`int`; it is `int` because `int` was the WhyML sort that every early lowering already used.

**What is not a choice:**
- **Python operators dispatch on the runtime type.** `==`, `in`, truthiness, `len`, `+` and `[i]` mean
  different things on `str`, `list`, `dict` and user objects.
- **Every WhyML operator the emitter can emit is monomorphic in practice.** There is int `=` vs a
  string equality op, `<> 0` vs `str_length_op`, `Map.get` on `map string` vs `map int`.

So at every *consumer* the emitter must commit to a type, and when it does not know one it commits to
`int`. §3.5 and §3.7 measure exactly this:
- annotations fix consumers and leave producers int;
- polymorphic producers fix producers, and then the clash surfaces at a consumer the emitter already
  lowered as int (3 of the 4 residual failures).

The seam is where those two commitments disagree.

**What is fundamental, then:** for a dynamically typed source, a static verifier must obtain, at each
consumer, either a **static type**, or a **dynamic tag together with an obligation that the tag is
right**:
- a static type can come from annotations, inference, or the mirror's modelling annotations;
- a tag-plus-obligation needs a universal sum type and projections whose safety must be proved, or
  whose failure is modelled as an exception.

The current design does neither at erased sites. It *defaults*, which is sound only because the
default is opaque and guarded. The two coexisting models are the visible consequence. Nothing about
Why3 or the ledger prevents either alternative.

**Three facts make the alternatives expensive here:**
1. **The emitter is written in its own erased dialect.** 62% of the live trusted signatures are
   imprecise (§3.4). The IR is `Dict[str, Any]` JSON, and the external libraries (`re`, `subprocess`,
   `tempfile`, `shutil`, `json`) are unmodelled or untyped.
2. **The fixed contract shape is `requires True`.** A tagged model would have to prove that
   `d["name"]` is a `PStr`. That requires either:
   - a precondition such as `requires wf_ir node`, which changes the fixed shape (rule 5); the
     `wf_ir_gen.py` predicate exists for exactly this; or
   - a total over-approximating projection, whose wrong-tag case must be modelled the way Python
     behaves (`AttributeError`/`TypeError` raised, or a different method run), not as an arbitrary
     string.
3. **Corpus inertness.** Every lowering in the §4 table is shared with user programs. Changing a
   default changes thousands of corpus `.mlw` files, and each moved file must be inspected and
   re-proved, because rule 4 forbids re-baselining.

---

## 6. The state-of-the-art lens: how other deductive verifiers type a dynamic source

| system | how a value gets a static type | universal type? | what it does with untyped code | lesson for PyCSL |
|---|---|---|---|---|
| **Nagini** (Eilers & Müller, CAV 2018), Python → Viper | Requires PEP 484 annotations and mypy type-checking. Every value is a Viper `Ref`, with a `typeof` function into a `PyType` domain and subtype axioms. Primitive values are boxed. | Yes: `Ref` plus type predicates | Rejects programs mypy cannot type | Static types come from an external checker. Dynamic type facts are assumptions or obligations over one universal sort. Close to route R4 with types from R2. |
| **Viper** (Müller, Schwerhoff, Summers, VMCAI 2016) | Front ends encode source types as domains | Typically one `Ref` sort plus domains | Front end's job | A universal sort plus axiomatised type predicates is the standard intermediate pattern |
| **Prusti** (Astrauskas et al., OOPSLA 2019), Rust → Viper | Types from rustc (MIR). Each type gets a pure "snapshot" domain. | No (one domain per type) | n/a: the source is statically typed | Per-family typed models (R5) are natural only when every value is statically typed. That is not true here (62% imprecise). |
| **Why3 mini-Python** (Why3 1.8.2, `-F python`; stdlib `share/why3/stdlib/python.mlw`) | Hindley–Milner inference with optional annotations. Unannotated `def f(x): return x` is accepted at both `list[int]` and `int` (probe `scratchpad/wall-ies/why3py/c.py`, rc 0). | No | Restricts the language: no `str` type at all (`a.py`: "unbound type symbol 'str'"); values are `int`, `bool`, `list 'a` | Inference instead of a default is the native Why3 answer. It works because the language is restricted so that every operator is typable. |
| **Dafny → Boogie** (Leino) | Polymorphism through a universal `Box` type with `$Box`/`$Unbox` and `$Is` typing axioms | Yes: `Box` | n/a | An injection/projection pair with typing predicates. Projection safety is axiomatised, which this project's ledger forbids unless it is certified. |
| **Gillian-JS / JaVerT** (Santos, Maksimović, Gardner et al., POPL 2018) | JS values form a tagged union in the logic; type tests are assertions | Yes: tagged | Every operation dispatches on the tag symbolically | The faithful version of route R4: the dispatch is modelled, not defaulted. The VC cost is the price. |
| **CompCert `val`** (Leroy) | `Vundef \| Vint \| Vlong \| Vfloat \| Vptr …` | Yes | `Vundef` is a sound unknown | A tagged universal type with an explicit "unknown" tag. This is a better unknown than an `int` placeholder. |
| **Frama-C E-ACSL** (Signoles et al.) | A typing pass over ACSL integer terms chooses machine int or GMP per term, by interval inference | — | Falls back to the most general **sound representation** (GMP), not an opaque token | Representation by inference, with a general fallback. Compare: PyCSL falls back to an opaque one. |
| **Why3 polymorphism encoding** (Bobot & Paskevich, FroCoS 2011) | Polymorphic WhyML is encoded soundly into many-sorted SMT | — | — | Route R3 (polymorphic opaque ops) needs no new trust *from Why3*. §3.7 measured its limits. |
| **Typed Racket occurrence typing** (Tobin-Hochstadt & Felleisen, ICFP 2010); soft typing (Cartwright & Fagan, PLDI 1991); gradual verification (Bader, Aldrich & Tanter, VMCAI 2018) | Flow-sensitive narrowing on type tests (`isinstance`); static where possible, checks where not | — | Inserted checks or residual obligations | How projections out of a tagged model become provable under `isinstance` guards, which are frequent in the emitter. |
| **Type inference for Python** (mypy/pyright; runtime-trace annotators such as MonkeyType) | Inference or recorded runtime types | — | `Any` | A cheap way to raise the 38% of precise live signatures. In the mirror, annotations are free (§1.2). |

---

## 7. Routes, honestly costed

**R1. Fix the signature drifts first** (58 of the 179; 142/394 overall, 100 with `int` placeholders).
- *Measured yield:* in the 12-stub sample, 3 stubs have drift in their own signature. Re-typing moved
  0 of the 2 tested to type-check (§3.5): `calcsize` did not change, and `_split_rocq_check_output`
  moved one link. The "real #1 blocker" entry and #64 recorded the same chain behaviour.
- *Cost:* each re-typed stub changes its emitted `val`, so every mirror file that imports it is owed a
  whole-file re-proof. Mirror files are large; proofs reported in census r3 take 7,000–8,600 s.
- *Value:* necessary hygiene, and it makes the next blocker visible. **It is not a lever on its own.**
- *Cheapest piece:* extend the drift oracle from parameter names to annotation classes. It is
  read-only and has no corpus impact.

**R2. Typed signatures from live annotations, including a mapper for `Iterator`/`Optional`/`Tuple`/`Set`.**
- *Ceiling:* only 150/394 live signatures are precise (§3.4).
- *Gaps found in the sample:* `Iterator[str]` lowers to `int` (stub 7); unannotated stdlib stub
  params lower to `int` (stub 8).
- *Cost:* a mapper extension at `functions.py:20-264` / `ir_scanner.py:762-812` is low per type, but
  generators hit the separate yield-erasure wall. Corpus impact is limited to programs that use those
  annotations.
- *Value:* moderate, and an enabler for R3 and R4. Annotations fix **consumers** only (§3.5), so R2
  alone does not close a chain.

**R3. Polymorphic opaque operations: let Why3 infer the type at the seam** (new in this report).
- *Measured:* 3 of 7 real emitted files type-check after a textual rewrite (§3.7). Hand-written shapes
  type-check and prove.
- *Required work:*
  - type-variable results and parameters in the four synthesis points
    (`expressions.py:7774`, `:10836-10844`, `functions.py:11716`, `ir_scanner.py:812`);
  - polymorphic local pre-declaration (`statements.py:9044`);
  - an `array 'e` family for list-returning ops (the mutable-instantiation limit);
  - **type-directed consumer lowering**: `=`, truthiness and `in` must not commit to int when the
    operand's type is a type variable. That needs the type, so R3 must be paired with inference on
    the emitter side.
- *Soundness obligation, not optional:* R325's taint must follow type-variable-typed results.
  Otherwise an unknown value that Why3 unifies to `int` regains int theory, which is the exact bug
  class of routes #325 and #241.
- *Ledger:* no new axiom. It is arguably not a new value shape (Why3's polymorphism is already used by
  `getattr_*_poly`), but LINK-2 must be re-argued for polymorphic vals.
- *Corpus cost:* the highest of all routes. Every corpus program that uses a synthesised op moves. If
  the change is gated to the mirror, it creates a third coexisting model.
- *Does not fix* input-blind receiver-dropping facades (`stdout_splitlines_0 ()`), which fail hard
  rule 3 independently.

**R4. One tagged universal value type (`pyval`/`hval`) at every erased site.**
- *Exists and is certified:* `Phase2f_PyVal.v`; `preamble.py:4326`, `:8000-8082`.
- *Measured so far:* 0 stubs converted alone (pyval I2); the return-annotation selection gap (#69) is
  still open (probe p3).
- *Cost:*
  - an injection at every producer and a projection at every consumer, i.e. operator dispatch over
    tags (the JaVerT approach);
  - projection safety needs `wf_ir`-style preconditions (`wf_ir_gen.py`), which conflict with the
    fixed `requires True` shape (rule 5), or exception-modelling projections;
  - a VC-size increase that is unmeasured at mirror scale.
- *Coupling rule:* satisfied for the existing shapes. New arms (bytes, user objects) need a
  co-landing certificate.
- *Value:* the only route that removes the seam rather than moving it.
- *Scale:* the backlog estimates multi-session work; §8 lists what is not known.

**R5. Per-family typed models of external libraries** (`re`, `subprocess`, `tempfile`, `shutil`,
`json.dumps`, `str` methods; typed stubs in `src/pycsl_lib/` under its zero-`\trusted` policy).
- *Measured:* external, stdlib or `str`-method producers are the origin in **6 of 12** sampled stubs
  (§3.3).
- *Cost:* per family, small and independent. Corpus impact is limited to users of each family.
- *Catch:* most of these calls also drop the receiver or keyword arguments (`tempfile_mkstemp_0 ()`,
  `stdout_splitlines_0 ()`, `strip_0 ()`), so the typed model must also **pass the receiver**. That is
  the same capability as the in-place-mutator wall (receiver plus `writes`). Otherwise the result is
  an input-blind facade that rule 3 rejects.

**R6. Leaf-first conversion order.**
- *Measured:* 184/394 stubs call no other trusted stub. Conversion does not change a callee's `val`
  type (§3.8).
- *Value:* scheduling only (fewer re-proofs). **Zero type-seam leverage by itself.**

**Expected combination.** No single route is measured to unlock any stub alone:
- R1, R2 and R6 are cheap enablers.
- R5 together with receiver passing addresses the largest origin class in the sample.
- R3 and R4 are the two real alternatives for the core lowering:
  - R3 is inference-based. It is cheap in model terms and expensive in corpus churn and in the
    soundness obligation it re-opens.
  - R4 is tag-based. It is faithful and expensive in VCs and in contract shape.

Choosing between R3 and R4 is the main question for the reviewer.

---

## 8. Honest limits of this report

- **The sample is 12 hand-picked stubs**, chosen to span the clash classes. Its origin counts (§3.3)
  illustrate the classes and are **not** population estimates. The 179-stub composition is quoted from
  census r3 and was not re-measured here.
- **Census base vs this tree.** Census r3 ran at `ba41be495`; the re-measurement ran at `afcadd6f6`.
  All 12 reproduce, but other members of the 179 may have moved since.
- **R3 is shown only on emitted text.** It is a textual rewrite of emitted `.mlw`
  (`polypatch.py`), not an emitter change. "Type-checks" means `why3 prove --type-only` rc 0. No
  proof, no L1/L3 gate and no vacuity oracle was run on it. Two of the three type-checking files keep
  input-blind 0-ary ops and would fail the non-vacuity oracle.
- **The leaf census (§3.8) matches names approximately** (bare and `self.` calls only).
- **The live-annotation census (§3.4) is syntactic.** It classifies annotation strings and does not
  resolve aliases (`PyVal = Any` counts as precise).
- **No route's corpus impact was measured.** The corpus-cost statements in §7 are inferred from which
  lowerings are shared, not from a byte-diff.
- **The SOTA characterisations in §6 are from the literature.** Only the Why3 mini-Python row was
  re-measured here (probes `a.py`, `b.py`, `c.py`).
- **Nothing was committed, and `src/` was not edited.** All experiments ran in
  `scratchpad/wall-ies/tree` (a `git archive HEAD` copy) or on copies of emitted files.

---

## 9. Open questions for the reviewer, with anchors

1. For a self-verifying emitter whose own code is about 62% imprecisely typed, which is the better
   foundation: inference at the IL (R3; anchors: Why3 mini-Python HM, Bobot–Paskevich), or a tagged
   universal value type (R4; anchors: Nagini `Ref`+`typeof`, Dafny `Box`, JaVerT, CompCert `val`)?
   What is the expected VC-cost ratio?
2. Under a fixed `requires True` contract, can projections out of a tagged model be made provable
   without a `wf` precondition, using occurrence typing on `isinstance` guards plus modelled exceptions
   on the wrong-tag path, while staying sound?
3. Does making abstract ops polymorphic preserve the soundness invariant of route #325, that an
   unknown value never acquires int theory, given that Why3 may unify the type variable with `int`?
   What is the minimal taint discipline that does?
4. Is there a principled, type-directed lowering of Python's overloaded operators (`==`, `in`,
   truthiness, `len`) when the operand type is a type variable? For example, deferred operator
   selection, or dictionary passing as in Haskell type classes.
5. Are there known techniques for keeping a large regression corpus **byte-inert** while changing a
   core lowering default, for example by staging the new default behind a typing predicate that holds
   only where the old default was unused?

## 10. The frozen benchmark

A proposal is judged on:
- **The 12 stubs of §3.2.** Each must reach L3 type-check (`--no-proof` rc 0), then whole-file proof
  with 0 non-Valid, verbatim body (L1), the non-vacuity oracle green, and the corpus byte-diff with
  every moved file inspected and re-proved.
- **The ledger:** unchanged at 3 axioms (`proof_axiom_allowlist.py`). Any new value shape co-lands an
  axiom-free Rocq/Lean certificate.
- **The population target:** the 179 type-clash stubs of census r3. Success is the count reaching L3
  type-check, then proof.

A rigorous demonstration that **no technique can convert these under §1.4** is an accepted closure.

---

## 11. Reproduction

Run from `/home/fabrice/git/pycsl` at `afcadd6f6`. First run
`eval $(opam env --switch=framac-coq8 --set-switch)`. Every `pycsl.py` and `why3` run goes through
`scratchpad/heavy/heavy.sh`.

1. **12-stub re-measurement:** `scratchpad/wall-ies/tc.sh`, which reads `scratchpad/wall-ies/sample.tsv`
   and writes `scratchpad/wall-ies/out/<key>.{out,mlw,ported.py}`. Each run is about 10–60 s.
2. **Clash extraction:** `scratchpad/wall-ies/clash.sh`. For each `.out` it takes the last
   `File "…", line L, characters A-B` and slices the kept `.mlw` at `[L][A:B]`. It covers 11 of the
   12. `_make_temp_mlw_path` reports a multi-line span (`line 1491, character 4 to line 1497`); read
   it with `sed -n 1487,1497p` on its `.mlw`. Run `grep -n "val <op> "` on the `.mlw` to get the
   `val` signatures quoted in §3.2.
3. **Signature drift and live-annotation census:** `python3 scratchpad/wall-ies/sigdrift.py /home/fabrice/git/pycsl`
   prints `{'identical': 252, 'differ': 142, 'no-live-or-mirror': 24}`, the int-placeholder count of
   100, and the live-quality counts.
4. **Annotation spikes:** `scratchpad/wall-ies/spike.sh <name> <file> out/<key>.ported.py spike/ed_<x>.py`,
   with edits `spike/ed_{calcsize,split,parse,ident}.py`.
5. **Emitter lines:** `sed -n '<L>p' src/pycsl/<file>` for each row of §4. These were spot-verified:
   - `functions.py:264`, `:212`, `:174`, `:11716`;
   - `expressions.py:22056`, `:22270-22292`, `:7774-7775`, `:8088-8090`, `:10836`, `:1156-1157`,
     `:22431`;
   - `statements.py:9044-9045`;
   - `Module5_IREmitter.py:2871-2872`, `:6339-6340`, `:6150-6185`;
   - `ir_scanner.py:799-812`;
   - `preamble.py:4326-4335`, `:9209-9215`;
   - `identifiers.py:82`;
   - `pycsl.py:13482-13503`.
6. **User-level probes:** `heavy.sh python3 src/pycsl/pycsl.py scratchpad/wall-ies/probes/p{1..4}_*.py --no-proof --keep-mlw`.
7. **Polymorphic-seam probes:**
   - `why3 prove --type-only scratchpad/wall-ies/why3py/poly.mlw`: fails with the mutable-instantiation
     message;
   - `why3 prove -P alt-ergo scratchpad/wall-ies/why3py/poly-seam-spike.mlw`: Valid;
   - `why3 prove --type-only scratchpad/wall-ies/why3py/poly{3,4}.mlw`: rc 0;
   - `python3 scratchpad/wall-ies/polypatch.py out/<key>.mlw <fn> poly/<key>.mlw`, then
     `why3 prove --type-only` on both the original and the rewritten file (§3.7 table).
8. **Why3 mini-Python:** `why3 prove -F python --type-only scratchpad/wall-ies/why3py/{a,b,c}.py`.
9. **Leaf census:** `python3 scratchpad/wall-ies/leaf.py /home/fabrice/git/pycsl`.
10. **Drift oracle (names only):** `python3 bin/check-mirror-signature-drift.py` prints "0 / ratchet 0".
