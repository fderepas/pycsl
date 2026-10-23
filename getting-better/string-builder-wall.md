# W-SB — the string-builder value-model wall: census + routes

*State-of-the-art report for an independent reviewer. 2026-10-12, branch `ghost-assign-bc6`, HEAD
`11834d83`. Self-contained: every number below comes from a command in this document that was
actually run on this tree, and the instrument code is in Appendix A. Nothing under `src/` was
modified to produce it (the porting probes edit a mirror file and restore it after each
candidate; parallel runs used throw-away copies of `src/`, `bin/`, `config/`).*

**Short version.**
1. The string-builder constructs (`''.join`, list-of-str accumulation, f-string format specs,
   str-keyed dict constants, `.encode`, `%`) appear in **94** of the 435 `\trusted` mirror stubs
   (a further 126 use only the softer string forms). But a string-builder lowering is the **first**
   blocker for only **10** of those 94 (16 of the 435 overall). In those 94 stubs the in-place
   mutator refusal comes first more often (27) than W-SB does. W-SB is a widespread *co*-blocker,
   not the head of the queue.
2. A **soundness bug**, separate from the wall, turned up while measuring it. The live emitter
   drops f-string format specs and `!r`/`!s` conversions. As a result PyCSL reports
   `Verification SUCCESS! All contracts formally proven` for
   `f"{b:02x}" == f"{b}"` and for `f"{s!r}" == f"{s}"`, both of which are `False` in CPython (§3.5).
3. A faithful, axiom-free `join` model is feasible: 17/17 goals discharged by Z3+Alt-Ergo,
   including a char-by-char builder loop whose result is proven equal to its input (§4.3). The
   reference corpus emits **zero** `join_array`/`join_1`/`str_join_*` today, so a join route
   should not move the corpus byte-diff (§3.6).

---

## 1. Global picture

### 1.1 What PyCSL is
PyCSL is a deductive verifier for Python annotated with `#@` contracts (`requires`, `ensures`,
`assigns`, loop invariants/variants). Its pipeline runs Module 1 (ingest), Module 2 (parse
contracts), Module 3 (weave), Module 4 (semantic checks), Module 5 (JSON IR) and Module 6 (WhyML
emission, `src/pycsl/module6_whyml/`). Why3 1.8.2 then discharges the VCs with Alt-Ergo 2.6.3
and Z3 4.13.3. Commands below assume `. scratchpad/g29/env.sh`, which puts the opam
`framac-coq8` switch (why3, provers) on `PATH` and sets `PYTHONHASHSEED=0`. **This is
load-bearing:** without why3 on `PATH`, the L3 type check *silently reports success* (§6.4).

### 1.2 The mirror and the `\trusted` metric
The self-annotation campaign keeps a MIRROR of PyCSL's own source in `src/self-annotate/src/**`.
It has the same file layout as `src/pycsl/`, with `#@` contracts added. A mirror function is in
one of two states:
* **un-trusted**: a verbatim copy of the live function body plus annotations. PyCSL itself
  verifies it.
* **`\trusted`**: a `#@ \trusted` directive above a bodyless (or unverified) stub. Its contract
  is assumed, not proved. This is the trusted computing base (TCB) the campaign shrinks.

```
$ for f in $(find src/self-annotate/src -name '*.py'); do grep -cF '#@ \trusted' "$f"; done | paste -sd+ | bc
477                    # lines mentioning the marker (includes comments)
$ grep -rhE '^\s*#@\s*\\trusted\b' src/self-annotate/src --include='*.py' | wc -l
449                    # directive lines
```
The porting instrument (`bin/probe-conversion-candidates.py`, function `all_trusted`) finds
**435** stub *functions* behind those directives. It skips `__init__` and functions that are not
direct children of a class or module body. 411 of the 435 have a same-named live counterpart in
`src/pycsl/`; 23 do not (`NO-LIVE-SOURCE`); 1 (a nested helper `_e`) was not enumerated by the
probe. **The census unit below is these 435 stubs.**

