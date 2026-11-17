# Run #8 lvX report (WIP)

Executor lvX, driver run #8 batch C. Tree `/home/fabrice/git/pycsl-lvX`, branch `run8-lvX`, base 0057c8b94.
Evidence: `scratchpad/lvX/` in the tree (`L/` gate logs, `p/` probes, `w1/` witness emissions).

## Stub 1 `_sha256_file` (pycsl.py) -- gates in progress

- --fun: SUCCESS, 754 goals Valid, 0 non-Valid, oom 0->0 (`scratchpad/lvX/L/fun._sha256_file.log`).
- leaf `#@ assert 1 == 2` at the head: FAILS (only that assertion, Timeout) (`L/var.leaf.log`).
- mutant `_n7 = 7 // len(path)`: FAILS (division-by-zero goal) (`L/var.mut.log`).
- fuzz live chunked vs respelled body: 219 cases, 218 identical, 1 same-family difference
  (`""`: FileNotFoundError vs IsADirectoryError, both OSError) (`scratchpad/lvX/fuzz_sha.py`).
- fidelity x3 rc 0 (`L/E.txt`).
- witnesses 10140-10145: hoare as expected; typed/store 10140 FAILED (under investigation).
