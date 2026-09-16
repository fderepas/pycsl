# ROUTE #154 — an ELEMENT store into a field's container inside `__init__` is dropped from the literal

**Status: REPAIR DRAFTED by gen #29 (worktree wt152, with #152/#153); battery F' pending.** Severity 1.
Generator: carrier-rerun (the #150 construction neighbourhood, after battery E).

## Measured at `52a02d5a` (CPython contradicting)

    self.xs: List[int] = [1, 2]; self.xs[0] = 9      C().xs[0] == 1   PROVED   (CPython 9)
    self.d: Dict[int, int] = {1: 5}; self.d[1] = 9   C().d[1] == 5    PROVED   (CPython 9)
    xs = self.xs; xs[0] = 9                           C().xs[0] == 1   PROVED   (a carrier of the first draft)

Routes #85/#87 made a list/dict field literal FAITHFUL; only ATTRIBUTE stores (#83/#88) were checked
afterwards, so a subscript store — or a store through an alias of the container — left the literal
in place as a definite wrong value.

## Repair (draft 2)

A subscript store / augmented store / `del` rooted at `self.<f>` makes `<f>` unknown on both
channels; a LOAD of `self.<f>` whose value can escape — anything other than an element read, an
attribute read, a callee, a pure builtin's argument, an operand, a test or an iteration source —
makes its contents unknown (collection channel). Witnesses 1517-1519 (XFAIL), 1521 (PASS control).
