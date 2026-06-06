# Promela Basics

Promela ("Process Meta-Language") is the modeling language Spin verifies. It is intentionally small: a few primitive types, processes, channels, and a handful of control structures. Everything else is layered on top of these.

## File structure

A Promela file conventionally has the `.pml` extension. A typical model looks like:

```promela
/* type declarations */
mtype = { req, ack, nack };

/* channel declarations */
chan link = [0] of { mtype };

/* global variables */
bool ready = false;

/* process types */
proctype Sender() {
    /* ... */
}

proctype Receiver() {
    /* ... */
}

/* initial process */
init {
    run Sender();
    run Receiver();
}
```

`active proctype Name()` is shorthand for declaring a process and starting one instance automatically — equivalent to a `proctype Name()` plus `run Name()` in `init`. Use it when you don't need explicit control over startup ordering or parameters.

## Primitive types

- `bit` — 0 or 1 (one bit)
- `bool` — `true` / `false` (one bit)
- `byte` — 0 to 255 (eight bits)
- `short` — −2^15 to 2^15 − 1
- `int` — −2^31 to 2^31 − 1
- `mtype` — a single enumeration of named symbolic constants, declared once with `mtype = { name1, name2, ... }`

Pick the smallest type that fits. Spin's state vector includes every variable; using `int` where `byte` would do bloats memory consumption.

Arrays: `byte buffer[8];` — fixed size, declared at scope.

## Channels

Channels carry typed tuples between processes:

```promela
chan c = [N] of { type1, type2, ... };
```

- `N = 0` — *rendezvous* channel. Send blocks until receiver is ready; receive blocks until sender is ready. Synchronous handshake.
- `N > 0` — *buffered* channel with capacity N. Send blocks only when the buffer is full; receive blocks only when empty.

Operations:

- `c ! v1, v2` — send the tuple `(v1, v2)` on `c`. Blocks if the channel is full (or, for rendezvous, if no receiver is ready).
- `c ? v1, v2` — receive a tuple from `c` into `v1` and `v2`. Blocks if the channel is empty.
- `c ? eval(v1), v2` — receive *only if* the first slot matches `v1`'s current value; otherwise blocks. Useful for pattern matching.
- `len(c)` — current number of messages in the channel.
- `full(c)`, `nfull(c)`, `empty(c)`, `nempty(c)` — predicates on the channel state, safe to use as guards.

## Control flow

Two control structures, both with the same form:

**Selection** (`if`):

```promela
if
:: guard1 -> stmt1
:: guard2 -> stmt2
:: else  -> stmt3
fi
```

Spin evaluates all guards. If exactly one is true, that branch executes. If multiple are true, Spin *non-deterministically* picks one — this is the source of the interleaving Spin explores. If none are true, the `if` blocks until one becomes true (or `else` is taken, if present).

**Repetition** (`do`):

```promela
do
:: guard1 -> stmt1
:: guard2 -> stmt2
od
```

Same semantics as `if`, but loops: after a branch executes, control returns to the top. Exit with `break` (or `goto` to a label, though this is discouraged).

Most process bodies are a single `do ... od` loop, with each arm representing one transition the process can take.

## Guards

A guard is an expression that gates whether a choice arm is executable. A guard of just `true` (or a bare statement) is always executable. The most common guards:

- Boolean expressions: `x == 0`, `ready && !done`
- Channel predicates: `nempty(c)`, `nfull(c)`
- Receive operations: `c ? msg` — fires when a message is available

A guard combined with a `d_step` body is the canonical transition pattern (see `modeling-discipline.md`).

## Atomicity primitives

- `atomic { stmts }` — execute as a single transition, but inner statements may block. If a block occurs, other processes can execute, and the `atomic` resumes when the blocked statement becomes executable.
- `d_step { stmts }` — execute as a single transition, deterministically. Inner statements **may not block**; if any does, Spin reports an error. Cheaper to verify than `atomic`.

Use `d_step` whenever you can; fall back to `atomic` only when you need to block inside the block. See `modeling-discipline.md` for the discipline that makes this work.

## Assertions

```promela
assert(expression)
```

If the expression is false at this point in any execution, Spin reports an assertion violation and writes a counter-example trail. Assertions are the simplest way to express safety properties.

## Labels

Three label categories carry special meaning to Spin:

- `end:` (or any label beginning with `end`) — marks a state as a *valid* terminal state. A process stopped at a state without an `end` label is treated as a deadlock when there are no other enabled transitions.
- `progress:` (or any label beginning with `progress`) — marks a state that "real progress" passes through. Used for liveness checking with `-l`.
- `accept:` (or any label beginning with `accept`) — used in never claims for LTL verification.

A typical use of `end`:

```promela
proctype Worker() {
    do
    :: in ? job -> process(job)
    :: shutdown -> break
    od;
end_worker:
    skip
}
```

Without the `end_worker:` label, Spin would flag a process sitting after `break` as a deadlock.

## Variables: global vs. process-local

Variables declared at file scope are global; processes share them. Variables declared inside a `proctype` are local to the process instance. Promela has no nested scopes — a variable declared inside an `if` or `do` is visible for the rest of the process. (PlantUML readers used to lexical scoping should treat this as a Promela quirk to remember.)

## Inline functions (no real procedures)

Promela has `inline` for textual macro expansion:

```promela
inline send_request(target, payload) {
    target ! req, payload
}
```

These are *not* procedures: parameters are substituted textually, there's no return value, and there's no scope. Useful for de-duplicating boilerplate; don't try to use them as functions.

## Comments

`/* ... */` block comments and `//` line comments (in newer Spin versions). Use them; Promela models without comments are nearly unreadable a week later.

## What Promela deliberately *doesn't* have

- Floating-point. The whole language is integer-only.
- Dynamic memory. Arrays are fixed-size; processes have a static number of variables.
- Recursion. Each `proctype` is a flat control flow.
- Real numbers, strings, or rich data structures.

These omissions are deliberate: a finite, statically-bounded language is what makes exhaustive verification possible. If your model needs floats or dynamic memory, you're trying to verify computation, not coordination — re-abstract before continuing.
