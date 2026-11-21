# Independent review of `int-erasure-seam-r3.md`

*Reviewer run 2026-10-26, 08:51–09:15 UTC, against `ghost-assign-bc6` HEAD `deb39c0b0`.
`git diff --stat afcadd6f6..HEAD -- src/pycsl src/self-annotate bin` is empty, so every emitter
line the report cites was checked against the same code it measured. All spikes, probes and
outputs are under `scratchpad/wall-ies-review/` (nothing under `src/` or `bin/` was edited). Every
`why3` and `pycsl.py` run went through `scratchpad/heavy/heavy.sh`, one at a time.*

---

## 0. Verdict in one paragraph

The report's measurements hold: every number and line I re-ran or re-read reproduces (§1). Its
central diagnosis — the emitter commits to a type at every **consumer**, and defaults to `int`
when it has none, so annotations fix consumers and polymorphism fixes producers but neither
closes a chain — is correct, and I can sharpen it with three oracle facts the report did not
have: (i) WhyML has **no polymorphic program equality at all** (`(=)` in program code is a
monomorphic `val` per theory: `int.Int:16`, `string.OCaml:487`), so route R3's residual `=`
failures are structural, not an emitter "choice"; (ii) route #325 taints only a `val` whose
return type is literally `int` (`pycsl.py:13611`), so an R3 `: 'a` result **silently regains int
theory** (`t1_poly_regains_int.mlw`, rc 0); (iii) the typed `str`-method path the emitter already
has (`str_strip_op`, `str_eq_op`, `str_split_op`) **passes the receiver** with no `writes`, so the
report's claim that R5 needs the in-place-mutator capability is over-scoped. My recommendation is
therefore not R3 and not R4 now, but a narrow carve-out of R5+R2 that I call **R5-str**: un-gate
and extend the existing monomorphic, receiver-passing `str`-method models, and extend the
`_is_string_expr` consumer typing to element reads and `for` targets of `array string` locals.
It adds no axiom (the ledger stays at 3), no new value shape, no polymorphism, and its corpus
footprint is measured at ≤ 20 files per family. The make-or-break spike for it (§4) is already
written and type-checks; its Alt-Ergo outcome is in §4.2.

---

## 1. Claims checked against the oracle

Legend: **C** confirmed as stated; **C+** confirmed and sharpened; **R** refuted or over-scoped;
**Q** quoted correctly from the cited file (not re-measured).

