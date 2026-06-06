# Library Method Calls — English Descriptions

Per-symbol English descriptions for every stdlib API entry used
inside `src/pycsl/`. Anchored to vendored CPython docs at the
submodule HEAD (Python 3.16-alpha at the time of scaffolding).

Each entry follows the workplan §3.1 template:

```
## `<qualified.name>`
<English description, anchored to CPython doc paragraph>.
Raises: <exceptions> | nothing
Source: cpython/Doc/library/<module>.rst
Modeled in: src/pycsl_lib/<module>.py
PyCSL contract: calls-pycsl.md#<anchor>
```

**Status:** scaffolded. Entries marked `TODO` need hand-written
English from the CPython doc files. See workplan §13 step 4 and
`config/skills/pycsl-stdlib-coverage/SKILL.md` for the curation
discipline.

---

## Module — `argparse`

## `argparse`

TODO — describe `argparse` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/argparse.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/argparse.py
PyCSL contract: calls-pycsl.md#argparse

## `argparse.ArgumentParser`

TODO — describe `argparse.ArgumentParser` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/argparse.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/argparse.py
PyCSL contract: calls-pycsl.md#argparseargumentparser

## `argparse.Namespace`

TODO — describe `argparse.Namespace` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/argparse.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/argparse.py
PyCSL contract: calls-pycsl.md#argparsenamespace

## `argparse.Namespace.provers.split`

TODO — describe `argparse.Namespace.provers.split` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/argparse.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/argparse/Namespace/provers.py
PyCSL contract: calls-pycsl.md#argparsenamespaceproverssplit

---

## Module — `ast`

## `ast`

TODO — describe `ast` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#ast

## `ast.AST`

TODO — describe `ast.AST` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astast

## `ast.AST.csl_shared_decls.append`

TODO — describe `ast.AST.csl_shared_decls.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/AST/csl_shared_decls.py
PyCSL contract: calls-pycsl.md#astastcsl_shared_declsappend

## `ast.Add`

TODO — describe `ast.Add` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astadd

## `ast.And`

TODO — describe `ast.And` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astand

## `ast.AnnAssign`

TODO — describe `ast.AnnAssign` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astannassign

## `ast.Assert`

TODO — describe `ast.Assert` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astassert

## `ast.Assign`

TODO — describe `ast.Assign` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astassign

## `ast.AsyncFunctionDef`

TODO — describe `ast.AsyncFunctionDef` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astasyncfunctiondef

## `ast.Attribute`

TODO — describe `ast.Attribute` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astattribute

## `ast.AugAssign`

TODO — describe `ast.AugAssign` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astaugassign

## `ast.BinOp`

TODO — describe `ast.BinOp` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astbinop

## `ast.BitAnd`

TODO — describe `ast.BitAnd` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astbitand

## `ast.BitOr`

TODO — describe `ast.BitOr` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astbitor

## `ast.BitXor`

TODO — describe `ast.BitXor` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astbitxor

## `ast.BoolOp`

TODO — describe `ast.BoolOp` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astboolop

## `ast.Break`

TODO — describe `ast.Break` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astbreak

## `ast.Call`

TODO — describe `ast.Call` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astcall

## `ast.ClassDef`

TODO — describe `ast.ClassDef` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astclassdef

## `ast.ClassDef.csl_class_invariants.append`

TODO — describe `ast.ClassDef.csl_class_invariants.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/ClassDef/csl_class_invariants.py
PyCSL contract: calls-pycsl.md#astclassdefcsl_class_invariantsappend

## `ast.Compare`

TODO — describe `ast.Compare` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astcompare

## `ast.Constant`

TODO — describe `ast.Constant` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astconstant

## `ast.Constant.value.decode`

TODO — describe `ast.Constant.value.decode` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/Constant/value.py
PyCSL contract: calls-pycsl.md#astconstantvaluedecode

## `ast.Continue`

TODO — describe `ast.Continue` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astcontinue

## `ast.Delete`

TODO — describe `ast.Delete` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astdelete

## `ast.Dict`

TODO — describe `ast.Dict` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astdict

## `ast.DictComp`

TODO — describe `ast.DictComp` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astdictcomp

## `ast.Div`

TODO — describe `ast.Div` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astdiv

## `ast.Eq`

