# Lessons and gotchas

Consult this when debugging a specific WhyML/emission gotcha (naming clashes, re-export contract loss, constants, string methods, inliner limits, loop patterns, exception propagation, `assigns`, tuple results, stuck-proof strategy) or a codec (the serialization / pack-unpack discipline).

## Lessons learned

### Naming: Why3 keyword and symbol clashes

PyCSL lowercases Python class names to form Why3 types. Several
Python names collide with Why3 keywords or with PyCSL's own emitted
symbols:

| Python name | Clash | Fix |
|-------------|-------|-----|
| `Match` | `match` is a Why3 keyword | Rename to `ReMatch` |
| `Pattern` | `isinstance` emits `val constant pattern` colliding with `type pattern` | Rename to `RePattern` |
| `compile(pattern, ...)` | Parameter `pattern` collides with type `pattern` | Rename parameter to `pat_src` |

**Rule:** Always check generated `.mlw` for name collisions after
adding a new class. Keep Python API compatibility via `__init__.py`
re-exports (`ReMatch as Match`).

### Naming: Python stdlib module name clashes

PyCSL's import resolver can pick up the *real* stdlib module instead
of your `src/pycsl_lib/` version if names collide:

| Module name | Clash | Fix |
|-------------|-------|-----|
| `warnings` | Resolves to stdlib `warnings` | Name directory `warn/` |

**Rule:** If your pycsl_lib module shares a name with a top-level
Python stdlib package, rename it. Use `__init__.py` to re-export
under the expected API names.

### Function contracts don't propagate through re-exports

**Critical architecture decision:** When `__init__.py` does
`from ._core import my_function`, PyCSL generates a stub for
`my_function` but **does NOT carry its `requires`/`ensures` contracts
through**. Only **class** contracts (invariants, method specs) survive
re-export.

**Consequence:** For modules that export top-level functions (not
classes), put the annotated function definitions **directly in
`__init__.py`**, not in a submodule. This is why `src/pycsl_lib/warn/`
has everything in `__init__.py`.

### Constants: use literals, not imports

Cross-module constants (e.g., `O_CREAT = UnixInodeFileSystem.O_CREAT`)
become abstract `val constant` with no value in WhyML. PyCSL's
`module_constants` works for the file being verified but NOT for
imported modules.

**Fix:** Define constants as literals directly:
```python
O_RDONLY = 0
O_WRONLY = 1
O_CREAT = 64
```

### String methods: known postconditions

- `.ljust(width)` — has `ensures Array.length result >= x0` ✅
- `.ljust(width, fillchar)` — 2-arg form has type issues (fillchar
  `b'\x00'` becomes `array int`, stub expects `int`) ❌
- `.encode()` — length is genuinely unknown; no useful postcondition
- `.zfill(width)` — has length ensures ✅

### Default arguments and type annotations

- Default arguments: PyCSL generates N-arg stubs; callers must pass
  all args explicitly. `open(filename, O_RDONLY)` not `open(filename)`.
- `filename: str` annotation: causes type mismatch (string → int in
  Why3). Drop the `: str`.

### Inliner limitations

- Module-level helper calls in inlined bodies get replaced with
  `Array.make 1 0` instead of the actual function call.
- **Workaround:** Remove preconditions that depend on helper
  postconditions, or inline the logic directly.
- Method calls on module-level objects may miscount arguments
  (`self` not counted), causing inliner errors.

### Loop patterns: tuple unpacking and chained comparisons

**Tuple unpacking in for-loops is broken.** Code like
`for action, cat in _filters:` generates WhyML where `cat` is
undefined. **Workaround:** Use parallel lists + index-based access:

```python
_filter_actions = []  # list of action strings
_filter_cats = []     # list of category strings
# Access via _filter_actions[i], _filter_cats[i] in a while loop
```

**Chained comparisons are broken.** `0 <= i <= n` lowers to
`((0 <= !i) <= !n)` — applying `<=` to a boolean. **Workaround:**
Split into two separate invariants:

```python
#@ loop invariant 0 <= i
#@ loop invariant i <= n
```

### Exception propagation across functions

PyCSL does not propagate `raises` clauses through callees. If
function `A` calls function `B` which raises `Exception`, `A` does
NOT automatically get a `raises` annotation.

**Consequence:** Functions that call exception-raising helpers can't
be formally tested (the formal test can't declare the exception
possibility). **Workaround:** Either restructure to avoid calling
the exception-raising function, or exclude that function from formal
tests and document why.

### `assigns \nothing` is implicit

In Why3, a `val` without `writes` clause is already effect-free.
You do NOT need to explicitly emit `writes {}`. The `assigns \nothing`
annotation is still useful documentation but doesn't change the proof.

### Tuple result postconditions

`\result[0] >= 0` correctly lowers to
`let (_r0_, _) = result in _r0_ >= 0`.

### Proof strategy for remaining failures

When body-level proof is stuck:

1. Check if the failure is a **PyCSL tool gap** (subscript_get, string
   ops, etc.) — document in requirements, move on.
2. Check if a **stronger precondition** helps — e.g., adding
   `inode_num < 32` guard made a loop invariant provable.
3. Check if a **weaker postcondition** is still useful — removing
   `\valid(name_bytes, 30)` eliminated downstream failures.
4. Fall back to **stub-level** formal tests through `__init__.py`.

---

## Serialization (pack/unpack): leaf-first, value+round-trip, compose-don't-re-derive

Binary serialization (the os inode/direntry codecs, struct-style packers) is where "shape-only"
contracts hide a hollow model. Discipline (learned closing the os inode round-trip):

- **Bottom-up: byte leaves → field composers → records.** Verify `_pack_uintN_be` /
  `_unpack_uintN_be` FIRST with VALUE contracts (`\result[0]*256 + \result[1] == v` and the inverse),
  so `unpack(pack(v)) == v` proves by CONTRACT COMPOSITION (no body tracking). Only then the
  inode/direntry packers. A composer built on length-only leaves can prove `\length == 64` and STILL be
  a no-op on the contents — the round-trip is the property that makes `_read_inode(_write_inode(x)) ==
  x` provable, which every syscall ultimately rests on.

- **Compose, don't re-derive (the array-state wall).** A packer that writes a struct into a fixed
  `out = [0]*K` and RE-derives each field's byte math (`out[o] = f // 2**24; ...`) TIMES OUT once K is
  large (K=64 for the inode) — the solver carries all K writes per goal. Instead CALL the proven leaf
  and copy: `b = _pack_uint32_be(f); out[o]=b[0]; out[o+1]=b[1]; ...`. The field ensures then follows
  from the leaf's already-proven contract, no div/mod re-derivation. This turned a hard SMT timeout
  into SUCCESS for the full 18-field inode pack — with zero Rocq/Lean.

- **Contract gotchas** (also in pycsl-annotate): no `<<` in contracts (use `*256`); `\valid(data,
  offset + N)` NOT `\valid(data, N)`; arithmetic bodies (`v // 256`) for provability; range-bound byte
  params (`0 <= data[i] <= 255`). And `\result[i]` / `data[i]` in contracts lower to `Array.get` (a
  tool fix that was a prerequisite — without it no value-over-array post can even be expressed).

- **Proof-cost vs the full-module sweep.** Rich round-trip contracts that prove in `--fun` can push the
  WHOLE-module proof over its wall-clock budget (the os proof slowed markedly once `_pack_inode` carried
  18 field ensures). Budget for it; a heavy serializer only ever *called* (not re-proven per caller) is
  a candidate for `#@ no_inline` to keep the module proof affordable.

- **SMT escape order** (see csl-philosophy): compose from a proven leaf FIRST; a cross-validated
  `#@ proof rocq/lean` lemma (e.g. `UnixFs.Struct.*` round-trips) only for irreducible facts; never a
  bare SMT skip.