| # | report claim (§) | status | artifact / command and key output |
|---|---|---|---|
| 1 | 446 `#@ \trusted` lines (§1.2) | **C** | `grep -rhF '#@ \trusted' src/self-annotate/src --include=*.py \| wc -l` → `446` |
| 2 | sigdrift 252 identical / 142 differ / 24 no-live; 100 `int` placeholders; live quality 150/135/99/12 (§3.4) | **C** | `python3 scratchpad/wall-ies/sigdrift.py /home/fabrice/git/pycsl` → `{'identical': 252, 'differ': 142, 'no-live-or-mirror': 24}`, `{'int placeholder where live is typed': 100}`, `{'stubs': 394, … 'live fully precisely annotated': 150, …Any: 135, unannotated: 99, bare: 12}` |
| 3 | leaf census 184 / 210 / 24 (§3.8) | **C** | `python3 scratchpad/wall-ies/leaf.py …` → `{'leaf w.r.t. trusted stubs': 184, 'calls >=1 other trusted stub (name match)': 210, 'no live': 24}` |
| 4 | drift oracle compares names only, prints "0 / ratchet 0 over 1265 pairs" (§3.4) | **C** | `python3 bin/check-mirror-signature-drift.py` → `… over 1265 mirror/live signature pair(s) … OK (0 / ratchet 0, 0 converted)` |
| 5 | every `file:line` in the §4 erasure table | **C** | `sed -n` on each: `functions.py:174/212/264/11690/11705/11716`, `expressions.py:1156-1157/7774-7775/8088-8090/10618/10836/14566-14568/22056/22270-22292/22431`, `statements.py:8968/9044-9045`, `ir_scanner.py:799-812` (incl. the odd `String` return → `"int"` at `:800-801`), `Module5_IREmitter.py:2871-2872/5307-5309/6160-6161/6339-6340`, `preamble.py:4326-4335`, `pycsl.py:13482-13503`. All match the quoted lowering. |
| 6 | `poly.mlw` fails with the mutable-instantiation message (§3.7, §11.7) | **C** | `heavy.sh why3 prove --type-only scratchpad/wall-ies/why3py/poly.mlw` → `line 16, characters 21-40: This application instantiates pure type variable 'a with a mutable type array` |
| 7 | `poly-seam-spike.mlw` proves with Alt-Ergo (§3.7) | **C** | `heavy.sh why3 prove -P alt-ergo poly-seam-spike.mlw` → `split_like'vc … Valid (0.03s, 14 steps)`, `split_arr'vc … Valid (0.03s, 14 steps)`, rc 0 (`ident_like` emits no goal) |
| 8 | `poly3.mlw`, `poly4.mlw` type-check (§3.7) | **C** | both `--type-only` rc 0 |
| 9 | §3.7 residual: "the emitter chose **int `=`**" for `(strip_1 …) = !qn` | **C+** | `scratchpad/wall-ies-review/eq1.mlw` (`use int.Int`, `a = b` on strings) → `expected to have type int`; `eq2.mlw` (no `int.Int`) → `Logical symbol (=) is used in a non-ghost context`; `eq3.mlw` (`String.(=)`) → same. Stdlib: `int.mlw:16 val (=) (x y: int)`, `string.mlw:487` (module `OCaml`) `val (=) (x y: string)`. **There is no polymorphic program `=` in WhyML.** R3 cannot leave `=` to unification; it must emit a type-directed equality op. The emitter already does this for known strings (`str_eq_op`, `expressions.py:12402`) and, when one side is `int`, hashes the string side: probe `q1a` line 27 `(strip_1 (!lines)[!i]) = (str_hash_op qn)`. |
| 10 | §3.5: an annotation fixes the consumer, never the producer | **C+** | user-level probe `q1a_split_typed.py` (`lines: List[str] = stdout.split("\n")` on a **`str` parameter**): emitted `val stdout_split_1 (x0: int) : int`, `let lines = ref (stdout_split_1 1470490902)`, consumer `Array.length (!lines)`; clash `int ⇒ array`. Sharpening: even a fully typed `str` receiver does not reach `str_split_op`, because the whole-list `.split` model is gated on `self._current_self_type in self._mutable_state_classes` (`expressions.py:10027-10031`), not on the receiver's type. Probe `q2_ms_split_chain.py` (same body inside a `@mutable_state` class) gets `let lines = ref (snapshot (str_split_op stdout "\n"))`. |
| 11 | stub 3's `int` originates at the receiver-less `stdout_splitlines_0 ()` (§3.2 row 3) | **C+** | `out/proof2why3_extract.py::_split_rocq_check_output.mlw:26 val stdout_splitlines_0 () : int`, body `lines := (stdout_splitlines_0 ());` while the parameter is `(stdout: string)`. Sharpening: the row also lists `.strip()` as an origin, but `str.strip` **has** a faithful model (`expressions.py:3659-3664`, `val str_strip_op (s: string) : string`) that fires whenever `_is_string_expr(receiver)` holds (`:3450-3459`); `strip_1 (x0: int)` is a downstream consequence of `lines` being erased, not a second origin. Probe `q3a_strip_eq.py` (`a.strip() == b`, `a: str` param, outside any gate) → `if (str_eq_op (str_strip_op a) b)`, rc 0. |
| 12 | hard rule 3: a receiver-dropping 0-ary op fails the non-vacuity oracle (§3.7.3, §7 R5) | **C** | `bin/check-emitted-vacuity.py:467-477`: any NEW partial parameter erasure (`erased=… of …`) returns 1; `stdout` never read ⇒ `_split_rocq_check_output` would be a new erasure. |
| 13 | Q3 / §7 R3 soundness obligation: a type-variable result may regain int theory under R325 | **C+ (hole is real)** | `pycsl.py:13611`: a `val` is an opaque fallback only `if … _rt325 == ["int"]`; route #334 (`:13571-13601`, `:15205-15220`) only exempts `'a`/`'b`-typed **parameters** as sinks. `scratchpad/wall-ies-review/t1_poly_regains_int.mlw`: `val os_getcwd_0 () : 'a` then `let x = os_getcwd_0 () in x + 1` and `x * 0 = 0` → `--type-only` **rc 0**. Why3 unifies silently; nothing in R325 would refuse it. The one polymorphic-result precedent in the emitter, `getattr_<cls>_poly … : 'a` (`expressions.py:14566`), is kept sound only by a per-method gate (`_emitting_refine_tuple_return_type()`). Note also that `polypatch.py` emitted `'t7`-style variables, which #334's `[":", "'", "a"]` token pattern would not even recognise as polymorphic. |
| 14 | R5 "must also pass the receiver. That is the same capability as the in-place-mutator wall (receiver plus `writes`)" (§7 R5) | **R (over-scoped)** | Probes `q3a` and `q4a_elem_strip.py` (`lines: List[str]` **parameter**, `lines[0].strip() == b`) → `if (str_eq_op (str_strip_op lines[0]) b)`, rc 0. The receiver is passed as a plain argument of a pure `val`; no `writes`, no mutator machinery. The in-place-mutator capability is needed only for mutating methods (`list.insert`, `set.add`), which are not the `str`/`re`/`subprocess` producers of §3.3. |
| 15 | §8: "No route's corpus impact was measured" | **C**, and here is a proxy | `grep -l` over `test-suite/corpus/pycsl-reference/*.py` (3,837 files): `.split(` 14, `.strip(` 14, `.join(` 20, `.splitlines(` 0, `subprocess.run` 2, `tempfile.` 1, `shutil.which` 0, `json.dumps` 0, `re.(match\|compile\|search)` 0 (`python-reference`: 3/2/4/0/0/0/0/3/1). A per-family typed model moves at most ~20 corpus `.mlw` per family; each can be inspected and re-proved, as rule 4 demands. R3's "highest corpus cost" is plausible but remains unmeasured. |
| 16 | census r3 numbers (179, 89, 2 of 153, clash pairs, 58 drifts) (§2) | **Q** | `getting-better/conversion-census-r3.md:66-110` says exactly that; I did not re-run the guard-neutralised census. |
| 17 | pyval I2 "converts 0 stubs on its own" (§2) | **Q** | `getting-better/pyval-value-model-wall-impl.md:87-104`. |
| 18 | `Iterator[str]` is not in the annotation mapper (§3.2 row 7) | **C** | `grep -c Iterator`: `ir_scanner.py` 0, `functions.py` 1 (an unrelated allow-set at `:2330`). |
| 19 | SKILL rules quoted (§1.3, §1.4) | **Q** | `config/skills/self-tcb-reduction/SKILL.md:44-58`, `:244-250` match. |