### 1.3 Two coexisting value models
The mirror is emitted with two value models at once (backlog #62, `getting-better/driver-backlog.md`):
* **FAITHFUL**: `string`, `array τ`, `seq τ`, `pyval`, `term`, `emit_ir`, `map k (option v)`.
* **INT-ERASED**: every value is an `int`, and a string literal becomes its `stable_hash`
  constant (e.g. `"\""` becomes `210923450`).

A conversion fails when the function it retires sits **on the seam**: it hands a faithful value
to a consumer that still takes `int`, or the reverse. Backlog #62 (2026-09-26) measured that 102
of 116 type-error markers have exactly one `int` side (16 `string -> int`, 23 `int -> string`).
Backlog #64 then found the seam is a **chain per marker**: three seam repairs moved 11 markers and
lowered 0, because each had a second blocker behind the first.

### 1.4 The three oracle planes (lower bounds) and the ledger
| plane | command | what it pins |
|---|---|---|
| fidelity | `bin/check-self-annotate-sync.sh` | every un-trusted mirror function is byte-verbatim to the live one. **Measured now:** `OK: all 897 un-trusted … mirror functions … are verbatim copies of the live source; 37 class-level constants are subsets of live` (8.6 s) |
| proof | `.venv/bin/python3 src/pycsl/pycsl.py <mirror-file> --import-path src/pycsl` | the whole mirror file type-checks (L3-tc) and every VC is discharged |
| corpus inertness | `bin/byte-diff-sweep.sh <dir>` then `bin/byte-diff-compare.py` | an emitter change moves no corpus `.mlw` except the intended semantic correction. The compare step also flags REFUSED→EMITTED transitions as soundness losses |

**Axiom ledger:** the Rocq/Lean certificates under `src/formal-semantics/` must keep exactly **3**
axioms (`Print Assumptions` / `#print axioms`). Any new WhyML value shape must co-land with an
axiom-free soundness certificate (self-tcb-reduction SKILL §5 "coupling rule").

---

## 2. The wall as first seen (the spike)

The spike ported the live `whyml_string_literal` (`src/pycsl/module6_whyml/identifiers.py:202`)
into the mirror verbatim. The function **does not exist in the mirror today**, so this was a
coverage addition, not a `\trusted` conversion. Live source:

```python
_WHYML_STR_ESCAPES = {'\\': '\\\\', '"': '\\"', '\n': '\\n', '\r': '\\r', '\t': '\\t', '\b': '\\b'}

def whyml_string_literal(value: str) -> str:
    out: List[str] = []
    for ch in value:
        esc = _WHYML_STR_ESCAPES.get(ch)
        if esc is not None:
            out.append(esc)
        elif 32 <= ord(ch) <= 126:
            out.append(ch)
        else:
            for b in ch.encode("utf-8"):
                out.append(f"\\x{b:02x}")
    return '"' + ''.join(out) + '"'
```

Emitted WhyML (saved at `getting-better/composition-wall/spike-identifiers.mlw`; key lines):

```
  val _WHYML_STR_ESCAPES_get_1 (x0: int) : int
  val ch_encode_1 (x0: int) : array int
  val join_array (a: array int) : int
  val str_concat (x: int) (y: int) : int
  ...
    let out = ref Seq.empty in
      esc := (_WHYML_STR_ESCAPES_get_1 (str_hash_op !ch));               (1)
      if (not (!esc = pycsl_none)) then begin out := Seq.snoc !out !esc
      ...  out := Seq.snoc !out !ch                                      <- L3 TYPE ERROR (string into int seq)
          let _len_idx_b = (iter_length (ch_encode_1 1501791143)) in      (2)
            out := Seq.snoc !out (str_concat_op "\\x" (int_to_string !b)); (3)
    (str_concat (str_concat 210923450 (join_array !out)) 210923450)       (4)
```
1. A module-level `str -> str` dict constant read with `.get(ch)` and **no default** becomes an
   unconstrained `int -> int` val applied to `str_hash_op ch`. The dict's contents are gone.
2. `ch.encode("utf-8")` becomes `ch_encode_1 <hash of "utf-8">`. The receiver's *value* is not
   an argument (input-blind).
3. `f"\\x{b:02x}"` loses `:02x`. `int_to_string b` is *decimal*. This is unfaithful (see §3.5).
4. `'"' + ''.join(out) + '"'`: `join` returns `int`, which pulls the whole `+` chain into the
   int-model `str_concat` and hashes both quote literals.

---

## 3. CENSUS

### 3.1 Method
* **Static (A.1 `census.py`).** For each of the 435 stubs, take the *live* function's AST
  (nested defs included, as a port includes them) and count:
  * `J`: `X.join(arg)` (one argument, excluding `os.path.join`). `J.lit-sep` marks a literal
    separator; `J.over-comprehension` marks a generator or list-comprehension argument.
  * `B`: the builder pattern, a local that is both `.append`-ed to and passed to `.join`.
  * `F`: any f-string. `F.spec` = a `FormattedValue` with a format spec; `F.conv` = `!r`/`!s`/`!a`.
  * `D`: `.get` / `[k]` on a module-level dict literal with all-`str` keys in the same live
    module (`D.str2str` when all values are `str` too).
  * `E`: `.encode` / `.decode`.
  * `C`: `+` with a string literal or f-string operand.
  * `R`: `.replace` with 2 or more arguments.
  * `P`: `%` with a literal-string left operand, or `"...".format`.

  *SB-core* = J ∪ B ∪ F.spec ∪ D ∪ E ∪ P (the forms with no faithful lowering today).
  *SB-soft* = C, R, plain F (these already have a faithful `string` lowering when their operands
  are string-typed; §3.4).
* **Dynamic (A.2 `firsterr.py`).** For each stub, port the live body into the mirror
  *signature-preservingly*, using `probe-conversion-candidates.py`'s own `probe()` with its
  emit step replaced. Then run `pycsl.py <mirror> --import-path src/pycsl --no-proof --keep-mlw`
  and record the **first** Why3 error with its location, plus the emitted fragment
  (`characters a-b`) and line it points at. The mirror file is restored after every candidate.
  Runs were parallelised over 8 isolated copies of `src/`+`bin/`+`config/`, so no candidate saw
  another's port (the cross-file contamination of wall-lessons t6 cannot occur). The copies were
  `diff -rq`-verified identical to the real mirror afterwards.
* **Attribution (A.3 `classify.py`).** A first error counts as *at an SB lowering* if its
  fragment or line contains an SB lowering token: `join_array|join_1|str_join_*`, int-model
  `(str_concat `, `<x>_get_N (str_hash_op`, `_encode_N|bytes_N`, `str_mod_op`,
  `str_replace_op`. It also counts if the line is a `Seq.snoc` (list append) and the message is
  `string`↔`int` (the builder signature).

### 3.2 Whole-population first-blocker distribution (435 stubs, 434 probed)
```
L3TC-FAIL 394 = 229 located Why3 errors + 165 pipeline refusals
   refusals: in-place-mutator 77 · name-rebinding 9 · heterogeneous-list 5 · array-local-reassign 4 · other 70
   located : first error AT an SB lowering 16 · elsewhere 213
L3TC-OK   17   (type-checks; not "CLEAN" — the facade markers were not applied here)
NO-LIVE   23
```
Of the 229 located errors, **61** are `string`↔`int`. Only **11** of the 61 sit at an SB
lowering; the other 50 are seam errors at non-SB sites (27 in stubs that do contain SB
constructs, 23 in stubs that contain none).

### 3.3 Per-construct table (static use × measured first blocker)
| construct | stubs using it | occurrences | files | first error **at an SB lowering** | first error: other type error | first blocker: pipeline refusal | L3TC-OK |
|---|---|---|---|---|---|---|---|
| `J` `sep.join(...)` | **74** | 174 | 27 | 7 | 23 | 44 | 0 |
| ↳ over a comprehension | 31 | 64 | 15 | 2 | 9 | 20 | 0 |
| `B` append-then-join builder | **33** | 39 | 18 | 4 | 9 | 20 | 0 |
| `F.spec` f-string format spec | 4 | 4 | 3 | 1 | 2 | 1 | 0 |
| `F.conv` `!r`/`!s` | 13 | 22 | 6 | 2 | 5 | 3 | 3 |
| `D` str-keyed dict const `.get` | 5 | 6 | 5 | 1 | 0 | 4 | 0 |
| `D` str-keyed dict const `[k]` | 7 | 8 | 4 | 1 | 4 | 2 | 0 |
| ↳ `D.str2str` (`str→str`) | 1 | 1 | 1 | – | – | – | – |
| `E` `.encode`/`.decode` | 9 | 19 | 3 | 2 | 2 | 4 | 1 |
| `P` `%`-format | 17 | 60 | 7 | 1 | 3 | 13 | 0 |
| `P` `"...".format` | 2 | 3 | 1 | 0 | 2 | 0 | 0 |
| `R` `str.replace` | 26 | 63 | 13 | 4 | 9 | 13 | 0 |
| `C` literal `+` chain | 63 | 255 | 19 | 2 | 20 | 41 | 0 |
| `F` any f-string | 183 | 1393 | 36 | 10 | 89 | 80 | 4 |

Group view:
```
SB-core  (94 stubs): first error at SB lowering 10 · other type error 29 · in-place-mutator 27 ·
                     other refusal 21 · name-rebinding 4 · heterogeneous-list 2 · L3TC-OK 1
SB-soft only (126):  at SB lowering 6 · other type error 73 · other refusal 20 · in-place-mutator 18 ·
                     array-local-reassign 3 · heterogeneous-list 2 · L3TC-OK 4
trusted-reasons.tsv classes of the 94 SB-core: unclassified 61 · int-erasure-seam 14 · in-place-mutator 7 ·
                     nested-closure-lift 5 · context-manager 3 · name-rebinding 2 · faithful-string-hash 1 · heterogeneous-list 1
```
SB-core stubs by file: expressions.py 15, pure_ast.py 11, pycsl.py 8, statements.py 6,
Module6_WhyMLTranspiler.py 4, audit_proof_reverify.py 4, Module3_Weaver.py 4, functions.py 4,
preamble.py 4, audit_proof.py 3, Module5_IREmitter.py 3, extract.py 3, and 20 more files with ≤2 each.

**The 16 stubs whose first error is at an SB lowering.** "F" = the error *fragment* itself is
the SB lowering (8); "L" = the SB lowering is on the error line but the fragment is something
else (8).
| | stub | family | first error |
|---|---|---|---|
| F | `module6_whyml/identifiers.py::whyml_ident` | builder | `sanitized := Seq.snoc !sanitized (… (str_concat_op "u" (int_to_string (ord_op !ch))))`: string into an int seq |
| F | `proof2why3/canonical.py::_normalize_type_string` | builder | `out_parts := Seq.snoc !out_parts (_camel_to_snake !token)` |
| F | `proof2why3/crosscheck.py::CrossCheckResult.diagnostic` | builder | `lines := Seq.snoc !lines (str_concat_op …)` string into an int seq |
| F | `module6_whyml/preamble.py::PreambleEmissionMixin._emit_class_inv_axioms` | builder + int-concat | `out := Seq.snoc !out (str_concat (… 1286055330 !qn) …)` |
| F | `proof2why3/from_lean_json.py::project_to_ir` | int-concat | `reason = (str_concat 1199451630 (py_type_1 ast))`: int where a string field is expected |
| F | `proof2why3/canonical.py::substitute` | get (a **param** dict, not a constant) | `mapping_get_2 (str_hash_op …)` int where string expected |
| F | `frontend/desugar.py::_ChainDesugarer.visit_Compare` | `%` | `tmp := (str_mod_op "_pycsl_cmp_%d" …)`: string into an int-erased local |
| F | `pycsl.py::_synthesize_legacy_text` | join | `(join_1 0)`: iterable erased to `0`, int where string expected |
| L | `pycsl.py::_parse_goal_blocks` | join | `header := (join_1 !cur_header)`: `seq` where int expected |
| L | `audit_proof_reverify.py::_cache_key` | join | `_alit[1] <- (join_1 (sorted_1 qualnames))` with `qualnames: array string` |
| L | `pycsl.py::_synthesize_block` | join | `join_array (… (Array.make 1024 0))` |
| L | `proof2why3/normalize.py::normalize_prover_output` | replace | `out := (str_replace_op !out u a)`, loop target `u` int-erased |
| L | `proof2why3/parser.py::normalize_surface` | replace | same shape |
| L | `frontend/pure_ast.py::_Tok.__repr__` | int-concat | a tuple field inside an int `str_concat` chain |
| L | `frontend/pure_ast.py::literal_eval` | int-concat | `msg := !msg + (str_concat 544907596 !lno)` |
| L | `frontend/pure_ast.py::_decode_string` | encode | real error: `unbound … 'body'` (not SB) |

**"Only blocker" is not measured and cannot be measured with this instrument.** Only the first
error is observable without building the capability. Backlog #64's measurement (0 of 11 moved
markers lowered) is the best available prior that a single SB capability retires few markers
outright.

