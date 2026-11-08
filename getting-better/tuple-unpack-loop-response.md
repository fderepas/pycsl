# Independent review: tuple-unpack-loop.md

**Reviewer basis:** report + repo + oracles only (pycsl, why3 1.8.2 / Alt-Ergo 2.6.2 / Z3 4.13.3,
grep, AST census). No access to the sub-loop's rationale. All commands below were actually run on
2026-08-14/15; outputs quoted verbatim.

## 0. Verdict summary

| Report claim | Verdict | Oracle |
|---|---|---|
| Count 721 / `no_cheap_remaining` | **CONFIRMED** | census grep (§1) |
| Machinery exists: enumerate-over-seq-local + items-over-hval lower + typecheck today | **CONFIRMED** | canonical emission, L3-tc ✓ (§2) |
| ...and PROVE today | **not independently re-proven** (typecheck plane confirmed; proof runs exceeded my budget — noted honestly, §2.3) | |
| (c) direct seq-of-pairs dual-binding proves (make-or-break) | **CONFIRMED — PROVES, trivially** (hand `.mlw` Valid in ≤0.15 s on BOTH provers; patched real emission Valid in 0.04 s) (§3) | |
| (b) enumerate-over-array is a pure binding gap | **CONFIRMED as a gap**, with one under-stated co-gap (int-hash leak on the element, §4) | |
| (a) `symbol_table` int-erased to `map string (option int)` | **CONFIRMED verbatim** for a `Dict[str, Any]` param (§5) — but the "needs the faithful-value map build first" boundary framing is **WEAKENED/PARTIALLY REFUTED**: `Dict[str, str]` already lowers to `map string (option string)` in-tree today (§5.2) |
| "≥6 stubs stuck on it and nothing else" | **DIRECTIONALLY SUPPORTED, count-cut at risk**: tuple-unpack appears in the live bodies of **118** trusted stubs (AST census, §6), but 2 of the report's own 3 rows carry co-blockers, so the binder alone converts fewer than the rows suggest |

Bottom line: the wall is real, the split is *more* tractable than the report claims for both (c)
and (a)'s value half, and the proposed make-or-break spike is **already discharged by this review**
— the build should be gated on a different falsifier (§7).

## 1. Count claim — CONFIRMED

```
$ grep -rc '#@ \\trusted' --include='*.py' src/self-annotate/src/ | awk -F: '{s+=$NF} END {print s}'
721
```

Matches the report's "drained to `no_cheap_remaining` at count 721" exactly (the git log's latest
commit message says 727; the tree is 6 ahead of the last ledger commit — the report reflects the
tree, not the log).

## 2. "Machinery already exists" — CONFIRMED at the wall's own oracle plane

### 2.1 Code reality
`src/pycsl/module6_whyml/stmt_control_flow.py` contains exactly what the report names:
`_enumerate_seq_recv` (L700-721, `for i, x in enumerate(<seq local>)`), `_string_char_iter`
(L670-698, `for i, ch in enumerate(<string>)`), and the `.items()` twins `_hval_items_recv`
(L242-262) / `_hval_items_local_recv` (L264-293) feeding `_classify_iterable` (L318+), with the
dual-binding emitted in `_handle_for_stmt`.

### 2.2 Emission + typecheck oracle
The mirror exerciser is `_try_union_is_none_match` (mirror `stmt_control_flow.py` L534, a
**converted** method — contract `requires True / ensures True / assigns self._in_spec`, no
`\trusted`) containing `for i, ctor_name in enumerate(other_ctors)` at L620. Canonical emission:

```
$ PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py --no-proof --keep-mlw \
    src/self-annotate/src/module6_whyml/stmt_control_flow.py --import-path src/pycsl
[level] L1 ✓  L2 ✓  L3-tc ✓
[+] Verification SUCCESS (--no-proof: WhyML generated AND type-checks [L3-tc ✓]; proof skipped).
```

The emitted `stmt_control_flow.mlw` contains the dual-binding loop (lines 2033-2035):

```
variant { (Seq.length !other_ctors) - !_idx__for_target }
let i = ref !_idx__for_target in
let ctor_name = ref (Seq.get !other_ctors !_idx__for_target) in
```

and the items-over-hval dual binding (lines 1819-1820):

```
let ctor_name = ref (hval_keys_get (hval_as_map constructors) !_idx__for_target) in
let ctor = ((hval_values_get (hval_as_map constructors) !_idx__for_target)) in
```

The wall's failure symptom is an **unbound-symbol typecheck error**, so whole-file L3-tc ✓ is the
directly relevant plane: the covered shapes clear the plane the uncovered shapes fail on (my probes
in §4-§5 fail exactly there). Machinery-exists claim CONFIRMED.

Methodological note: emitting with the wrong flag (`--import-path src/self-annotate/src` instead of
the canonical `--import-path src/pycsl` used by `bin/run-self-annotation-suite.sh`) produces a
spurious type error at the emitted `_handle_for_stmt` — reviewers must use the canonical
invocation before concluding anything from a failed emission.

