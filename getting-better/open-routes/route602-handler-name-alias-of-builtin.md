# OPEN ROUTE #602 — A MODULE ALIAS OF A BUILTIN EXCEPTION USED AS A HANDLER (`Err = ValueError; except Err:`) IS LOWERED TO A DISTINCT `exception Err`, SO THE RAISED ValueError ESCAPES IN THE MODEL
**Status: OPEN, Severity 1, PRE-EXISTING (proves at base and at L9). Found by red team rt58.**

## Exemplar (witnesses-r602/)
- d08_handler_name_alias.py: proves; CPython returns 1.