### 3.4 Current lowering of each construct (tiny probes, `--no-proof --keep-mlw`)
Probe sources are in `scratchpad/…/wsb/p_*.py` and are reproduced here.
| Python | emitted WhyML | L3-tc | verdict |
|---|---|---|---|
| `''.join(xs)`, `xs: List[str]` | `(join_array xs)` with `val join_array (a: array int) : int` | ✗ `array string` vs `array int` | type error; **separator dropped** (`", ".join(xs)` emits the *same* term) |
| `"a" + s + "b"`, `s: str` | `(str_concat_op (str_concat_op "a" s) "b")` with `ensures { result = concat a b }` | ✓ | **faithful**: literals stay strings when the operands are string-typed |
| `ESC.get(c)`, `ESC: Dict[str,str]` module const | `(eSC_get_1 (str_hash_op c))` with `val eSC_get_1 (x0: int) : int` | ✗ `int` vs `_union_f_0` | contents lost, unconstrained |
| `ESC.get(c, c)` / `c in ESC` | `(if (str_eq_op c "\\") then "\\\\" else (if … else c))` | ✓ | **faithful** (`expressions.py:11953` module-const-dict-get; its comment says "`.get(k)` without a default … is out of scope … fail-closed") |
| `f"{b:02x}"`, `b: int` | `(int_to_string b)` | ✓ | **spec silently dropped** |
| `f"x{b}y"` | `(str_concat_op (str_concat_op "x" (int_to_string b)) "y")` | ✓ | faithful shape, opaque `int_to_string` |
| `s.replace("a","b")` | `(str_replace_op s "a" "b")` (partial spec: length law + no-occurrence ⇒ identity) | ✓ | typed |
| `"%d items" % n` | `(str_mod_op "%d items" n)` with `val str_mod_op (s: string) (x: 'a) : string` | ✓ | typed, opaque |
| `s.encode("utf-8")` | `(s_encode_1 1501791143)`, `val s_encode_1 (x0: int) : array int` | ✓ | **input-blind** (receiver not an argument; the only argument is the hash of `"utf-8"`) |
| builder: `out.append(ch)` … `'"' + ''.join(out) + '"'` | `out := Seq.snoc !out !ch` … `(str_concat (str_concat 210923450 (join_array !out)) 210923450)` | ✗ `seq string` vs `array int` | the spike's shape exactly |