**Nothing in the report was found false.** Two statements are over-scoped (rows 11 and 14) and one
limit is stronger than the report says (row 9).

---

## 2. Findings beyond the report

### 2.1 A population census of producers (the report only had 12 hand-picked stubs)

`scratchpad/wall-ies-review/census_origins.py` walks the LIVE body of every row of
`trusted-reasons.tsv` (392 with a live body, 26 without; name-based like `leaf.py`):

| live body contains … | stubs (of 392) |
|---|---|
| a `str`-method call (`join` 85, `startswith` 74, `strip` 62, `split` 57, `endswith` 44, `lower` 34, `replace` 26, `lstrip` 23, `rsplit` 20, `splitlines` 19) | **176** |
| a stdlib-module call (`ast` 27, `os` 21, `re` 15, `subprocess` 14, `tempfile` 7, `json` 5, `hashlib` 4) | 81 |
| either of the two | 206 |
| an empty `[]` literal | 204 |
| a comprehension or generator expression | 172 |
| an `Any`-annotated parameter | 120 |
| an unannotated parameter | 71 |
| none of the above | 39 |

This is "contains", not "first blocker", so it bounds reach from above. Still, the `str`-method
family is the single largest producer class in the population, consistent with the sample's
6/12, and it is the one family the emitter already models faithfully under a gate.

### 2.2 The facade trap is live in user programs, not only in the mirror

Two probes type-check (rc 0) while reading none of the receiver:

- `q2_ms_split_chain.py` (inside `@mutable_state`): `if ((strip_0 ()) = (str_hash_op qn))` for
  `lines[i].strip() == qn` with `lines : seq string`.
