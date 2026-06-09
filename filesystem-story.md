# LES OCTETS
### *The Bytes — a philosophie-fiction in three acts*

> *A test asks: did it work this time? A proof asks: could it ever fail?*
> — Edmond Wells, *Encyclopedia of Relative and Absolute Knowledge, Vol. VII: On Faithful Machines*

---

## ACT ONE — THE PLEDGE

### 1.

Ada read the old law by the light of one screen.

It was written in English, the way all the oldest laws are, in a tongue that had outlived the
machines it governed. *When a file is opened for writing and bytes are written to it,* the law said,
*then closed, then opened again and read, the bytes that return shall be the bytes that went in.* No
clause excepted. No footnote forgave. It had the flat certainty of scripture, and like scripture it
promised something it did not itself prove. POSIX. The Open Group base specifications. The source of
truth.

She had read it a hundred times. Tonight she read it once more and underlined a single word: *shall.*

Not *usually.* Not *in our tests.* *Shall.*

"All right," she said to the empty room. "Let's see if you mean it."

---

### 2.

In the warm country above the disk — the country of *meaning*, where a number was simply a number and
nobody had yet been folded into bytes — Seventy-Two woke to the news that they were going on a journey.

There were five of them. Seventy-Two, who in the old human alphabet had once been the shape **H**;
then One-Hundred-and-One, who was **e**; then the twins, both One-Hundred-and-Eight, who were the two
**l**s and never could be told apart; and last, round and cheerful, One-Hundred-and-Eleven, the **o**.
Together they spelled a small word that meant *greeting.* Together they were content. They were, in the
most literal sense, *the content.*

"Where are we going?" asked the **o**.

"Down," said Seventy-Two, because it was the eldest and felt it ought to know. "Down to the disk. We're
to be written."

The twins shivered as one. Everyone in the warm country had heard about the disk. It was vast — a
hundred and thirty-one thousand and seventy-two cells of pure dark — and it did not care what you meant.
Down there you were not a letter. You were a value between nought and two hundred and fifty-five, and
nothing more, and if a single bit of you was lost in the writing or muddled in the reading you would
come back as some other number entirely, some stranger wearing your place, and the word you had spelled
would be a word no longer.

"But we'll come back?" said the **o**. "The same? We'll come back *the same?*"

Seventy-Two looked down the long shaft toward the dark and did not answer, because answering honestly
would have frightened them, and answering dishonestly was against its nature.

---

> *Every faithful machine is built of faithful parts. You cannot inspect the honesty of the whole by
> staring at it; the whole is too large to hold in one mind. So you do the opposite. You find the
> smallest part — the part so small its honesty can be checked at a glance — and you prove that one
> faithful. Then you prove the next part faithful given the first. Faithfulness, unlike doubt, composes
> upward.*
> — Edmond Wells, *Encyclopedia*, Vol. VII

---

### 3.

Ada did not own a kernel, so she built one.

This was the strange discipline of it. The real `os`, the one that shipped, reached down through the C
and trapped into the operating system and let the hardware keep its secrets. She could not prove what
she could not see, and she could see none of that. So she rebuilt the whole of it upward, in plain
Python, in the light: a disk that was only an array of a hundred and thirty-one thousand and seventy-two
honest integers; an inode region staked out from byte five hundred and twelve to byte two thousand five
hundred and sixty, thirty-two little records of sixty-four bytes each; a bitmap; a root directory living
in block five; data blocks after. Where the true kernel would have trapped into mystery, her model did,
in the open, exactly the work the kernel would have done.

People asked her why she didn't simplify. Why model the bytes at all — why not let a file just *be* its
content, abstract and clean, and skip the grubby business of packing integers into big-endian quartets?

Because a filesystem *is* a byte layout under an interpretation, she said. A file's data really does
live in a block whose number is really written, most-significant byte first, into the bytes of its
inode. If she abstracted that away she would be proving a story about a filesystem, not a filesystem.
And the old law had said *shall.* You do not answer *shall* with a story.

So she wrote the codec — the narrow bridge between the warm country of meaning and the cold country of
bytes. `_pack_uint16_be`, that took a number and laid it down as two bytes. `_unpack_uint16_be`, that
took two bytes and lifted a number back out. And above them, composed of them, `_pack_inode` and
`_unpack_inode`, the great gate through which every traveler had to pass.

She did not annotate them yet. First, she said, I run it. A model you cannot run is a model you cannot
trust.

She typed a word into the test by hand — `HELLO` — watched five known integers go down into the dark
and come back five known integers, and saw the word survive.

"Good," she said. "It works."

And then, because she was honest, she said the thing that ruined the night: "It works *this time.*"

---

## ACT TWO — THE TURN

