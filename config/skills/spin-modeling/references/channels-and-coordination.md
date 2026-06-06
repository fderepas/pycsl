# Channels and Coordination

At the System and Component levels of the methodology, the *coordination spec* is the most error-prone artifact: it says how multiple sub-actors interact, and it is where deadlocks live. Spin's primary modeling primitive for this is the channel. This page covers how to model coordination cleanly and the natural failure modes that come up.

## Channel capacity is a modeling choice, not a fact about the system

The first decision when modeling an interaction is the channel's capacity. The choice has semantic consequences:

- **Capacity 0 — rendezvous.** Sender and receiver synchronize on every message. The send transition and the receive transition fire *simultaneously*, as a single combined transition in the model. Use rendezvous when the real system has hand-shake semantics: a procedure call, a synchronous RPC, a barrier.

- **Capacity N — buffered.** Sender can put a message in the buffer and continue; receiver picks it up later. Use buffered channels when the real system has asynchronous semantics: a message queue, a network socket, an event bus.

The mistake is to default to whichever you used last. The choice should mirror the system you're modeling. A queue with capacity 1 is *not* a rendezvous channel — it lets the sender complete and walk away, which a rendezvous channel does not.

When unsure, model the most permissive case first (buffered, large capacity) and check whether the property still holds. If yes, you can then tighten the model to ask whether smaller buffers still satisfy the property — a useful question in its own right.

## Channel declarations

```promela
chan rdv     = [0] of { mtype };               /* rendezvous */
chan small   = [1] of { mtype };               /* capacity 1 */
chan medium  = [16] of { mtype, byte };        /* capacity 16, tuples */
chan typed   = [4] of { mtype, byte, byte };   /* capacity 4, three-field tuples */
```

The tuple type is fixed at declaration. Every send and receive on that channel must match the tuple shape.

## Sending and receiving

```promela
chan c = [4] of { mtype, byte };

c ! req, 42;          /* send (req, 42) */
c ? msg, value;       /* receive into msg and value */
c ? eval(req), value; /* receive *only if* first field equals req */
c ? eval(req), 42;    /* receive only if (req, 42) — full pattern match */
```

`eval(x)` in a receive turns that slot into a pattern-match against the current value of `x`. Without `eval`, the receive binds the slot to a variable. This is how you filter messages by type without an `if` cascade after the receive.

## Receive as a guard

The cleanest coordination pattern is to put the receive directly in the guard of a `do` arm:

```promela
do
:: in ? req, value ->
   d_step {
     /* msg is bound; process the request */
     reply_to_sender(value);
   }
:: in ? eval(shutdown) ->
   d_step {
     /* received the shutdown signal */
     break;
   }
od
```

This says: "when a request arrives, do this; when a shutdown arrives, exit." Spin will explore both possibilities. The receive itself is the guard, and the `d_step` body cannot block (the message is already in hand).

## The classic deadlock: missing acknowledgement

The simplest deadlock to model and the easiest to find by inspection — and Spin will find it in milliseconds:

```promela
mtype = { req, ack };
chan a_to_b = [0] of { mtype };
chan b_to_a = [0] of { mtype };

active proctype A() {
    a_to_b ! req;       /* send request */
    b_to_a ? ack;       /* wait for ack — but B is busy waiting for a different message */
}

active proctype B() {
    a_to_b ! req;       /* WRONG: B is sending a request, not receiving one */
    b_to_a ? ack;
}
```

Both processes send before they receive, on rendezvous channels. Neither send can complete because there's no waiting receiver. Spin reports an invalid end state at depth 0 or 1 — neither process can take any transition.

The fix depends on the intended semantics: usually one of the two participants should be a server that *receives* the request and *sends* the ack:

```promela
active proctype B() {
    do
    :: a_to_b ? req ->
       d_step { b_to_a ! ack }   /* but: rendezvous send in d_step — see below */
    od
}
```