A faithful-typed join already exists, but it is gated. `_handle_join_call`
(`expressions.py:6778`) lowers to `str_join_arr`/`str_join_seq (sep) (xs) : string` only when
`_join_arg_elem_is_string` is true. That map is populated **only under `@mutable_state`**
("@mutable_state only (the map is empty elsewhere)", `expressions.py:6893`), or by two
method-name-gated special cases (`_build_param_list`, `_refine_str_comp_locals`). Even then the
contract is `String.length result >= 0` only. A literal-list `sep.join([a, b])` is exact
(nested `str_concat_op`, faithful-string-op §3.5).

### 3.5 Side finding — the format-spec / conversion drop is UNSOUND (live emitter)
`Module5_IREmitter._py_expr_fstring` (`src/pycsl/frontend/Module5_IREmitter.py:1645`) keeps only
`v.value` of each `ast.FormattedValue` and discards `format_spec` and `conversion`. Module 6's
int-model f-string joiner maps an int part to the deterministic `val function str_of_int_hash`.
So two f-strings that differ only in spec or conversion get *the same term*:

```
$ cat p_unsound_fmt3.py
#@ ensures \result == True
def hex_equals_plain(b: int) -> bool:
    return f"{b:02x}" == f"{b}"
$ .venv/bin/python3 src/pycsl/pycsl.py p_unsound_fmt3.py --import-path src/pycsl
Prover result is: Valid (0.01s, 5 steps).
[+] Verification SUCCESS! All contracts formally proven.
$ python3 p_unsound_fmt3.py          # main: print(hex_equals_plain(10))
False
```
emitted: `(if ((str_of_int_hash b) = (str_of_int_hash b)) then 1 else 0)`.

```
#@ ensures \result == True
def repr_equals_plain(s: str) -> bool:
    return f"{s!r}" == f"{s}"
→ (if (str_eq_op s s) then 1 else 0)   ·  [+] Verification SUCCESS! All contracts formally proven.
→ CPython: repr_equals_plain("a") is False
```
`f"{10:02x}"` emits `(int_to_string 10)`. `ensures \result == "0a"` is *not* proven (Unknown), so
the defect shows only through equalities between two dropped forms. That is still a false
contract proved. Corpus exposure: **0** corpus files use a format spec or a conversion (static
census, §3.6). The route #203 f-string witnesses `1705`/`1706` are the nearest byte-diff
sentinels.

