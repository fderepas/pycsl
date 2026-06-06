# Bug Report: MutuallyExclusiveCallbackGroup Scheduling Weaknesses

**Component:** `rclpy` — `callback_groups.py`, `executors.py`
**Severity:** Medium (fairness/throughput degradation; optimization-mode integrity gap)
**Threat category:** ros-report.md Threat #2 — Executor starvation / GIL deadlock
**Audited version:** rclpy rolling, tag `11.0.1`, commit `69d5ea9`

---

## Summary

Code review of `MutuallyExclusiveCallbackGroup` confirms that the **actual
mutual-exclusion gate is `beginning_execution()`**, not the earlier
`can_execute()` check. That distinction matters for interpreting the findings:
the group does preserve its core mutex invariant, but the current scheduling
shape still exposes fairness, throughput, and diagnosability weaknesses.

This report documents **three findings**:

1. a TOCTOU scheduling window between `can_execute()` and
   `beginning_execution()` that wastes executor dispatches and can amplify
   starvation under load,
2. an `assert`-only integrity check in `ending_execution()` that disappears
   under `python -O`, and
3. the absence of built-in deadlock detection for synchronous self-calls in a
   mutually exclusive group — a documented limitation that is better addressed
   with lint/static analysis than an upstream bug filing.

---

## Finding 1 — TOCTOU race between `can_execute()` and `beginning_execution()`

### Severity: Medium

### Location

`callback_groups.py` lines 112–123 and `executors.py` lines 665–667, 907–949:

```python
# callback_groups.py

def can_execute(self, entity: 'Entity') -> bool:
    with self._lock:
        assert weakref.ref(entity) in self.entities
        return self._active_entity is None

def beginning_execution(self, entity: 'Entity') -> bool:
    with self._lock:
        assert weakref.ref(entity) in self.entities
        if self._active_entity is None:
            self._active_entity = entity
            return True
    return False
```

```python
# executors.py
if sub.callback_group.can_execute(sub):
    handler = self._make_handler(sub, node, self._take_subscription)
    yield handler, sub, node

...

if is_shutdown or entity.callback_group is not None and \
        not entity.callback_group.beginning_execution(entity):
    entity._executor_event = False
    gc.trigger()
    return
```

### Root cause

The executor first asks whether an entity **can** run, yields a handler, and
only later attempts to **claim** the callback group inside the handler via
`beginning_execution()`. Those are separate lock acquisitions with a scheduling
window between them.

In a `MultiThreadedExecutor`, two worker threads can both observe
`_active_entity is None` during `can_execute()`. Both handlers may be queued,
but only one thread will later win `beginning_execution()`. The loser exits
without doing useful work.

This is a textbook time-of-check/time-of-use race at the scheduler level.
Importantly, it is **not** a race that violates mutual exclusion: the second
phase still serializes access correctly.

### Impact

**Severity clarification:** This is a **fairness and throughput** issue,
not a safety violation. The mutex invariant is preserved because
`beginning_execution` is the actual gate. The TOCTOU window causes wasted
thread-pool dispatches and potential starvation, but cannot cause two
callbacks to execute simultaneously in the same MutuallyExclusiveCallbackGroup.

- Worker threads can be consumed by handlers that immediately fail the late
  `beginning_execution()` check
- Under heavy contention, callbacks in the same group may experience added
  latency and unfairness
- Systems with small thread pools are most exposed because rejected handlers
  still incur wakeup, scheduling, and bookkeeping cost
- The effect compounds with high-rate timers or subscriptions competing in the
  same callback group

### Recommendation

Tighten the scheduler contract so that reservation and dispatch happen in one
step. Options include:

- replace the two-phase `can_execute()` / `beginning_execution()` flow with a
  single atomic claim operation,
- reserve the group before yielding the handler, or
- keep the current behavior but document it explicitly as a fairness trade-off
  and add executor metrics for rejected late claims.

---

## Finding 2 — `ending_execution()` relies on `assert`, which disappears under `-O`

### Severity: Medium (defense-in-depth / diagnosability)

### Location

`callback_groups.py` lines 125–128:

```python
def ending_execution(self, entity: 'Entity') -> None:
    with self._lock:
        assert self._active_entity == entity
        self._active_entity = None
```

### Root cause

The only check that the entity finishing execution is the entity that actually
holds the callback-group slot is an `assert`. In optimized Python
(`python -O`), asserts are stripped entirely, so release builds reduce this
function to an unconditional clear of `_active_entity`.

### Impact

- Debug builds catch internal misuse or future refactors that call
  `ending_execution()` with the wrong entity
- Optimized builds silently skip that validation, weakening the invariant check
  exactly in production deployments where diagnostics matter most
- The current executor path appears to call `ending_execution()` only after a
  successful `beginning_execution()`, so this is primarily a robustness and
  future-maintenance concern rather than an immediately exploitable bug

### Recommendation

Replace the `assert` with an always-on runtime check:

```python
def ending_execution(self, entity: 'Entity') -> None:
    with self._lock:
        if self._active_entity != entity:
            raise RuntimeError('ending_execution called for non-active entity')
        self._active_entity = None
```

This preserves the diagnostic in both debug and optimized builds.

---

## Finding 3 — No deadlock detection for synchronous self-calls in a mutually exclusive group

### Severity: Informational (documented limitation; lint opportunity)

### Description

**Note:** This behavior is a known, documented design property of
`MutuallyExclusiveCallbackGroup`. The [ROS 2 documentation](https://docs.ros.org/en/rolling/How-To-Guides/Using-callback-groups.html)
explicitly warns against synchronous service calls inside mutually
exclusive groups. The actionable contribution here is the recommendation
for a **static analysis rule** (e.g., in `ament_lint`) that would flag
this pattern automatically, rather than filing this as an rclpy bug.

A callback running in a `MutuallyExclusiveCallbackGroup` can synchronously wait
for work whose completion callback is assigned to the same group. Because the
current callback holds the group slot, the response callback can never begin
execution, and the waiting callback never completes.

The executor therefore hangs without an exception even though the underlying
mutex logic is behaving as designed.

### Location

Relevant execution gate:

```python
if is_shutdown or entity.callback_group is not None and \
        not entity.callback_group.beginning_execution(entity):
    entity._executor_event = False
    gc.trigger()
    return
```

See also the ROS 2 callback-group guidance under “Avoiding deadlocks”.

### Impact

- A node can deadlock permanently when a callback performs a synchronous
  service or action wait whose completion depends on the same mutually
  exclusive group
- The failure mode is a silent hang / starvation condition rather than an
  explicit exception
- Because this is configuration-dependent and documented upstream, the highest
  value mitigation is early detection in tooling

### Recommendation

Do **not** file this upstream as an `rclpy` correctness bug. Instead:

1. add a static analysis rule in `ament_lint` (or equivalent ROS linting)
   flagging synchronous service/action calls from callbacks in a
   `MutuallyExclusiveCallbackGroup`,
2. add examples in project templates showing safe alternatives (separate
   callback groups, reentrant groups, or async calls), and
3. consider optional runtime warnings in debug tooling when a synchronous call
   is made from a callback context known to be mutually exclusive.

---

## Affected versions

The audited control flow is present in `rclpy` rolling tag `11.0.1`
(commit `69d5ea9`). The patterns are architectural enough that nearby releases
should be reviewed as well.

**Files:**
- `rclpy/rclpy/rclpy/callback_groups.py` — Findings 1 and 2
- `rclpy/rclpy/rclpy/executors.py` — Findings 1 and 3
