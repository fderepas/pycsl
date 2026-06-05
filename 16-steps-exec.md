# Minimal standard-library stubbing — executable plan (16 steps, 0–15)

Executable form of `16-steps.md` for:

```
./bin/agent-feature-supervisor --allow-llm-delegation --allow-load-bearing --feature-file 16-steps-exec.md
```

Each phase follows the worked example in `unix-filesystem/` (`UnixInodeFileSystem.py`
state class + `my_os.py` stub + `my_os_demo.py` formal driver). For each standard
library module the delegate must produce, with **no `\trusted`**:

1. **State / returned-type classes with contracts** (like `class UnixInodeFileSystem`)
   for any global state or types the library returns.
2. **Annotated Python stub** of the module in `src/pycsl_lib/<mod>.py` — verifies
   under `pycsl.py`, carries real `#@` contracts, contains **zero** `\trusted`.
3. **A formal test driver** beside the stub (`src/pycsl_lib/<mod>_demo.py`, the
   `my_os_demo.py` analog) that exercises the stub's contracts end-to-end.

References when in doubt: `unix-filesystem/` (syscall-stub example),
`config/skills/unix/` (unix concepts), `test-suite/library_reference/` (official
CPython behaviour).

> **Execution note.** Most phases live in `src/pycsl_lib/` (not load-bearing).
> A few (Phase 3 `ast`, and the self-annotation hooks) must edit the
> parser/IR/emitter pipeline — those are load-bearing, which is why this plan is
> run with `--allow-load-bearing`. Every delegated edit must still pass the gate
> or it is rolled back, and the surviving diffs require human review before
> merge. The `**Acceptance:**` block of each phase is its machine-checkable
> definition of done, re-verified on every supervisor run.

## Implementation surface

### Phase 0 — os + builtin prerequisites

**Level:** L2

Highest-leverage prerequisite. Lift the `unix-filesystem/` example into the stub
tree: merge `my_os.py` into `src/pycsl_lib/os.py` and copy
`UnixInodeFileSystem.py` under `src/pycsl_lib/os/`. Also close the builtin gaps
the toolchain flags (`isinstance`, set ops, dict membership, `open`) in
`src/pycsl_lib/builtins.py`. Driver: `src/pycsl_lib/os_demo.py` (the
`my_os_demo.py` analog).

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/UnixInodeFileSystem.py`, `unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/os.py` exits 0
- `test -f src/pycsl_lib/os/UnixInodeFileSystem.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/os.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/os.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/os_demo.py` exits 0

### Phase 1 — os.path (pure path algebra)

**Level:** L5

Pure string functions, no FS state: `join`, `dirname`, `basename`, `splitext`,
`normpath`. Fastest ROI. Stub `src/pycsl_lib/os/path.py`; driver
`src/pycsl_lib/os/path_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/os/path.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/os/path.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/os/path.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/os/path_demo.py` exits 0

### Phase 2 — io + builtin open (stream state)

**Level:** L2

Model the stream layer (position, buffer contents, open/closed state) — what
`open()` returns and what `Module1_Ingestor` consumes. A stateful class with
contracts (like `UnixInodeFileSystem`) plus the `open` builtin. Stub
`src/pycsl_lib/io.py`; driver `src/pycsl_lib/io_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/UnixInodeFileSystem.py`, `unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/io.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/io.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/io.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/io_demo.py` exits 0

### Phase 3 — ast (the parser-verification gate) — LOAD-BEARING

**Level:** L2

Model the AST node zoo + `NodeVisitor` dispatch as an algebraic data type — the
prerequisite to body-verifying `Module2_Parser.py` / `Module3_Weaver.py`. Stub
`src/pycsl_lib/ast.py`; this is the one phase that edits the load-bearing
pipeline (`src/pycsl/Module2_Parser.py`, `src/pycsl/Module3_Weaver.py`,
`src/pycsl/module6_whyml/preamble.py`) to thread the node model. Driver
`src/pycsl_lib/ast_demo.py` exercising visitor dispatch.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/ast.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/ast.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/ast.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/ast_demo.py` exits 0

### Phase 4 — collections (deque, Counter, defaultdict, namedtuple)

**Level:** L5

Reusable algebra: Counter = multiset/bag, defaultdict = total map, deque =
sequence. Stub `src/pycsl_lib/collections.py`; driver
`src/pycsl_lib/collections_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/collections.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/collections.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/collections.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/collections_demo.py` exits 0

### Phase 5 — re (API surface + no-raise contract)

**Level:** L5

Model the API surface: `match`/`search` return `Optional[Match]`, known group
arity, and the no-raise contract — NOT full regex semantics. Stub
`src/pycsl_lib/re.py`; driver `src/pycsl_lib/re_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/re.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/re.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/re.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/re_demo.py` exits 0

### Phase 6 — json (recursive union + round-trip)

