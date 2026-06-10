# stronger-than-os — a functionally-verified filesystem namespace

High-level plan to make `pure_lib/os` prove **functional consequences** (mkdir creates, rmdir removes,
write persists), not just totality. Leaves first; smallest syscall first. Grounded in the `unix` skill
(§3.3–3.6 on-disk layout, §4.1 inodes-and-names, §5.1 fd table) and the mkdir/rmdir/open walkthroughs.

## 1. Why — the diagnosis

`os` is **1804 VCs, 0 unproven** — but that is *totality / safety*: every syscall runs to a well-formed
result, returns the right *code*, and never faults. It is **not functional correctness**. The smoking gun:

```python
def _pad_name(name: str) -> list:
    out = [0] * 30          # the filename is THROWN AWAY (Gap 5: str.encode() unmodeled)
    return out
```

The model **does not store filenames**. So `mkdir("a")` and `mkdir("b")` write identical zero-named
entries, and `mkdir(d) → access(d)` cannot prove "present" — the namespace, the one thing that makes an
object reachable, is unmodeled. `formal_os_*` could only assert each syscall's own return-code disjunction
(`\result == 0 or -1`), which is true *by construction* and proves nothing (the vacuous test the
consequence rule forbids).

## 2. The structural fix — separate **naming** from **content** (the unix model)

From the walkthrough and `unix` §4.1: **the name lives ONLY in a directory entry (dirent) in the parent's
data block, mapping name → inode number; the inode holds metadata + block pointers and never the name.**
Path resolution is a *sequence of name→inode lookups*. Hard links = a second dirent for the same inode;
`unlink` removes a name, the inode persists until link-count + open-refs reach 0; `open` *consumes* the
naming structures and builds an in-memory fd chain.

So the model must gain three faithful structures it currently fakes or omits:

| Structure | What it is (unix) | Today | Target |
|---|---|---|---|
| **Directory namespace** | parent's data block = dirents `(name → inode)` | name discarded (`_pad_name`→`[0]*30`) | a faithful `name → inode` association with a provable round-trip |
| **Inode** | metadata + block pointers, **no name** | modelled + codec round-trip proven ✓ | reuse as-is (the content side) |
| **fd chain** (open/dup) | fd-table → open-file-description (offset+flags) → in-core inode | fd table cols return-code-only | the three levels, so offset/dup consequences prove |

The inode (content) side is already done; the **namespace** is the missing leaf.

## 3. `#@ interface` — manage the byte-level complexity

Present the directory namespace as an **abstract `name → inode` map** behind `#@ interface` (Track B
opacity / narrowing VC, committed `b3d65d1`). Syscalls (`mkdir`/`access`/`rmdir`/`link`/`rename`/`open`)
are specified and proved against the **map view** — `dir_lookup(insert(d,i)) == i`,
`dir_lookup(remove(d)) == absent` — which is trivially provable (map-get-after-set, exactly the dict model
`map 'k (option 'v)`). The concrete on-disk **dirent byte layout** (variable-length records, encode/decode)
is the **hidden refinement** below the interface:

- proved *separately* to satisfy the interface (`decode(encode(name)) == name` — the string analogue of the
  already-proven inode-field codec round-trip), **or**
- left as a trusted leaf (TCB-ledgered) **if** the byte round-trip is still blocked by Gap 5
  (`str.encode()` opacity — the same gap strmod hit).

This is the lever: **we get provable name-keyed consequences NOW against the map interface, without waiting
on the `.encode()` tool gap** — the byte layer is refined (or trusted) underneath.

## 4. The plan — leaves first, smallest syscall first

