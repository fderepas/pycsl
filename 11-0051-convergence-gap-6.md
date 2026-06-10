STATUS: OPEN

# Convergence gap — iteration 6 (variable-length byte-codec round-trip: the loop-string-invariant wall)

**Loop:** `config/skills/pycsl-stdlib-coverage` — `stronger-than-os.md` Phase 0/1: the BYTE-domain
directory-entry NAME codec round-trip, now that Gap 5 (the `ord`/`chr` char↔int bridge) is CLOSED
(commit 7f53db2).
**Iteration:** N = 6.

## What LANDED this iteration (so this gap is the residue, not a blocker)

The byte codec is now FAITHFUL and PROVEN where the namespace consequence actually needs it:

- `_pad_name` (UnixInodeFileSystem.py) now ENCODES the name's bytes: `out[i] = ord(name[i])`,
  null-padded to the 30-byte field (replacing the old `[0]*30` that discarded the name). It is
  **total** (clamps `m = min(len(name), 30)` — the faithful `struct '30s'` truncation), so no
  caller (`_write_entry`, the symlink target write) needs a length precondition. Proves standalone.
- `_byte_codec_char` / `_decode_byte` leaves: the per-char byte round-trip `chr(ord(c)) == c`
  (a Why3 `string.Char` THEORY lemma — zero TCB growth). Proven.
- `formal_os_namecodec.py`: the byte codec leaf incl. the **disk-array-slice** round-trip
  (`disk[off+2] = ord(name[0]); chr(disk[off+2]) == name[0]`) — the byte twin of the inode-field
  codec round-trip, AGAINST THE ON-DISK BYTES. Proven.
- `formal_os_namespace.py` (THE BEACHHEAD): `mkdir(d) → access(d) PRESENT`, `rmdir(d) →
  access(d) ABSENT`, and two-distinct-names-resolve-distinctly — the OBSERVED post-state against
  the disk bytes, **not** a return-code disjunction. Proven (Valid, all goals).
- os re-proves **1804 VCs, 0 unproven** (identical to baseline); corpus byte-diff identical
  (594/594); conformance 38/38; doc-coherency green.

## The residual gap — the GENERAL variable-length round-trip

The proven forms above are **fixed-width** (each name char stored/recovered at a known slot
offset). The fully general round-trip — decode an *arbitrary-length* name by accumulating
`out = out + chr(b[j])` over a `range(n)` loop and proving `decode(encode(name)) == name` — does
NOT prove.

## Minimal reproducer

```python
#@ requires \str_length(name) <= 30
#@ assigns \nothing
#@ ensures \result == name
def name_codec_roundtrip(name: str) -> str:
    n = len(name)
    b = [0] * 30
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    for i in range(n):
        b[i] = ord(name[i])
    out: str = ""
    #@ loop invariant 0 <= j and j <= n
    #@ loop invariant \str_length(out) == j
    #@ loop variant n - j
    for j in range(n):
        out = out + chr(b[j])
    return out
```
Run: `.venv/bin/python3 src/pycsl/pycsl.py /tmp/name_codec_roundtrip.py`

## Symptom

Two distinct sub-walls:

1. **Re-assigning an empty-string accumulator + concat in a loop mis-types.** `out: str = ""`
   followed by `out = out + chr(b[j])` inside a `for` emits a `string`-where-`int`-expected error
   on the re-assignment / invariant. (The single-shot `out: str = chr(...)` form types fine —
   gap is specifically the loop-carried string accumulator.)

2. **The round-trip invariant is not establishable.** Even with the accumulator typed, the
   decode loop needs the invariant `out == String.substring(name, 0, j)`, whose inductive step is
   `concat(substring(name,0,j), chr(ord(name[j]))) == substring(name,0,j+1)`. That requires
   composing the per-char `chr(ord(c)) == c` lemma *under* `String.concat`/`String.substring`, and
   the solver returns **Unknown / Timeout** (Alt-Ergo + Z3, 30s). The fixed-width decompositions
   prove instantly (the per-char facts are exposed directly, no loop induction over strings).

## Root cause (where to look)

- For (1): the loop-carried string-local lowering — `module6_whyml/statements.py::_typed_local_vars`
  recognises a `str`-annotated local (`_string_local_vars`), but a loop-body re-assignment
  `out = out + chr(...)` where `out` was seeded `""` appears to fall back to the int `ref 0` /
  hash path inside the loop. Compare the working single-assignment path.
- For (2): this is an SMT/spec-expressiveness wall, not an emitter bug. PyCSL contracts have
  `\strconcat` / `\str_sub` / `\str_length`, but no lemma-mode hook to teach the solver the
  `concat∘substring` step over a loop. Candidate fixes: a `#@ proof rocq|lean` lemma
  `string_build_substring` (concat-prefix identity) cited on the decode loop; OR a Why3 `string`
  prefix-build lemma added to the preamble. Either keeps the general round-trip out of the TCB.

## Proposed fix / interim

**Interim (LANDED):** the namespace consequence rests on the **fixed-width** recovery (a name is
recovered char-for-char at known offsets and compared), which is exactly what `mkdir → access`
does and is fully proven. The general variable-length leaf is NOT needed for the beachhead.

**Fix (for the tool-agent):** (1) extend the loop-carried `str`-local recognition so a
`""`-seeded, concat-updated accumulator stays string-typed inside a `for`; (2) provide the
`concat∘substring` prefix-build lemma (preamble `string` lemma or a cited `#@ proof` lemma) so the
general `decode(encode(name)) == name` over an unbounded name discharges. Then the variable-length
codec leaf can replace the fixed-width composition and the namespace consequence generalises to
arbitrary name lengths.
