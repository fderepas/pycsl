# W-SB — independent review of `string-builder-wall.md`

*Reviewer: independent (no access to the campaign's attempt history; read only the report,
`src/`, `bin/`, `docs/`, and the executable oracles). 2026-10-12, branch `ghost-assign-bc6`,
HEAD `f1488bfb`. Every oracle below was run on this tree with `. scratchpad/g29/env.sh` in
effect (why3 1.8.2 / Z3 / Alt-Ergo on `PATH`, `PYTHONHASHSEED=0`) unless the line says
otherwise. Probe sources live in the session scratchpad `wsb-review/`; nothing under `src/`,
`test-suite/`, `bin/` was touched.*

## 0. Verdict in brief

1. **The report's facts hold.** Every census number I could spot-check reproduces exactly
   (449 directive lines, 435 stubs over 53 mirror files, corpus `F.spec`/`F.conv` = 0/0, corpus
   `J` = 8 occurrences in 4 files `0958–0961`, python-reference `J` = 5/4). Every §3.4 lowering
   reproduces term-for-term. The §4.3 hand model reproduces at 16 Valid + 1 Timeout under Z3 and
   `substring_extend` Valid (1.61 s) under Alt-Ergo. The §6.4 fail-open hazard reproduces.
2. **The unsoundness is real and the report UNDER-states it.** The report says the defect
   "shows only through equalities between two dropped forms". It does not: `#@ ensures
   \result == s` on `return f"{s!r}"` PROVES (`Verification SUCCESS`), because `!r` is dropped
   and the f-string lowers to the identity `s`. That is a directly false postcondition on a
   single expression, not a comparison artefact (§2.2 below).
3. **The wall is a modelling choice, not a logical limit** — the report is right, and the
   single root cause is correctly identified: `_collect_array_elem_types` (`statements.py:6451`)
   returns `{}` outside `@mutable_state`, so no `List[str]` local/param/loop-target carries its
   element type to the join / `+` / f-string consumers.
4. **Route ranking: D first is right, A second is right, but A as written is over-scoped.** The
   cheapest sound step for A is *not* the ghost `join_from` model; it is (i) alone — carry
   `List[str]` element types outside `@mutable_state` so `.append`/`join` type-check — with the
   existing opaque `str_join_seq (length >= 0)` contract. Step (ii) (definitional join) only pays
   when a converted stub's *contract* mentions the joined content, and no first-blocker row in
   the report's table needs that. Keep (ii) behind its own Gate-B spike.
5. **Minimal sound repair for the unsoundness: fail closed at the IR.** Have
   `Module5_IREmitter._py_expr_fstring` raise `PyCSLIRError` on any `FormattedValue` with
   `format_spec is not None` or `conversion != -1`. It is a 4-line change, byte-inert on the
   corpus by measurement (0 files use either), and strictly safer than the spec-keyed opaque,
   which is the right *second* step (its soundness sketch is in §2.4).

## 1. Oracle artifacts

Each line names the report claim it tests and what the run showed.

