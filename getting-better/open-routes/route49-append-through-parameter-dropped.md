# OPEN ROUTE #49 — `a.append(x)` ON A LIST **PARAMETER** IS INVISIBLE TO THE CALLER

**Found 2026-09-08 by relaunch #48, at commit `c85526c4`, by the same method that found
route #48: read the emitter's own soundness claims and probe each.** The claim here is
`functions.py`'s "params with a real `writes {p}` frame (the sound in-place-append model)" —
sound where it fires, and it fires only for STATEMENT-IR appends.

## The demonstration (default `hoare` model, no flags, Python run to confirm)

```python
#@ requires True
#@ ensures True
#@ assigns a
def g(a: list) -> None:
    a.append(1)

#@ requires \length(a) == 0
#@ ensures \result == 0        # Python: f([]) returns 1
#@ assigns a
def f(a: list) -> int:
    g(a)
    return len(a)
```
`[+] Verification SUCCESS! All contracts formally proven.`

## The mechanism, read off the emission

```whyml
  let g (a: array int) : unit
    requires { true }
    ensures  { true }
  =
    let a = ref (snapshot a) in        (* <-- a LOCAL COPY *)
    a := Seq.snoc !a 1                 (* <-- appended to the COPY *)

  let f (a: array int) : int
    requires { ((Array.length a) = 0) }
    ensures  { (result = 0) }
  =
    let _ = (g a) in ();
    (Array.length a)
```

`g` has **no `writes` clause at all**, so Why3 knows `a` is unchanged across the call and
`f` proves `Array.length a = 0` afterwards. The mutation is not merely un-modelled, it is
modelled as ABSENT.

## Scope, measured — it is exactly ONE method, and that is the argument for a refusal

| shape | verdict |
|---|---|
| `a.append(x)` on a list param, plain function | **PROVES a false contract** |
| `a.append(x)` on a list param, through a METHOD (`c.push(a)`) | **PROVES** |
| `a.append(x)` with the callee declaring `assigns \nothing` | **PROVES** — the frame lie is not caught either |
| `a.pop()` / `a.insert(...)` / `a.clear()` / `a.extend(...)` | PIPELINE ERROR — already refused |
| `a[0] = 99` on a list param | fails closed — element writes ARE caller-visible |
| `d[1] = 5` on a dict param | fails closed — dict writes ARE caller-visible |
| `a = []; a.append(1); a.append(2); len(a)` (SAME function) | fails closed — modelled correctly |

So `append` is the **odd one out** of its own family: four sibling mutators are refused, the
two non-method mutation forms are faithful, the same-function case is faithful, and only the
cross-call `append` is silently dropped.

Reproducers: `scratchpad/w48/probe/w1_append_param.py`, `y1_append_nothing.py`,
`y2_append_method.py`, and the control `x7_elem_write.py`.

## THE PLANE THAT SHOULD HAVE CAUGHT IT DID NOT, AND ITS LIMIT IS HONEST

`bin/check-dropped-mutation.py` reports **0 dropped** at the same commit where this route
proves, and that is not a bug in the plane: its stated population is Module 5's
ASSIGNMENT-FAMILY statements — "a shape no branch matches produces no IR at all". Route #49
is a MODULE 6 lowering of a `.append` CALL. The statement IS in the IR; it is the LOWERING
that writes a local copy. So the two are disjoint by construction, and the campaign has no
instrument for the second half.

**REOPENING CAPABILITY FOR THE INSTRUMENT** (worth more than the route): a plane that
enumerates, for each list/dict/set MUTATOR method (`append`, `pop`, `insert`, `clear`,
`extend`, `remove`, `add`, `discard`, `update`, `setdefault`, …), how Module 6 lowers it
when the RECEIVER is a formal PARAMETER, and classifies each as CALLER-VISIBLE / REFUSED /
DROPPED. Route #49 is exactly one cell of that table — `append` DROPPED while its four
siblings were REFUSED — and the table is what makes the asymmetry visible without probing
each one by hand.

## REOPENING CAPABILITY

**REFUSE it**, exactly as `pop`/`insert`/`clear`/`extend` are already refused — a designed
refusal that makes the family consistent, rather than a fifth special case. The alternative,
extending the `writes {p}` in-place-append model from statement-IR appends to any list param,
is the larger build: it must give the callee a real `writes {a}` frame AND write through to
the caller's `array`, which the snapshot lowering deliberately does not do.

MEASURE FIRST: the refusal must not break the mirror's own appends. The statement-IR appends
already have the `writes {p}` model and would be exempt by construction, but
`_stmt_seq_append_params`'s seed is narrow (a literal `{"stmt": K}` node, or a local built up
to one) and any OTHER list-param append in the mirror would be refused. The emission diff is
the instrument.

NOT CLOSED IN THIS INCREMENT: routes #47 and #48 were already staged with their mirror
re-proofs unrun, and this is the third change to the same emitter in one window.