TODO — describe `ast.Eq` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#asteq

## `ast.Expr`

TODO — describe `ast.Expr` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astexpr

## `ast.FloorDiv`

TODO — describe `ast.FloorDiv` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astfloordiv

## `ast.For`

TODO — describe `ast.For` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astfor

## `ast.For.csl_ghost_assigns.append`

TODO — describe `ast.For.csl_ghost_assigns.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/For/csl_ghost_assigns.py
PyCSL contract: calls-pycsl.md#astforcsl_ghost_assignsappend

## `ast.For.csl_invariants.append`

TODO — describe `ast.For.csl_invariants.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/For/csl_invariants.py
PyCSL contract: calls-pycsl.md#astforcsl_invariantsappend

## `ast.For.csl_variants.append`

TODO — describe `ast.For.csl_variants.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/For/csl_variants.py
PyCSL contract: calls-pycsl.md#astforcsl_variantsappend

## `ast.FormattedValue`

TODO — describe `ast.FormattedValue` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astformattedvalue

## `ast.FunctionDef`

TODO — describe `ast.FunctionDef` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astfunctiondef

## `ast.FunctionDef.csl_assigns.append`

TODO — describe `ast.FunctionDef.csl_assigns.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/FunctionDef/csl_assigns.py
PyCSL contract: calls-pycsl.md#astfunctiondefcsl_assignsappend

## `ast.FunctionDef.csl_ensures.append`

TODO — describe `ast.FunctionDef.csl_ensures.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/FunctionDef/csl_ensures.py
PyCSL contract: calls-pycsl.md#astfunctiondefcsl_ensuresappend

## `ast.FunctionDef.csl_function_variants.append`

TODO — describe `ast.FunctionDef.csl_function_variants.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/FunctionDef/csl_function_variants.py
PyCSL contract: calls-pycsl.md#astfunctiondefcsl_function_variantsappend

## `ast.FunctionDef.csl_no_exception.append`

TODO — describe `ast.FunctionDef.csl_no_exception.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/FunctionDef/csl_no_exception.py
PyCSL contract: calls-pycsl.md#astfunctiondefcsl_no_exceptionappend

## `ast.FunctionDef.csl_proof.append`

TODO — describe `ast.FunctionDef.csl_proof.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/FunctionDef/csl_proof.py
PyCSL contract: calls-pycsl.md#astfunctiondefcsl_proofappend

## `ast.FunctionDef.csl_raises.append`

TODO — describe `ast.FunctionDef.csl_raises.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/FunctionDef/csl_raises.py
PyCSL contract: calls-pycsl.md#astfunctiondefcsl_raisesappend

## `ast.FunctionDef.csl_requires.append`

TODO — describe `ast.FunctionDef.csl_requires.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/FunctionDef/csl_requires.py
PyCSL contract: calls-pycsl.md#astfunctiondefcsl_requiresappend

## `ast.FunctionDef.name.endswith`

TODO — describe `ast.FunctionDef.name.endswith` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/FunctionDef/name.py
PyCSL contract: calls-pycsl.md#astfunctiondefnameendswith

## `ast.FunctionDef.name.startswith`

TODO — describe `ast.FunctionDef.name.startswith` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/FunctionDef/name.py
PyCSL contract: calls-pycsl.md#astfunctiondefnamestartswith

## `ast.Gt`

TODO — describe `ast.Gt` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astgt

## `ast.GtE`

TODO — describe `ast.GtE` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astgte

## `ast.If`

TODO — describe `ast.If` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astif

## `ast.IfExp`

TODO — describe `ast.IfExp` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astifexp

## `ast.Import`

TODO — describe `ast.Import` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astimport

## `ast.ImportFrom`

TODO — describe `ast.ImportFrom` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astimportfrom

## `ast.In`

TODO — describe `ast.In` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astin

## `ast.Index`

TODO — describe `ast.Index` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astindex

## `ast.Is`

TODO — describe `ast.Is` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astis

## `ast.IsNot`

TODO — describe `ast.IsNot` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astisnot

## `ast.JoinedStr`

TODO — describe `ast.JoinedStr` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astjoinedstr

## `ast.LShift`

TODO — describe `ast.LShift` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astlshift

## `ast.Lambda`

TODO — describe `ast.Lambda` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astlambda

## `ast.List`