### 4.

The writing did not hurt, exactly. It was more that the warm country thinned, and meaning fell away.

Seventy-Two felt the **H** peeled off it like a coat. It felt itself approach the gate called
`_pack_inode` and pass through and become, on the far side, simply a quantity laid into a cell. It could
no longer tell the twins apart from the outside — they were both just *one hundred and eight* now, two
identical marks in two adjacent cells of block six. The word was gone. Only the values remained,
scattered along the dark, big-endian, patient.

Then `close` was called, and the lights went out.

This is the part the travelers never describe afterward, because there is nothing in it to describe.
The disk does not narrate. Seventy-Two lay in its cell in the absolute dark and did not know whether a
year passed or an instant, did not know whether the cell beside it still held One-Hundred-and-One or
some careless stranger, did not know whether, when the lights came back, there would be any *word* left
to be. It knew only its own value, and that it could not check.

*Will I come back the same,* it thought, into the dark, *and will there be anyone to know that I have?*

The dark did not answer. The dark never answers. That is precisely the problem.

---

> *The terror of the disk is not corruption. Corruption is rare. The terror is that corruption is
> **undetectable from the inside**: a byte cannot tell whether it has been changed, because change is
> exactly the loss of the thing it would compare against. The traveler who returns altered does not feel
> altered. He feels like himself. He has simply become a different self. This is why the disk must be
> made trustworthy from the **outside**, before the journey — by someone who can hold both the going-in
> and the coming-out in the same thought, and demand they match.*
> — Edmond Wells, *Encyclopedia*, Vol. VII

---

### 5.

Now Ada wrote the contracts, and she wrote them from the bottom.

She would not let a large function be believed on faith. She started with the smallest leaf, the
two-byte packer, and gave it a promise it could not wriggle out of:

```
#@ ensures \result[0] * 256 + \result[1] == v
```

*The two bytes I lay down, read back as a number, are the number you gave me.* Eleven symbols. A thing
so small its honesty could be checked at a glance — and she made the machine check it, not her. Why3
took the function and its promise and ground them into a logical formula, a verification condition, and
handed it to the solvers. Alt-Ergo considered the negation of the promise — *suppose the bytes did
**not** read back as `v`* — and found that supposition impossible. **Valid.**

One faithful part.

Then the next, given the first. `_pack_inode` and `_unpack_inode` did not need new faith; their honesty
*composed* from the leaves' — unpack of pack returns what you packed, not by decree but because each
field, byte by proven byte, came home. She climbed. `_write_inode`, with its promise that a written
inode could be recovered. The bitmap allocator. The directory lookup. The syscalls — `open`, `write`,
`read` — each given a contract narrow and exact, each standing on the proven contracts beneath it rather
than re-deriving them. Over every method she stretched a single invariant — *the disk is at least a
hundred and thirty-one thousand and seventy-two cells; the inode bytes stay bytes* — so that each
function both assumed the world was well-formed and left it well-formed for the next.

The unproven count fell. Forty. Twenty-three. Eleven. Three. One.

Zero.

She sat back. Every contract Valid. The whole tower stood, resting on the ground and on a single
cross-validated axiom she had written down by name and could point to — the one thing assumed in a
structure of ten thousand things proved.

And it was *not enough,* and she knew it was not enough, and that was the corner she had walked herself
into.

---

### 6.

Because what had she proved? That `pack` was faithful. That `write` changed exactly the cells it
claimed. That no array was ever read out of bounds. Safety. Structure. Real, and not nothing — but not
the old law.

The old law said the *content* comes back. The whole word. `HELLO` in, `HELLO` out. And how do you
prove *that?*

She wrote out the impossibility in plain words, the way you do at three in the morning to see how bad it
is. *To know the filesystem returns every file unchanged, I would have to write every file, and read it
back, and check. But there are more possible files than there are atoms. I cannot test my way to* shall.
*A test only ever samples. I could run it a billion years and cover nothing.*

The five bytes lay in the dark, and could not check themselves. Ada sat in the light, and could not
check them all. Between them was the disk, which does not answer.

It looked, for a while, genuinely impossible — the honest kind of impossible, with no convenient door.

And then she remembered the smallest entry, the one that had seemed like trivia, the one she'd read so
often she'd stopped hearing it.

*A test asks: did it work this time? A proof asks: could it ever fail?*

She had been trying to *test* her way to *shall.* But she had spent the whole night building the other
thing. She didn't have to run the file. She had to write the file as a *symbol* — an arbitrary
content, any content, every content at once — and ask the machine not *did this one survive* but *could
any one fail.* The thing she'd proved of the leaf — *for all `v`* — she could ask of the whole.

