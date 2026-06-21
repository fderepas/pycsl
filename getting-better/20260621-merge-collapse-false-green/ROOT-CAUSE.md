# Root cause: the "tool vacuity" was a SOUNDNESS bug in the best-of-N prover merge

Date: 2026-06-21
Branch: `os-exception-rootcause`

## TL;DR

The apparent corpus-wide "vacuity" the non-vacuity gate flagged on the os/csys
formal tests is NOT logic-context inconsistency. It is **two distinct defects**,
the first of which is a genuine **soundness bug that produced FALSE GREENS**:

1. **Merge collapse (soundness bug, FIXED).** `_merge_best_of_n` keyed each
   sub-goal by its *header* alone. `why3 prove -a split_vc` emits SEVERAL
   sub-goals that share a byte-identical header — e.g. the then-branch and
   else-branch obligations of one postcondition sit at the SAME source line and
   carry the SAME `Sub-goal Postcondition of goal f'vc.` text. Keying by header
   collapsed those distinct sub-goals into one, so a **Valid sibling MASKED a
   non-Valid one**. Any function with an unproven branch obligation co-located
   with a Valid one reported `Verification SUCCESS` while a real goal was never
   discharged.

2. **Gate dead-branch over-flagging (precision issue, separate).** `_probe_one`
   flags a function "vacuous" if ANY sub-goal proves `ensures { false }`. A
   *statically-dead* branch (e.g. the `else` of `if getpid()==1` when `getpid`'s
   ensures pins `result=1`) ALWAYS proves `false` — soundly, because it is
   unreachable. The gate therefore false-flags sound consequence-tests of the
   shape `if (property-the-callee-guarantees) return 1 else return 0`.

## How it was found

`getpid_constant` (body: `if getpid()==1 then return 1 else return 0`, with
`val getpid ensures result=1`) reported `Verification SUCCESS` for the FALSE TWIN
`ensures \result == 2`. Bisecting the actual proved module:

```
why3 prove -a split_vc -P z3 -t 30 <module>     # pycsl's real first pass
  Sub-goal Postcondition of goal getpid_constant'vc.  Timeout (then-branch, live)
  Sub-goal Postcondition of goal getpid_constant'vc.  Valid 762 steps (else-branch, DEAD)
```

Two postconditions at the same line. pycsl's *merged* output showed only ONE
(the Valid 762) — the Timeout then-branch was dropped → false SUCCESS.

Independent confirmation the context is NOT inconsistent: an `ensures { false }`
probe touching `_filesystem` times out at 120s on BOTH alt-ergo and z3 (no solver
derives `false`). So `getpid_constant` is SOUND; the false-green came purely from
the merge collapse.

## The fix (pycsl.py `_merge_best_of_n`)

Key sub-goals by `(header, occurrence-index-within-one-prover-output)` instead of
`header` alone. `split_vc` is deterministic, so the k-th occurrence of a header
denotes the SAME sub-goal across provers; align by occurrence and merge per
sub-goal. Distinct-line goals keep occurrence 0 — behaviour unchanged for them.

Verified:
- `getpid_constant` real test (`\result==1`) → SUCCESS (no false failure)
- `getpid_constant` false twin (`\result==2`) → FAILED (then-branch surfaces)

## Blast radius

- Formal suite `src/pycsl_lib_test/formal_*.py`: **120 / 121 still PASS**. The
  ONLY newly-RED test is `formal_os_close.py` — a genuine false-green (see below).
- Reference corpus `test-suite/corpus/pycsl-reference/`: sweep in progress.

## `formal_os_close.py` was a genuine false-green

`close_makes_fd_unusable` has THREE postcondition sub-goals; one timed out and was
masked. The contract chain does NOT actually compose: `fstat`'s contract
(`raises { OSError -> true }`, plus value-ensures) **permits fstat to return
normally on a CLOSED fd** — nothing forces it to raise EBADF when
`fd_open[fd]=0`. So the `return 0` path stays reachable and `\result==1` is
unprovable.

Honest fix (confirmed: makes the test prove cleanly, both sub-goals Valid):
add an EBADF normal-return ensures to `fstat` —

```
ensures { (fd < 64) -> (_filesystem.fd_open[fd] = 1) }   (* normal return only on an OPEN fd *)
```

This is faithful POSIX EBADF semantics and MUST be backed by the kernel
`sys_fstat` (no bare trust) before landing.

## Follow-ups

- [ ] Land the merge fix (done in working tree).
- [ ] Fix `formal_os_close` honestly via the `fstat` EBADF contract, backed by
      `sys_fstat`.
- [ ] Refine the vacuity gate so a statically-dead branch alone does not flag a
      function as vacuous (defect #2 — precision).
- [ ] Re-audit any corpus test the merge fix turns RED: each is a previously-
      hidden non-proof, not a regression.