TODO — describe `ast.List` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astlist

## `ast.ListComp`

TODO — describe `ast.ListComp` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astlistcomp

## `ast.Lt`

TODO — describe `ast.Lt` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astlt

## `ast.LtE`

TODO — describe `ast.LtE` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astlte

## `ast.Match`

TODO — describe `ast.Match` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astmatch

## `ast.MatchAs`

TODO — describe `ast.MatchAs` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astmatchas

## `ast.MatchOr`

TODO — describe `ast.MatchOr` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astmatchor

## `ast.MatchSequence`

TODO — describe `ast.MatchSequence` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astmatchsequence

## `ast.MatchSingleton`

TODO — describe `ast.MatchSingleton` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astmatchsingleton

## `ast.MatchValue`

TODO — describe `ast.MatchValue` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astmatchvalue

## `ast.Mod`

TODO — describe `ast.Mod` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astmod

## `ast.Module`

TODO — describe `ast.Module` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astmodule

## `ast.Module.csl_shared_decls.append`

TODO — describe `ast.Module.csl_shared_decls.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/Module/csl_shared_decls.py
PyCSL contract: calls-pycsl.md#astmodulecsl_shared_declsappend

## `ast.Mult`

TODO — describe `ast.Mult` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astmult

## `ast.Name`

TODO — describe `ast.Name` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astname

## `ast.NamedExpr`

TODO — describe `ast.NamedExpr` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astnamedexpr

## `ast.NodeVisitor`

TODO — describe `ast.NodeVisitor` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astnodevisitor

## `ast.Not`

TODO — describe `ast.Not` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astnot

## `ast.NotEq`

TODO — describe `ast.NotEq` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astnoteq

## `ast.NotIn`

TODO — describe `ast.NotIn` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astnotin

## `ast.Pass`

TODO — describe `ast.Pass` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astpass

## `ast.Pow`

TODO — describe `ast.Pow` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astpow

## `ast.RShift`

TODO — describe `ast.RShift` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astrshift

## `ast.Raise`

TODO — describe `ast.Raise` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astraise

## `ast.Return`

TODO — describe `ast.Return` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astreturn

## `ast.Set`

TODO — describe `ast.Set` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astset

## `ast.SetComp`

TODO — describe `ast.SetComp` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astsetcomp

## `ast.Slice`

TODO — describe `ast.Slice` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astslice

## `ast.Slice.get`

TODO — describe `ast.Slice.get` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/Slice.py
PyCSL contract: calls-pycsl.md#astsliceget

## `ast.Starred`

TODO — describe `ast.Starred` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#aststarred

## `ast.Sub`

TODO — describe `ast.Sub` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astsub

## `ast.Subscript`

TODO — describe `ast.Subscript` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astsubscript

## `ast.Try`

TODO — describe `ast.Try` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#asttry

## `ast.Tuple`

TODO — describe `ast.Tuple` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#asttuple

## `ast.UAdd`

TODO — describe `ast.UAdd` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astuadd

## `ast.USub`

TODO — describe `ast.USub` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astusub

## `ast.UnaryOp`

TODO — describe `ast.UnaryOp` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astunaryop

## `ast.While`

TODO — describe `ast.While` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astwhile

## `ast.While.csl_ghost_assigns.append`

TODO — describe `ast.While.csl_ghost_assigns.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/While/csl_ghost_assigns.py
PyCSL contract: calls-pycsl.md#astwhilecsl_ghost_assignsappend

## `ast.While.csl_invariants.append`

