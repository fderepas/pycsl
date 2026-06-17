# GAP: chmod / truncate CONSEQUENCE needs a multi-rung model extension (NOT a cheap win)

**STATUS: LOGGED GAP routed to the human.** Probed per WIN 3; it requires a
substantial model extension, so it is logged, not forced. No trust added; no weakening.

## What is PARTIAL today

Public `os.chmod(p, m)` and `os.truncate(p, n)` prove only their RETURN CODE
(`sys_chmod`/`sys_truncate` ensures `\result == 0 or \result == -1`, plus block-5
decode-frame ensures for the directory-uniqueness invariant). The real consequence —
`chmod(p,m)` ⇒ `stat(p).mode == m`; `truncate(p,n)` ⇒ `stat(p).size == n` — is NOT
stated, hence NOT proven. A formal test asserting only the return code is the
vacuous self-return shape (`[[feedback_formal_test_consequence]]`).

## Why it is not cheap — the missing rungs (probed at source)

1. **No public mode/size ACCESSOR.** `sys_stat`/`sys_lstat` (and the public
   `os.stat`/`os.lstat` wrappers) return only the inode NUMBER
   (`return self._dir_lookup(5, pathname)`), never a stat structure with a mode or
   size field. A formal test cannot observe the mode/size through the public API at
   all. Closing the consequence needs a NEW public observer that returns the field
   (e.g. `stat_mode(p)` / `stat_size(p)`), i.e. new public API surface in
   `pure_lib/os/__init__.py` + a new `sys_*` method.

2. **No MODE-field round-trip in the inode codec.** The zero-trust defined accessor
   `inode_size(disk, ino)` exists (`src/pycsl/module6_whyml/preamble.py:750`,
   decode of bytes [512+ino*64 .. +3]). There is NO `inode_mode` accessor. More
   importantly, `_write_inode`'s read-back ensures
   (`UnixInodeFileSystem.py:755-756`) cover ONLY field 0 (size, bytes 0-3) and
   field 8 (first data block, bytes 22-25). The MODE field (inode index 3, on-disk
   bytes 8-9, a uint16) has NO write-back ensures and NO read-back ensures on
   `_read_inode`. So even with an accessor, the mode bytes do not provably round-trip
   through `_write_inode` (the chmod body does `inode[3] = mode; _write_inode(...)`).

3. **`sys_chmod` is `#@ no_inline`** (E-matching isolation for the `__init__` gate),
   so a new `\result==0 ==> inode_mode(self.disk, dir_lookup(self.dir,5,p)) == mode`
   ensures must compose the new `_write_inode` mode rung and cross the no_inline
   boundary as a foldable atom — the same care the gap-17 SIZE round-trip needed.

4. **Frame + path consistency for the formal test.** The driver would
   `chmod(p,m)` then `stat_mode(p)`; the lookup `dir_lookup(self.dir,5,p)` must be
   stable across the observe call (chmod `assigns self.disk`, and its block-5 frame
   ensures already preserve the directory decode — that part exists), and the str
   path `p` must thread consistently through both public wrappers.

## The work needed (the rigorous, no-trust route)

For **mode** (chmod): (a) define `inode_mode(disk, ino)` (zero-trust, mirror of
`inode_size`, uint16 decode of bytes 8-9); (b) add `_write_inode` read-back ensures
for bytes [8-9] == inode[3] and a `_read_inode` ensures `\result[3] ==
inode_mode(...)`; (c) add the `sys_chmod` consequence ensures composing them across
no_inline; (d) add a public mode observer (`sys_stat_mode` + `os.stat_mode` or a
mode-returning stat); (e) propagate through the `__init__` chmod wrapper + observer,
re-running and KEEPING the load-bearing `__init__` gate green; (f) author a
`formal_os_chmod` test (chmod→observe mode==m), non-vacuity-seeded.

For **size** (truncate): the SIZE round-trip rung already exists on
`_read_inode`/`_write_inode` (field 0) + the `inode_size` accessor, so the codec
side is partly in place; still needs (c)–(f) for `sys_truncate` + a public size
observer + the formal test. (Note `sys_truncate`/`sys_ftruncate` set the size field;
verify their bodies establish `inode_size == length` and add the consequence ensures.)

This is a multi-rung extension spanning the preamble, the inode codec contracts, two
`sys_*` methods, new public API, the `__init__` wrapper plumbing, and two new formal
tests — with real `__init__`-gate E-matching regression risk. It is exactly the
"substantial model extension" the WIN 3 brief says is NOT a cheap win. Logged here
and routed to the human; NOT closed by trust, NOT papered over with a return-code-only
"formal" test.