But — and this is the second classic mistake — `d_step { b_to_a ! ack }` may itself block on the rendezvous. The proper fix is either to make `b_to_a` a buffered channel, or to take the send out of the `d_step`:

```promela
active proctype B() {
    do
    :: a_to_b ? req ->
       b_to_a ! ack          /* outside d_step; can block */
    od
}
```

## The second classic deadlock: circular wait

```promela
chan r1 = [0] of { mtype };   /* resource 1 lock */
chan r2 = [0] of { mtype };   /* resource 2 lock */

active proctype A() {
    r1 ! lock;
    r2 ! lock;
    /* use both */
    r2 ? unlock;
    r1 ? unlock;
}

active proctype B() {
    r2 ! lock;       /* B acquires in reverse order */
    r1 ! lock;
    r1 ? unlock;
    r2 ? unlock;
}
```

Classic Dijkstra-style deadlock: A holds r1 and wants r2; B holds r2 and wants r1. Spin finds this at a small depth, and the trail shows the exact interleaving — the most useful artifact, because it tells you which actors raced.

## Lost messages and faulty media

Reality is harsher than rendezvous. To model a lossy network, add an arm that *drops* messages:

```promela
proctype Network(chan in; chan out) {
    do
    :: in ? msg ->                 /* received from sender */
       if
       :: out ! msg                /* deliver normally */
       :: skip                     /* drop on the floor */
       fi
    od
}
```

The `if` with two arms is non-deterministic: Spin will explore both, so the property has to hold even when messages are dropped. This is how Spin verifies, e.g., the alternating bit protocol against a lossy medium.

## Polling vs. blocking receive

Sometimes you want to *test* whether a message is available without committing to receive it. Use `c ? <pattern>` is a blocking receive that fires only when matched; `c ?? <pattern>` does a random non-blocking poll. For most coordination modeling, the blocking variant in a guard is cleaner.

```promela
do
:: in ? msg ->                /* block until a message arrives */
   d_step { handle(msg); }
:: timeout ->                  /* fire if no transition is enabled anywhere */
   d_step { handle_timeout(); }
od
```

`timeout` is a Spin keyword: it becomes true *only* when no other process in the model has an enabled transition. This is Spin's way of modeling "nothing else is happening". Use it sparingly — it's not the same as a real-world timeout, which fires after a duration.

## Channels carrying complex coordination

For richer coordination — request/reply with IDs, multi-step protocols — encode the state in the message tuple:

```promela
mtype = { request, response, error };
chan link = [4] of { mtype, byte, byte };  /* (kind, id, payload) */

link ! request, 7, 42;       /* request with id 7, payload 42 */
link ? response, 7, value;   /* receive response specifically for id 7 */
```

The `eval` pattern lets you filter by id; without it, you'd model a race where one process can pick up another's response.

## Tips and pitfalls

- **Default to small buffers.** A channel of capacity 4 finds bugs that a channel of capacity 1000 misses, because realistic buffer pressure exposes more interleavings. Verify with capacity 1, 2, 4 incrementally if the buffer size matters.
- **Reach for rendezvous when modeling RPCs.** A synchronous call is most naturally a rendezvous; force-fitting it into a buffered channel hides the dependency between caller and callee.
- **Don't model retries unless they're part of the spec.** Adding retry logic to a Spin model doubles its size and rarely changes the answer. Either the underlying protocol is correct without retries (in which case the retry layer doesn't affect verification) or it isn't (in which case the spec should be fixed, not the model).
- **Watch for asymmetric channels.** If process A reads from `a_to_b` and process B writes to it, the names should make this obvious. `chan a_to_b` written-by-A-read-by-B is a strong convention; reversing it is a common source of confusion.
- **A `d_step` cannot contain a rendezvous send/receive.** This is the most common `d_step` violation. If you need synchronous handshake semantics, the rendezvous goes *outside* the `d_step`, or you switch to a capacity-1 buffered channel as the model and accept the slight semantic relaxation.