### 2.3 What I could NOT independently redo
The "both PROVE today" half: a `--fun controlflowstmtmixin___try_union_is_none_match` full proof and
a split-VC `why3 prove -P alt-ergo -a split_vc -t 10` on the fun-scoped `.mlw` both exceeded my
~10-minute-per-command budget (terminated, exit 143). Known behavior (whole-file mirror proofs run
70 min+; SMT-timeout ≠ unprovable). I therefore confirm the PROOF claim only indirectly: the
identical loop shape proves in isolation in §3, and the conversion is committed as proven
(28b2eed0 / 38a46208). Flagged, not refuted.

## 3. The load-bearing artifact — case (c) hand `.mlw` PROVES, on both provers

`scratchpad/pair_unpack_spike.mlw`: two modules, both a `while !idx < Seq.length ps` dual-binding
loop with `variant { Seq.length ps - !idx }` and a **non-vacuous** element-wise postcondition
(`Seq.get result i = concat (Seq.get ps i).nm (Seq.get ps i).ty` — the bindings are load-bearing,
fed through the emitter's own `val str_concat_op ... ensures { result = concat a b }` shape from
`preamble.py` L3667):

- `RecordPair`: element `{ nm: string; ty: string }`, bindings `let nm = (Seq.get ps !idx).nm` /
  `let ty = (Seq.get ps !idx).ty`
- `TuplePair`: element `(string, string)`, binding `let (nm, ty) = Seq.get ps !idx`

```
$ why3 prove -P alt-ergo -t 15 pair_unpack_spike.mlw
Goal build'vc.  Prover result is: Valid (0.06s, 170 steps).   # RecordPair
Goal build'vc.  Prover result is: Valid (0.15s, 892 steps).   # TuplePair

$ why3 prove -P z3 -t 15 pair_unpack_spike.mlw
Valid (0.02s, 28053 steps).  /  Valid (0.03s, 30040 steps).
```

**The faithful-pair dual-binding loop proves — termination, bindings, and a real elementwise
invariant — instantly, on both provers, in both element models.** Case (c) is NOT a boundary.

### 3.1 Stronger still: the *exact emitted file*, minimally completed, proves
I ran the live emitter on an isolation probe of the (c) shape (`scratchpad/probe_c_pairs.py`,
`def count_eq_pairs(params: List[Tuple[str, str]])` with `for nm, ty in params`):

```
$ PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py --keep-mlw probe_c_pairs.py --import-path src/pycsl
unbound function or predicate symbol 'nm'      # the report's exact claimed symptom — CONFIRMED
```

Two decisive facts from the emitted `probe_c_pairs.mlw`:
1. The emitter **already** lowers `List[Tuple[str, str]]` to a **faithful record element type**:
   `type pytuple_str_str = { field0: string; field1: string }`, `params: array pytuple_str_str`.
2. The loop skeleton and element read **already emit**
   (`let _for_target = ref (params[!_idx__for_target])`); only the target projections are missing.

Patching ONLY the missing piece (bind `nm`/`ty` to `.field0`/`.field1`, plus the standard
invariant/variant and a `str_eq_op` val — `probe_c_pairs_patched.mlw`):

```
$ why3 prove -P alt-ergo -t 15 probe_c_pairs_patched.mlw
Goal count_eq_pairs'vc.  Prover result is: Valid (0.04s, 17 steps).
```