### Phase 0 — the leaves (value + round-trip contracts; NO syscalls yet)
The serialization discipline (skill §"Serialization"): verify the leaves with VALUE contracts so the
syscalls compose, not re-derive.
- **L1 — directory-namespace leaf (THE key leaf).** `dir_insert(dir, name, ino)`, `dir_lookup(dir, name)`,
  `dir_remove(dir, name)` over the `name→inode` map, with round-trip value contracts:
  `lookup(insert(d,i)) == i`; `lookup(remove(d)) == none`; `lookup` of an *untouched* name unchanged
  (frame). Presented via `#@ interface` as the map; byte-dirent layer refined/trusted underneath. Everything
  name-keyed rests on this.
- **L2 — inode bitmap** alloc/free (value contracts: `alloc` returns a free slot and marks it used; `free`
  clears it; a freed-then-alloc'd slot is reusable). [largely exists]
- **L3 — block bitmap** alloc/free (ditto). [largely exists]
- **L4 — inode store** read/write — reuse the existing proven codec round-trip (`_read(_write(x)) == x`).
- **Gate:** each leaf proves its round-trip VALUE contract standalone (`--fun`).

### Phase 1 — the BEACHHEAD: the directory create/remove round-trip (the user's example)
The smallest real consequence — prove the namespace works end-to-end.
- `mkdir(d)` = compose L2+L3+L1 (alloc inode → alloc block → `dir_insert(d, ino)`). Contract: *after a
  successful `mkdir(d)`, `d` is present* (`dir_lookup(d) == ino`).
- `access(d)` = `dir_lookup(d)`. Contract: *present ⟺ `d` in the namespace*.
- **First functional-consequence formal test:** `mkdir(d)` → assert **present** → `rmdir(d)` → assert
  **absent**. *create → check present → remove → check absent.* This is the test that is `Unknown` today;
  making it **Valid** is the milestone that proves the restructure works.
- **Gate:** the directory round-trip formal test PROVES (not `Unknown`); os's existing totality proofs
  preserved.

### Phase 2 — the rest of the namespace syscalls (each a create→operate→observe consequence)
- `rmdir` (check-empty + `dir_remove` + free + link-count −1/−2 → 0), `unlink`/`remove` (remove name; inode
  persists until refs 0), `link` (second `dir_insert` → SAME inode; consequence: both names resolve to one
  inode), `rename` (atomic `dir_remove(old)+dir_insert(new)`; consequence: old **absent** AND new
  **present**, same inode).
- **Gate:** each has a passing consequence formal test.

### Phase 3 — the fd chain + content (open / read / write / dup)
- `open` (no `O_CREAT`): path walk = a sequence of `dir_lookup` → build the fd chain
  (fd-table slot → open-file-description {offset, flags} → inode). Consequence: `open(existing)` → valid fd
  resolving to the right inode; `open(absent)` → `ENOENT`.
- `read`/`write`: the **content round-trip** (`write(fd, data)` → `read(fd) == data`) — this is
  `formal_0008`'s target (currently failing on a pre-existing `int`-vs-array type error, gap-4), now resting
  on a faithful namespace + fd chain. `dup` → shared-offset consequence.
- **Gate:** content round-trip + open/dup consequences prove.

## 5. Execution — via the convergence loop, gated

This is a **model strengthening** run as the convergence principle (stdlib-agent strengthens the model +
the consequence formal tests; any tool limitation → `DD-HHMM-convergence-gap-N.md` → tool-agent → re-prove).
Discipline every step: the new leaf/syscall proves its **consequence** (not a return-code); os's existing
**totality** VCs stay green; conformance 38/38; byte-diff clean for unrelated drivers; the TCB ledger
records any trusted byte-dirent leaf. Budget for proof cost (rich round-trip contracts can slow the
whole-module proof — `#@ no_inline` the heavy leaves, prove once, reuse).

**Start here:** Phase 0 L1 (the `name→inode` namespace leaf behind `#@ interface`) + Phase 1 (the
`mkdir → access-present → rmdir → access-absent` beachhead). That one round-trip, proved, is the proof the
restructure is sound — then the rest of the namespace and the fd chain follow the same create→operate→observe
shape.