Checked and **not** unsound, only incomplete:
* `s.encode(..)` lowers to a plain (non-`function`) `val`, so two calls are not provably equal.
  A probe asserting `len(u.encode()) == len((u+"x").encode())` did not prove.
* `join_array` and the dict `_get_1` fail at L3-tc in comparison contexts (fail-closed).
* `f"{b:02x}" == str(b)` stays Unknown: `str(b)` lowers to `str_hash_op (str_of_int b)`,
  which is not the same symbol.

### 3.6 Corpus usage and current corpus lowering
Static census (same detector, whole files):
```
pycsl-reference (1850 .py): F 36 occ/20 files · C 13/12 · E 11/7 · D.get 8/7 (D.str2str 6/5) · J 8/4
                            (0958–0961 only) · R 4/2 · P.format 1/1 · D[k] 1/1 · B 0 · F.spec 0 · F.conv 0 · P% 0
python-reference (2217 .py): J 5/4 (stdlib str_methods join_*, multiprocessing join_call_*) · E 8/4 ·
                            R 2/2 · F 2/2 · C 1/1
```
Corpus baseline emission (`bin/byte-diff-sweep.sh` into scratch, 8m26s: **1394 of 1850**
pycsl-reference and **2199 of 2217** python-reference files emitted) and token census of the
emitted `.mlw`:
| token | pycsl-ref files | python-ref files |
|---|---|---|
| `join_array` / `join_1` / `str_join_arr` / `str_join_seq` | **0 / 0 / 0 / 0** | **0 / 0 / 0 / 0** |
| `__joinstr` (the term-pp recognizer's own `let rec` join over `list string`) | 4 (0958–0961) | 0 |
| int-model `(str_concat ` | 1 (`0450`) | 1 (`pyref__0075`) |
| `str_concat_op` | 16 | 3 |
| `str_mod_op` / `str_of_int_hash` | 1 (`0484`) / 2 (`1705`,`1706`) | 0 |
| `<x>_encode_N` | 0 | 8 (base64/codecs/json `encode_call_*`) |
| `<x>_get_N (str_hash_op` | 0 | 0 |
| `str_replace_op` | 2 | 2 |

Precedent worth noting: corpus `0958_term_string_pp` already emits a **faithful, total,
axiom-free join** (`let rec pp__joinstr (sep: string) (l: list string) : string … variant { l }`,
from `generic_fold.py:36238`). It also emits a faithful `str→int` dict constant as an if-chain
(`pp__binop_prec_OPPREC`). Both shapes exist, but only inside one recognizer.

---

## 4. Deeper truth: fundamental, or a modeling choice?

**A modeling choice, not a logical limit.** Every W-SB construct has a total, first-order
definition over Why3's standard `string` and `seq` theories. The wall exists because the
*element type of a Python list* is not carried into Module 6 outside `@mutable_state`. A
`List[str]` local, param or loop target therefore defaults to the int-erased element. Every
consumer downstream (`join`, the `+` chain, the f-string joiner) then picks its int-model variant.

### 4.1 What Why3 1.8.2's stdlib offers (`why3 --print-datadir`/`stdlib/string.mlw`)
* `module String`: `concat`, `length`, `lt`/`le`, `s_at`, `substring`,
  `prefixof`/`suffixof`/`contains`, `indexof`, `replace` (first occurrence), `replaceall`,
  `to_int`, `from_int` (decimal).
* `module Char`: `code`, `chr`, `get`, `make`, `eq_string`.
* `module OCaml` and `module StringBuffer` (extraction-oriented, `int63`).
* `module RegExpr`.
* `seq.Seq`: `empty`, `snoc`, `[]`, `length`, `++`.

There is **no `join`** and **no printf-style formatting**. Both are definable: `join` as a
recursive ghost function, and hex formatting as a recursive digit function.

### 4.2 What PyCSL already declares (Module 6 inventory, `grep -ohE '"\s*val …' src/pycsl/module6_whyml/*.py`)
* Faithful, with a definitional contract: `str_concat_op` (`result = concat a b`, length law),
  `str_sub_op` (`= substring`), `str_length_op` (`= length`), `str_eq_op`/`pystr_eq`,
  `str_lt_op`/`str_le_op`, `str_contains_op`, `str_startswith_op`/`str_endswith_op`,
  `str_find_op`, `str_split_op`, `str_split_elem_op`, `str_repeat_op`, `str_strip_op` (length bound).
* Typed but opaque: `str_join_arr`/`str_join_seq` (`length >= 0` only), `str_replace_op`
  (partial), `str_mod_op`, `int_to_string`, `str_of_int`, `str_repr_op`.
* Int model: `str_hash_op : string -> int`, `str_concat : int -> int -> int`,
  `join_array : array int -> int`, `join_1 : int -> int`, `str_of_int_hash : int -> int`
  (`val function`).

`preamble.py` itself only controls `use string.String`/`string.Char`/`seq.Seq` and `pystr_eq`.
The string ops are registered on demand through `_add_abstract_op` in `expressions.py`/`functions.py`.

### 4.3 Gate-B-style feasibility: a faithful join is axiom-free and SMT-tractable
File `scratchpad/…/wsb/join_feasibility.mlw` (full text):
```why3
module JoinModel
  use int.Int
  use string.String
  use seq.Seq
  use ref.Ref
  let rec ghost function join_from (sep: string) (xs: seq string) (i: int) : string
    variant { length xs - i }
  = if i < 0 || i >= length xs then ""
    else if i = length xs - 1 then xs[i]
    else concat xs[i] (concat sep (join_from sep xs (i + 1)))
  function join (sep: string) (xs: seq string) : string = join_from sep xs 0
  val str_join_seq (sep: string) (xs: seq string) : string
    ensures { result = join sep xs }
  val str_length_op (s: string) : int
    ensures { result = String.length s }
  val str_sub_op (s: string) (lo len: int) : string
    ensures { result = substring s lo len }
  goal join_two: join "," (snoc (snoc empty "a") "b") = "a,b"
  goal join_empty_sep_lit: join "" (snoc (snoc (snoc empty "x") "y") "z") = "xyz"
  let rec lemma join_empty_snoc_from (xs: seq string) (x: string) (i: int)
    requires { 0 <= i <= length xs }
    variant { length xs - i }
    ensures { join_from "" (snoc xs x) i = concat (join_from "" xs i) x }
  = if i < length xs - 1 then join_empty_snoc_from xs x (i + 1)
  lemma join_empty_snoc: forall xs: seq string, x: string.
    join "" (snoc xs x) = concat (join "" xs) x
  lemma substring_extend: forall s: string, i: int.
    0 <= i < String.length s ->
    substring s 0 (i + 1) = concat (substring s 0 i) (substring s i 1)
  lemma substring_whole: forall s: string. substring s 0 (String.length s) = s
  let copy (value: string) : string            (* the W-SB builder shape *)
    ensures { result = value }
  = let out = ref (empty: seq string) in
    let i = ref 0 in
    while !i < str_length_op value do
      invariant { 0 <= !i <= String.length value }
      invariant { join "" !out = substring value 0 !i }
      variant { String.length value - !i }
      out := snoc !out (str_sub_op value !i 1);
      i := !i + 1
    done;
    assert { !i = String.length value };
    assert { join "" !out = value };
    str_join_seq "" !out
end
```
Result: `why3 prove -a split_vc -P z3 -t 20` gives **16 Valid, 1 Timeout**. The timeout is
`substring_extend`, which `why3 prove -P alt-ergo -t 90 -T JoinModel -G substring_extend` proves
in **Valid (1.70s)**. So under PyCSL's Z3+Alt-Ergo portfolio, 17/17 goals are discharged, with
no `axiom`. (Z3 alone times out on `substring_extend` even at 90 s.)

Caveats:
* The `val`s with definitional `ensures` are trust points of the same status as today's
  `str_concat_op`. They are consistent because the ghost function realises them.
* First attempts failed in instructive ways. A non-ghost `let rec function` was rejected
  ("Logical symbol concat is used in a non-ghost context"), as was `String.length` in program
  code. Without the two substring lemmas, the loop invariant and the postcondition time out on
  Z3. Expect the emitter to need the ghost/val split and a small lemma prelude.

---

## 5. Routes, honestly costed

Payoff = stubs in the census whose **first** blocker the route addresses. Static reach (stubs
using the construct) is an upper bound on eventual relevance, not on retirements (#64: expect a
chain per marker). Corpus risk is under the M1 byte-diff discipline: a corpus diff is allowed
only if it is exactly the intended semantic correction **and** every affected program still proves.

| # | route | static reach | first-blocker payoff | corpus risk | cost |
|---|---|---|---|---|---|
| **D** | **Carry `format_spec`/`conversion` through the IR** (Module 5 `_py_expr_fstring`). Then lower a spec'd or converted part to an opaque **spec-keyed** `val function str_fmt (spec: string) (x: 'a) : string` (or `str_repr_op` for `!r`), or refuse it. | F.spec 4 + F.conv 13 stubs | 1 (+2 conv) | **0 corpus files** use a spec or conversion, so it should be byte-inert. Sentinels: `1705`/`1706` (route #203), `bin/check-fstring-lowering.py` (its return-set pin will need a justification row) | small: one IR field + one Module 6 branch + a corpus pair (the two §3.5 witnesses must stop proving; `f"{b}" == f"{b}"` must still prove) |
| **A** | **Faithful list-of-str + join.** (i) Populate `_array_elem_types`/`_seq_value_types` from declared `List[str]` annotations on locals, params and loop targets, not only under `@mutable_state`, so `.append` builds `seq string`. (ii) Strengthen `str_join_seq`/`str_join_arr` to `ensures { result = join sep xs }` over a ghost `join_from` (§4.3). (iii) Keep the separator. | J 74 · B 33 · J-over-comprehension 31 | 8 of the 16 attribute to join/builder (builder: whyml_ident, _normalize_type_string, CrossCheckResult.diagnostic, _emit_class_inv_axioms; join: _synthesize_block, _synthesize_legacy_text, _parse_goal_blocks, _cache_key). Per-construct column: 7 join-using + 4 builder-using stubs have an SB first error | **0 corpus files** emit `join_array`/`join_1`/`str_join_*`. The 4 `__joinstr` files use a separate recognizer. Python-ref join tests use literal lists (the `str_concat_op` path). Main risk is (i): element types newly known for `List[str]` *non-join* uses (`len`, indexing, `in`) could re-type other corpus emissions. Gate it on "consumer is a join/`+`/return-string" first, then widen with the sweep | medium. Prior art: the `pp__joinstr` recognizer and the mutable_state path. Needs the ghost/val split and a lemma prelude (`substring_extend` needs Alt-Ergo) |
| **B** | **Keep literals as strings in `+` chains** when any operand is string-typed. | C 63 | 2 | `0450`, `pyref__0075` emit int `str_concat` today (sentinels) | **mostly already done**: `"a" + s + "b"` is faithful (§3.4). The residual int `str_concat` appears only when an operand is int-erased (a `join` result, a `getattr`, a tuple field), so B is **subsumed by A + upstream seam work**. Do not build it standalone |
| **C** | **`str→str` dict constant with `.get(k)` (no default)** → `option string` if-chain, or `None` mapped to the existing None encoding. Extends `expressions.py:11953`, which already does `.get(k, d)` and `in`. | D.get 5 (D.str2str 1) | 1 (and that one, `canonical.substitute`, is a *param* dict, so 0 truly) | `<x>_get_N (str_hash_op` appears in **0** corpus emissions, so it should be inert. Route-132 corpus files (0872/0873/1369/1370/1373) use the 2-arg form; sentinels | small. **Low stub payoff**; its value is for not-yet-mirrored code like `whyml_string_literal` |
| **E** | **`.encode("utf-8")` as an input-carrying op** `str_encode_utf8 (s: string) : seq int` (at least `length s <= length result`, ASCII identity optional). | E 9 | 2 | python-ref `encode_call_*` (8 files) emit `<x>_encode_1`. **Not byte-inert**; each must still prove | small-medium |
| **P** | `%`-format / `.format` as spec-keyed typed opaques. | P% 17 · .format 2 | 1 | `0484` emits `str_mod_op` | **already typed** (`str_mod_op : string -> 'a -> string`). Its one first blocker is the *consumer* (an int-erased local), a seam issue, not a P issue |

**Recommended order.**
1. **D first**, as a soundness fix. Its stub payoff is ~1, but it closes a proved-false-contract
   route in the *live* tool, and it is corpus-inert by measurement.
2. **A next**: the only W-SB route with double-digit reach (74 join / 33 builder stubs) and a
   proven-feasible axiom-free model. Run it as a **chain probe on one marker**
   (`identifiers.whyml_ident`: builder first, then whatever is next), per #64, not as a class
   sweep. Measure "moved / lowered" with A.2 before and after.
3. C, E and P are cheap, but each retires ≤ 2 first blockers. Schedule them only when a chain
   probe from step 2 reaches them.

Expected net effect on the `\trusted` count from W-SB alone: **small**. The census says W-SB is
first in 16 of 435. For the 94 SB-core stubs, the in-place-mutator refusal (27) plus other
refusals (27) come first more often than W-SB does (10). Mirror-level marker retirement needs W-SB
**together with** the in-place mutator model and the general int-erasure seam (§3.2: 50 of the
61 `string`↔`int` first errors are at non-SB sites).

---

## 6. Honest limits

1. **First blocker only.** "Only blocker" is unmeasured. Retiring a first blocker may expose a
   second (backlog #64: 11 moved, 0 lowered).
2. **Attribution is lexical.** A.3 matches lowering tokens on the error line. "L" rows (8 of 16)
   include cases where the SB token is on the line but the fragment is another erasure
   (`_decode_string`'s real error is an unbound `body`). The `dict-get` rule also matched a
   *parameter* dict (`canonical.substitute`), not a constant.
3. **The static detector is syntactic.**
   * `D` only sees dict literals defined at module level *in the same live module*, so imported
     constants are missed.
   * `B` requires the same local to be appended and joined by name.
   * `J` excludes only `os.path`/`path`/`Path` receivers, so a non-str `.join` (e.g. a thread
     `.join()` with one argument) would be miscounted. None was observed in the stub lists.
4. **Instrument hazard (fail-open), measured.** With why3 not on `PATH`,
   `pycsl.py --no-proof` prints `[level] L1 ✓ L2 ✓ L3-tc ✓` and
   `Verification SUCCESS (… type-checks [L3-tc ✓] …)` for `p_join.py`, which does **not**
   type-check:
   `env -i HOME=$HOME PATH=/usr/bin:/bin .venv/bin/python3 src/pycsl/pycsl.py p_join.py --import-path src/pycsl --no-proof`.
   My first harness run hit this: it reported `whyml_ident` as L3TC-OK. Every number in this
   report was taken with `. scratchpad/g29/env.sh` in effect. `probe-conversion-candidates.py`
   sets `PATH` itself and is not affected.
5. **The corpus sweep emitted 1394 of 1850** pycsl-reference files (the rest are refusals or
   flagged files, per the sweep's normal behaviour). Token counts in §3.6 cover only emitted files.
6. **The feasibility file (§4.3) is hand-written WhyML**, not emitter output. It shows the model
   is expressible and dischargeable, not that the emitter produces it or that real mirror bodies
   (with their other erasures) will prove.
7. Snapshot: HEAD `11834d83`. `trusted-type-error-causes.tsv` (116 rows, 2026-09-28) is an
   earlier, differently scoped instrument (TYPE rows only), so its counts are not directly
   comparable to §3.2's 229 located first errors.

---

## Appendix A — instruments (verbatim logic; scratch copies under `$SCRATCH/wsb/`)

Reproduce:
```
. scratchpad/g29/env.sh
python3 census.py stubs stubs.json                        # §3.3 static columns
python3 census.py corpus 'test-suite/corpus/pycsl-reference/*.py'          # §3.6
python3 census.py corpus 'test-suite/corpus/python-reference/**/*.py'
WSB_ROOT=<copy-of-repo-subset> .venv/bin/python3 firsterr.py out.jsonl <mirror files…>   # §3.2
python3 classify.py v ; python3 xtab.py                   # §3.2/§3.3 dynamic columns
bin/byte-diff-sweep.sh <dir>; grep -lE '<token>' <dir>/*.mlw <dir>/pyref/*.mlw | wc -l   # §3.6 table
```
Wall-clock: pure_ast.py alone (58 stubs) took 8m19s serially (~8.6 s/stub). The other 376 ran
in 8 parallel isolated roots.

### A.1 `census.py` — construct detector (core)
```python
def is_str_const(n): return isinstance(n, ast.Constant) and isinstance(n.value, str)
def module_str_dicts(tree):   # module-level NAME = {str: ...}
    out = {}
    for st in tree.body:
        tgt = val = None
        if isinstance(st, ast.Assign) and len(st.targets) == 1 and isinstance(st.targets[0], ast.Name): tgt, val = st.targets[0].id, st.value
        elif isinstance(st, ast.AnnAssign) and isinstance(st.target, ast.Name): tgt, val = st.target.id, st.value
        if tgt and isinstance(val, ast.Dict) and val.keys and all(k is not None and is_str_const(k) for k in val.keys):
            out[tgt] = 'str2str' if all(is_str_const(v) for v in val.values) else 'str2any'
    return out
def constructs(fn, strdicts):
    c = {}; add = lambda k: c.__setitem__(k, c.get(k, 0) + 1); joined = set(); appended = set()
    for n in ast.walk(fn):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
            a, r = n.func.attr, n.func.value
            if a == "join" and len(n.args) == 1 and not (isinstance(r, ast.Attribute) and r.attr == "path") \
               and not (isinstance(r, ast.Name) and r.id in ("os", "posixpath", "path", "Path")):
                add("J:str.join"); arg = n.args[0]
                if is_str_const(r): add("J.lit-sep")
                if isinstance(arg, ast.Name): joined.add(arg.id)
                if isinstance(arg, (ast.GeneratorExp, ast.ListComp)): add("J.over-comprehension")
            if a == "append" and isinstance(r, ast.Name): appended.add(r.id)
            if a in ("encode", "decode"): add("E:encode/decode")
            if a == "replace" and len(n.args) >= 2: add("R:str.replace")
            if a == "format" and is_str_const(r): add("P:str.format")
            if a == "get" and isinstance(r, ast.Name) and r.id in strdicts:
                add("D:dictconst.get"); strdicts[r.id] == 'str2str' and add("D.str2str")
        if isinstance(n, ast.Subscript) and isinstance(n.value, ast.Name) and n.value.id in strdicts and isinstance(n.ctx, ast.Load): add("D:dictconst[k]")
        if isinstance(n, ast.JoinedStr):
            add("F:fstring")
            for v in n.values:
                if isinstance(v, ast.FormattedValue):
                    if v.format_spec is not None: add("F.spec")
                    if v.conversion not in (-1, None): add("F.conv(!r/!s)")
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add) and (is_str_const(n.left) or is_str_const(n.right)
               or isinstance(n.left, ast.JoinedStr) or isinstance(n.right, ast.JoinedStr)): add("C:lit+concat")
        if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Mod) and is_str_const(n.left): add("P:%-format")
    if joined & appended: c["B:append-then-join builder"] = len(joined & appended)
    return c
# stubs: for each mirror file, pcc.all_trusted(mirror) -> (cls, name); live fn via pcc._find_live_fn
```

### A.2 `firsterr.py` — first-error harness (core)
It imports `bin/probe-conversion-candidates.py` as `pcc` and replaces `pcc._probe_emit` so that
the probe's own signature-preserving port is used unchanged:
```python
def emit(name, cls, orig, new, note):
    try:
        open(pcc.MIRROR, "w").write(new)
        r = subprocess.run([VENV_PY, ROOT + "/src/pycsl/pycsl.py", pcc.MIRROR, "--import-path", ROOT + "/src/pycsl",
                            "--no-proof", "--keep-mlw"], capture_output=True, text=True, cwd=ROOT, timeout=400,
                           env=dict(os.environ, PYTHONHASHSEED="0"))
        txt = r.stdout + "\n" + r.stderr
        rec["l3tc_ok"] = "L3-tc ✓" in r.stdout
        m = re.search(r'File "([^"]+\.mlw)", line (\d+), characters (\d+)-(\d+):\n((?:.*\n){1,3})', txt)
        if m:   # record the emitted fragment + line the first why3 error points at
            ln = open(m.group(1)).read().split("\n")[int(m.group(2)) - 1]
            rec["frag"] = ln[int(m.group(3)):int(m.group(4))]; rec["line"] = ln.strip(); rec["msg"] = m.group(5)
        elif not rec["l3tc_ok"]:   # pipeline refusal: line after "[!] PIPELINE ERROR"
            ...
        return name, "X", []
    finally:
        open(pcc.MIRROR, "w").write(orig)            # restore after EVERY candidate
        if os.path.exists(pcc.MLW): os.remove(pcc.MLW)
```

### A.3 `classify.py` — attribution rules
```python
RULES = [("join", r"\bjoin_array\b|\bjoin_1\b|\bstr_join_(arr|seq)\b"), ("int-concat", r"\(str_concat "),
         ("dict-get", r"\b\w+_get_\d+ \(str_hash_op"), ("encode", r"_encode_\d+|\bbytes_\d+ "),
         ("pct-format", r"\bstr_mod_op\b"), ("replace", r"\bstr_replace_op\b")]
builder = re.search(r"Seq\.snoc|Seq\.\(\+\+\)", line) and "string" in msg and "int" in msg
# "F" = a rule matches the fragment (or builder); "L" = a rule matches the line only
```
