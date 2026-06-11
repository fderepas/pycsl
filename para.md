# Could these tasks be executed in parallel?

**Verdict: Mostly NO.** The run is an inherently sequential pipeline threaded
through a single file. Only the two read-only `grep` exploration calls (steps 3
and 4) can be lifted out and run in parallel — with each other and with the rest
of the chain.

## The sequence

| # | Action | Touches `__init__.py`? | Kind |
|---|--------|------------------------|------|
| 1 | Update `pure_lib/os/__init__.py` | **write** | edit |
| 2 | `pycsl.py --no-proof --keep-mlw … \| tail -25` | **read** | typecheck/emit |
| 3 | `grep … Module2_Parser.py \| head -40` | no (other file) | read-only |
| 4 | `grep -rn … pure_lib/ --include=*.py \| … head -30` | no (scan) | read-only |
| 5 | Update `pure_lib/os/__init__.py` | **write** | edit |
| 6 | Update `pure_lib/os/__init__.py` | **write** | edit |
| 7 | `pycsl.py --no-proof --keep-mlw … \| tail -25` | **read** | typecheck/emit |
| 8 | `pycsl.py … \| tail -30` (full proof, timeout 595) | **read** | prove |
| 9 | wait-loop polling proof process + tailing output | depends on 8 | wait |

## Dependency graph

```
            (independent, read-only)
   [3] grep Module2_Parser.py ─┐
   [4] grep pure_lib/ scan ────┘   no edges to/from the chain

   The serial pipeline (data dependency through ONE file):

   [1] edit ──> [2] typecheck ──> [5] edit ──> [6] edit ──> [7] typecheck ──> [8] prove ──> [9] wait
        \________________________/                              ^
         each typecheck/prove reads the file's CURRENT content,
         so it must follow every edit that precedes it
```

Edges (X → Y means "Y must wait for X"):

- `1 → 2` — typecheck reads what edit 1 wrote.
- `1 → 5 → 6` — three writes to the **same file** are strictly ordered: each
  edit operates on the text the previous edit produced. Parallel writes to one
  file race/clobber, so they cannot be reordered or concurrent.
- `5 → 7`, `6 → 7` — the second typecheck reads the file after both later edits.
- `6 → 8` — the full proof verifies the **final** edited content.
- `8 → 9` — the wait-loop polls the process that step 8 launched.
- `3`, `4` — **no incoming or outgoing edges.** Pure read-only inspection of
  *other* files (`src/pycsl/frontend/Module2_Parser.py` and a `pure_lib/` scan).
  Independent of the edits and of each other.

## What can actually be parallelized

- **Steps 3 and 4 with each other** — two independent read-only greps.
- **Steps 3 and 4 with the edit→typecheck→prove chain** — they could be fired at
  the very start (e.g. while the first `Update` is still being composed) and
  their output consumed whenever it lands. They block nothing and are blocked by
  nothing.

## What cannot

- **Edits 1, 5, 6** — sequential by construction (same file; later edit depends
  on earlier edit's result; concurrent writes would clobber).
- **Typecheck/prove 2, 7, 8** — each reads `__init__.py`'s *current* content, so
  each must follow the edits before it. They sit on the critical path.
- **Wait 9** — definitionally tied to the process started by 8.

## The real cost, and the general case

The dominant serial cost is the **two proof runs back-to-back**: the quick
`--no-proof` typecheck (`timeout 120`, steps 2 and 7) plus the full proof
(`timeout 595`, step 8). They cannot overlap *here* because step 8 proves the
file as it exists only after edit 6 — there is a true data dependency.

In **general**, though, *independent* proof targets (different files / different
functions with no shared edit) are exactly what parallelizes well: that is what
`bin/byte-diff-sweep.sh` exploits with its half-CPU `xargs -P $((nproc/2))` fan
-out. The constraint in this run is not that proving is unparallelizable — it is
that every step after the first edit reads from the same evolving file.

## Bottom line

The core `edit → typecheck → edit → edit → typecheck → prove → wait`
(1→2→5→6→7→8→9) is an irreducibly sequential pipeline. Only the two read-only
greps (3, 4) are off the critical path and can run concurrently — with each
other and alongside the chain.
