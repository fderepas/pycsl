# LES OCTETS
### *How a Python `os` module was made to keep its word — a technical novel in three acts*

> *A test asks: did it work this time? A proof asks: could it ever fail? The first samples the input
> space; the second quantifies over it. Only the second can say* shall.
> — field notes, PyCSL verification log

---

## ACT ONE — THE PLEDGE

### 1.

Ada read the specification by the light of one screen.

It was POSIX — the Open Group base specifications — and it was written in English, the way the oldest
laws are. *open* a path, *write* bytes, *close*; *open* it again, *read*; and the bytes that return
**shall** be the bytes that went in. No clause excepted it. It had the flat certainty of scripture, and
like scripture it promised something it never proved.

Python's `os` module was the priesthood of that law. Every program that touched a file trusted it.
`os.open`, `os.write`, `os.read`, `os.close`, `os.mkdir` — thin Python over a C runtime over a kernel
over a disk controller, four layers of machinery nobody could see into, all of them *believed* to obey
the English. Believed. Tested, on good days. Never proved.

She underlined one word. *Shall.*

"All right," she said to the empty room. "Let's find out if you mean it."

The plan was not to read `os`'s source. You cannot prove what you cannot see, and below the Python the
kernel kept its secrets. The plan was to *rebuild* the law's meaning in something a prover could hold
entirely in the light — pure Python, no syscalls, no C, no hardware — and then prove *that* obeyed the
English, byte for byte. If the model was faithful and the model was proved, then the law was no longer
believed. It was *known.*

She made a directory called `pure_lib/os/` and began.

---

### 2.

What she built was a real filesystem, in the only honest sense: a byte layout under an interpretation.

The disk was one array — `disk`, a hundred and thirty-one thousand and seventy-two integers, two hundred
and fifty-six blocks of five hundred and twelve bytes, each cell holding a value in `[0, 255]` and
meaning nothing on its own. Out of that flat dark she staked the structure a Unix filesystem needs: a
block bitmap in the low blocks; an **inode region** from byte 512 to byte 2560 — thirty-two inodes of
sixty-four bytes each, inode *n* living at offset `512 + n*64`; the root directory in block 5; data
blocks from block 6 up. The open files became columns of a table indexed by descriptor — `fd_open`,
`fd_inode`, `fd_offset`, `fd_flags`, and `fd_block`, the in-core cache that is the kernel's open-file
table in miniature.

An inode, in the warm typed world, was eighteen integers: size, link count, type, mode, uid, gid, two
timestamps, and ten data-block pointers. On the disk it was sixty-four bytes, big-endian. Between those
two worlds ran a codec — the narrow bridge every file had to cross. At the bottom, the leaves:
`_pack_uint16_be`, which took an integer and laid it down as two bytes high-then-low; `_pack_uint32_be`,
four bytes; and their inverses, `_unpack_uint16_be`, `_unpack_uint32_be`. Above them, composed of them,
`_pack_inode` and `_unpack_inode`. Above *those*, `_write_inode` and `_read_inode`, moving an inode
between its eighteen fields and its sixty-four bytes on disk.

People asked why she modelled the bytes at all. Why not let a file simply *be* its content, abstract and
clean? Because then she would prove a story about a filesystem and not a filesystem. A file's data
really does live in a data block whose number is really written, most-significant-byte-first, into the
bytes of its inode. Abstract that and you have proved nothing the law cares about. The law said *shall.*
You do not answer *shall* with a convenient abstraction.

She did not annotate any of it yet. First she *ran* it. She wrote a plain Python test — `pure_lib_test/`
held a row of them, `0001.py` through `0008.py` — create a file, write the five bytes of `HELLO`
(`[72, 101, 108, 108, 111]`), close, reopen, read, assert the list comes back equal. It came back equal.

"Good," she said. "It works."

And then, because she was honest, she said the sentence that cost her the night: "It works *this
time.*"

---

> *A concrete test fixes the inputs. `HELLO` goes in; `HELLO` comes out; you have learned exactly one
> fact about one file. The filesystem accepts more files than there are atoms in the observable
> universe. A test, run until the heat death of that universe, would sample a measure-zero fraction of
> them. To learn anything about* all *files you must stop running the program and start reasoning about
> it.*
> — field notes, PyCSL verification log