| # | claim (report §) | command | result | verdict |
|---|---|---|---|---|
| O1 | §3.5 `f"{b:02x}" == f"{b}"` proves with `ensures \result == True`; CPython says `False` | `.venv/bin/python3 src/pycsl/pycsl.py p_fmt.py --keep-mlw` / `python3 ground.py` | `Prover result is: Valid (0.00s, 5 steps)` · `[+] Verification SUCCESS! All contracts formally proven.` · emitted `(if ((str_of_int_hash b) = (str_of_int_hash b)) then 1 else 0)` · CPython `hex_equals_plain(10) = False` | **CONFIRMED** (unsound) |
| O2 | §3.5 `f"{s!r}" == f"{s}"` proves; CPython `False` | same, `p_repr.py` | `Valid (0.01s, 252 steps)` · `SUCCESS` · emitted `(if (str_eq_op s s) then 1 else 0)` · CPython `repr_equals_plain('a') = False` | **CONFIRMED** (unsound) |
| O3 | §3.5 "the defect shows *only* through equalities between two dropped forms" | `p_repr_id.py`: `#@ ensures \result == s` over `return f"{s!r}"` | `Valid (0.01s, 479 steps)` · `SUCCESS` · emitted body is literally `s` with `ensures { (result = s) }`; CPython `f"{'a'!r}" == "'a'"` ≠ `"a"` | **REFUTED** — a direct false postcondition proves; the hazard is wider than stated |
| O4 | §3.5 `f"{10:02x}"` with `ensures \result == "0a"` is Unknown (not proven, not refuted) | `p_fmt_str.py`, and the false twin `p_fmt_str2.py` (`== "10"`) | both `Prover result is: Unknown` · emitted `(int_to_string 10)` | **CONFIRMED** (incomplete, not unsound, on this shape) |
| O5 | §3.4 `", ".join(xs)` and `"".join(xs)` (`xs: List[str]`) emit the *same* `(join_array xs)` with `val join_array (a: array int) : int`; L3-tc fails `array string` vs `array int` | `pycsl.py p_join.py --no-proof --keep-mlw`, `p_join0.py` | both: `L3-tc ✗`, `line 14 … but is expected to have type array.Array.array int`; both `.mlw` line 14 = `(join_array xs)`; separator absent | **CONFIRMED** |
| O6 | §3.4 builder `out.append(ch) … '"' + ''.join(out) + '"'` emits `Seq.snoc` into an int seq and `(str_concat (str_concat 210923450 (join_array !out)) 210923450)` | `p_builder.py --no-proof --keep-mlw` | `L3-tc ✗` at line 32 chars 50-54 (`!out` vs `array int`); line 29 `out := Seq.snoc !out !ch;`; line 32 exactly as claimed, hash `210923450` for `'"'` | **CONFIRMED** |
| O7 | §3.4 `ESC.get(c)` (no default) → `(eSC_get_1 (str_hash_op c))`, `val eSC_get_1 (x0: int) : int`; `ESC.get(c, c)` → faithful `str_eq_op` if-chain | `p_dict.py` | line 18 `(eSC_get_1 (str_hash_op c))` (L3-tc ✗ `int` vs the Optional union); line 22 `(if (str_eq_op c "\\") then "\\\\" else (if (str_eq_op c "\"") … else c))` | **CONFIRMED** |
| O8 | §3.4 `s.encode("utf-8")` is input-blind: `(s_encode_1 1501791143)` | `p_encode.py` | line 11 `val s_encode_1 (x0: int) : array int`; line 15 `(iter_length (s_encode_1 1501791143))` — `s` does not appear | **CONFIRMED** |
| O9 | §3.4 `"%d items" % n` → `(str_mod_op "%d items" n)`, typed, L3-tc ✓ | `p_mod.py` | `L3-tc ✓`; `val str_mod_op (s: string) (x: 'a) : string`; `(str_mod_op "%d items" n)` | **CONFIRMED** |
| O10 | §4.3 hand join model: Z3 `split_vc -t 20` 16 Valid + 1 Timeout (`substring_extend`); Alt-Ergo proves `substring_extend` | `why3 prove -a split_vc -P z3 -t 20 join_feasibility.mlw`; `why3 prove join_feasibility.mlw -T JoinModel -G substring_extend -P alt-ergo -t 90` | Z3: 16 × Valid, 1 × `Timeout (11.7s, 2163253 steps)` on `Goal substring_extend`; Alt-Ergo: `Valid (1.61s, 15458 steps)`. No `axiom` in the file | **CONFIRMED** (note the report's `-T … -G …` before the file name is rejected by why3 1.8.2; the file must come first) |
| O11 | §1.2 census units: 449 directive lines; 435 stubs via `all_trusted` | `grep -rhE '^\s*#@\s*\\trusted\b' … \| wc -l`; `sum(len(pcc.all_trusted(f)))` over `src/self-annotate/src/**/*.py` | `449`; `mirror files: 53 all_trusted stubs: 435` | **CONFIRMED** |
| O12 | §3.6 corpus static census: `F.spec` 0, `F.conv` 0, `J` 8 occ / 4 files (0958–0961); python-ref `J` 5/4 | own `ast` walker with the report's A.1 join rule | pycsl-ref (1850 files): `F.spec 0/0 · F.conv 0/0 · J 8/4 [0958,0959,0960,0961]`; python-ref (2217): `J 5/4 [multiprocessing/join_call_*, str_methods/join_*]`, `F.spec/F.conv 0/0` | **CONFIRMED** |
| O13 | §6.4 without why3 on `PATH`, `--no-proof` reports `L3-tc ✓` and `Verification SUCCESS` for a file that does not type-check | `env -i HOME=$HOME PATH=/usr/bin:/bin PYTHONHASHSEED=0 .venv/bin/python3 src/pycsl/pycsl.py p_join.py --no-proof` (`which why3` → none) | `[level] L1 ✓  L2 ✓  L3-tc ✓` · `[+] Verification SUCCESS (--no-proof: WhyML generated AND type-checks …)` — for the very file O5 shows fails L3-tc | **CONFIRMED** (fail-open; this is a tool bug in its own right, see §5) |
| O14 | §5 route D: a spec-keyed `val function str_fmt (spec: string) (x: int)` would keep `f"{b:02x}" == f"{b:02x}"` provable and leave `f"{b:02x}" == f"{b}"` undecided | `why3 prove -P z3 -t 5 fmt_keyed.mlw` | `same_spec_same_val: Valid (0.01s)` · `diff_spec_undecided: Unknown (0.11s)` | **CONFIRMED** (sketch only — not emitter output) |

Not run: the 8 m 26 s `byte-diff-sweep` and the §3.2 dynamic first-error harness (~1 h on 8
cores). Their inputs (the static census) and their claimed outputs (0 emitted `join_array`/
`str_join_*` in the corpus) are consistent with O12: the only corpus `.join` sites are the four
`0958–0961` files, whose join is the separate `pp__joinstr` recognizer (`generic_fold.py:35724`
ff.), and the python-reference joins are over literal lists (the `str_concat_op` path at
`expressions.py:6818`). I did not independently re-derive the 16 / 94 / 10 first-blocker
numbers; they depend on the A.2 harness, which I treat as the report's responsibility. Their
*direction* (W-SB is rarely first) is corroborated by the per-file construct list: joins live
in `pycsl.py`, `pure_ast.py`, `proof2why3/*`, exactly the files whose stubs the report shows
refusing on in-place mutators first.

## 2. Assessment of the factual claims (a)

### 2.1 Lowerings and gating
All ten rows of §3.4 reproduce (O5–O9 plus the f-string rows under O1/O4). The code reading
agrees with the report's gating story:
* `_join_arg_elem_is_string` (`expressions.py:6890`) consults `_refine_str_comp_locals`,
  `_array_elem_types`, `_seq_value_types`, and the `@mutable_state`-only `_seq_locals` arm.
* `_collect_array_elem_types` (`statements.py:6451`) starts with `if _current_self_type not in
  _mutable_state_classes: return out` — empty outside `@mutable_state`. This is the one line
  that makes W-SB a wall.
* `str_join_seq`/`str_join_arr` carry only `ensures { String.length result >= 0 }`
  (`expressions.py:6801/6813/6850/6854/6882`, `functions.py:6770`).
* The literal-list exact join (`expressions.py:6818–6835`) and the module-constant dict
  `.get(k, d)`/`in` if-chain (O7 line 22) are real existing capabilities, as the report says.

### 2.2 The unsoundness (O1–O3)
Confirmed at the source: `Module5_IREmitter._py_expr_fstring` (`:1645–1654`) appends
`self._py_expr_to_ir(v.value)` for a `FormattedValue` and never reads `v.conversion` or
`v.format_spec`. Nothing downstream can recover them: the IR node is `{"type": "FString",
"parts": [...]}` and Module 6 (`_handle_fstring_expr`, `expressions.py:15978` ff.) has three
joiners — all-string `str_concat_op`, the `-> str`/`@mutable_state` `int_to_string` joiner, and
the int-hash `str_concat`/`str_of_int_hash` joiner — none of which has a spec to look at.

The report's scoping sentence ("shows only through equalities between two dropped forms") is
refuted by O3: with a declared `-> str` return the all-string joiner path makes `f"{s!r}"`
*the identity on `s`*, so any contract about `s` transfers to the f-string. That is the most
dangerous of the three shapes because it needs no second f-string to compare against, and
because `!r` is by far the most common of the dropped forms in the mirror (13 stubs / 22
occurrences vs 4 / 4 for specs, per §3.3). The `ir_resolve.py:286` ADT (`IrPyFormattedValue`
with `conversion`/`format_spec`) shows the *self-annotation* IR already carries the fields; the
live IR does not.

### 2.3 Census
O11/O12 reproduce every number I could reach cheaply. One nuance the report should state:
its `J` rule counts `thread.join(x)`-style one-argument joins only if the receiver is not a
path object; it says none were observed, which O12's corpus listing supports (multiprocessing
`join_call_*` files are `.join()` with *one* argument on a process object and were counted as
`J` — so the python-reference `J 5/4` figure includes 2 non-string joins; harmless for the
argument, but the number is not "string joins").

