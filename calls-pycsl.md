# Library Method Calls — PyCSL Contracts

Per-symbol PyCSL contract for every stdlib API entry used inside
`src/pycsl/`. The contract is the source of truth for proof
generation; the English in `calls-english.md` is the source of
truth for *what the contract is supposed to mean*.

Each entry follows the workplan §3.2 template:

    ## `<qualified.name>`
    ```python
    #@ requires <expr>
    #@ ensures <expr>
    #@ assigns <targets> | \nothing
    #@ raises { <ExcA>, <ExcB> } | raises { }
    #@ \trusted
    def <name>(...) -> <ret>: ...
    ```
    Cross-check: read the contract above and rewrite it in
    English; compare to calls-english.md.

**Status:** scaffolded with `TODO` contracts. The `raises { }`
clause is mandatory per workplan §8.3 — empty braces when total.
Hand curation pending; see workplan §13 step 5.

---

## Module — `argparse`

## `argparse`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def argparse(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#argparse`.

## `argparse.ArgumentParser`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def ArgumentParser(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#argparseargumentparser`.

## `argparse.Namespace`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
class Namespace: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#argparsenamespace`.

## `argparse.Namespace.provers.split`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def split(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#argparsenamespaceproverssplit`.

---

## Module — `ast`

## `ast`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def ast(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ast`.

## `ast.AST`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
class AST: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astast`.

## `ast.AST.csl_shared_decls.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astastcsl_shared_declsappend`.

## `ast.Add`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Add(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astadd`.

## `ast.And`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def And(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astand`.

## `ast.AnnAssign`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def AnnAssign(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astannassign`.

## `ast.Assert`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Assert(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astassert`.

## `ast.Assign`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Assign(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astassign`.

## `ast.AsyncFunctionDef`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def AsyncFunctionDef(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astasyncfunctiondef`.

## `ast.Attribute`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Attribute(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astattribute`.

## `ast.AugAssign`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def AugAssign(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astaugassign`.

## `ast.BinOp`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def BinOp(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astbinop`.

## `ast.BitAnd`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def BitAnd(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astbitand`.

## `ast.BitOr`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def BitOr(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astbitor`.

## `ast.BitXor`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def BitXor(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astbitxor`.

## `ast.BoolOp`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def BoolOp(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astboolop`.

## `ast.Break`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Break(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astbreak`.

## `ast.Call`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Call(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astcall`.

## `ast.ClassDef`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
class ClassDef: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astclassdef`.

## `ast.ClassDef.csl_class_invariants.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astclassdefcsl_class_invariantsappend`.

## `ast.Compare`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Compare(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astcompare`.

## `ast.Constant`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Constant(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astconstant`.

## `ast.Constant.value.decode`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def decode(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astconstantvaluedecode`.

## `ast.Continue`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Continue(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astcontinue`.

## `ast.Delete`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Delete(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astdelete`.

## `ast.Dict`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Dict(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astdict`.

## `ast.DictComp`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def DictComp(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astdictcomp`.

## `ast.Div`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Div(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astdiv`.

## `ast.Eq`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Eq(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#asteq`.

## `ast.Expr`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Expr(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astexpr`.

## `ast.FloorDiv`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def FloorDiv(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfloordiv`.

## `ast.For`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def For(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfor`.

## `ast.For.csl_ghost_assigns.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astforcsl_ghost_assignsappend`.

## `ast.For.csl_invariants.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astforcsl_invariantsappend`.

## `ast.For.csl_variants.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astforcsl_variantsappend`.

## `ast.FormattedValue`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def FormattedValue(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astformattedvalue`.

## `ast.FunctionDef`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def FunctionDef(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondef`.

## `ast.FunctionDef.csl_assigns.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondefcsl_assignsappend`.

## `ast.FunctionDef.csl_ensures.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondefcsl_ensuresappend`.

## `ast.FunctionDef.csl_function_variants.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondefcsl_function_variantsappend`.

## `ast.FunctionDef.csl_no_exception.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondefcsl_no_exceptionappend`.

## `ast.FunctionDef.csl_proof.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondefcsl_proofappend`.

## `ast.FunctionDef.csl_raises.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondefcsl_raisesappend`.

## `ast.FunctionDef.csl_requires.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondefcsl_requiresappend`.

## `ast.FunctionDef.name.endswith`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def endswith(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondefnameendswith`.