- `q4b_for_strip.py` (plain function, `lines: List[str]` parameter): `for ln in lines: if
  ln.strip() == b` → `if ((ln_strip_0 ()) = (str_hash_op b))`.

The `for` target `ln` is never typed `str` in the symbol table, so `_is_string_expr(ln)` is
false and the generic dotted-call path mints a 0-ary `val ln_strip_0 () : int`. This is sound
(the value is fresh and opaque) but it is the exact "type-checks ≠ progress" trap the report warns
about in §3.7.3, and `check-emitted-vacuity.py` only runs on the mirror. Any route that is judged
by `--no-proof` rc 0 on user-level probes will over-count.

### 2.3 Two more consumer-typing gaps, located

- Subscript of an **annotated local** `xs: List[str] = …` is not recognised by `_is_string_expr`
  (`q1a` line 27, `strip_1 (!lines)[!i]`), while the same subscript of a **parameter** is
  (`q4a`). The Subscript arm of `_is_string_expr` only knows `os.path.split*` slots
  (`expressions.py` at the `def` + 52).
- `for` targets over `array string`/`seq string` (§2.2).

Both are consumer-side, monomorphic, and in the emitter's own typing predicate — the cheapest
kind of edit in the §4 table, and corpus-visible only on programs that index or iterate a list
of strings and then call a `str` method on the element.

---

## 3. What the report over- and under-scopes

**Over-scoped**

1. *R5 needs receiver-plus-`writes`.* No: pure `str`/`re`/`os.path` methods are already modelled as
   receiver-passing pure `val`s (`str_strip_op`, `str_split_op`, `path_isfile_op`, `re_sub`).
   Only mutating methods need the mutator wall (row 14).
2. *R3 fails on "the emitter's erased type guess".* It fails first on WhyML itself: no
   polymorphic program `=`, truthiness or `in` exist to defer to (row 9). R3 therefore reduces to
   R2-style type-directed lowering **plus** polymorphic producers, and the type-directed part is
   the whole cost. Once the emitter knows the consumer type, a monomorphic producer typed from the
   same knowledge is strictly simpler than a type variable (no mutable-instantiation limit, no
   R325 hole).
3. *`strip` as an origin* (row 11): it is downstream of the erased receiver.

**Under-scoped**

1. *The R325 hole for polymorphic results* is listed as an "obligation"; it is a present-day
   unsoundness as soon as one `: 'a` val is emitted outside a per-method gate (row 13). Any R3
   increment must first extend `_S325` to `'a`-returning vals **and** add the result-side taint
   (the Why3 type-only run will not catch it, as `t1` shows).
2. *The contract-shape conflict for R4* is stated correctly but under-weighted: `requires True`
   with a tagged model means every projection either needs `wf_ir`-style preconditions (rule 5
   broken) or exception-modelled wrong-tag paths, and the emitter's own `isinstance` dispatch is
   gated behind the `stmts_of : emit_ir -> array int` input wall (pyval I2). R4 is not a
   candidate for this wall until the input-dispatch wall is broken; the report's §7 "the only
   route that removes the seam" is true and currently unreachable.
3. *The population.* 12 hand-picked stubs cannot say which family to build first; §2.1 can.
4. *Corpus cost of R5* was called "limited to users of each family" — it is in fact ≤ 20 files
   per family on the reference tree (row 15), which changes the cost ranking: R5-str is the
   cheapest route on every axis the report lists.

---

## 4. Recommended route: **R5-str**, a carve-out of R5 + R2 (monomorphic, receiver-passing)

### 4.1 The route

Four additive emitter edits, each corpus-bounded by the grep in row 15, no new WhyML value
shape (`string`, `array string`, `seq string`, `map string (option string)` all exist and are
covered by the existing certificates), no polymorphism, no axiom:

