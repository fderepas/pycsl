# Spin and the Five-Level Methodology

The five-level methodology (Business / System / Component / Module / Unit) places a **Verifier** role at every level whose job is to design and run the test plan that proves the Specifier's spec is met. At the System and Component levels, where the work is delegated across multiple sub-actors, the test plan needs to prove that the *coordination spec* is sound — and "sound" usually starts with "doesn't deadlock". This is Spin's home territory.

This page covers when to write a Spin model as part of the Verifier's work, what bugs Spin catches that other tests don't, and how a Spin counter-example routes through the Reconciliator role.

## Where Spin fits in the methodology

| Level     | Spin's role                                                  |
|-----------|--------------------------------------------------------------|
| Business  | Rarely used directly. Business-level coordination is usually too abstract to model concretely. |
| System    | Verifier's primary tool for proving the coordination of Systems is deadlock-free. |
| Component | Verifier's primary tool when a Component is built from coordinating Modules. |
| Module    | Used only if the Module itself has internal concurrency.     |
| Unit      | Not applicable. Units are sequential; verification at this level uses ACSL, Pearlite, or unit tests. |

The pattern is consistent: **Spin is the right tool wherever the Specifier has written a coordination spec that says how sub-actors interact**. That coordination spec is itself a concurrent program, and concurrent programs need exhaustive verification, not example-based testing.

## When the Verifier should write a Spin model

The trigger is in the Specifier's coordination spec. If the spec says:

- "Sub-actor A sends a message to sub-actor B and waits for a response" — model it. Race conditions and missing acks live here.
- "Sub-actor X and sub-actor Y both update shared state Z" — model it. Mutual exclusion bugs live here.
- "Sub-actor P, Q, R run concurrently and synchronize at the end" — model it. Barrier coordination bugs live here.
- "A request is broadcast to all sub-actors and the system waits for all responses" — model it. Lost-message and slow-actor coordination bugs live here.

If the spec involves *no* coordination — each sub-actor operates independently, with no shared state and no messages — Spin doesn't add value. Use the level's regular test plan.

## What Spin catches that other tests don't

Conventional testing — even with concurrency injected — explores a tiny fraction of possible interleavings. A bug that requires a specific ordering of three messages from three different processes will reliably evade a hundred test runs and reliably appear in production. Spin's *exhaustive* search finds these every time.

Concretely, Spin will find:

- **Deadlocks** in any interleaving, no matter how rare.
- **Race conditions** on shared variables.
- **Lost-acknowledgement** patterns where a message goes nowhere because no process is waiting for it.
- **Livelock**: cycles of activity that never make progress (with progress labels).
- **Violation of safety invariants** that hold in test runs but break in some particular interleaving.

Things Spin doesn't catch (and which the rest of the test plan must cover):

- Logic bugs *within* a sub-actor (the abstracted-away parts of the model).
- Performance issues — Spin doesn't model time.
- Resource leaks or memory issues.
- Bugs that only manifest at scales larger than the model.

This is why Spin is *part* of the Verifier's plan, not the whole plan.

## How a Spin counter-example maps to Reconciliation

When Spin reports a deadlock, the Reconciliator's job is to route the fault to one of three parties: Specifier, Verifier, or a specific sub-actor. The trail file usually makes the routing obvious; here's the decoding table:

| What the trail shows                                                                  | Likely fault   |
|---------------------------------------------------------------------------------------|----------------|
| Two sub-actors both waiting on the other to send first                                | Specifier — the coordination spec doesn't say who starts |
| A sub-actor sends a message that no other sub-actor is configured to receive          | Specifier — the message routing in the coordination spec is wrong |
| A sub-actor's behavior in the model contradicts its individual spec                   | Verifier — the model misrepresents the sub-actor; fix the model |
| The model is faithful to the spec, and the spec deadlocks                             | Specifier — the spec is the bug |
| The model passes Spin but the deployed system still deadlocks                         | Sub-actor — one sub-actor isn't implementing its individual spec correctly |

The key skill is reading the trail and identifying which row applies. The trail file (`spin -t -p -g -l`) is the diagnostic input; routing is the judgment.