## `ast.FunctionDef.name.startswith`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def startswith(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astfunctiondefnamestartswith`.

## `ast.Gt`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Gt(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astgt`.

## `ast.GtE`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def GtE(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astgte`.

## `ast.If`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def If(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astif`.

## `ast.IfExp`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def IfExp(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astifexp`.

## `ast.Import`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Import(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astimport`.

## `ast.ImportFrom`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def ImportFrom(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astimportfrom`.

## `ast.In`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def In(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astin`.

## `ast.Index`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Index(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astindex`.

## `ast.Is`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Is(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astis`.

## `ast.IsNot`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def IsNot(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astisnot`.

## `ast.JoinedStr`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def JoinedStr(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astjoinedstr`.

## `ast.LShift`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def LShift(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astlshift`.

## `ast.Lambda`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Lambda(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astlambda`.

## `ast.List`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def List(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astlist`.

## `ast.ListComp`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def ListComp(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astlistcomp`.

## `ast.Lt`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Lt(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astlt`.

## `ast.LtE`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def LtE(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astlte`.

## `ast.Match`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Match(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmatch`.

## `ast.MatchAs`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def MatchAs(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmatchas`.

## `ast.MatchOr`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def MatchOr(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmatchor`.

## `ast.MatchSequence`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def MatchSequence(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmatchsequence`.

## `ast.MatchSingleton`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def MatchSingleton(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmatchsingleton`.

## `ast.MatchValue`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def MatchValue(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmatchvalue`.

## `ast.Mod`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Mod(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmod`.

## `ast.Module`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
class Module: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmodule`.

## `ast.Module.csl_shared_decls.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmodulecsl_shared_declsappend`.

## `ast.Mult`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Mult(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astmult`.

## `ast.Name`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Name(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astname`.

## `ast.NamedExpr`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def NamedExpr(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astnamedexpr`.

## `ast.NodeVisitor`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def NodeVisitor(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astnodevisitor`.

## `ast.Not`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Not(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astnot`.

## `ast.NotEq`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def NotEq(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astnoteq`.

## `ast.NotIn`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def NotIn(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astnotin`.

## `ast.Pass`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Pass(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astpass`.

## `ast.Pow`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Pow(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astpow`.

## `ast.RShift`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def RShift(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astrshift`.

## `ast.Raise`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Raise(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astraise`.

## `ast.Return`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Return(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astreturn`.

## `ast.Set`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Set(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astset`.

## `ast.SetComp`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def SetComp(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astsetcomp`.

## `ast.Slice`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Slice(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astslice`.

## `ast.Slice.get`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def get(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astsliceget`.

## `ast.Starred`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Starred(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#aststarred`.

## `ast.Sub`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Sub(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astsub`.

## `ast.Subscript`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Subscript(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astsubscript`.

## `ast.Try`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Try(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#asttry`.

## `ast.Tuple`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Tuple(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#asttuple`.

## `ast.UAdd`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def UAdd(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astuadd`.

## `ast.USub`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def USub(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astusub`.

## `ast.UnaryOp`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def UnaryOp(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astunaryop`.

## `ast.While`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def While(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astwhile`.

## `ast.While.csl_ghost_assigns.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astwhilecsl_ghost_assignsappend`.

## `ast.While.csl_invariants.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astwhilecsl_invariantsappend`.

## `ast.While.csl_variants.append`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def append(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astwhilecsl_variantsappend`.

## `ast.With`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def With(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astwith`.

## `ast.cmpop`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def cmpop(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astcmpop`.

## `ast.comprehension`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
class comprehension: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astcomprehension`.

## `ast.dump`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def dump(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astdump`.

## `ast.expr`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
class expr: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astexpr`.

## `ast.iter_child_nodes`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def iter_child_nodes(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astiter_child_nodes`.

## `ast.operator`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def operator(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astoperator`.

## `ast.parse`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def parse(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astparse`.

## `ast.stmt`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def stmt(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#aststmt`.

## `ast.unaryop`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def unaryop(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astunaryop`.

## `ast.walk`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def walk(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#astwalk`.

---

## Module — `builtins`

## `builtins.abs`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def abs(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsabs`.

## `builtins.all`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def all(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsall`.

## `builtins.any`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def any(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsany`.

## `builtins.bool`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def bool(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsbool`.

## `builtins.dict`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def dict(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsdict`.

## `builtins.enumerate`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def enumerate(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsenumerate`.

