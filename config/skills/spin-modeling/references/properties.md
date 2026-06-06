# Properties Beyond Deadlock

Deadlock — Spin's "invalid end state" — is the default property and the most common one to check. But the same model can be checked against many other properties, and at the System and Component levels of the methodology, you usually want at least a few of these alongside deadlock.

This page covers, in order of increasing power: assertions, end labels, progress labels, and LTL formulas. Each adds expressive power and verification cost.

## Assertions: pointwise safety

The simplest property is an assertion at a specific point:

```promela
assert(buffer_count >= 0 && buffer_count <= MAX);
```

Spin checks the assertion every time control reaches that point in *any* execution. If it ever fails, Spin reports an assertion violation and writes a trail.

Assertions are *pointwise*: they only check the assertion at that exact line. To check "this invariant always holds", you'd need to add the assertion at every place state changes. For that, see global invariants below.

### Global invariants via a monitor process

To check "this invariant holds in every reachable state", spin up a monitor process that asserts the invariant non-deterministically:

```promela
active proctype Monitor() {
    do
    :: assert(buffer_count >= 0 && buffer_count <= MAX)
    od
}
```

The monitor's `do` loop has one always-fireable arm. Spin will explore states in which the monitor fires at every reachable global state — so the assertion is effectively checked everywhere.

This is the canonical way to express "invariant I should hold in every reachable state of the system".

## End labels: valid termination states

By default, a process that has run off the end of its body is in an "end state" and that's considered valid termination. But a process *blocked* at a non-end label is a deadlock contribution.

Mark valid waiting states with labels beginning with `end`:

```promela
active proctype Worker() {
    do
    :: job_queue ? task -> process(task)
    :: shutdown -> break
    od;
end_worker:
    skip
}
```

A Worker sitting at `end_worker` is fine. A Worker stuck mid-process (e.g., in `process(task)`) when no other process can advance — that's a deadlock.

End labels also matter for receivers waiting on channels indefinitely. A request-handling process that "always" waits for the next request should have an end label at the receive point:

```promela
end_idle:
    in ? req ->
    d_step { ... }
```

Spin will treat sitting at `end_idle` as valid termination if everyone else is also done.

## Progress labels: liveness

Deadlock is the absence of *any* progress. Livelock is the absence of *meaningful* progress — the system keeps moving, but never accomplishes anything useful. To check for livelock, mark the states that represent real progress:

```promela
do
:: in ? msg ->
   d_step {
     /* genuine work happening here */
     processed++;
   };
progress_handled:
   skip
:: cleanup ->
   d_step { ... }
od
```

Then run `./pan -l` (liveness mode): Spin will look for cycles that don't pass through any `progress`-labeled state. Such a cycle is a non-progress cycle — the system loops without doing work.

This is the standard way to catch protocols that ack each other forever without ever delivering a payload.

## LTL: rich temporal properties

Linear Temporal Logic lets you say things like:

- "Every request eventually gets a response": `[]( req -> <> resp )`
- "Once shutdown is signaled, no further work begins": `[]( shutdown -> [] !work )`
- "Mutual exclusion": `[]( !(in_cs1 && in_cs2) )`

The operators are:

- `[] P` — *always* P (P holds in every state)
- `<> P` — *eventually* P (P holds in some future state)
- `P U Q` — P holds *until* Q (P stays true until Q becomes true)
- `X P` — *next* P (P holds in the next state)
- `!P`, `P && Q`, `P || Q`, `P -> Q` — Boolean

To use LTL, write a claim and reference it in the model:

```promela
bit req = 0;
bit resp = 0;

ltl response_after_request {
    [] (req -> <> resp)
}
```

Compile and verify against the claim:

```bash
spin -a model.pml
gcc -O2 -o pan pan.c
./pan -a -N response_after_request
```

`-a` enables acceptance-cycle detection (needed for the `<>` operator); `-N name` selects which named claim to check.

For Promela versions where named LTL isn't supported, use `never claims` (see below) or pass the formula on the command line: `spin -f '[] (req -> <> resp)' > claim.pml` produces a never-claim file you can `#include`.

### Practical LTL patterns at the System/Component level

A short catalog of useful properties for verifying a coordination spec:

| Pattern              | LTL                              | Meaning                                              |
|----------------------|----------------------------------|------------------------------------------------------|
| Eventually responds  | `[]( req -> <> resp )`           | Every request gets a response                        |
| Mutual exclusion     | `[]( !(p1_in_cs && p2_in_cs) )`  | Two processes never simultaneously in critical state |
| One-shot startup     | `<> initialized && [] (initialized -> [] initialized)` | Init happens once and stays    |
| No work after stop   | `[]( stopped -> [] !working )`   | Once stopped, work never restarts                    |
| Bounded delay        | `[]( req -> ((!ack) U (ack && bounded_count_ok)) )` | ack arrives within bound       |

The last one is awkward in pure LTL (LTL can't directly express "within N steps"); usually you encode the bound as a counter in the model and assert the counter stays small.

## Never claims: the underlying machinery

Both LTL and progress labels compile down to *never claims*. A never claim is a Promela-like process that describes a "bad" sequence of states; Spin verifies that no execution of the model produces a behavior accepted by the never claim. This is the machinery the LTL `ltl { ... }` block compiles into.

You almost never write never claims by hand — `ltl { }` is strictly easier — but you'll see them in tutorials and older models. Treat them as the assembly language of Spin properties.

## Fairness

By default, Spin explores *all* interleavings, including ones where one process never runs. This is sometimes too pessimistic — a real scheduler is usually weakly fair (every enabled process eventually runs).

`./pan -f` (weak fairness) constrains the search to fair interleavings only. This often eliminates false-positive liveness counter-examples. Use it for liveness checks; safety checks don't need it (a safety violation under unfair scheduling is still a real bug).

## Picking the right properties for the level

At the **System level**: the most important property is usually "no deadlock". Secondary properties to add:
- Every external request gets a response (LTL).
- The system reaches the operational state (assertion on a state variable, or LTL `<> operational`).
- The system never enters two incompatible modes at once (mutual exclusion via assertion or LTL).

At the **Component level**: properties tighten to the component's contract:
- The component's interface never deadlocks against an arbitrary caller.
- The component's internal state invariant holds globally (monitor process with assertion).
- The component eventually completes any operation it accepts (LTL).

At the **Module level**: rarely needs Spin. Spin's strength is concurrent coordination; sequential module logic is better verified with unit tests, types, or formal proof (ACSL, Pearlite). If a module has *internal* concurrency, then yes, Spin applies — but the model is usually small.

## What Spin cannot verify

Useful to remember the limits:

- **Real time.** Spin's "time" is a count of transitions, not seconds. Discrete-time extensions exist but aren't first-class.
- **Probabilistic properties.** "This happens with probability 0.99" is outside Spin's reach. (Tools like PRISM handle it.)
- **Infinite-state systems.** A model with an unbounded counter or a channel of unbounded size cannot be verified by Spin's exhaustive search. Bound everything.
- **Hyperproperties.** Properties over pairs of executions (information flow, noninterference) need a different framework.

For everything inside those limits — particularly concurrent coordination at the System and Component level — Spin is one of the strongest tools available.
