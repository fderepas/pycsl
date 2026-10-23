# FINDING (#49, gen #31) — `#@ critical` / `#@ acquires` / `#@ releases` never validate the mutex NAME

**Not a route: nothing false is certified.** It is the silent-name family's fifth, sixth and
seventh members, and it comes with a CORRECTION to this session's own earlier sweep.

## Measured, on a `with lock_bal:` block that touches nothing shared

```python
#@ shared balance protected_by lock_bal
#@ mutex_invariant lock_bal: balance >= 0
...
def touch() -> int:
    local = 10
    #@ critical no_such_lock          # -> [+] Verification SUCCESS!
    with lock_bal:
        local = local + 1
    return local
```

All three directives behave the same way, and `no_such_lock` is bound NOWHERE in the file —
it is a `NameError` in CPython. Nothing says so.

## THE CORRECTION — `#@ critical` does not refuse an unknown name

This session's silent-name sweep recorded `#@ critical` among the directives that DO refuse
an unknown name, and used it as one of the controls that made the four silent ones look like
a defect rather than a policy. That verdict is wrong, and the reason is instructive: the
file it was measured on wrote to a PROTECTED SHARED VARIABLE inside the block, so the
refusal came from the protection analysis —

    Function 'deposit': unprotected write to shared variable 'balance'
    (protected_by 'lock_bal', but held mutexes are ['no_such_lock']).

— which is a statement about protection, not about the name. Take the shared access out of
the block and the same file verifies. Two of my seven "controls" were this same mechanism
wearing a name check's clothes.

| directive | unknown name, block TOUCHES a protected shared var | unknown name, block touches nothing shared |
|---|---|---|
| `#@ critical` | refused (by the protection analysis) | **SUCCESS** |
| `#@ acquires` | refused (by the protection analysis) | **SUCCESS** |
| `#@ releases` | **SUCCESS** | **SUCCESS** |

`#@ releases` is never caught by anything, in any program: `Module3_Weaver.visit_With` sets
`node.csl_releases` and **no downstream stage reads it**, so the name has no second chance.
The other two reach the IR as a `CriticalSection` and are masked by a different check that
happens to fire on the programs people actually write.

## The rule, and the (u4) counter-program that chose it

A rule keyed on the MUTEX REGISTRY (`#@ shared … protected_by <m>` / `#@ mutex_invariant
<m>`) would forbid a good program: a lock that protects an invariant PyCSL does not model is
legitimately annotated and legitimately absent from the registry. So the rule is the WEAKEST
one that still catches the typo — **the name must be bound somewhere in the file** — under
which an unresolvable name cannot belong to a program that runs. A file containing a star
import is exempt, because then the binding set is not knowable from the file.

## Census, both rules

53 directive sites across 38 files in both corpora, `src/pycsl`, `src/self-annotate/src` and
`src/pycsl_lib`. Sites whose name is bound nowhere in their file: **ZERO**. Sites whose name
is absent from the mutex registry: **ZERO**. So the strict rule would also have been free
TODAY — which is exactly why the census is not the argument; the counter-program is.

## Mirror cost: none

Both `PyCSLWeaver.visit_Module` (which collects the binding set) and `PyCSLWeaver.visit_With`
(which refuses) are `#@ \trusted` in `src/self-annotate/src/frontend/Module3_Weaver.py`,
checked per lesson (n4) — the cost is a property of the FUNCTION, not the file. No marker is
added and nothing is re-proved.

Patch `$SCRATCH/g31/fix_mutex_name.py`; witnesses `1893` (releases, the one nothing else
could catch), `1894` (the control), `1895` (critical with nothing shared touched — the file
that produced the correction above). All three measured SUCCESS on the pre-repair tree and
REFUSED / SUCCESS / REFUSED on a patched offline copy.
