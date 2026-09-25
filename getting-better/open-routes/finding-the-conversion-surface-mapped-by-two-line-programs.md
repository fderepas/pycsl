# The conversion surface, mapped by two-line programs

**Status: METHOD + MAP.** Not a defect report — a measurement of what PyCSL actually
supports, taken with the cheapest instrument available and replacing three generations of
backlog rankings that were taken by counting.

## Why this exists

`getting-better/driver-backlog.md` has ranked the conversion track's blockers three times.
Every ranking was produced by reading candidates or counting the bodies that contain a
construct, and the file itself records the result: *"top-level statement count is a proxy and
it has now been wrong four times"*, and *"a refusal message tells you what stopped YOU, not
what stops the population"*.

A two-line program costs twenty seconds and answers the question the count is a proxy for.
Forty-nine of them, in one afternoon, moved four backlog entries from counts to facts and
one of them from "a wall" to "not a wall at all".

## Strings — SIXTEEN probes, SIXTEEN verify

    s.startswith("a")    s.endswith("a")     s.replace("a", "b")   s.upper()
    s.split(".")[0]      s.split(".", 1)[0]  s.strip()             s.isdigit()
    s[0:2]               s[0]                len(s)                s + t
    s == t               s in t              str(n)                int(s)

**Every one VERIFIES.** The string surface is not a conversion blocker in any of the shapes
the mirror actually uses, including `s.split(".", 1)[0]` — the exact expression at the top of
`import_classifier.classify`, one of the backlog's candidates.

This is a NEGATIVE result and it is the most useful kind: it removes a whole class of
suspicion from every future conversion attempt. When a conversion fails, it is not the
strings.

## The three "population walls" — two of them are not walls

Counted at f-strings 186 of 442 bodies, comprehensions 170, dict literals 160. Probed:

    VERIFIES
      f"a{s}b"   f"{n:03d}"   f"{s}={n}"          f-strings, three shapes
      [y + 1 for y in xs]                         comprehension over a List param
      [y for y in xs if y > 0]                    ... with a filter
      [y for y in xs]; [z for z in ys]            nested
      {"a": 1, "b": 2} then d[k]                  dict literal, STRING keys
      ys = [1, 2]; ys.append(n)                   list literal then append

    FAILS
      [y for y in range(n)]        comprehension over a RANGE        array mismatch
      [abs(y) for y in xs]         comprehension with a CALL element array mismatch
      {y: y for y in xs}           DICT comprehension                unbound type symbol
      {y for y in xs}              SET comprehension                 unbound type symbol
      s = {1, 2, 3}; n in s        SET LITERAL                       type mismatch
      ",".join(xs)                 str.join over a list              array int mismatch

**F-strings are not a wall.** Nor are list comprehensions or dict literals in the shapes
that dominate. What remains is narrow and nameable, and the list above is the one to build
against.

## Dicts — ten probes, six verify, and one asymmetry worth knowing

    VERIFIES                                   FAILS
      d[k]                                       len(d)                 array mismatch
      d.get(k, 0)                                for k in d             array mismatch
      k in d                                     d.setdefault(k, 0)     explicit REFUSAL
      d[k] = v      (mutation, `assigns d`)      Dict[str, Dict[str,int]]  int mismatch
      len(d.keys())
      len(d.items())

**`len(d)` fails and `len(d.keys())` verifies.** That is the kind of fact a probe map exists
to produce: a one-token workaround for a construct that otherwise stops a conversion, found
by running two programs that differ by six characters.

`d.setdefault` is the only REFUSAL in the whole map rather than a type error, and its message
is exemplary — *"MUTATES its receiver in place, and no certified lowering models it: the call
becomes an abstract operation that takes NEITHER the receiver NOR a `writes` clause"*. A
refusal that explains itself is worth more than a lowering that does not, and this one is the
reason `d[k] = v` is safe: the mutation that IS modelled carries its frame.

