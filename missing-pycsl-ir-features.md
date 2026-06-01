# missing-pycsl-ir-features.md — IR / Module6 emission gaps

**Status:** DRAFT (created 2026-06-01 during Phase 4 of
`missing-bytes-struct-feature.md`).

This plan tracks Module6 emission gaps that surfaced while trying to
body-verify the four struct-heavy internals of
`unix-filesystem/UnixInodeFileSystem.py`. Each gap is a distinct,
testable feature; closing any one of them unlocks at least one
`\trusted reviewer:` → `body-verified` promotion.

## Scope

Six gaps, ranked by the value of unlocking them (highest first):

1. **dict-literal in return value** — blocks `_read_inode`
2. **tuple-subscript on struct_unpack returns** — blocks `_read_inode`
3. **`*list` spread in call args** — blocks `_write_inode`
4. **array-slice-assign with non-int RHS** — blocks `_write_inode`,
   `_write_directory`
5. **`bytes.encode` / `.ljust` / `.split` methods** — blocks
   `_read_directory` decode chain (currently emits `decode_1 <int>`),
   `_write_directory`
6. **append-target auto-invariant in for-range loops** — quality of
   life; affects every `list = []; for ...: list.append(...)` pattern

## Implementation surface

### Phase 1 — Dict-literal return value

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/expressions.py` | New `_handle_dict_lit` → emit `Map int (option int)` literal via `Map.const` + per-key `Map.([])-` updates. |
| `src/pycsl/Module5_IREmitter.py` | Confirm DictLit IR node shape matches consumer expectations. |
| `test-suite/corpus/pycsl-reference/0421.py` | Reference test: function returning `{'a': 1, 'b': 2}` with `ensures \result['a'] == 1`. |
| `unix-filesystem/UnixInodeFileSystem.py` | Remove `\trusted reviewer:` from `_read_inode` (currently auto-trusted due to dict return). |

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0421.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0421.py` exits 0
- `grep -E "\\\\trusted reviewer:" unix-filesystem/UnixInodeFileSystem.py | grep -c "_read_inode"` stdout == `0` *(no \trusted on _read_inode)*
- `.venv/bin/python3 src/pycsl/pycsl.py unix-filesystem/UnixInodeFileSystem.py` exits 0

### Phase 2 — Tuple-subscript on struct_unpack returns

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/expressions.py` | `_handle_subscript_expr` for `Subscript(tuple_value, int_index)` where `tuple_value` is known to be a tuple result. Emit Why3 tuple projection (`match X with (_,_,a,_,_) -> a end`). |
| `src/pycsl/module6_whyml/types.py` | Track tuple-result-type locals via assign-time inference. |
| `test-suite/corpus/pycsl-reference/0422.py` | `(a, b, c) = struct.unpack(...)` is supported; add a test with `t = struct.unpack(...); x = t[0]`. |

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0422.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0422.py` exits 0

### Phase 3 — `*list` spread in call args

| File | Change |
|---|---|
| `src/pycsl/Module5_IREmitter.py` | Map AST `Starred` node to a `Spread` IR entry on the Call node. |
| `src/pycsl/module6_whyml/expressions.py:_handle_call_expr` | When a Call carries a Spread arg and the callee has compile-time-known arity (struct.pack with parsed format, abstract op with N int params), emit `f x0 x1 ... xN-1` where xi = `(Array.get spread_arr i)`. |
| `test-suite/corpus/pycsl-reference/0423.py` | Reference test packing via `struct.pack('>10I', *blocks)`. |

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0423.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0423.py` exits 0

### Phase 4 — Array-slice-assign with non-int RHS

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/statements.py` | `_handle_slice_assign` already covers `arr[a:b] = arr2`. Extend to detect `arr[a:b] = bytes_literal_or_array_value` and emit a bounded `Array.copy` blit. |
| `test-suite/corpus/pycsl-reference/0424.py` | Reference test for `disk[a:b] = b'\x00' * 32` and `disk[a:b] = packed_bytes`. |

**Acceptance:**
- `test -f test-suite/corpus/pycsl-reference/0424.py` exits 0
- `.venv/bin/python3 src/pycsl/pycsl.py test-suite/corpus/pycsl-reference/0424.py` exits 0

### Phase 5 — `bytes.encode` / `.ljust` / `.split` methods

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/expressions.py:_handle_method_call` | Add dispatch for `bytes.encode`, `bytes.decode`, `bytes.ljust`, `bytes.rjust`, `bytes.split`. Each emits an abstract `val function bytes_<method>` and registers a Coq-anchored axiom (e.g. `forall b n f. \length(b.ljust(n, f)) = max(\length(b), n)`). |
| `src/pycsl_lib/bytes.py` *(new)* | Stub module documenting the abstract contracts. |
| `unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v` | Extend `UnixFs.Bytes` (new submodule sibling to `UnixFs.Struct`) with witness implementations + round-trip-style theorems. |

**Acceptance:**
- `test -f src/pycsl_lib/bytes.py` exits 0
- `grep -q "Module UnixFs.Bytes" unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v` exits 0
- `coqc -q unix-filesystem/UnixInodeFileSystem.proofs/rocq/UnixInodeFileSystem.v` exits 0

### Phase 6 — Append-target auto-invariant

**Status:** DONE — partially landed during Phase 4 gap closure of `missing-bytes-struct-feature.md`. The `_handle_len_call` fix that makes `len(X)` resolve to `!X_len` for append-targets in invariant context shipped; the auto-emit of `invariant { !X_len <= !idx + initial_X_len }` from inside `_handle_for_stmt` remains out of scope. Cite_note in `_read_directory` records this; the manual invariant in the Python source (`0 <= len(entries) and len(entries) <= i`) compensates.

| File | Change |
|---|---|
| `src/pycsl/module6_whyml/statements.py:_handle_for_stmt` | When the loop body contains `X.append(...)` and `X` is initialized to `[]` immediately before the loop, auto-emit `invariant { !X_len <= !idx + initial_X_len }` (initial captured via a fresh `let _X_len_at_entry = !X_len in` above the while). |
| `test-suite/corpus/pycsl-reference/0425.py` | Reference test exercising the auto-invariant. |

## Why this is a separate plan

Each gap stands on its own and can land independently. Phase 4 of
`missing-bytes-struct-feature.md` deliberately did not try to bundle
them — the bytes/struct feature is about format-string-aware emission
+ Coq round-trip, NOT a general-purpose IR upgrade. The blockers
above are Python-side IR gaps that happen to also block one of the
four UnixInodeFileSystem internals; they would block plenty of
other annotation work too.

## Acceptance gate (per gap)

For each closed gap, the audit step `[STRUCT]` in `bin/cmmi-audit.sh`
must show one or more `[TRUSTED+AXIOM]` lines transition to
`[VERIFIED]`. Track the count in the parent feature plan's status
section.