### 2.4 Axiom-free join model
O10 reproduces. Two observations the implementation plan should carry:
* The model is axiom-free only because `str_join_seq`'s `ensures { result = join sep xs }` is a
  `val` *realised* by a ghost function. That is the same trust status as `str_concat_op`
  (`ensures { result = concat a b }`), as the report says — but it is strictly *more* than the
  current `length >= 0` contract and it couples to the formal-semantics "3 axioms" ledger only
  if a Rocq/Lean certificate is required for new value shapes. `seq string` is not a new
  shape (it exists under `@mutable_state`), so the coupling rule should not bite for step (i).
* Z3 alone cannot do `substring_extend`; the portfolio does. If the emitter ever runs a
  single-prover profile (e.g. the `--typecheck`/CI fast path), the lemma prelude must be
  marked so that a Z3-only run reports *Timeout* and not a silent drop.

## 3. Fundamental or modelling choice? (b)
Modelling choice. The evidence is O6 against O10: the same builder loop fails L3-tc in the
emitter and proves in 17/17 goals by hand, with identical `val` vocabulary (`str_length_op`,
`str_sub_op`, `str_join_seq`) and standard theories only. The wall is the single
`@mutable_state` gate in `_collect_array_elem_types` plus the absence of a `format_spec`
carrier. Neither is a limit of Why3 or of the string theory.

