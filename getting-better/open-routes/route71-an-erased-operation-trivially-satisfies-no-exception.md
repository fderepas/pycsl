# OPEN ROUTE #71 — AN **ERASED** OPERATION TRIVIALLY SATISFIES `no_exception`
# (found 2026-09-11 by relaunch #55, at `3f0858f4`)

## THE CARRIER

```python
@mutable_state
@dataclass
class C:
    s: Set[int] = field(default_factory=set)

    #@ requires True
    #@ no_exception \all
    #@ ensures True
    #@ assigns \nothing
    def probe(self, t: Set[int]) -> int:
        t.remove(5)          # CPython: KeyError: 5
        return 0
```

**`[+] Verification SUCCESS! All contracts formally proven.`** The emitted body is:

```whyml
  let c__probe (self: c) (t: map int (option int)) : int
  = ();
    0
```

**The operation is GONE.** `t.remove(5)` lowered to `()` — the documented
`@mutable_state` collection-parameter no-op — and an operation that is not emitted cannot
carry an obligation, so `#@ no_exception \all` discharges over a body that does nothing.

## THE GENERAL PRINCIPLE, WHICH IS WORTH MORE THAN THIS CARRIER

**ANY ERASURE IS AUTOMATICALLY `no_exception`-CLEAN.** The exception model injects
obligations at emission sites; an operation the emitter DROPS has no site, so it silently
satisfies every `no_exception` claim. That inverts the usual reading of an erasure: a dropped
mutation is normally argued to be *fail-closed* ("the post-state claim becomes unprovable"),
and that argument is about POSTCONDITIONS. For `no_exception` it runs the other way — the
erasure makes the claim EASIER, not harder.

So every documented erasure in the compiler is a `no_exception` hole by construction. The
ones already on record: the `@mutable_state` collection-param no-op (this carrier), the
`with`-body erasure, and the `emit_ir` in-place store no-op. **Each should be re-read with
the question "what does `no_exception \all` say about this body once the operation is gone?"**

## SCOPE, MEASURED

  * A set PARAM `.remove` inside `@mutable_state`, contract NOT naming the param: **BROKEN**
    (the headline).
  * The same with the contract NAMING the param: already refused by route #62's guard.
  * A LOCAL set `.remove`: **does NOT prove** — the local path is not erased.
  * `del d[k]` on a local dict: wired in route #66, and it discriminates.

## RELATION TO ROUTES #62 AND #63

This is the THIRD gap found in the same `@mutable_state` exemption. #62 was the mutation one
call away from the contract; #63 was the same collection in two argument positions; #71 is
the exemption meeting `no_exception`. The exemption's own documentation says it rests on "a
claim about the corpus, not a property of the lowering" — three independent probes have now
each found a way through it, which is the strongest available argument that the exemption
should be replaced by a real caller-visible mutation frame rather than guarded case by case.

## THE REPAIR SHAPE

In the same `\trusted` pre-pass that already carries the #62/#63/#65 guards: when a function
declares `no_exception` covering `KeyError` (or `\all`), refuse a collection-parameter
mutation that would be erased. The operation cannot raise in the model precisely because it
does not exist there, and that is not a fact a soundness claim may rest on.