## Sets — ten probes, and one line of source explains all of them

Recorded in full in `finding-a-set-has-no-element-type-and-no-union.md`. In short:
membership and `add` are modelled, a union with a set LITERAL inside a `@mutable_state` class
is modelled, and everything else — `&`, `-`, `^`, `.union`, `.intersection`, `len`, a
set-to-set union, a union outside `@mutable_state` — is not. A read-only `Set[str]`
parameter is int-keyed while a mutated one is string-keyed, which is one gate
(`functions.py` ~137) seen from two sides.

## Past lowerability: SIX faithfulness probes, each with a FALSE TWIN

The map's boundary says a VERIFY means "lowers and type-checks". The obvious next question —
does the lowering MEAN anything — is answered the same cheap way, with the twin discipline
the directive sweep already uses: a true claim must SUCCEED and its false neighbour must FAIL.

    TRUE                                                    FALSE TWIN
    len(s) == \str_length(s)                 SUCCESS        ... + 1          unproven
    len(s + t) == \str_length(s) + \str_length(t)  SUCCESS   ... + 1          unproven
    len(s[0:0]) == 0                         SUCCESS        == 1             unproven
    ("" + s) == s                            SUCCESS
    len(s.upper()) == \str_length(s)         **unproven**
    s.replace("a", "a") == s                 **unproven**

So `len`, concatenation length, the empty slice and the empty-string identity are FAITHFUL —
they prove, and their false neighbours do not, which is what makes "prove" evidence rather
than a shrug.

**`.upper()` and `.replace()` are OPAQUE, and that is documented.** The static-semantics
reference says so at §697 — *"like `s.upper()` — an opaque `str_upper_op`, genuinely
non-injective"*. The probe confirms the documentation rather than finding a defect, which is
worth recording precisely because the temptation in a session full of findings is to read
every `unproven` as one.

A converted function may therefore use `.upper()`/`.replace()` freely — they LOWER — but it
cannot carry a contract that depends on what they return. That is a different and much
smaller restriction than "strings are a wall", and it is the kind of sentence the map exists
to produce.

## The method, stated so it can be reused

1. **When a conversion attempt produces a type error, do not re-attempt the conversion.**
   Write the two-line program that isolates the operator. Twenty seconds, and it tells you
   which half of a compound error is which.
2. **Probe the neighbours of every failure.** Four probes that fail the same way is a reason
   to ask how far the sameness goes — that is how "union is missing" became "membership and
   `add` are the entire modelled surface".
3. **When a mechanism explains N probes, run probe N+1 that the mechanism FORCES and the
   symptoms do not.** Wall-lesson (a6). Three wrong write-ups of the set table were each
   fitted to the same ten rows; the one that survived predicted an eleventh.
4. **Read the MESSAGE, never the verdict column.** The first run of the wall probes reported
   six failures that were the PROBE — a `printf` that did not expand `\n`. The column said
   "PIPELINE ERROR" six times and looked like a finding; the message said
   `unexpected character after line continuation character`.

## What this does not tell you — and it is a sharp boundary

**Every probe carries `#@ ensures True`, so a SUCCESS means the construct LOWERS AND
TYPE-CHECKS. It does not mean the lowering is FAITHFUL.** `len(d.keys())` verifying says
Why3 accepted the emission; whether the value it produces is the dict's size is a different
question, and the one the corpus-truth oracles exist to answer. The two questions are worth
keeping apart: a conversion is stopped by the first and a soundness route lives in the
second.

That scoping is also why the map is cheap. A faithfulness probe needs a contentful
postcondition and a reason to believe it; a lowerability probe needs `ensures True` and
twenty seconds, and lowerability is exactly what a conversion attempt runs into.

And a probe says an operator lowers — not that a REAL function converts. A real body is a
CHAIN of operators, and the second link is invisible until the first is closed; the set
record documents exactly that, twice. The map narrows the search. It does not replace the
conversion.