What *is* close to fundamental in this family: `%`-format and `.format` with arbitrary specs
(`str_mod_op : string -> 'a -> string` is a polymorphic opaque; a faithful model is a printf
interpreter), and `.encode` for non-ASCII (needs a UTF-8 model). Those should stay opaque
but *input-carrying*. The report's E/P verdicts agree.

## 4. Route ranking (c)

| route | report rank | my view |
|---|---|---|
| **D** (carry spec/conv, then spec-keyed opaque or refuse) | 1 | **Agree it is first**, but split it: **D0 = refuse** (fail-closed at Module 5), ship immediately with the 3 witnesses of §5; **D1 = spec-keyed opaque** (`str_fmt spec x`, `str_repr_op` for `!r`, identity for `!s` on strings) as the follow-up that reopens the 13 `!r` stubs. O14 shows D1's shape is sound in the model. |
| **A** (faithful list-of-str + join) | 2 | Agree it is the only route with reach, but **over-scoped as a unit**. Rank **A(i)** alone — populate `_array_elem_types`/`_seq_value_types` from declared `List[str]` annotations (params, `x: List[str] = []` locals, loop targets over `str`) outside `@mutable_state`, consumers restricted to `.append`/`join`/`+`/`return str` — above everything else. It uses only existing `seq string` machinery and the existing opaque `str_join_seq`. **A(ii)** (definitional `join_from` + lemma prelude) is a separate Gate-B item: it only pays when a contract constrains the *content* of a join, and none of the 8 join/builder first-blocker stubs in §3.3 has such a contract today (their ensures are type-safety + frame shapes). Do not couple (i) to (ii). |
| **B** | subsumed | Agree. O6 shows the int `str_concat` appears only because `join_array` returned `int`; fix A(i) and the `+` chain re-types itself (`expressions.py:4625` already routes `+` to `concat` when the join is string). |
| **C** (`.get(k)` no default on str→str const) | 3rd tier | Agree it is cheap and its stub payoff is ~0. One correction: the if-chain exists today for the 2-arg form (O7 line 22); the no-default form only needs the *same* chain into the Optional carrier. It is the cheapest route of all, but it should wait for a chain probe that actually reaches it. |
| **E** (`encode` input-carrying) | 3rd tier | Agree. O8 shows the receiver is dropped; a `str_encode_utf8 (s: string) : seq int` with `length s <= length result` is a one-`val` change. **Not corpus-inert** (python-ref `encode_call_*` emit `<x>_encode_1`), so it needs the sweep. |
| **P** | 3rd tier | Agree; `str_mod_op` is already typed (O9). |