| step | edit (file, function) | WhyML shape produced | corpus files touched (upper bound) |
|---|---|---|---|
| a | `expressions.py:10027-10031`: gate the whole-list `.split(sep)` model on `self._is_string_expr(receiver)` instead of `_current_self_type in _mutable_state_classes` | `val str_split_op (s sep: string) : array string` (already declared at `:3373`/`:10036`) | 14 (`.split(`) |
| b | same file, next to `:3659`: add `splitlines`, `rsplit`, and `join` on the `str_split_op`/`str_strip_op` pattern | `val str_splitlines_op (s: string) : array string ensures { Array.length result >= 0 }`; `val str_join_op (sep: string) (parts: seq string) : string` | 0 (`.splitlines(`), 20 (`.join(`) |
| c | `_is_string_expr` (Subscript arm, `expressions.py` def+52): a `Subscript` whose value is a Var typed `array string`/`seq string` in `_current_symbol_table` — **including annotated locals** — is a string expr; same for a `for` target over such a var | `str_strip_op lines[!i]`, `str_eq_op (…) !qn` instead of `strip_1 (subscript_get …)` / `strip_0 ()` | programs that index/iterate a `List[str]` and call a `str` method on the element (bounded by the `.strip(`/`.lower(`… greps: ≤ 14 each) |
| d | mirror only, zero corpus cost: annotate the producer-bound locals (`lines: List[str] = stdout.splitlines()`), which the fidelity plane allows (`check-self-annotate-mirror-sync.py:78-92`) and which removes the `ref 0` pre-declaration (`q1a` line 20) | `let lines = ref (str_splitlines_op stdout)` | 0 |

Why this and not R3/R4:

- it is the only route whose every piece is **already in the emitter** under a narrower gate,
  which is exactly rule-4-friendly: the shape of every moved corpus `.mlw` is known in advance
  (`str_split_op`/`snapshot` where `x_split_1 <hash>` was);
- it keeps R325 intact (every op is monomorphic `string`/`array string`; no `'a` result);
- it reads the receiver, so hard rule 3 is satisfied by construction (the vacuity oracle counts
  the parameter as used);
- the contract shape is unchanged (`requires True`): `str_strip_op`, `str_split_op`, `str_eq_op`
  carry only cheap `ensures` and no `requires`.

Expected reach: the `str`-family is present in 176/392 live bodies (§2.1). It will not close a
chain on its own where the next link is a comprehension (172 bodies; stub 6's `''.join(c for c
…)` stays `(any int)`), `re` (stub 2), `subprocess`/`tempfile`/`shutil` (stubs 1, 4, 5) or an
unmodelled self-method across files (stub 10). Of the 12 benchmark stubs, R5-str is the full
chain for **stub 3** and the first link for stubs 2 and 6; the external-library families (`re`,
`subprocess`, `tempfile`, `shutil`, `json.dumps`) are the natural second carve-out (R5-lib) on
the same pattern — an abstract typed record per library object (`re_match` with
`val re_match_group_op (m: re_match) (i: int) : string`) is a **new value shape** and would
owe a coupling-rule side-car certificate; `subprocess.run` is simpler (`CompletedProcess` as a
record of `string`/`int` fields, no new theory).

### 4.2 The make-or-break spike (done, before any emitter edit)

`scratchpad/wall-ies-review/s3_split_typed_model.mlw` is the **whole** body of stub 3
(`_split_rocq_check_output`, 40 lines of Python including the `(A or B) if C else False` monster)
hand-written in the exact shape steps a–d would emit: `str_splitlines_op`, `str_strip_op`
on `lines[!i]`, `str_eq_op`, `seq string` block, `map string (option string)` result, the
emitter's `try … raise PyCSL_Break` loop lowering, fixed contract `requires { true } ensures {
true }`, and loop `variant`s. Every `val` has at most a cheap `ensures` (the emitter's existing
discipline); nothing is an axiom.

- `heavy.sh why3 prove --type-only s3_split_typed_model.mlw` → **rc 0** (the first four attempts
  failed on my own WhyML — `mod`, `option`, `const`, and the `([])` overload resolved by `use`
  order, which is why the emitter puts `use array.Array` last — all recorded in the shell history,
  none on the route).
- `heavy.sh why3 prove -P alt-ergo -t 30 s3_split_typed_model.mlw` (with `qualnames.index`
  left as an **unconstrained** typed op, the way the generic dotted-call path would mint it) →
  `Goal _split_rocq_check_output'vc. Prover result is: Timeout (30.00s, 939997 steps)`, rc 2.
  `heavy.sh why3 prove -a split_vc -P alt-ergo -t 10 s3_split_typed_model.mlw` → the **only**
  non-Valid sub-goals are the two `Sub-goal Index in array bounds of goal
  _split_rocq_check_output'vc` (Timeout 10 s each) — the two reads `qualnames[index(qn) + 1]`.
  Every other sub-goal (loop variants, `pycsl_mod` divisor, all `lines[!i]` reads, the
  `map_update_some` result) is Valid. So the one obligation the typed route surfaces is a real
  Python one (an unconstrained `list.index` result indexes `qualnames`), present identically in
  today's erased emission, and discharged by a faithful `val` contract (`s3b`), not an axiom.
