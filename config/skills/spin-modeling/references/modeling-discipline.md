# Modeling Discipline: Guarded `d_step` Transitions

This is the central discipline of the skill. **Every transition in the model is a guarded `d_step` whose precondition guarantees the body runs to completion.** If you follow this rule, your models map cleanly to state diagrams, stay small enough to verify, and force you to think clearly about every transition's precondition.

## Why this matters

Spin works by exhaustively exploring the global state space of the model — every possible interleaving of every transition of every process. The size of that state space grows exponentially in two ways:

1. With the number of *processes* (each adds an axis of interleaving)
2. With the number of *transitions per process* (each becomes a branch point in the search)

You can't help the first one without reducing what you model. But you can help the second one enormously by collapsing internal sequences of statements into single transitions. Spin doesn't interleave statements *within* a `d_step` block — it treats the whole block as one transition. Every statement you fold into a `d_step` is one less interleaving point Spin has to consider.

This is the difference between a model that verifies in 0.2 seconds and one that exhausts memory.

## The pattern

```promela
do
:: guard1 ->
   d_step { /* transition 1 body, proven non-blocking by guard1 */ }
:: guard2 ->
   d_step { /* transition 2 body, proven non-blocking by guard2 */ }
:: guard3 ->
   d_step { /* transition 3 body, proven non-blocking by guard3 */ }
od
```

- The `do` loop is the process's "live forever, take any available transition" frame.
- Each `::` arm is one transition.
- The guard names the precondition that makes the transition *fireable*.
- The `d_step` body is the deterministic, atomic update — what state changes when the transition fires.

This is exactly the shape of a UML state diagram: each arm corresponds to one outgoing arrow from the current state, the guard is the arrow's `[condition]` annotation, and the `d_step` body is the action label.

## Spin's hard rule on `d_step`

From the Promela reference: *"It is an error if the execution of any statement inside the sequence can block."* During verification, Spin will reject the model if any statement inside a `d_step` blocks.

The blocking statements in Promela are:

- A send `c ! v` on a channel that is full (or, for rendezvous, where no receiver is ready)
- A receive `c ? v` on a channel that is empty (or, for rendezvous, where no sender is ready)
- An evaluation of a guard that is false (`if`, `do`, or standalone Boolean expression)

The guard on the *outside* of the `d_step` is what makes the body safe: by the time the choice arm fires, the guard has already established that every potentially-blocking statement inside will succeed.

## Deriving the guard from the transition body

For each transition, ask: "what must be true *before* this transition fires for every statement inside to succeed?"

| Body statement       | Required precondition (add to guard)              |
|----------------------|---------------------------------------------------|
| `c ! v` (buffered)   | `nfull(c)`                                        |
| `c ? v` (any)        | `nempty(c)` or do the receive *as* the guard      |
| `x = y / z`          | `z != 0` (to avoid the divide-by-zero modelled state) |
| `arr[i] = v`         | `i >= 0 && i < SIZE`                              |
| `assert(P)`          | `P` (or model the failure as part of the spec)    |
| Plain assignment     | (no precondition needed, never blocks)            |

For a receive specifically, the cleanest pattern is to put the receive *in the guard* — Promela allows a receive as a guard expression, and it fires only when a message is available:

```promela
:: link ? msg ->
   d_step {
     /* msg is now bound; rest of transition cannot block on link */
     state = process_message(msg);
   }
```

This is idiomatic and preferred: it expresses "this transition fires when a message arrives" naturally and keeps the `d_step` non-blocking.

## A complete worked example: a two-state component

A Component with two internal states (`Ready` and `Busy`) and three transitions:

- Receive a job: `Ready → Busy`
- Finish the job: `Busy → Ready`
- Reject a job while busy (drop it): `Busy → Busy`