**Missing from the routes:** the **fail-open `--no-proof` path (O13)**. It is an instrument
bug in the live tool, not just a harness hazard: anything that gates on `L3-tc ✓` (the A.2
harness, `bin/check-*` scripts, a CI job on a machine without why3) is reporting success on
ill-typed emission. The fix is to make the L3-tc step *fail* when `why3` is not found, and it
should land *before* any W-SB route so that the "moved / lowered" measurements are trustworthy.
It is cheaper than D0.

**Nothing to reuse that the report missed.** I checked `preamble.py` and `expressions.py` for
a hex/format capability: there is none (`zfill`/`ljust`/`rjust` are length-only opaques at
`expressions.py:14087`; `format(x)` is handled only as `str(x)` at `:10701/10745`). `repr(s)`
already has `str_repr_op` with `length >= 2` (`:10755`) — that is exactly what `!r` should map
to in D1, so D1 needs no new op for the conversion case.

## 5. The minimal sound repair and its witnesses (d)

**D0 (ship first, 4 lines):** in `_py_expr_fstring`, for a `FormattedValue` with
`v.format_spec is not None` or `v.conversion not in (-1, None)`, raise `PyCSLIRError` with a
message naming the construct (`f-string format spec / conversion is not modelled`). It
surfaces as `[!] PIPELINE ERROR` (`pycsl.py:3746`) in both proof and `--no-proof` modes,
which is the established fail-closed channel (cf. the `xs.pop()` refusal, `statements.py:3326`).
Corpus impact: 0 files (O12), so the byte-diff must be empty; any REFUSED→EMITTED or
EMITTED→REFUSED transition in the sweep is a bug in the patch.

Why refuse rather than lower immediately: the spec-keyed opaque (D1) changes *three* joiners
and the `check-fstring-lowering.py` return-set pin, and `!s` on a non-string, `!a`, nested
specs (`f"{x:{w}}"`) and `=` debug specs each need a decision. D0 closes the proved-false
route in one step with zero decisions; D1 then reopens shapes one at a time behind witnesses.

**Witness files to pin D0 (all `# pycsl-expected: FAIL` today with a *proved* contract, must
become refusals):**
1. `f"{b:02x}" == f"{b}"` with `ensures \result == True` (O1 shape).
2. `return f"{s!r}"` with `ensures \result == s` (O3 shape — the direct one; this is the
   witness that must never prove again).