When in doubt: **does the model accurately reflect the spec?** If not, fix the model and re-verify. If yes, the spec is the fault and Reconciliation routes upward to the Specifier.

## A complete worked example

Two Components, A and B, with a shared resource. A's spec says it acquires the resource, then notifies B. B's spec says it waits for the notification, then uses the resource.

### The Specifier's coordination spec (informal)

- A acquires `resource`
- A sends `notify` to B
- A releases `resource`
- B receives `notify`
- B acquires `resource`
- B uses it and releases it

### The Verifier writes a Spin model

```promela
mtype = { notify };
chan a_to_b = [1] of { mtype };
bit resource_held = 0;
bit a_done = 0;
bit b_done = 0;

active proctype A() {
    /* acquire */
    !resource_held ->
    d_step { resource_held = 1; }

    /* notify */
    nfull(a_to_b) ->
    d_step { a_to_b ! notify; }

    /* release */
    d_step { resource_held = 0; a_done = 1; }

end_A:
    skip
}

active proctype B() {
    /* wait for notify */
    a_to_b ? notify ->
    d_step { skip; }

    /* acquire */
    !resource_held ->
    d_step { resource_held = 1; }

    /* use and release */
    d_step { resource_held = 0; b_done = 1; }

end_B:
    skip
}
```

Each transition is a guarded `d_step`. Each guard is the precondition that lets the `d_step` body run without blocking. The model maps directly to the spec, line by line.

### Run Spin

```bash
spin -a model.pml
gcc -O2 -o pan pan.c
./pan
```

In this case Spin reports `errors: 0` — the model verifies. The coordination spec is sound.

### Now introduce a subtle bug to see what catches it

Change A's spec to: "send `notify` *while still holding* the resource". This models a real-world mistake where the release is forgotten or moved.

```promela
active proctype A() {
    !resource_held ->
    d_step { resource_held = 1; }

    nfull(a_to_b) ->
    d_step { a_to_b ! notify; }     /* note: no release before notify */

end_A:
    skip                              /* never releases */
}
```

Now Spin reports `invalid end state at depth 3`. The trail shows B is stuck at `!resource_held ->` because A never released. The Reconciliator's job: read the trail, look at the row in the table above, and route. This deadlock pattern — "sub-actor never releases" — comes from the spec, so the routing is to the Specifier of A's component.

## Practical workflow

A practical step-by-step:

1. **Specifier writes the spec.** Includes the coordination between sub-actors.
2. **Specifier and Verifier synchronize.** The Verifier reads the spec and asks: "what could go wrong here?"
3. **Verifier writes a Promela model** of the coordination. One `proctype` per sub-actor, one guarded `d_step` per transition. The model is the executable form of the spec.
4. **Verifier runs Spin.** `spin -a`, compile, `./pan`.
5. **If Spin reports errors**, the Verifier replays the trail (`spin -t -p`), classifies the fault using the table above, and hands the diagnosis to the Reconciliator.
6. **The Reconciliator routes**: Specifier (spec is wrong), Verifier (model is wrong), or sub-actor (implementation will diverge from spec — caught at sub-actor verification).
7. **The cycle repeats** until Spin verifies the model cleanly. At that point, the *spec* has been proven free of deadlock; whether the *implementation* matches the spec is the sub-actor's level to verify.

This is the rigor that the five-level methodology asks for: every level's coordination has its own proof artifact, and Spin is that artifact at the levels where it applies.

## Anti-patterns

Three failure modes show up repeatedly when integrating Spin into a methodology:

- **Modeling the computation instead of the coordination.** If the Spin model mirrors the production code line-by-line, it will be too large to verify. The model should reflect *only* the interactions between sub-actors. Each sub-actor's internal behavior is an abstraction — usually a single transition that updates a state variable.

- **Skipping the `d_step` discipline because "it's just a quick model".** The state space explodes invisibly. By the time the Verifier notices, the model has grown too large to re-write. Start with `d_step` from the first transition.

- **Treating a Spin pass as full verification.** Spin verifies the *model*, not the system. Even after a clean Spin run, the sub-actors must still be verified against their individual specs. Spin's contribution is: the spec is free of coordination bugs. The rest is the sub-actors' job.
