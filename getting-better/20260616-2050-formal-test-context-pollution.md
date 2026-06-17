# Proof-context pollution: a theorem that proves ALONE fails when co-located

## Observation

Authoring os fd-chain formal tests, several theorems that PROVE when alone in a
file FAIL (SMT `Unknown`) when co-located in the same module with a heavy
`read`/`write` consequence theorem. The theorem body and the import set are
BYTE-IDENTICAL between the passing and failing cases — only the set of OTHER
theorems in the module differs.

Concrete:
- `open_existing_yields_valid_fd(p)` and `whole_file_read_returns_size(p, c)`
  each prove `SUCCESS` in a one-theorem file (full `pure_lib.os` fd import set).
- The SAME bodies FAIL `Unknown` when the module also contains the heavy
  `content_round_trip` / `content_round_trip_count` theorems (which chain
  `open → write → close → reopen → read` and reason over the disk/inode arrays).
- `pure_lib_test/formal_os_fdchain.py` proves four fd-chain theorems TOGETHER —
  so light fd-chain theorems co-exist fine; the poison is specifically the
  array-heavy read/write reopen chain dragging the shared E-matching context
  past the solver's step budget for the sibling goals.

## Why it matters

This is a silent trap for the formal-test author: a green theorem can go red
purely by being added next to an unrelated heavy one, with no contract or body
change. The natural debugging reflex ("my theorem is wrong / a contract is
missing") is wrong — the theorem is fine; the module is over-loaded. It cost a
mis-diagnosis cycle this session (a theorem was first blamed on a missing
contract, then found to prove in isolation).

## Suggested ergonomic improvements (any one would help)

1. **Per-goal context isolation flag.** A `--isolate-goals` (or per-function
   fresh Why3 session) mode that proves each VC in a context containing only the
   declarations it transitively needs, so a heavy sibling cannot starve a light
   goal's step budget. (Slower, but deterministic per-goal.)
2. **A diagnostic hint.** When a goal returns `Unknown` at a low step count but
   the same goal proves under `--fun NAME` isolation, emit a note:
   "goal X proves in isolation but not in-module — likely context pollution;
   consider splitting the file." This turns a silent red into an actionable one.
3. **Author guidance (already actionable today):** keep array-heavy
   reopen/read/write consequence theorems in their OWN file, separate from light
   fd-chain / namespace theorems. (This session split `content_round_trip*` out
   of `formal_os_fd.py` / `formal_os_rwsize.py` for exactly this reason.)

## Repro sketch

```
# proves:
printf 'from pure_lib.os import open, close, fstat, O_RDONLY, O_WRONLY, O_CREAT\n#@ requires True\n#@ ensures \\result == 1\ndef t(p: str) -> int:\n    f0 = open(p, O_CREAT | O_WRONLY, 0o777)\n    if f0 < 3:\n        return 1\n    close(f0)\n    f = open(p, O_RDONLY, 0o777)\n    if f >= 3:\n        return 1\n    return 0\n' > /tmp/a.py
PYTHONHASHSEED=0 PYTHONPATH=src/pycsl .venv/bin/python -m pycsl /tmp/a.py   # SUCCESS
# add a content_round_trip(open→write→close→reopen→read, assert n_read==len(c))
# theorem to the same file → the open theorem above flips to Unknown.
```

## Context

Surfaced during the test-supervise-sl os-coverage mission (close/lseek leaf-first
+ repair of the stale fd/rwsize/meta/query/dir formal tests).