Of course. *Of course.* Why hadn't she seen it. The proof had never been about a file. It had been
about the *symbol* standing in the place of every file.

She began, very quietly, to write the last test.

---

## ACT THREE — THE PRESTIGE

### 7.

It looked exactly like the rehearsal. That was the trick of it; that was always the trick.

```
#@ ensures \result == True
def formal_test_0008(f: str, c: list) -> bool:
```

The same scenario she had run by hand with `HELLO` — create the file `f`, write the content `c`, close
it, open it again, read it back, return whether what came out equalled what went in. The same six steps.
A reader glancing at it would have seen the concrete test of Act One and thought: *more of the same; she
is sampling again.*

But `f` was not `"HELLO"`. `f` was *a filename* — any filename. And `c` was not five known integers.
`c` was *the content* — bounded by a `requires` and otherwise utterly arbitrary, a symbol standing in
the place of every file that could ever be. And the postcondition did not hedge. It did not say *usually*
or *in our tests.* It said `\result == True`. It said *shall.*

She gave it to Why3. Why3 turned the whole scenario — every syscall, every codec leaf, the inode round-
trip now available as a *proven* contract, the block recoverable across the close and the reopen — into
one weakest-precondition formula whose meaning was simply: *for this to return False, some content must
fail to come home.* And it handed that formula to the solver, and the solver did the only thing it knows
how to do. It tried to make it False. It searched for the one content, out of all the contents more
numerous than atoms, that the filesystem would corrupt.

---

### 8.

In the dark, the lights came back.

Seventy-Two felt itself approach the gate from the cold side — `_unpack_inode`, the same gate run
backward — felt two patient bytes in block six be lifted and become, once more, a quantity that
remembered it had been *one hundred and eight,* and another, and the round cheerful *o,* and itself,
**H,** seventy-two, unaltered, every bit accounted for. The word reassembled around it out of the dark
like a held breath let go.

But this time something was different, and the difference was the whole point. This time Seventy-Two was
not *a* traveler who had happened to come home. This time it was *every* traveler. It was the symbol. It
stood, in that final reading, for all the words that had ever been written and all the words that ever
would be, and the gate it passed through had been proven — leaf by faithful leaf, composed upward, all
the way to the law — to return *every one of them* unchanged.

"We came back," whispered the **o**.

"Yes," said Seventy-Two. And then, because it was old, and honest, and had waited all night in the dark
for the right to say it: "And not because we were lucky. Because we could not have done otherwise."

---

### 9.

The solver searched the space of all possible contents for one that would fail.

It found none. It could find none. The negation was unsatisfiable. There was no corrupting file, not
among the billion, not among the atoms, not anywhere, because every byte's journey had been built from
parts each proven faithful, and faithfulness composes upward.

The screen returned one word, and Ada had engineered the entire night so that this one word would mean
everything:

**Valid.**

Not *it worked this time.* Not *it passed our tests.* For every filename. For every content. For all
inputs the contract admits — at once, forever, with one trusted axiom named and the rest proved.

She looked at the underlined word in the old law. *Shall.*

"You meant it," she said.

The trivia had been the trick. The little entry about tests and proofs, read so often it went invisible
— that had been the key the whole time, planted on the first page, disguised as a thought. The smallest
contract, eleven symbols on a two-byte leaf, the one that looked like a detail — that had been the
foundation the law stood on. The concrete test she ran in Act One to convince herself the model was
right was, it turned out, only the rehearsal for the symbol that proved it right for everyone.

She had descended from the English law down through the faithful model to the smallest honest part. And
then she had climbed back, proving as she went, until at the top she wrote the law out again — *the
bytes that return shall be the bytes that went in* — and the machine, for the first time in the history
of the law, replied not *we tried it* but *it cannot fail.*

The five bytes, up in the warm country, spelled their small word again, and meant *greeting,* and did
not know — could not know, being only content — that they had been made immortal. That every word like
them, now and forever, would come home as itself.

Ada knew. She turned off the one screen, in the country of meaning, above the disk.

It was, she thought, the best kind of magic trick. Every piece had either set up the reveal or hidden
it. There was no dead weight in the whole machine.

And the reveal was only this: that *shall* is a promise a machine can keep, if you are willing to build
it from faithful parts and prove, of the symbol that stands for everything, that it could never fail.

---

> *The proof is the return journey of the specification. The law goes down in English, becomes a
> faithful model, becomes the smallest checkable part; and then it comes back up, carried on proofs,
> until it is the law again — but now mechanically true, for every input, closed. A concrete test
> convinces you. A proof obliges the universe. Learn the difference, and you can make a machine keep
> its word.*
> — Edmond Wells, *Encyclopedia of Relative and Absolute Knowledge*, Vol. VII: *On Faithful Machines*