3. `f"{s!r}" == f"{s}"` with `ensures \result == True` (O2 shape).

**Completeness controls (must keep PASSING):** `1705`/`1706` (route #203) and a new twin
`a = f"{n}"; b = f"{n}"; a == b` with no spec — D0 must not touch spec-free f-strings.
`bin/check-fstring-lowering.py` needs no new row for D0 (no new return in
`_handle_fstring_expr`); D1 will need one justified row per new return.

For D1, the pins are the inverse: witness 1 becomes `Unknown` (O14 `diff_spec_undecided`),
a new `f"{b:02x}" == f"{b:02x}"` → `\result == True` must PASS (O14 `same_spec_same_val`),
and `len(f"{s!r}") >= 2` must PASS via `str_repr_op`.

## 6. Make-or-break spikes for the implementation plan (e)

**S0 — fail-open L3-tc (precondition for every measurement).** Patch the L3 step to fail when
`why3` is absent; refutation criterion: `env -i … pycsl.py p_join.py --no-proof` must print
`L3-tc ✗` or a `[!] … why3 not found` error, never `SUCCESS`. Cost: minutes.

**S1 — D0 refusal + the three witnesses.** Refutation: any corpus `.mlw` byte moves, or any
of the three witnesses still proves, or `1705`/`1706` stop passing.

**S2 — A(i) on one marker (`identifiers.whyml_ident`, the report's own pick).** Build only the
`List[str]`-annotation → `_array_elem_types`/`_seq_value_types` population for params and
annotated locals, outside `@mutable_state`, and re-run the A.2 first-error probe on that stub
before/after. **Refute** the route if (a) the first error does not move off the `Seq.snoc`
line, or (b) the corpus sweep moves any file other than by a REFUSED→EMITTED-free re-typing
that still proves — the report correctly flags `len`/indexing/`in` on newly-typed `List[str]`
locals as the byte-diff risk. Decision rule for the gate: consumer-restricted first (join /
`+` / `return`), widen only with a clean sweep. Expected: the marker *moves* and likely does
not *lower* (the #64 prior); that is still a pass for the spike if the next blocker is not
another SB token.

**S3 — A(ii) definitional join, only if S2 reaches a contract that needs content.** Emit the
§4.3 ghost/`val`/lemma prelude from the emitter (not by hand) for the O6 builder probe, with
`ensures \result == '"' + value + '"'`. **Refute** if the emitted module does not type-check or
if the portfolio (Z3 20 s + Alt-Ergo 90 s) leaves the loop invariant or `substring_extend`
undischarged in emitter output; also refute if the prelude moves any of the 16 corpus files
that emit `str_concat_op` (it must be registered on demand like the other ops, not in the
preamble).

**S4 — E on `_decode_string` only if a chain probe reaches it.** The report's own "L" row says
its real first error is an unbound `body`, i.e. not SB; do not start there.

## 7. Minor corrections to the report
* §4.3: `why3 prove -P alt-ergo -t 90 -T JoinModel -G substring_extend <file>` is rejected by
  why3 1.8.2 ("Option '-T' with a non-qualified argument requires an input file"); put the file
  before `-T`/`-G`.
* §3.5: replace "shows only through equalities between two dropped forms" with the O3 fact —
  the `!r` drop makes `f"{s!r}"` the identity on `s` under a `-> str` return, a directly
  false postcondition.
* §3.6 / python-reference `J 5/4`: two of those are `Process.join()` calls, not string joins.
* §6.4: the fail-open is confined to `--no-proof`. A *full-proof* run with why3 absent fails
  closed (`env -i … pycsl.py p_join.py` → `[!] ERROR: 'why3' command not found. Please ensure
  Why3 is installed and in your PATH.`), so S0 is a one-branch fix: make the `--no-proof`
  L3-tc step take the same exit as the proof step when `why3` is missing.
