# Route #209 — the `protects` trust boundary asked a Python-AST matcher about a CSL node

**Status:** CLOSED (gen #30). SEV-1. An inert check that had looked satisfied for its
whole life.

## The witness

`1716_route209_protects_trust_boundary_never_fired.py` (expected FAIL):

```python
#@ happy own:
#@     protects g.v
#@     except setter

#@ requires n >= 0
#@ assigns g.v
#@ \trusted
def sneaky_stub(n: int) -> None:
    g.v = n
```

PROVED. `sneaky_stub` is NOT in the `except` set and writes the protected field; CPython
agrees with the violation (`sneaky_stub(5)` sets `g.v` to 5).

## The mechanism

The `protects` form injects `#@ check False` at every direct write to a protected path
outside the exempt set — corpus `0612` is that negative and has always failed correctly. A
`\trusted` body has NO SITE to inject into, so R1.1 adds a trust boundary: a non-exempt
trusted function whose `#@ assigns` names a protected path must carry `#@ \preserves`.

That boundary computed the written paths with `_target_dotted_path`, whose branches are

```python
if isinstance(target, ast.Subscript): ...
if isinstance(target, ast.Attribute): ...
if isinstance(target, ast.Name): ...
```

— a `pure_ast` matcher. An `#@ assigns` target is a **CSL** object:

```
assigns g.v          ->  FieldAccess(object='g', field='v')
assigns self.disk[i] ->  FieldSubscript(field='disk', index=Var(name='i'))
```

Neither is a `pure_ast` node, so the matcher returned `None` for every target, the computed
set was `{None}`, and the intersection with the protected paths was **always empty**.

## Why nothing noticed

The REGION form's identical boundary (`0461` positive, `0462` teeth) DOES fire, because it
reads the declared REGION rather than the assigns targets. An untested inert check sat
beside a tested live one and looked exactly the same from outside. No witness exercised
THIS form's trust boundary.

>>> A CHECK WITH NO WITNESS IS A CHECK WITH NO EVIDENCE THAT IT CAN FIRE, and "the sibling
>>> form has a witness" is not evidence about this one.

## The repair

Derive the dotted path from the CSL node as well — a bounded peel of
`FieldAccess`/`FieldSubscript`/`Var` (guard 8, no nested def), at the same choke point in
`Module3_Weaver::_expand_happy_properties` whose mirror twin is `\trusted`.

## Controls

`1717_route209_protects_trusted_writer_with_preserves_control.py` (expected PASS) is the
same trusted writer WITH `#@ \preserves` — the rule is "it must say so", not "it may not
write", exactly as `0461` is accepted for the region form. `0611` proves, `0612`/`0613`
stay refused, `0461` proves, `0462` stays refused.