## `builtins.eval`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def eval(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinseval`.

## `builtins.float`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def float(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsfloat`.

## `builtins.frozenset`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def frozenset(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsfrozenset`.

## `builtins.getattr`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def getattr(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsgetattr`.

## `builtins.hasattr`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def hasattr(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinshasattr`.

## `builtins.hash`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def hash(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinshash`.

## `builtins.id`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def id(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsid`.

## `builtins.int`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def int(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsint`.

## `builtins.isinstance`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def isinstance(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsisinstance`.

## `builtins.iter`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def iter(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsiter`.

## `builtins.len`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def len(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinslen`.

## `builtins.list`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def list(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinslist`.

## `builtins.max`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def max(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsmax`.

## `builtins.min`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def min(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsmin`.

## `builtins.next`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def next(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsnext`.

## `builtins.open`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def open(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsopen`.

## `builtins.ord`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def ord(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsord`.

## `builtins.print`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def print(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsprint`.

## `builtins.range`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def range(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsrange`.

## `builtins.reversed`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def reversed(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsreversed`.

## `builtins.set`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def set(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsset`.

## `builtins.sorted`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def sorted(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinssorted`.

## `builtins.str`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def str(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinsstr`.

## `builtins.sum`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def sum(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinssum`.

## `builtins.super`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def super(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinssuper`.

## `builtins.type`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def type(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinstype`.

## `builtins.zip`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def zip(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#builtinszip`.

---

## Module — `collections`

## `collections.defaultdict`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def defaultdict(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#collectionsdefaultdict`.

---

## Module — `dataclasses`

## `dataclasses.dataclass`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def dataclass(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#dataclassesdataclass`.

## `dataclasses.field`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def field(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#dataclassesfield`.

---

## Module — `datetime`

## `datetime`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def datetime(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#datetime`.

## `datetime.datetime`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def datetime(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#datetimedatetime`.

## `datetime.datetime.fromisoformat`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def fromisoformat(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#datetimedatetimefromisoformat`.

## `datetime.datetime.now`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def now(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#datetimedatetimenow`.

---

## Module — `hashlib`

## `hashlib`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def hashlib(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#hashlib`.

## `hashlib.sha256`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def sha256(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#hashlibsha256`.

---

## Module — `importlib`

## `importlib.util`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def util(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#importlibutil`.

## `importlib.util.module_from_spec`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def module_from_spec(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#importlibutilmodule_from_spec`.

## `importlib.util.spec_from_file_location`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def spec_from_file_location(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#importlibutilspec_from_file_location`.

---

## Module — `json`

## `json`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def json(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#json`.

## `json.JSONDecodeError`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def JSONDecodeError(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#jsonjsondecodeerror`.

## `json.dumps`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def dumps(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#jsondumps`.

## `json.load`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def load(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#jsonload`.

## `json.loads`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def loads(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#jsonloads`.

---

## Module — `os`

## `os`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def os(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#os`.

## `os.X_OK`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def X_OK(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#osx_ok`.

## `os.access`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def access(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#osaccess`.

## `os.close`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def close(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#osclose`.

## `os.environ`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def environ(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#osenviron`.

## `os.environ.get`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def get(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#osenvironget`.

## `os.getcwd`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def getcwd(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#osgetcwd`.

## `os.listdir`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def listdir(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#oslistdir`.

## `os.makedirs`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def makedirs(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#osmakedirs`.

## `os.pardir`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def pardir(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospardir`.

## `os.path`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def path(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospath`.

## `os.path.abspath`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def abspath(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathabspath`.

## `os.path.basename`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def basename(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathbasename`.

## `os.path.dirname`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def dirname(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathdirname`.

## `os.path.exists`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def exists(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathexists`.

## `os.path.expanduser`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def expanduser(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathexpanduser`.

## `os.path.isdir`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def isdir(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathisdir`.

## `os.path.isfile`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def isfile(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathisfile`.

## `os.path.join`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def join(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathjoin`.

## `os.path.normpath`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def normpath(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathnormpath`.

## `os.path.splitext`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def splitext(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#ospathsplitext`.

## `os.remove`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def remove(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#osremove`.

## `os.unlink`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def unlink(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#osunlink`.

---

## Module — `pathlib`

## `pathlib.Path`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Path(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#pathlibpath`.

## `pathlib.Path.cwd`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def cwd(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#pathlibpathcwd`.

## `pathlib.Path.home`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def home(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#pathlibpathhome`.

