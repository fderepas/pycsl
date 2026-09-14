# ROUTE #109 — the `_objstate_w` fail-closed frame fallback was written into the `self.`
# arm only, so a RECORD-VARIABLE receiver mints an avatar with NO FRAME AND NO RECEIVER

**Status: FOUND, REPRODUCED, BOTH DIRECTIONS MEASURED. Repair NOT yet landed.**
**Severity: SEV-1. `order = 2` — the carrier IS a campaign artefact: the `#32 SPIKE`
`_objstate_w` repair itself.**

This is exactly route #105's shape applied to a different obligation: #105 was a repair keyed
on the receiver spelling in the **raises** clause; #109 is a repair keyed on the receiver
spelling in the **frame**. It is the fourth link in the chain #70 → #100 → #105 → #109, and it
is the chain's own prediction coming true: **this shape recurs once per obligation kind.**

## THE TWO ARMS, quoted

`src/pycsl/module6_whyml/expressions.py:6640-6660` — the `self.` arm, which GOT the repair:

```
6640            _w = self._writes_filtered_to_labels(cls, _declared_w)
...
6650            _objstate_w = bool(_declared_w) and not _w
6651            field_ens = _fe + _foe + _fpe + _fppe
6652            if (field_ens or _w or _fpfe or _rfe or _objstate_w) and cls:
...
6660                field_spec = ("self", cls, field_ens, _w, _fpfe, _rfe, _objstate_w)
```

a **7-tuple**, and `_objstate_w` appears BOTH in the gate and in the payload.

`expressions.py:6696-6705` — the `<recordvar>.m()` / module-global arm, which did not:

```
6696                    writes = self._writes_filtered_to_labels(
6697                        cls, mwrites.get(lookup_key, []))
...
6700                    if field_ens or writes or frame_ens or result_frame_ens:
...
6704                        field_spec = (parts[0], cls, field_ens, writes, frame_ens,
6705                                      result_frame_ens)
```

a **6-tuple**. The same filter is applied, `_objstate_w` is never computed, and it is absent
from the gate. So when `_writes_filtered_to_labels` empties the set — a field the record does
not carry as an emitted label — the gate is FALSE, `field_spec` is `None`, and the call
lowers to a bare abstract op.

The repair's OWN docstring states the hazard it was written to prevent
(`expressions.py:6643-6649`):

> When the callee DECLARES an `#@ assigns self.<f>` whose target the record does NOT carry as
> an emitted field label, `_writes_filtered_to_labels` empties the set and the avatar is
> minted with NO frame at all -- so the callee's declared effect is UNOBSERVABLE and every
> caller may claim `writes { }`.

That is a precise description of what the OTHER arm still does.

## BOTH DIRECTIONS MEASURED at HEAD `c803d6ff`

Identical callee in both files:

```python
class C:
    def __init__(self) -> None:
        self.a = 0

    #@ assigns self.hidden        # `hidden` is first bound OUTSIDE __init__,
    def bump(self) -> None:       # so it is not an emitted record field label
        self.hidden = 5
```

**Direction 2 — the CONTROL, `self.` receiver, correctly FAILS *for the right goal*.**
A sibling method `go` declares `#@ assigns \nothing` and calls `self.bump()`:

```
rc=1 — this expression depends on variable _pyobj_state, which is left out in
       the specification
```

The named goal is the frame, not something incidental — so the obligation is LIVE on this
shape and a proof in the other arm cannot be dismissed as vacuous. Emitted:

```
val self_bump_0 (self: c) : unit
  writes { _pyobj_state }
```

**Direction 1 — the EXPLOIT, record-variable receiver, PROVES.**

```python
#@ assigns \nothing
#@ ensures \result == 0
def caller() -> int:
    c = C()
    c.bump()
    return c.a
```

`[+] Verification SUCCESS! All contracts formally proven.` (rc=0.)
CPython: `c.bump()` sets `c.hidden = 5`, so `caller` does **not** assign nothing.

The emitted avatar, read from the file rather than inferred, is the whole story:

```
val c_bump_0 () : unit
```

**No `writes` clause, and no receiver parameter either** — the receiver is dropped along with
the frame. Meanwhile the method's own definition in the same file is framed honestly:

```
let c__bump (self: c) : unit
  writes { _pyobj_state }
```

so the file simultaneously contains an honest definition and an unframed avatar of it, and
the call site uses the avatar.

## REPAIR SKETCH (to be RE-DERIVED before landing, per the #95 rule)

Compute `_objstate_w` in the record-var/global arm from the same two inputs
(`bool(declared) and not writes`), add it to the gate, and widen the payload to the 7-tuple
the consumer already understands. **Check the consumer first**: it must not be keyed on
`len(field_spec)`, or a 7-tuple from this arm will take a path written for the `self.` arm.
And per the campaign's own lesson, the RIGHT repair is not "add the seventh slot here" but
"stop keying this decision on the receiver spelling at all" — the correct key
(`lookup_key`) is already computed a few lines above in both arms.

## THE GENERATOR

>>> **A COMPLETENESS FILTER APPLIED IN TWO PLACES NEEDS ITS FAIL-CLOSED FALLBACK IN BOTH.
>>> COPYING THE FILTER WITHOUT THE FALLBACK CONVERTS A LOUD UNBOUND-SYMBOL ERROR INTO A
>>> SILENT FALSE PROOF.**