---

## ACT TWO — THE TURN

### 3.

She annotated from the bottom, because a caller's proof must rest on its callees' *proved contracts*,
never on re-deriving their bodies. That is the only way a fifty-function module stays tractable: you
prove the leaves, then let every layer above stand on what is already proved.

The smallest leaf got the smallest, hardest promise. Above `_pack_uint16_be` she wrote, in PyCSL's
`#@` annotation syntax, a postcondition it could not wriggle out of:

```python
#@ requires 0 <= v and v <= 65535
#@ ensures \result[0] * 256 + \result[1] == v
def _pack_uint16_be(v: int) -> list:
    return bytes([v // 256, v % 256])
```

*The two bytes I lay down, read back as a big-endian number, are the number you gave me.* And note the
`requires`: the function is **not** total — `v` above 65535 would not fit in two bytes — so she stated
the partiality honestly rather than pretending the leaf could swallow any integer. Faithfulness over
convenience; every shortcut declined is a place the proof stays honest.

This was the machinery she had built the language for. PyCSL took the annotated Python and lowered it,
through six modules, into **WhyML** — the input language of the **Why3** platform. Why3 computed the
function's **verification conditions** by a weakest-precondition calculus: first-order formulas whose
validity means *this body satisfies its postcondition, calls every callee inside that callee's
precondition, keeps every loop and class invariant, and indexes every array in bounds.* Those formulas
went to two SMT solvers — **Alt-Ergo 2.6.2** and **Z3 4.13.3** — each given thirty seconds a goal. A
solver does not check that the promise holds; it assumes the promise is **false** and tries to build a
world where it fails. For the packer it tried to find a `v` whose two bytes did *not* read back as `v`,
and could not. The negation was unsatisfiable.

**Valid.** One leaf, proved — not for `HELLO`, for *every* `v` in range.

---

### 4.

Then the climb.

`_pack_inode` and `_unpack_inode` needed no new article of faith. Their honesty *composed* from the
leaves': the inode round-trip — `_unpack_inode(_pack_inode(fields)) == fields` — held not by decree but
because each of the eighteen fields, byte by proved byte, came home. (The codec's clauses were a wall of
near-identical range constraints — sixty-four bytes each in `[0, 255]`, eighteen fields each within
their width. She wrote them once with a small expansion sugar, `#@ for i in range(0, 64):`, which
desugars to the exact ground clauses a human would type — *not* a `\forall`, so the solver paid no
instantiation cost. She had checked that the generated WhyML was byte-for-byte identical to the
hand-written form. The sugar was a spelling, not a meaning.)

Up she went. `_write_inode`, with a read-after-write contract: an inode persisted to its region is
recoverable, its block number and size intact across the bytes. The bitmap allocator `_alloc_block`,
given a narrow contract — returns `-1` or a valid block index, preserves the layout invariant.
`_dir_lookup`, `_write_entry`. Then the syscalls themselves — `sys_open`, `sys_write`, `sys_read`,
`sys_mkdir`, `sys_unlink`, `sys_link`, `sys_symlink` — each with a contract faithful to its POSIX page,
each cited in the source by a `# cite:` line back to the sentence it encoded, each standing on the
proved contracts of its helpers rather than re-proving their inlined bodies. Over every method she
stretched one **class invariant**: `\length(self.disk) >= 131072`, the descriptor columns well-sized,
the inode bytes provably bytes. Each method assumed a well-formed filesystem and left one behind for the
next.

She ran the whole module and watched the unproven-goal count fall. Forty. Twenty-three. Eleven. Three.
One.

**Zero unproven.**

The entire tower stood — every array access in bounds, every on-disk layout invariant preserved, every
syscall returning a result faithful to POSIX — resting on the ground and on a single cross-validated
axiom she had written down by name: one bitwise bound, the lone assumption in a structure of thousands
of proved facts. The trusted base was *one line,* and she could point to it.

And it was not enough, and she knew it, and that was the corner.