So (c) is **cheaper than the report states**: it is not "a new dual-binding while-loop" — the
loop, the element read, and the faithful pair type all exist; the build is the target-projection
binder (+ threading the targets' string types into the body, see §4).

## 4. Case (b) — gap CONFIRMED, plus an under-stated co-gap

Probe `probe_b_enum_param.py` (`for i, line in enumerate(out)`, `out: List[str]` param):

```
This expression has type array.Array.array string @rho, but is expected to have type int
```

— enumerate over a non-seq-local falls to the opaque int path (`iter_length (enumerate_1 out)`),
exactly as claimed. **But** the emitted body also shows `if (line <> 313406155)` — the element's
`!= ""` comparison is **int-hashed**. The binder extension alone will not make the body faithful;
the element target must be threaded into `_string_local_vars` (as `_enumerate_seq_recv` already
does for the seq case). The report's (b) row lists `.strip()`/`.startswith` facades as co-blockers
but does not name this element-typing threading; it is small but must be in the build's scope.

## 5. Case (a) — the named type claim CONFIRMED verbatim; the boundary framing WEAKENED

### 5.1 The erasure is real
Probe `probe_a_dictany.py` (`symbol_table: Dict[str, Any]`, `for var, symtype in
symbol_table.items()`):

```
let scan_table (symbol_table: map string (option int)) : int     # exactly the report's type
...
unbound function or predicate symbol 'symtype'                   # exactly the report's symptom
```

(The mirror's current `\trusted` stub is even more erased — its val emits `symbol_table: int`,
mirror `functions.py` L179 annotates the param `int`; the `map string (option int)` shape appears
on a conversion attempt, as probed.)

### 5.2 But the "faithful value type" prerequisite ALREADY EXISTS
The same probe with `Dict[str, str]` emits:

```
let scan_table (symbol_table: map string (option string)) : int   # faithful string values, TODAY
```

(still `unbound symtype` — i.e. with a `Dict[str, str]` annotation the residual gap is the SAME
items-binder as (b)/(c), NOT a value-model build). This machinery is live in the tree: the emitted
mirror `functions.mlw` already has
`let functionemissionmixin___infer_tuple_slot_type ... (symtab: map string (option string))`
(L2064) with a faithful `Map.get symtab !nm` string read (L2090), fed by
`symbol_table_symmap_of func` (L2183).

The live `_emit_union_arm_vc` (live `functions.py` L1060) uses `symtype` purely as a string
(`symtype.startswith("_union_")`, key into `variant_types`), and mirror stubs retype params freely
(the current stub already says `int`), so retyping the mirror param `Dict[str, str]` is available.
What (a) then still needs: (1) the same binder as (b)/(c) over a **native** `map string (option
string)` — which is not finitely iterable, so it needs `keys_get/values_get`-style over-approx
vals, i.e. the device already banked for hval items; (2) the nested `variant_types[symtype]` /
`vinfo["whyml_name"]` / `constructors.items()` reads — for which hval machinery exists
(`_hval_items_local_recv` covers `vinfo.get("constructors", {}).items()` per its own docstring);
(3) a check that live symtable values are never non-str (the `if not symtype` guard hints at
None/"" — the one honest residual risk).

**Reclassification:** (a) is not a value-model boundary needing "the heterogeneous-map
faithful-value build first"; it is the same binder family plus known banked devices, with one open
fidelity check. Keeping it out of this cycle is still defensible (co-blockers), but the stated
REASON is refuted by the oracle.

## 6. Is the frontier tuple-unpack-dominated? — directionally yes; the count-cut is at risk

AST census (python3 `ast` walk): of the 721 `\trusted` stubs, **118** have a live body containing a
tuple-target `for`/comprehension. That is pervasive — far beyond the report's "≥6" — and includes
the report's named rows (`_emit_union_arm_vc`: `symbol_table.items()` + `constructors.items()`;
`_mixin_dep_pseudo_functions`: `COMP:params` ×2; `_find_abstract_val_insert_idx`:
`enumerate(out)` ×2; `_build_method_param_types_map`: `symtable.items()`). So "dominant blocker
class" holds.

However, the report's own table lists co-blockers on 2 of its 3 rows (string facades; value model +
nested facades), and §3 concedes conversions land "ONLY where tuple-unpack is the SOLE blocker".
My probes add one more co-blocker ((b)'s element int-hash). So the **immediate** count cut from the
binder build alone is plausibly < the ≥6 headline; the 118-body census is the reason to build it
anyway (cascade surface), not the near-term ledger delta. No cheaper alternative path was found:
the probes confirm nothing else stands between these shapes and the existing machinery.

## 7. Is the proposed make-or-break the right falsifier? — it WAS; it is now discharged

The report's spike question ("does a hand `.mlw` for the faithful seq-of-pairs dual-binding loop
prove?") is answered **YES** by §3 — on both provers, in both element models, and on the exact
emitter-emitted artifact minimally completed. As a falsifier it no longer carries information: the
adjacent in-tree shape already typechecks whole-file (§2.2), and the isolation proof is 17-892
steps — nowhere near any E-matching cliff.

The build's real residual risks are NOT the loop proof. The impl plan's gate should instead be:

1. **End-to-end conversion of ONE named stub** whose blocker set is smallest — the census suggests
   `_mixin_dep_pseudo_functions`' `{nm: ty for nm, ty in params}` (dict-comp over pairs) or a
   `_build_method_*_map` row — under the standard three L-planes (mirror-sync, whole-file proof,
   corpus byte-diff 0 with `_emitting_*` gating). That tests the parts my spike could not: target
   string-type threading (§4), dict-comp (vs `for`) unpack, and co-blocker interaction.
2. The corpus byte-diff-0 claim for the `List[Tuple[str,str]]` faithful-record path: note my probe
   shows `pytuple_str_str` emission is ALREADY live for corpus-visible annotations, so the new
   binder must be shown inert only where the loop shape newly fires — the report's `_uses_/
   _emitting_` gating discipline (§5 of the report) is the right control; keep it.

## 8. Files

- This review: `getting-better/tuple-unpack-loop-response.md`
- Oracle scratch (outside the tree, per rules):
  `/tmp/claude-1346829620/.../scratchpad/{pair_unpack_spike.mlw, probe_c_pairs.py,
  probe_c_pairs_patched.mlw, probe_b_enum_param.py, probe_a_dictany.py, probe_a_dictstr.py,
  tuim_fun.mlw}`
- No emitter/mirror edits; no commits; no background processes left running.