- `s3b_split_typed_indexspec.mlw` = the same file with the faithful contract on
  `qualnames.index(qn)` (`requires { exists k. 0 <= k < length a /\ a[k] = x } ensures { 0 <=
  result < length a /\ a[result] = x }`), prepared because the read `qualnames[index(qn) + 1]`
  is a genuine bounds obligation that the current erased emission carries too
  (`qualnames[((qualnames_index_1 !qn) + 1)]` in `out/…_split_rocq_check_output.mlw`):
  `--type-only` rc 0; `heavy.sh why3 prove -P alt-ergo -t 30 s3b_split_typed_indexspec.mlw` →
  **`Goal _split_rocq_check_output'vc. Prover result is: Valid (0.10s, 486 steps)`, rc 0.** The
  whole stub-3 body — both nested loops with `variant`s, the `try … raise PyCSL_Break` lowering,
  every array read including `qualnames[index(qn) + 1]` and the `pycsl_mod` divisor — proves
  under the fixed contract with monomorphic typed `val`s and no axiom.

Interpretation rule, fixed before the result: if `s3` (or `s3b`) proves, the route cannot be
refuted at the Why3 level for stub 3 and the next spike is the emitter one below; if both fail
on anything other than the `index` bounds goal, the route is refuted for stub 3 and the failing
goal names the missing model.

### 4.3 The next spike, on the emitter, still before touching `src/`

In the scratch tree `scratchpad/wall-ies/tree` (a `git archive` copy):
1. apply step a (one condition) and step b (`splitlines` only) — about 15 lines;
2. `tc.sh` for stub 3 with the mirror local annotated (step d) → expected residual: the
   Subscript/`for`-target gap (step c), visible as `strip_1 (!lines)[!i]` or `strip_0 ()`;
3. apply step c; re-run; expect `--no-proof` rc 0 **and** `grep -c '_0 ()' ` on the emitted
   function = 0 (the facade test);
4. byte-diff the 14 `.split(` and 0 `.splitlines(` corpus programs against the baseline; inspect
   each moved file (the shape change is `x_split_1 <hash>` → `snapshot (str_split_op x sep)`),
   and re-prove them;
5. only then port to `src/`, run L1/L2/L3 and the vacuity oracle on `proof2why3/extract.py`.

### 4.4 What this route does **not** do

It does not remove the seam; it moves the `int` default's boundary outward one family at a
time, with each family's corpus footprint measured first. That is the only shape of progress
compatible with rules 3–5 today. The seam itself is removable only by R4, and R4 is blocked by
the input-dispatch wall (pyval I2) and the contract shape, as the report says.

---

## 5. On the reviewer questions of §9

1. **R3 vs R4 foundation.** Neither, for this wall. R3 is not inference at the IL — WhyML
   offers unification of **types**, not of **operations** (row 9) — so the operator selection
   must still be done by the emitter, i.e. R3 ⊂ R2 + a polymorphic producer, and the polymorphic
   producer costs the R325 hole (row 13) and the mutable-instantiation limit (row 6). R4 is
   faithful and currently unreachable (§3). The VC-cost ratio of R4 is unmeasured; the JaVerT
   experience (every operation dispatches on the tag) suggests an order of magnitude on
   dispatch-heavy bodies, which the emitter's handlers are.
2. **Projections under `requires True`.** Only with modelled exceptions on the wrong-tag path
   (`raise TypeError`/`AttributeError` as Python does), never with a total projection to an
   arbitrary value; and the emitter's own `isinstance` chains are gated behind the opaque
   `stmts_of`, so occurrence typing has nothing to narrow yet.