**Level:** L5

Model the recursive value union and the round-trip property
(`loads(dumps(x)) == x` under stated constraints). Stub `src/pycsl_lib/json.py`;
driver `src/pycsl_lib/json_demo.py` asserting the round-trip.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/json.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/json.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/json.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/json_demo.py` exits 0

### Phase 7 — typing (types as cheap invariants)

**Level:** L5

Model `Optional`/`Union`/`List[T]`/`Dict[K,V]` so annotations become free
contract facts. Stub `src/pycsl_lib/typing.py`; driver
`src/pycsl_lib/typing_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/typing.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/typing.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/typing.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/typing_demo.py` exits 0

### Phase 8 — math (integer half)

**Level:** L5

Model the pure integer functions onto Why3's int theory: `gcd`, `isqrt`,
`factorial`, `comb`, `perm`. Defer the float transcendentals. Stub
`src/pycsl_lib/math.py`; driver `src/pycsl_lib/math_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/math.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/math.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/math.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/math_demo.py` exits 0

### Phase 9 — sys

**Level:** L5

`argv` (list of str), `exit` (maps to `\diverges`), `maxsize`, `recursionlimit`.
Stub `src/pycsl_lib/sys.py`; driver `src/pycsl_lib/sys_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/sys.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/sys.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/sys.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/sys_demo.py` exits 0

### Phase 10 — bisect

**Level:** L5

Binary search + sorted insertion over `\is_sorted`/`\sum` predicates. Stub
`src/pycsl_lib/bisect.py`; driver `src/pycsl_lib/bisect_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/bisect.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/bisect.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/bisect.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/bisect_demo.py` exits 0

### Phase 11 — functools (reduce, lru_cache)

**Level:** L5

`reduce` = fold (inductive spec); `lru_cache` = memoization sound iff
referentially transparent (formalize purity / `assigns \nothing`). Scope around
`partial` (closures). Stub `src/pycsl_lib/functools.py`; driver
`src/pycsl_lib/functools_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/functools.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/functools.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/functools.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/functools_demo.py` exits 0

### Phase 12 — enum

**Level:** L5

Finite domains → clean finite types; sharpens dispatch-exhaustiveness proofs.
Stub `src/pycsl_lib/enum.py`; driver `src/pycsl_lib/enum_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/enum.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/enum.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/enum.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/enum_demo.py` exits 0

### Phase 13 — dataclasses

**Level:** L5

Model the auto-generated `__init__`/`__eq__` over the class-as-mutable-record
encoding. Stub `src/pycsl_lib/dataclasses.py`; driver
`src/pycsl_lib/dataclasses_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/dataclasses.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/dataclasses.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/dataclasses.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/dataclasses_demo.py` exits 0

### Phase 14 — itertools (eager/bounded half)

**Level:** L5

Model only the bounded operators with finite specs: `chain`, `islice`,
`product`, `combinations`. Explicitly defer the lazy/infinite generators. Stub
`src/pycsl_lib/itertools.py`; driver `src/pycsl_lib/itertools_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/itertools.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/itertools.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/itertools.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/itertools_demo.py` exits 0

### Phase 15 — heapq

**Level:** L5

Min-heap invariant spec (`heappush`/`heappop` preserve the property) over an
ordinary list. Stub `src/pycsl_lib/heapq.py`; driver
`src/pycsl_lib/heapq_demo.py`.

**Reference (read-only context — do not modify; shows the `unix-filesystem/` pattern + unix skill):**
`unix-filesystem/my_os.py`, `unix-filesystem/my_os_demo.py`, `config/skills/unix/SKILL.md`

**Acceptance:**
- `test -f src/pycsl_lib/heapq.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/heapq.py` exits 0
- `grep -c "trusted reviewer:" src/pycsl_lib/heapq.py` stdout == `0`
- `.venv/bin/python3 src/pycsl/pycsl.py src/pycsl_lib/heapq_demo.py` exits 0

## Notes

- **Definition of done per phase** = the stub exists and verifies, carries zero
  `\trusted reviewer:` markers, and a sibling `*_demo.py` formal driver verifies
  end-to-end (the `my_os_demo.py` analog). These are read-only checks the
  supervisor re-runs every invocation.
- **Sequencing**: 0 (os/builtins) and 3 (ast) are prerequisites/gates; 1, 8–10,
  12, 15 are the cheapest wins; 5/6/14 carry explicit "model the API surface /
  bounded half only" scope limits — keep them.
- **Load-bearing**: only Phase 3 (and any self-annotation hook) edits the
  parser/IR/emitter; `--allow-load-bearing` authorizes the delegate to attempt
  those, gated + rolled back. Review the surviving diffs before merge.
- On completion, mark each finished phase `**Status:** DONE` (keep its
  Acceptance block) so future runs re-verify it as `STATUS_VERIFIED`.
