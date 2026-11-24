# Run #9 u67 report: `SertopSession.type_of_batch` converted (VERIFIED), `parse_format` measured, not converted

Executor u67, driver run #9, self-tcb-reduction base loop.

- Branch `run9-u67` in the tree `/home/fabrice/git/pycsl-u67`. Base `ghost-assign-bc6` = **e0d77c919** (log 1319: L20 LANDED).
- Commits:
  - d877e5177: the conversion (emitter and mirror);
  - 50bbf1141: WIP evidence;
  - 9d01f76d3: the trusted-reasons row is dropped;
  - this report.
  - Never pushed.
- Base tree (detached at e0d77c919): `/home/fabrice/git/pycsl-u67b`. Head snapshot tree (detached at d877e5177): `/home/fabrice/git/pycsl-u67h`.
- Paths are relative to `scratchpad/u67/` unless absolute.
- Every heavy job went through `heavy.sh` (NORMAL; probes HEAVY_QUICK) with `PYTHON_CPU_COUNT=2`. The slice `oom_kill` counter was **15 at the start and end of every proof and sweep** (`pr/summary.txt`, `logs/G.out`).
- Time box: the 10:00Z box was overrun. The master gate job ended at 08:43Z, but the session was stopped by an API rate limit from about 07:05Z and resumed at 11:24Z. The trusted-reasons fix and its re-check were done after the resume.

## 1. Verdict

`SertopSession.type_of_batch` (proof2why3/sertop.py) is **VERIFIED**:
- the live body is ported verbatim;
- the contract is type-safety plus frame (`requires True / ensures True / assigns \nothing`);
- the whole-file proof of sertop.py passes: 64 goals, 0 non-Valid, and the non-vacuity gate passes.

`\trusted` goes from **366 to 365**, counted as `grep -rhF '#@ \trusted' src/self-annotate/src --include='*.py' | wc -l`. The base value was measured in u67b and the head value in u67h.

`parse_format` was measured only (section 7). It needs two emitter links plus two live rewrites, and it was not attempted inside the time box.

## 2. The measured chain (re-measured at e0d77c919, after L18's Path model)

All probes are `--no-proof` (Why3 type-check) emissions of a scratch copy of the mirror in `st/` (`git archive HEAD bin src`).
- Driver script: `probe.sh`.
- Variant files: `v/*.py`; logs: `v/*.log`.
- Each run passes `--verification-image`.

| step | variant | verdict |
|---|---|---|
| verbatim port of the live body and the live return `-> Dict[str, object]` (also on the `run_sertop_batch` stub) | `v0` | REFUSED **R614**: `self.load_paths` (`List[Path]`) is passed to the stub's *unannotated* `load_paths` parameter. NEW since the census: L18 (lvZ2 / R614). |
| [T] the `run_sertop_batch` stub gets `load_paths: List[Path]` | `v1` | REFUSED **R487**: `self.cwd or Path.cwd()` is used as a value. Same as cv15 `k341_0`. |
| [R] census rewrite `if self.cwd is not None: … else: …` (rejected route, kept for the record) | `v2` | REFUSED R325: `SertopSession.cwd` (`Optional[Path]`) is an opaque int |
| capability **A1**: the field lowered as `option string` | `v3` | L3-TC: `self.cwd = pycsl_none`; a `ref int` local shadows the `cwd` field label |
| [R] variants `v4`–`v8` (IfExp, renamed local) | — | each still needs the option read *and* a string-typed local. The `or` arm (A2) makes both unnecessary, so **no live rewrite is used** |
| capability **A2** (the option match for `self.f or y`) + **A3** (`_is_string_expr` of the same shape) | `v9` | L3-TC: the omitted `require_prefix: Optional[str] = None` is filled with the int `pycsl_none`, but the parameter's type is `_union_run_sertop_batch_1`. This is census link 2. |
| capability **B** (the union None arm fills the omitted default) | `v10` | **TC-OK** |

So the chain closed with:
- **two links**: A, which is A1 + A2 + A3, and B;
- one free [T] on the trusted stub's interface: `load_paths: List[Path]` and the live return type `Dict[str, object]`.

The census's [R] live rewrite was **not** needed: the mirror body is byte-verbatim the live body `cwd = self.cwd or Path.cwd()`.

The [T] narrows the stub's declared `load_paths` domain. The live function also accepts `(Path, name)` tuples. This only narrows the stub's interface premise:
- its two mirror callers pass a `List[Path]`: `type_of_batch`, and the trusted `extract_via_sertop` with `[proof_dir]`;
- the live code is unchanged.

## 3. Capability edits (d877e5177; every edited method has a `\trusted` mirror twin or none)

