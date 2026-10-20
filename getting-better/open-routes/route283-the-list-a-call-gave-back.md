# OPEN ROUTE #283 — A LIST RETURNED BY A USER FUNCTION: append WRITES SLOT 0, len NEVER GROWS, ALIAS AND FRAME LOST
**Status: OPEN (gen #37, 2026-10-20), Severity 1.** Red-team round 7; driver-reproduced at 83aa79bd (p143/p130/p003/p019 rc=0; CPython AssertionError).
Witnesses `witnesses-r283/`. `b = ident(a); b.append(1)` lowers to `let b = (ident a) in b[!b_len] <- 1; b_len := !b_len + 1` with
`b_len` starting at 0 and `len` reading `Array.length`: the append overwrites b[0] (p130 claims b[0]==9, CPython 5), the length is
frozen (p143 len==1, CPython 2), and when `ident` returns its parameter the alias is lost (p003/p012/p017) and an `assigns \nothing`
caller mutates its own parameter through it (p019). Only `append` (+=/extend/insert/pop/clear/remove fail closed, p151-p156). #279's
alias refusal sees name-to-name aliases only. Repair: model or refuse `append` on a list local bound from a call result (length
counter must start at the real length; a returned parameter must be treated as an alias), census every list-from-call binding shape.
