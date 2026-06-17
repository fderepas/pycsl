# Feature: a public-API surface lister (`pycsl --list-api`)

**What's painful now.** `test-supervise-sl`'s *scoper* and `formal-test-sl`'s
*probe* both need the ground-truth list of a module's public API (e.g. every `os.*`
syscall) to (a) decompose a mission into a work-list and (b) confirm an API symbol
exists before authoring a property. Today that means hand-reading
`pure_lib/<m>/__init__.py` and matching `def`/`val` declarations — error-prone, and
exactly the place a *coverage over-claim* or *missed syscall* slips in.

**Proposed feature.** A mode that emits the public surface mechanically, e.g.:

```
pycsl --list-api pure_lib/os/__init__.py
# -> name, signature, and the exposed contract (requires/ensures) per public symbol,
#    as JSON or a table.
```

**Why it helps the loop.** It turns the scope decomposition into an **executable
lower bound** (`L`): the in-scope work-list becomes "the listed symbols minus the
guidance's exclusions", counted rather than asserted — closing the coverage-over-claim
and missed-target coherent-and-wrong shapes at their source. It also gives the
`formal-test-sl` probe a cheap "does this API symbol exist / what does it promise?"
check before property authoring.

**Rough effort / risk.** Low–medium. The information already exists in the
module's emitted contracts; this is a read-only projection of the parser/IR output.
No proof-path change, so low risk to the gates.