---

### 5.

Because read what she had proved. That the codec is faithful. That `write` mutates exactly the bytes it
claims and no others. That nothing reads past the end of an array. That every syscall returns a
well-formed code. **Safety. Structure.** Real, hard-won, and not the law.

The law said the *content* comes back — the whole list, `[72, 101, 108, 108, 111]` in and the same list
out — and it said it for *every* file. She had proved the **parts**: that the codec round-trips, that
`write` lands its bytes where the inode records, that a written block is recoverable across a close. But
proving the parts is not the same as exhibiting the **whole**, and two questions remained that no test
could touch. Could the full API — open, write, close, reopen, read, *composed* end to end — be driven
into a fault by some file, somewhere, out of all the files there are? And the law's literal final clause:
are the bytes that return *equal* to the bytes that went in, as a single theorem over every content?

She wrote the impossibility out in plain words, at three in the morning, to see how bad it was. *To
answer either by testing I would have to enumerate every file — and the content is a list of bytes of
arbitrary length, of which there are more than there are atoms. I cannot sample my way to* shall.

It was the honest kind of impossible, with no convenient door — the descriptor table on one side, the
disk that does not answer on the other, and between them an input space no machine could enumerate.

And then she reread the first line of her own log, the one she had typed so often she had stopped seeing
it. *A test asks: did it work this time? A proof asks: could it ever fail?*

She had been trying to *enumerate* her way to *shall.* But she had spent the whole night building the
other instrument. A verification condition does not run on a value; it quantifies over a **symbol.** The
thing she had proved of the leaf — *for all `v` in range* — she could ask of the entire composed API at
once. Not *does this file survive* but *could any file fault.* You do not enumerate the inputs. You make
one symbol stand for all of them and prove the solver cannot break it.

Of course. *Of course* — why hadn't she seen it. The proof had never been about a file. It had been
about the symbol that stands in the place of every file.

She opened a new test and began, very carefully, to write it.

---

## ACT THREE — THE PRESTIGE

### 6.

It looked exactly like the concrete test from Act One. That was the trick of it; that is always the
trick.

```python
#@ requires \length(data) >= 1
#@ requires \length(data) <= 512
#@ ensures \result == 0 or \result == 1
def formal_test_0001(filename: str, data: list) -> int:
    fd = open(filename, O_CREAT | O_WRONLY, 0o777)
    if fd < 3:
        return 1
    write(fd, data)
    close(fd)
    fd2 = open(filename, O_RDONLY, 0o777)
    if fd2 < 3:
        return 1
    lseek(fd2, 0, SEEK_SET)
    back = read(fd2, len(data))
    close(fd2)
    if back != data:
        return 1
    return 0
```

The same six steps she had run by hand with `HELLO`. But `filename` was not `"testfile"` and `data` was
not five known integers — `filename` was *a* filename and `data` was *a* buffer, any buffer of length
one to five hundred and twelve: a symbol standing for every file that could be. The postcondition
`\result == 0 or \result == 1` is a **totality and safety** claim — *for every symbolic input, this
entire composed scenario runs to a well-formed result: no out-of-bounds index into the disk array, no
violated precondition on any syscall, no broken class invariant, no stuck state.* (Note what it does
*not* yet claim: not `\result == 0`. The mismatch branch is allowed to exist; this test proves the
machine cannot *fault*, not yet that the content is *equal*.)

She gave it to Why3. The verification conditions came back **Valid**, every one, with no `\trusted` in
the chain. The full open-write-close-reopen-read API, composed end to end, could not be driven into a
fault — not by `HELLO`, not by any file in the input space. Proved, not sampled.

### 7.

Here is what the prover actually does, because the magic is mechanical and the mechanism is the point.

Why3 takes the whole driver — every `open`, the `write` that runs through `_write_inode` through
`_pack_inode` through the proved byte leaves; the `close`; the second `open` that walks the directory,
reads the inode off disk through `_unpack_inode`, and rebuilds `fd_block`; the `read` — and collapses it
by weakest precondition into a single first-order formula. The formula's meaning is exactly: *for this
driver to reach a bad state, there must exist some `filename` and some `data` that take it there.* It
hands that formula to Alt-Ergo 2.6.2 and Z3 4.13.3, which do the only thing they know how to do: they
try to satisfy it. They search the input space — larger than atoms — for one file that faults the
machine.