3. **R325 and type variables.** Not preserved today (`t1`). Minimal discipline: treat every
   `val … : 'a` without `ensures` as an opaque origin in `_S325` and taint its result exactly
   like an `int` fallback; and refuse any instantiation of that `'a` at a consumer other than
   bind/pass/return/`=`-against-different. The cheaper discipline is to not emit `: 'a` results
   at all outside per-method gates — which is R5-str.
4. **Type-directed overloaded operators on type variables.** There is no deferred selection in
   WhyML; dictionary passing would need a type-class record per sort and a certificate for its
   laws. The practical answer is the one the emitter already implements: decide at the consumer
   from the symbol table, and make the symbol table know more (step c).
5. **Byte-inertness while changing a default.** Gate the new lowering on a predicate that is
   false wherever the old default fired — exactly what `_mutable_state_classes` does today for
   `.split`, and what step a replaces by the weakest predicate that is still static
   (`_is_string_expr(receiver)`). The grep bound in row 15 is the cheap pre-measurement; the
   byte-diff is the oracle.

---

## 6. Risks

1. **Step c is corpus-visible.** Any program that indexes a list of strings and calls a `str`
   method on the element will change shape (from `strip_1 (subscript_get …)`/`x_strip_0 ()` to
   `str_strip_op xs[i]`). The grep bound is ≤ 14 files per method on `pycsl-reference`, but
   each must be re-proved, and a stricter `ensures` on `str_strip_op` (`length result <= length
   s`) may make a previously vacuous proof fail or a previously-proved bound change. Mitigation:
   byte-diff first (§4.3 step 4), never re-baseline.
2. **Genuine obligations surface.** Typed models expose VCs the opaque model hid: array bounds on
   `qualnames[index(qn) + 1]` (`s3b`), `pycsl_mod` by `len(qualnames)` (provable from the loop
   guard), `str_slice` bounds if modelled. Each is either provable under the fixed contract or
   needs a faithful `val` contract (`s3b`), never an axiom — but it is proof work per stub, and
   the chains of backlog #64 (depth ≥ 3) remain.
3. **Reach is bounded by the next link.** 172 bodies contain a comprehension and 204 an empty
   `[]`; R5-str does not touch those producers. Expect single-digit conversions from steps a–d
   alone on the 12-stub benchmark (stub 3 certainly; 2 and 6 only after `re` and the genexp
   wall), and tens only after R5-lib.
4. **Facade false positives.** Judging by `--no-proof` rc 0 over-counts (§2.2). Every claimed
   type-check must be paired with `grep -c '_0 ()'` on the emitted function and the vacuity
   oracle.
5. **The `index` contract.** `requires { exists k … }` is sound (Python raises otherwise), but if
   the mirror file is ever run under `no_exception`, the obligation becomes a hard VC at every
   `.index` call; acceptable here, worth noting in the model's comment.
6. **R5-lib's new value shapes** (`re_match`, `CompletedProcess`) fall under the coupling rule and
   owe a side-car certificate; keep them out of the first increment.

---

## 7. Artifacts

All under `/home/fabrice/git/pycsl/scratchpad/wall-ies-review/`:

- `eq1.mlw`, `eq2.mlw`, `eq3.mlw` — WhyML program `=` is monomorphic (row 9).
- `t1_poly_regains_int.mlw` — a `: 'a` result unifies with `int` silently (row 13).
- `q1{a,b,c}_*.py/.mlw/.out` — annotated local vs producer; `.split` on a `str` param erased
  (row 10).
- `q2_ms_split_chain.py/.mlw/.out` — the chain under `@mutable_state`: type-checks, facade
  `strip_0 ()` (§2.2).
- `q3{a,b}_*.py/.mlw` — `str_eq_op (str_strip_op a) b` on a `str` param (rows 11, 14).
- `q4{a,b}_*.py/.mlw` — element read typed for a parameter; `for` target not typed (§2.2, §2.3).
- `census_origins.py` — the population census (§2.1).
- `s3_split_typed_model.mlw`, `s3b_split_typed_indexspec.mlw` — the make-or-break spike (§4.2).

Report artifacts re-run: `scratchpad/wall-ies/why3py/{poly,poly3,poly4,poly-seam-spike}.mlw`,
`scratchpad/wall-ies/{sigdrift,leaf}.py`, `bin/check-mirror-signature-drift.py`.