| file / method | mirror twin | change |
|---|---|---|
| `frontend/Module5_IREmitter.py` `_M5_OPTION_FIELD_ALLOWLIST`, `_m5_get_option_field_inner` | ABSENT from the Module5 mirror | `("SertopSession", "cwd")` is allow-listed. `Optional[Path]` maps to value_type `"path_str"`, for allow-listed fields only. |
| `module6_whyml/preamble.py` `_emit_type_decls` | `\trusted` | a `path_str` option field becomes `option string` (the #31 Path-as-string model of a `Path` parameter) |
| `module6_whyml/expressions.py` `_handle_binop` | `\trusted` | `self.<path_str option field> or <y>` in body context becomes `(match self.f with Some _p67 -> _p67 \| None -> <y> end)`. This is faithful because a `pathlib.Path` is always truthy (no `__bool__` / `__len__`). A non-string `y` is a Why3 type error, so it fails closed. |
| `module6_whyml/expressions.py` `_is_string_expr` | `\trusted` | the same shape is string-typed when `y` is, so the local is let-bound as a string (`let cwd = ref (match …)`), not `ref 0` |
| `module6_whyml/expressions.py` `_handle_call_expr` (module-function default fill) | `\trusted` | for an omitted `None` default whose callee parameter symtype (read from this unit's IR) is a synthesized `_union_*`, the fill is that union's nullary None arm. It replaces the int `pycsl_none`, which is ill-typed against the union. |

- No edit touches `pycsl.py` (and so nothing between `_BODY_EQ_RE` and `def main`), and none touches `frontend/ir_resolve.py`.
- No new `\trusted`, no axiom, no gate change.
- `proof_axiom_allowlist.py` is unchanged: 0 diff lines vs e0d77c919 (`logs/G.out`).

**Soundness of the Path-as-string model.** The new string local carries a Path's value. R614's AST pass treats `cwd = self.cwd or Path.cwd()` as path-ish, because a boolean of a path-ish value is path-ish. So any comparison of `cwd` with a str stays refused. Any other use of the `option string` field is a Why3 type error:
- `is None`, which lowers to `= pycsl_none`;
- a truth test, which lowers to `<> 0`;
- `str()`.

## 4. Mirror (sertop.py) and contract

```python
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def type_of_batch(self, require_module: str, qualnames: List[str]) -> Dict[str, object]:
        cwd = self.cwd or Path.cwd()
        return run_sertop_batch(self.load_paths, cwd, require_module, qualnames)
```

The emitted body (`pr/whole.mlw`):

```
let cwd = ref (match self.cwd with Some _p67 -> _p67 | None -> (ext_path_cwd_op ()) end) in
(run_sertop_batch self.load_paths !cwd require_module qualnames 60.0 Arm_1_None)
```

- The record is `cwd: option string`.
- The body reads both `self.cwd` and `self.load_paths`.
- The raises set is lvQ's OS family, from `Path.cwd()`.
- This is a THIN delegation to the trusted `run_sertop_batch`, as the census said, so its value is low.
- Premise inherited from the trusted stub (lesson 13): `run_sertop_batch` declares no raises, while live `Popen` can raise OSError. This is a pre-existing trusted-stub premise and was not changed.

## 5. Proofs (`proofs.sh`, summary `pr/summary.txt`; oom_kill 15 before and after each)

| run | command | result | log |
|---|---|---|---|
| `--fun sertopsession__type_of_batch` | pycsl.py sertop.py --fun … --import-path src/pycsl --verification-image src/self-annotate/src | rc 0, SUCCESS (05:56–05:57Z) | `pr/fun.log` |
| **whole file** sertop.py | same, without `--fun` | **rc 0, "All contracts formally proven"**: 64 Valid, 0 non-Valid; the non-vacuity gate passed (it prints only on failure) | `pr/whole.log`, `pr/whole.mlw` |

## 6. Leaf reachability and mutation

- **Leaf** (`#@ assert 1 == 2` at the head of the single body block, one `--fun`): **NOT proved**. The assertion goal of `sertopsession__type_of_batch` timed out, rc 1, so the body is reachable (`pr/leaf.log`).
- **Arm reachability**, checked on the emitted whole-file `.mlw`:
  - **Some arm → `absurd`**: the "Unreachable point" goal of type_of_batch is **not proved** by either z3 or alt-ergo (rc 2), so the Some arm is reachable (`pr/arm_some_{z3,alt-ergo}.log`).
  - **None arm → `absurd`**: Why3 *rejects* the program because the declared raises set is no longer raised ("does not raise exception BlockingIOError"). So the None arm is the only source of the OS-family effect (`pr/arm_none_*.log`).
  - A cleaner variant, `None -> (let _w = ext_path_cwd_op () in absurd)` in `pr/arm_none2.mlw`, is prepared but **NOT RUN**. Its heavy job (`fin.sh`) sat queued behind the driver's PRIO job from 11:24Z to 11:55Z, well past the time box, so I killed it (it never started; it was mine, checked by its parent chain).
- **Mutation 1** (`self.seq = self.seq + 1` added, which violates `assigns \nothing`): **FAILS**. The postcondition goal `self.seq = old self.seq` timed out under both provers (`pr/mut_frame.log`).
- **Mutation 2** (`cwd = self.cwd or self.seq`, an int fallback): **rejected** at Why3 type-check (`pr/mut_type.log`). The non-string `or` is not taken by the new arm, so the local takes the int `ref 0` pre-decl, and that pre-decl shadows the field label. It fails closed, but through the shadowing error, not through the arm's own type check.

## 7. `parse_format` (module6_whyml/struct_format.py): measured, NOT converted

Same probe harness; the variants are `v/p0.py`–`v/p2.py`.

| step | verdict |
|---|---|
| p0, verbatim port (the mirror class is stale: `slots: List[str]`, no `chars`) | REFUSED R369: unexpected keyword `chars` |
| p1, [T] class sync: `slots: Tuple[str, ...]`, `chars: Tuple[str, ...] = ()` | REFUSED: `slots.extend(...)` has no certified mutation lowering |
| p2, [R] `for _ in range(count): slots.append(slot_type); chars.append(char)` | REFUSED R325: `tuple(slots)` is the opaque `tuple_1` (link 1: `tuple(<list>)` into a variadic `Tuple[str, ...]` field) |

After link 1, cv15's `k315_T1S` wall remains: an `Optional[StructFormat]` return whose record has array fields (a mutable exception payload). That is link 2. It would retype `slots` to a pure carrier, and so move the VERIFIED `arity` / `slot_id` lowering.

Total: two emitter links, plus two live rewrites ([T] and [R]), plus a struct_format whole-file re-proof. The chain is unchanged from cv15 in substance.

## 8. Gates

Base = `/home/fabrice/git/pycsl-u67b` (e0d77c919); head = `/home/fabrice/git/pycsl-u67h` (d877e5177). Each sweep ran with cwd = its own tree root, in one NORMAL job (`master.sh`, output in `logs/G.out`).

| gate | result | log |
|---|---|---|
| byte-diff root, base vs head | rc 0: **3329 / 3329** .mlw, 0 MOVED, 0 GONE, 0 APPEARED (emitted 3330 on each side) | `logs/G/C-root.txt`, `sw/{base,head}/bd.log` |
| byte-diff pyref | rc 0: **2185 / 2185**, 0 / 0 / 0 | `logs/G/C-pyref.txt` |
| mirror sweep (53 / 53) + `diff -rq` | **1 MOVED: `proof2why3__sertop.mlw`**, which is the converted file. Its whole-file proof is in section 5. | `logs/G/C-mir.txt`, `logs/G/diffrq-mir.txt` |
| check-self-annotate-sync.sh | rc 0 | `logs/G/sync.txt` |
| self-annotate-mirror-check.sh | rc 0 | `logs/G/mircheck.txt` |
| doc-coherency --check | rc 0 | `logs/G/doccoh.txt` |
| check-assigns-writes-survival (head single-underscore mirror emission, 53 files) | rc 0 | `logs/G/lg/check-assigns-writes-survival.txt` |
| check-trusted-frame-honesty | rc 0 | `logs/G/lg/check-trusted-frame-honesty.txt` |
| check-getattr-erasure | rc 0 | `logs/G/lg/check-getattr-erasure.txt` |
| run-soundness-planes.sh fast, at d877e5177 | rc 1: 61 / 62 ok. The only red plane is **check-trusted-reasons**: the converted stub's row was still in `getting-better/trusted-reasons.tsv`. | `logs/G/planes.txt` |
| check-trusted-reasons after 9d01f76d3 (row deleted) | rc 0: 337 markers ↔ 337 rows | `logs/trusted-reasons.txt` |
| run-soundness-planes.sh fast, at 9d01f76d3 | **NOT RE-RUN** (same queued `fin.sh` job, killed before it started). The one red plane was re-checked directly, and the fix changes only the TSV. The driver should re-run the fast planes at 9d01f76d3. | `logs/planes2.txt` |
| count-trusted-directives | rc 0 | `logs/G/count-trusted.txt` |
| `\trusted` (canonical grep) | 366 → **365** | `logs/G.out` |
| proof_axiom_allowlist diff vs base | 0 lines (ledger stays 3) | `logs/G.out` |

The emitter edits are inert for the corpus: 0 MOVED in both root and pyref. So no corpus file owes a re-proof (M1: none).