```promela
mtype = { job, done };
chan in   = [4] of { mtype };
chan out  = [4] of { mtype };

active proctype Component() {
    bit busy = 0;

    do
    /* transition 1: receive job while ready */
    :: !busy && nempty(in) ->
       d_step {
         mtype m;
         in ? m;            /* guaranteed non-empty by guard */
         assert(m == job);  /* sanity */
         busy = 1;
       }

    /* transition 2: finish the current job */
    :: busy && nfull(out) ->
       d_step {
         out ! done;        /* guaranteed has space by guard */
         busy = 0;
       }

    /* transition 3: drop a job because we're busy */
    :: busy && nempty(in) ->
       d_step {
         mtype m;
         in ? m;
         /* dropped */
       }
    od
}
```

Each arm has a guard that establishes the precondition for every blocking statement in the body. Each `d_step` is then deterministic and atomic. The model has exactly three transitions per logical state, matching the state diagram exactly.

## When you legitimately cannot use `d_step`

Three cases come up in practice. In each, fall back to `atomic` (or a plain sequence) — but only after you've satisfied yourself you can't refactor.

### 1. A transition that genuinely needs to wait mid-sequence

Sometimes the *semantics* of the transition is "send this, then wait for a response, then update state". You can't collapse the wait into a guard because the wait happens *after* the first send. The right model here is to split into two transitions, with an intermediate state variable that says "I am waiting for the reply":

```promela
:: state == idle ->
   d_step { link ! request; state = waiting; }
:: state == waiting && link ? eval(reply) ->
   d_step { state = idle; result_ready = 1; }
```

Two transitions, one intermediate state, both `d_step`-clean.

### 2. A rendezvous send

`d_step { rendezvous_chan ! v; ... }` is unsafe even with `nfull` in the guard, because rendezvous channels are always "full" — they hold no messages. The pattern is either to switch to a buffered channel of capacity 1 (if the synchrony isn't essential to the property you're checking), or to put the send outside the `d_step`:

```promela
:: ready_to_send ->
   atomic {
     rdv ! msg;          /* may block until receiver is ready */
     ready_to_send = 0;
   }
```

`atomic` here permits the block; the trade-off is a slightly larger state space than a true `d_step` would give.

### 3. A genuine non-determinism inside the body

A `d_step` resolves non-determinism deterministically (always taking the first true guard of an inner `if`/`do`). If the model's correctness depends on Spin exploring *both* arms, you can't use `d_step`. Either split the transitions, or use `atomic`.

## Checklist before writing a `d_step`

Before you write the closing `}` of a `d_step` block, walk through it line by line and answer:

1. Can this statement block? If yes, is the precondition that prevents the block in the guard?
2. Is the body deterministic? (Any inner `if` whose arms must both be explored is wrong here.)
3. Is there a `goto` into or out of this block? (Spin forbids it — and the `break` inside a final `do ... od` of a `d_step` is also a parse error; use a trailing `skip` if needed.)
4. Could the body loop forever? (Spin does not save states inside a `d_step`; an infinite loop here hangs the verifier with no diagnostic.)

If any answer is "I don't know", figure out the answer before continuing. Quietly violating these rules is the dominant way `d_step`-based models become subtly wrong.

## Why this discipline aligns with state-diagram modeling

A UML state diagram is exactly: states, plus transitions, plus guard conditions, plus action labels. The Promela `do ... od` with guarded `d_step` arms is the *direct textual translation* of that diagram:

| State diagram element       | Promela construct                  |
|-----------------------------|------------------------------------|
| State                       | Implicit between transitions       |
| Transition                  | `::` arm in `do ... od`            |
| Guard condition `[cond]`    | Guard expression before `->`       |
| Action `/ action`           | Body of the `d_step`               |
| Outgoing arrows from state  | Multiple `::` arms                 |
| Self-loop                   | Arm whose `d_step` doesn't change state |

This isn't a coincidence — Spin's underlying model is the labeled transition system, which is exactly what a state diagram describes. The `d_step` discipline is what makes the textual model and the visual diagram say the same thing.

When you draw a state diagram for a Component or Module and then write a Spin model of it, the diagram is the contract; the Promela is the executable proof. If the two diverge, the model is wrong (you've introduced behavior the diagram doesn't permit) or the diagram is incomplete (Spin has found behavior the diagram missed).