---

## Module — `re`

## `re`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def re(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#re`.

## `re.DOTALL`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def DOTALL(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#redotall`.

## `re.IGNORECASE`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def IGNORECASE(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#reignorecase`.

## `re.MULTILINE`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def MULTILINE(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#remultiline`.

## `re.Match`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
class Match: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#rematch`.

## `re.Match.group`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def group(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#rematchgroup`.

## `re.compile`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def compile(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#recompile`.

## `re.escape`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def escape(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#reescape`.

## `re.findall`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def findall(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#refindall`.

## `re.finditer`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def finditer(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#refinditer`.

## `re.match`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def match(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#rematch`.

## `re.search`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def search(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#research`.

## `re.sub`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def sub(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#resub`.

---

## Module — `shutil`

## `shutil`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def shutil(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#shutil`.

## `shutil.copy2`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def copy2(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#shutilcopy2`.

## `shutil.rmtree`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def rmtree(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#shutilrmtree`.

## `shutil.which`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def which(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#shutilwhich`.

---

## Module — `subprocess`

## `subprocess`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def subprocess(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#subprocess`.

## `subprocess.CompletedProcess`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
class CompletedProcess: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#subprocesscompletedprocess`.

## `subprocess.SubprocessError`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def SubprocessError(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#subprocesssubprocesserror`.

## `subprocess.TimeoutExpired`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def TimeoutExpired(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#subprocesstimeoutexpired`.

## `subprocess.run`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def run(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#subprocessrun`.

---

## Module — `sys`

## `sys`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def sys(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#sys`.

## `sys.executable`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def executable(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#sysexecutable`.

## `sys.exit`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def exit(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#sysexit`.

## `sys.path`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def path(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#syspath`.

## `sys.path.insert`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def insert(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#syspathinsert`.

## `sys.stderr`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def stderr(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#sysstderr`.

## `sys.stdin`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def stdin(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#sysstdin`.

## `sys.stdin.read`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def read(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#sysstdinread`.

## `sys.stdout`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def stdout(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#sysstdout`.

## `sys.stdout.write`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def write(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#sysstdoutwrite`.

---

## Module — `tempfile`

## `tempfile`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def tempfile(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#tempfile`.

## `tempfile.NamedTemporaryFile`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def NamedTemporaryFile(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#tempfilenamedtemporaryfile`.

## `tempfile.TemporaryDirectory`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def TemporaryDirectory(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#tempfiletemporarydirectory`.

## `tempfile.mkstemp`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def mkstemp(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#tempfilemkstemp`.

---

## Module — `textwrap`

## `textwrap`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def textwrap(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#textwrap`.

## `textwrap.indent`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def indent(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#textwrapindent`.

---

## Module — `time`

## `time`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def time(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#time`.

## `time.monotonic`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def monotonic(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#timemonotonic`.

---

## Module — `typing`

## `typing.Any`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Any(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#typingany`.

## `typing.Callable`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Callable(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#typingcallable`.

## `typing.Dict`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Dict(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#typingdict`.

## `typing.List`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def List(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#typinglist`.

## `typing.Optional`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Optional(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#typingoptional`.

## `typing.Set`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Set(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#typingset`.

## `typing.Tuple`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Tuple(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#typingtuple`.

## `typing.TypedDict`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def TypedDict(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#typingtypeddict`.

## `typing.Union`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Union(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#typingunion`.

---

## Module — `unicodedata`

## `unicodedata`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def unicodedata(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#unicodedata`.

## `unicodedata.normalize`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def normalize(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#unicodedatanormalize`.

---

## Module — `urllib`

## `urllib.request`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def request(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#urllibrequest`.

## `urllib.request.request`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def request(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#urllibrequestrequest`.

## `urllib.request.request.Request`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def Request(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#urllibrequestrequestrequest`.

## `urllib.request.request.urlopen`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def urlopen(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#urllibrequestrequesturlopen`.

---

## Module — `warnings`

## `warnings`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def warnings(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#warnings`.

## `warnings.warn`

```python
#@ requires True  # TODO
#@ ensures True  # TODO
#@ assigns \nothing  # TODO
#@ raises { }  # TODO — fill in raised exceptions per CPython docs
#@ \trusted
def warn(*args, **kwargs) -> int: ...
```

Cross-check: TODO — verify the contract above is faithful to `calls-english.md#warningswarn`.

---