They find none. They can find none. The negation is **unsatisfiable** — because every step was built
from parts each independently proved within its contract, and the class invariant the search would have
to break is re-established by every method the driver passes through. There is no faulting file. Not
among the billion, not among the atoms, not anywhere.

And the formal test did not stand alone. It rested on the whole module beneath it — the one she had
already driven, function by function, to **zero unproven goals** on a one-line trusted base. Those
proved contracts were the rungs; the formal test was the thing that climbed all of them at once, `open`
through `read`, end to end, and could not be made to fall.

This was the prestige: not a green test suite but a **proved module** with its public API demonstrated
total and safe on every input. The Python `os` module's filesystem, re-implemented faithfully in
`pure_lib/os/` and then mechanically verified — its on-disk machinery correct by construction, its
round-trip API faultless for all files at once.

### 8.

She looked at the underlined word in the specification. *Shall.*

The trivia had been the trick the whole time. The first line of the log — *a test asks did it work this
time; a proof asks could it ever fail* — read so often it went invisible: that had been the key, planted
on page one, disguised as a maxim. The smallest contract, the eleven symbols on a two-byte leaf, the one
that looked like a footnote: that had been the foundation everything stood on, because faithfulness
composes upward and the whole proof was only the leaves' honesty, climbing. The concrete `HELLO` test
from Act One, the one that convinced her the model was right, turned out to be the rehearsal for the
symbolic test that proved it right for *everyone* — the same six steps, the inputs made universal.

What she had done was nameable in one sentence, and the sentence was the achievement: *the Python `os`
module's filesystem semantics, re-expressed faithfully in pure Python, were mechanically proved — zero
goals unproven, one axiom in the trusted base — total and safe over every possible file, with the codec
round-trip and the read-after-write recovery proved as contracts rather than tested as examples.* Not
believed. Not green-on-CI. *Proved.*

One clause of the old law remained — the deepest one, and she knew exactly where it sat. The law did not
only promise the machine would not fault; it promised the returned bytes would *equal* the written
bytes, end to end, as one theorem:

```python
#@ ensures \result == True
def formal_test_0008(f: str, c: list) -> bool:
    fd = open(f, O_CREAT | O_WRONLY, 0o777)
    if fd < 3:
        return False
    write(fd, c)
    close(fd)
    fd2 = open(f, O_RDONLY, 0o777)
    if fd2 < 3:
        return False
    lseek(fd2, 0, SEEK_SET)
    back = read(fd2, len(c))
    close(fd2)
    return back == c
```

`\result == True`, for every `f` and every `c`. She was honest about this one: it was **not yet
discharged.** But it was no longer *impossible*, only *expensive* — the foundation it needs was already
in place and already proved (the inode round-trip composes; the written block is recoverable across the
reopen), so what stood between her and `Valid` was the proof cost of the content-effect chain, not any
missing foundation. It was the law's last word, and it was within reach of exactly the tower she had
built.

She turned off the one screen.

It was, she thought, the best kind of magic trick: every piece had either set up the reveal or hidden
it, and there was no dead weight in the whole machine. And the reveal was only this — that a real module,
the Python `os` that every program leans on, can be made to *prove* it keeps its word, for every input
at once, if you are willing to rebuild it from faithful parts, prove the smallest part, and climb.

---

> *The proof is the return journey of the specification. The law descends in English, becomes a faithful
> model, becomes the smallest checkable contract; then it climbs back, carried on verification
> conditions, until it is the law again — but mechanically true now, quantified over every input,
> closed. A concrete test convinces a person; a discharged verification condition obliges the input
> space. The whole craft is learning the difference, and then building a machine honest enough that the
> answer comes back* Valid.
> — field notes, PyCSL verification log: `pure_lib/os/` — 0 goals unproven, 1 axiom in the trusted base;
> the end-to-end content-equality theorem (`formal_0008`) the standing frontier.
