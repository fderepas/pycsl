# OPEN ROUTE #593 — A USER CLASS INHERITING TWO ast NODE CLASSES (class B(ast.Name, ast.Call)) MAKES isinstance(x, ast.Name) and isinstance(x, ast.Call) BOTH TRUE, BUT THE emit_ir MODEL TREATS THE CONSTRUCTORS AS DISJOINT
**Status: OPEN, Severity 1, pre-existing (red team rt56; Verification SUCCESS on the run #6 base 822621340 and on int55; CPython breaks the claim).** Witnesses witnesses-r593/.