TODO — describe `ast.While.csl_invariants.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/While/csl_invariants.py
PyCSL contract: calls-pycsl.md#astwhilecsl_invariantsappend

## `ast.While.csl_variants.append`

TODO — describe `ast.While.csl_variants.append` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast/While/csl_variants.py
PyCSL contract: calls-pycsl.md#astwhilecsl_variantsappend

## `ast.With`

TODO — describe `ast.With` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astwith

## `ast.cmpop`

TODO — describe `ast.cmpop` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astcmpop

## `ast.comprehension`

TODO — describe `ast.comprehension` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astcomprehension

## `ast.dump`

TODO — describe `ast.dump` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astdump

## `ast.expr`

TODO — describe `ast.expr` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astexpr

## `ast.iter_child_nodes`

TODO — describe `ast.iter_child_nodes` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astiter_child_nodes

## `ast.operator`

TODO — describe `ast.operator` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astoperator

## `ast.parse`

TODO — describe `ast.parse` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astparse

## `ast.stmt`

TODO — describe `ast.stmt` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#aststmt

## `ast.unaryop`

TODO — describe `ast.unaryop` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astunaryop

## `ast.walk`

TODO — describe `ast.walk` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/ast.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/ast.py
PyCSL contract: calls-pycsl.md#astwalk

---

## Module — `builtins`

## `builtins.abs`

TODO — describe `builtins.abs` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsabs

## `builtins.all`

TODO — describe `builtins.all` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsall

## `builtins.any`

TODO — describe `builtins.any` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsany

## `builtins.bool`

TODO — describe `builtins.bool` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsbool

## `builtins.dict`

TODO — describe `builtins.dict` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsdict

## `builtins.enumerate`

TODO — describe `builtins.enumerate` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsenumerate

## `builtins.eval`

TODO — describe `builtins.eval` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinseval

## `builtins.float`

TODO — describe `builtins.float` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsfloat

## `builtins.frozenset`

TODO — describe `builtins.frozenset` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsfrozenset

## `builtins.getattr`

TODO — describe `builtins.getattr` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsgetattr

## `builtins.hasattr`

TODO — describe `builtins.hasattr` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinshasattr

## `builtins.hash`

TODO — describe `builtins.hash` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinshash

## `builtins.id`

TODO — describe `builtins.id` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsid

## `builtins.int`

TODO — describe `builtins.int` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsint

## `builtins.isinstance`

TODO — describe `builtins.isinstance` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsisinstance

## `builtins.iter`

TODO — describe `builtins.iter` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsiter

## `builtins.len`

TODO — describe `builtins.len` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinslen

## `builtins.list`

TODO — describe `builtins.list` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinslist

## `builtins.max`

TODO — describe `builtins.max` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsmax

## `builtins.min`

TODO — describe `builtins.min` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsmin

## `builtins.next`

TODO — describe `builtins.next` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsnext

## `builtins.open`

TODO — describe `builtins.open` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsopen

## `builtins.ord`

TODO — describe `builtins.ord` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsord

## `builtins.print`

TODO — describe `builtins.print` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsprint

## `builtins.range`

TODO — describe `builtins.range` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsrange

## `builtins.reversed`

TODO — describe `builtins.reversed` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsreversed

## `builtins.set`

TODO — describe `builtins.set` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsset

## `builtins.sorted`

TODO — describe `builtins.sorted` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinssorted

## `builtins.str`

TODO — describe `builtins.str` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinsstr

## `builtins.sum`

TODO — describe `builtins.sum` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinssum

## `builtins.super`

TODO — describe `builtins.super` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinssuper

## `builtins.type`

TODO — describe `builtins.type` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinstype

## `builtins.zip`

TODO — describe `builtins.zip` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/functions.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/builtins.py
PyCSL contract: calls-pycsl.md#builtinszip

---

## Module — `collections`

## `collections.defaultdict`

TODO — describe `collections.defaultdict` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/collections.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/collections.py
PyCSL contract: calls-pycsl.md#collectionsdefaultdict

---

## Module — `dataclasses`

## `dataclasses.dataclass`

TODO — describe `dataclasses.dataclass` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/dataclasses.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/dataclasses.py
PyCSL contract: calls-pycsl.md#dataclassesdataclass

## `dataclasses.field`

TODO — describe `dataclasses.field` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/dataclasses.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/dataclasses.py
PyCSL contract: calls-pycsl.md#dataclassesfield

---

## Module — `datetime`

## `datetime`

TODO — describe `datetime` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/datetime.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/datetime.py
PyCSL contract: calls-pycsl.md#datetime

## `datetime.datetime`

TODO — describe `datetime.datetime` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/datetime.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/datetime.py
PyCSL contract: calls-pycsl.md#datetimedatetime

## `datetime.datetime.fromisoformat`

TODO — describe `datetime.datetime.fromisoformat` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/datetime.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/datetime/datetime.py
PyCSL contract: calls-pycsl.md#datetimedatetimefromisoformat

## `datetime.datetime.now`

TODO — describe `datetime.datetime.now` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/datetime.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/datetime/datetime.py
PyCSL contract: calls-pycsl.md#datetimedatetimenow

---

## Module — `hashlib`

## `hashlib`

TODO — describe `hashlib` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/hashlib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/hashlib.py
PyCSL contract: calls-pycsl.md#hashlib

## `hashlib.sha256`

TODO — describe `hashlib.sha256` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/hashlib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/hashlib.py
PyCSL contract: calls-pycsl.md#hashlibsha256

---

## Module — `importlib`

## `importlib.util`

TODO — describe `importlib.util` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/importlib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/importlib.py
PyCSL contract: calls-pycsl.md#importlibutil

## `importlib.util.module_from_spec`

TODO — describe `importlib.util.module_from_spec` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/importlib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/importlib/util.py
PyCSL contract: calls-pycsl.md#importlibutilmodule_from_spec

## `importlib.util.spec_from_file_location`

TODO — describe `importlib.util.spec_from_file_location` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/importlib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/importlib/util.py
PyCSL contract: calls-pycsl.md#importlibutilspec_from_file_location

---

## Module — `json`

## `json`

TODO — describe `json` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/json.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/json.py
PyCSL contract: calls-pycsl.md#json

## `json.JSONDecodeError`

TODO — describe `json.JSONDecodeError` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/json.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/json.py
PyCSL contract: calls-pycsl.md#jsonjsondecodeerror

## `json.dumps`

TODO — describe `json.dumps` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/json.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/json.py
PyCSL contract: calls-pycsl.md#jsondumps

## `json.load`

TODO — describe `json.load` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/json.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/json.py
PyCSL contract: calls-pycsl.md#jsonload

## `json.loads`

TODO — describe `json.loads` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/json.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/json.py
PyCSL contract: calls-pycsl.md#jsonloads

---

## Module — `os`

## `os`

TODO — describe `os` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#os

## `os.X_OK`

TODO — describe `os.X_OK` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#osx_ok

## `os.access`

TODO — describe `os.access` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#osaccess

## `os.close`

TODO — describe `os.close` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#osclose

## `os.environ`

TODO — describe `os.environ` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#osenviron

## `os.environ.get`

TODO — describe `os.environ.get` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/environ.py
PyCSL contract: calls-pycsl.md#osenvironget

## `os.getcwd`

TODO — describe `os.getcwd` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#osgetcwd

## `os.listdir`

TODO — describe `os.listdir` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#oslistdir

## `os.makedirs`

TODO — describe `os.makedirs` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#osmakedirs

## `os.pardir`

TODO — describe `os.pardir` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#ospardir

## `os.path`

TODO — describe `os.path` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#ospath

## `os.path.abspath`

TODO — describe `os.path.abspath` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathabspath

## `os.path.basename`

TODO — describe `os.path.basename` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathbasename

## `os.path.dirname`

TODO — describe `os.path.dirname` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathdirname

## `os.path.exists`

TODO — describe `os.path.exists` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathexists

## `os.path.expanduser`

TODO — describe `os.path.expanduser` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathexpanduser

## `os.path.isdir`

TODO — describe `os.path.isdir` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathisdir

## `os.path.isfile`

TODO — describe `os.path.isfile` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathisfile

## `os.path.join`

TODO — describe `os.path.join` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathjoin

## `os.path.normpath`

TODO — describe `os.path.normpath` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathnormpath

## `os.path.splitext`

TODO — describe `os.path.splitext` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os/path.py
PyCSL contract: calls-pycsl.md#ospathsplitext

## `os.remove`

TODO — describe `os.remove` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#osremove

## `os.unlink`

TODO — describe `os.unlink` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/os.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/os.py
PyCSL contract: calls-pycsl.md#osunlink

---

## Module — `pathlib`

## `pathlib.Path`

TODO — describe `pathlib.Path` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/pathlib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/pathlib.py
PyCSL contract: calls-pycsl.md#pathlibpath

## `pathlib.Path.cwd`

TODO — describe `pathlib.Path.cwd` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/pathlib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/pathlib/Path.py
PyCSL contract: calls-pycsl.md#pathlibpathcwd

## `pathlib.Path.home`

TODO — describe `pathlib.Path.home` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/pathlib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/pathlib/Path.py
PyCSL contract: calls-pycsl.md#pathlibpathhome

---

## Module — `re`

## `re`

TODO — describe `re` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#re

## `re.DOTALL`

TODO — describe `re.DOTALL` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#redotall

## `re.IGNORECASE`

TODO — describe `re.IGNORECASE` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#reignorecase

## `re.MULTILINE`

TODO — describe `re.MULTILINE` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#remultiline

## `re.Match`

TODO — describe `re.Match` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#rematch

## `re.Match.group`

TODO — describe `re.Match.group` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re/Match.py
PyCSL contract: calls-pycsl.md#rematchgroup

## `re.compile`

TODO — describe `re.compile` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#recompile

## `re.escape`

TODO — describe `re.escape` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#reescape

## `re.findall`

TODO — describe `re.findall` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#refindall

## `re.finditer`

TODO — describe `re.finditer` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#refinditer

## `re.match`

TODO — describe `re.match` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#rematch

## `re.search`

TODO — describe `re.search` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#research

## `re.sub`

TODO — describe `re.sub` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/re.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/re.py
PyCSL contract: calls-pycsl.md#resub

---

## Module — `shutil`

## `shutil`

TODO — describe `shutil` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/shutil.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/shutil.py
PyCSL contract: calls-pycsl.md#shutil

## `shutil.copy2`

TODO — describe `shutil.copy2` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/shutil.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/shutil.py
PyCSL contract: calls-pycsl.md#shutilcopy2

## `shutil.rmtree`

TODO — describe `shutil.rmtree` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/shutil.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/shutil.py
PyCSL contract: calls-pycsl.md#shutilrmtree

## `shutil.which`

TODO — describe `shutil.which` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/shutil.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/shutil.py
PyCSL contract: calls-pycsl.md#shutilwhich

---

## Module — `subprocess`

## `subprocess`

TODO — describe `subprocess` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/subprocess.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/subprocess.py
PyCSL contract: calls-pycsl.md#subprocess

## `subprocess.CompletedProcess`

TODO — describe `subprocess.CompletedProcess` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/subprocess.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/subprocess.py
PyCSL contract: calls-pycsl.md#subprocesscompletedprocess

## `subprocess.SubprocessError`

TODO — describe `subprocess.SubprocessError` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/subprocess.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/subprocess.py
PyCSL contract: calls-pycsl.md#subprocesssubprocesserror

## `subprocess.TimeoutExpired`

TODO — describe `subprocess.TimeoutExpired` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/subprocess.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/subprocess.py
PyCSL contract: calls-pycsl.md#subprocesstimeoutexpired

## `subprocess.run`

TODO — describe `subprocess.run` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/subprocess.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/subprocess.py
PyCSL contract: calls-pycsl.md#subprocessrun

---

## Module — `sys`

## `sys`

TODO — describe `sys` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys.py
PyCSL contract: calls-pycsl.md#sys

## `sys.executable`

TODO — describe `sys.executable` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys.py
PyCSL contract: calls-pycsl.md#sysexecutable

## `sys.exit`

TODO — describe `sys.exit` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys.py
PyCSL contract: calls-pycsl.md#sysexit

## `sys.path`

TODO — describe `sys.path` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys.py
PyCSL contract: calls-pycsl.md#syspath

## `sys.path.insert`

TODO — describe `sys.path.insert` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys/path.py
PyCSL contract: calls-pycsl.md#syspathinsert

## `sys.stderr`

TODO — describe `sys.stderr` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys.py
PyCSL contract: calls-pycsl.md#sysstderr

## `sys.stdin`

TODO — describe `sys.stdin` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys.py
PyCSL contract: calls-pycsl.md#sysstdin

## `sys.stdin.read`

TODO — describe `sys.stdin.read` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys/stdin.py
PyCSL contract: calls-pycsl.md#sysstdinread

## `sys.stdout`

TODO — describe `sys.stdout` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys.py
PyCSL contract: calls-pycsl.md#sysstdout

## `sys.stdout.write`

TODO — describe `sys.stdout.write` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/sys.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/sys/stdout.py
PyCSL contract: calls-pycsl.md#sysstdoutwrite

---

## Module — `tempfile`

## `tempfile`

TODO — describe `tempfile` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/tempfile.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/tempfile.py
PyCSL contract: calls-pycsl.md#tempfile

## `tempfile.NamedTemporaryFile`

TODO — describe `tempfile.NamedTemporaryFile` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/tempfile.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/tempfile.py
PyCSL contract: calls-pycsl.md#tempfilenamedtemporaryfile

## `tempfile.TemporaryDirectory`

TODO — describe `tempfile.TemporaryDirectory` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/tempfile.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/tempfile.py
PyCSL contract: calls-pycsl.md#tempfiletemporarydirectory

## `tempfile.mkstemp`

TODO — describe `tempfile.mkstemp` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/tempfile.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/tempfile.py
PyCSL contract: calls-pycsl.md#tempfilemkstemp

---

## Module — `textwrap`

## `textwrap`

TODO — describe `textwrap` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/textwrap.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/textwrap.py
PyCSL contract: calls-pycsl.md#textwrap

## `textwrap.indent`

TODO — describe `textwrap.indent` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/textwrap.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/textwrap.py
PyCSL contract: calls-pycsl.md#textwrapindent

---

## Module — `time`

## `time`

TODO — describe `time` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/time.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/time.py
PyCSL contract: calls-pycsl.md#time

## `time.monotonic`

TODO — describe `time.monotonic` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/time.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/time.py
PyCSL contract: calls-pycsl.md#timemonotonic

---

## Module — `typing`

## `typing.Any`

TODO — describe `typing.Any` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/typing.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/typing.py
PyCSL contract: calls-pycsl.md#typingany

## `typing.Callable`

TODO — describe `typing.Callable` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/typing.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/typing.py
PyCSL contract: calls-pycsl.md#typingcallable

## `typing.Dict`

TODO — describe `typing.Dict` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/typing.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/typing.py
PyCSL contract: calls-pycsl.md#typingdict

## `typing.List`

TODO — describe `typing.List` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/typing.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/typing.py
PyCSL contract: calls-pycsl.md#typinglist

## `typing.Optional`

TODO — describe `typing.Optional` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/typing.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/typing.py
PyCSL contract: calls-pycsl.md#typingoptional

## `typing.Set`

TODO — describe `typing.Set` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/typing.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/typing.py
PyCSL contract: calls-pycsl.md#typingset

## `typing.Tuple`

TODO — describe `typing.Tuple` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/typing.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/typing.py
PyCSL contract: calls-pycsl.md#typingtuple

## `typing.TypedDict`

TODO — describe `typing.TypedDict` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/typing.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/typing.py
PyCSL contract: calls-pycsl.md#typingtypeddict

## `typing.Union`

TODO — describe `typing.Union` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/typing.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/typing.py
PyCSL contract: calls-pycsl.md#typingunion

---

## Module — `unicodedata`

## `unicodedata`

TODO — describe `unicodedata` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/unicodedata.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/unicodedata.py
PyCSL contract: calls-pycsl.md#unicodedata

## `unicodedata.normalize`

TODO — describe `unicodedata.normalize` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/unicodedata.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/unicodedata.py
PyCSL contract: calls-pycsl.md#unicodedatanormalize

---

## Module — `urllib`

## `urllib.request`

TODO — describe `urllib.request` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/urllib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/urllib.py
PyCSL contract: calls-pycsl.md#urllibrequest

## `urllib.request.request`

TODO — describe `urllib.request.request` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/urllib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/urllib/request.py
PyCSL contract: calls-pycsl.md#urllibrequestrequest

## `urllib.request.request.Request`

TODO — describe `urllib.request.request.Request` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/urllib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/urllib/request/request.py
PyCSL contract: calls-pycsl.md#urllibrequestrequestrequest

## `urllib.request.request.urlopen`

TODO — describe `urllib.request.request.urlopen` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/urllib.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/urllib/request/request.py
PyCSL contract: calls-pycsl.md#urllibrequestrequesturlopen

---

## Module — `warnings`

## `warnings`

TODO — describe `warnings` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/warnings.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/warnings.py
PyCSL contract: calls-pycsl.md#warnings

## `warnings.warn`

TODO — describe `warnings.warn` in plain English, anchored to CPython doc.

Raises: TODO
Source: cpython/Doc/library/warnings.rst (Python 3.16-alpha)
Modeled in: src/pycsl_lib/warnings.py
PyCSL contract: calls-pycsl.md#warningswarn

---
