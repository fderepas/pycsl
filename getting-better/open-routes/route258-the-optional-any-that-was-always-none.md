# OPEN ROUTE #258 — `Optional[Any]` / `Any | None` IS LOWERED WITH ONLY THE `None` ARM

**Status: REPAIRED (gen #36, 2026-10-17; opened the same day), Severity 1.** Residual of the #254/#255 repair; driver-reproduced at
HEAD 6f8937b1: `u_Optional_Any__.py` and `u_Any___None_.py` rc=0 (CPython 6, claim `\result == 5`).

## Witness (`witnesses-r258/u_Optional_Any__.py`)
    def f(x: Optional[Any]) -> int:     # ensures \result == 5   <-- PROVED
        if x is not None:
            return 6
        return 5
Siblings: `Any | None`, `Optional[object]`, `Union[Any, None]`, `Union[int, Any]` (check each).

## Mechanism
Module 5 `_normalize_union_annotation` drops the `Any` arm (GT1); `core_ir_semantic` only warns. The parameter
becomes a union whose only inhabitant is `None`, so `x is not None` is dead in the model.

## Repair direction
A union containing `Any`/`object` (or an unknown arm) must lower to an erased value (Any) — never drop the arm;
or refuse. Measure corpus/mirror blast radius of the normalization change (M1).

## Repair landed (gen #36, 2026-10-17)

### Step 1: census (base 183c35a2, measured before any code)
A static walk over every `Optional[...]` / `Union[...]` / `X | Y` parameter, return and annotated-assignment
annotation, classifying each arm with `_union_arm_tag`'s own rules: root 0 files, pyref 0 files, mirror 7 sites
in 4 files (`Optional[_Tok]` x5 in `pure_ast`/`Module2_Parser` -- `_Tok` is a record there, so kept --,
`Optional[subprocess.Popen]` in `proof2why3/sertop`, `Optional[Any]` in `module6_whyml/expressions`). Probes
(`probe-base.log`): PROVED at base, FALSE in CPython: `Optional[Any]`, `Any | None`, `Optional[object]`,
`Union[Any, None]`, `Optional[Optional[Any]]`, `Optional[Sequence[int]]`, `Optional[Callable[[int], int]]`,
`Optional[foo]` (lowercase class). `Union[int, Any]`, `Union[int, str, Any]` and the `-> Optional[Any]` return /
`x: Optional[Any]` local seams FAILED at base (the dropped arm left an `int`-only variant, or L3-tc refused
`return y` into the None-only type); `Optional[T]` (TypeVar) and `Optional[List[Any]]` keep a real payload arm and
FAILED at base.

### Step 2: the rule
In `_normalize_union_annotation` (mirror twin `\trusted`; inline, no new def, ledger 3): if ANY arm is one
`_union_arm_tag` answers `Any` for (`Any`, `object`, a lowercase/unknown name, a nested `Optional`/`Union`, an
unmodelled generic, a quoted non-IR name), the WHOLE annotation lowers to the erased `Any` tag instead of a variant
with that arm dropped. The value may be any Python object, so it is one: route #249/#251/#252's erased treatment
(an `Any` formal/field, a `-> Any` result; uninterpreted `==`/arithmetic; the #252 refusal into builtin slots)
applies to it unchanged, and `x is not None` is `not (x = pycsl_none)` over a free value. The per-site union index
is still consumed so every other synthesized union keeps its name. Nothing is refused; the GT1 `union_gt1_sites`
warning no longer fires because nothing is dropped. `Optional[T]` with a TypeVar keeps its two-armed variant with
an opaque payload (relaunch #17), untouched.

### Blast radius and gates (logs: `/tmp/claude-1000/-home-fabrice-git-pycsl/7bdb4936-b536-4d12-86b7-7ad1b607106c/scratchpad/r258/`)
- Witnesses (`witness-base.log`, `witness-after.log`): 2580 `Optional[Any]`, 2581 `Any | None`, 2582
  `Optional[object]`, 2583 `Union[Any, None]`, 2584 `Optional[Optional[Any]]`, 2585 `Optional[Sequence[int]]`,
  2586 `Optional[Callable[[int], int]]`, 2587 `Optional[foo]` -- each PROVED at 183c35a2, FAILS after (prover
  Unknown, file type-checks). Coverage 2588 (`-> Optional[Any]` return; L3-tc FAIL at base, prover FAIL after),
  2589 (`Optional[Any]` record field; FAIL both). Controls: 2590 `Optional[int]` narrowing PASS both, 2591 a true
  claim over `Optional[Any]` PASS both, 2592 `Optional[T]` false claim FAIL both. CPython ground truth in each
  `__main__`.
- Corpus byte-diff vs a fresh 183c35a2 worktree: root 1697 baseline / 1710 candidate, 0 MOVED, 0 GONE, 0 APPEARED,
  13 new sources (`compare-root.log`); pyref 2197 / 2197, 0 MOVED/GONE/APPEARED (`compare-pyref.log`). No mover,
  so no M1 re-proof is owed.
- Mirror (`compare-mirror.log`): 53/53, 3 MOVED, 0 GONE, 0 APPEARED: `ir_schema` and `proof2why3/sertop` each
  lose one UNREFERENCED None-only type declaration (`_union_functionir_16`, `_union_sertopsession_3`);
  `module6_whyml/expressions` loses `_union__dotted_ensures_suffix_4` and the abstract `val` of
  `_dotted_ensures_suffix` takes `(field_spec: int)` (its `Optional[Any]` formal, now erased) instead of the
  None-only type. `why3 --type-only` rc=0 for all six (`mirror-typeonly.log`); `ir_schema` and `sertop` whole-file
  re-proved after (`mirror-prove-*.log`, SUCCESS). `module6_whyml/expressions` whole-file proof: OWED (big file;
  the change is one abstract `val` signature).
- Planes 61/61 incl. `frontend-only-conformance` / `core-only-conformance` (no IR golden carries a dropped
  `Any` arm; `planes.log`); `check-self-annotate-sync.sh` rc=0 (917 verbatim, `sync.log`);
  `self-annotate-mirror-check.sh` rc=0 (`mirror-check.log`). The only edited live method
  (`_normalize_union_annotation`) has a `\trusted` mirror twin: no re-port. Docs: static-semantics τ(Union),
  translational §T.14 `Any` arm, `test-suite/annotations.md` Union entry.

## Residuals (NOT repaired here)
- `Optional[T]` (TypeVar) / `Optional[C]` (non-record class) keep an OPAQUE `int` payload that is not route
  #249-erased once narrowed (`x == y` on two narrowed payloads is Why3 `=`); the probe `q_opt_T_eq.py` (symmetry
  through two `Optional[T]` payloads) does NOT prove at base or after, so no witness was found.
- Container element annotations (`List[Optional[Any]]`, `Dict[str, Optional[Any]]`) do not go through this seam.
