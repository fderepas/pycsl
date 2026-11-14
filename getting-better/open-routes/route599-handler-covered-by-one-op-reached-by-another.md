# OPEN ROUTE #599 — ROUTE #174 ADMITS `except C` WHEN ANY ONE OPERATION OF THE `try` BODY RAISES C IN THE MODEL; A LATER OPERATION THAT RAISES C ONLY IN CPYTHON REACHES THE HANDLER IN A STATE THE PROOF NEVER CONSIDERED
**Status: OPEN, Severity 1. INTRODUCED by run #7 (L9, lvQ's external-effect raise rows now count as raisers of AttributeError / the OSError family / UnicodeDecodeError / SystemExit / ...; base 73fd1874f refuses the five introduced exemplars via route #174) + one PRE-EXISTING twin (an explicit `raise OSError` as the coverer, c06b, proves at base too). MANDATORY repair (plan §4: introduced by the run).** Found by red team rt58 (scratchpad/rt58/FINDINGS.txt, families.txt, logs/). Related lvQ defect: the PATH-RECEIVER check accepts a `str` receiver for `.mkdir()` / `.write_text()` (CPython raises AttributeError, not in the declared set).

## Exemplars (witnesses-r599/)
- c01_cover_argparse_mkdir_str.py: `argparse.ArgumentParser()` covers `except AttributeError`, then `s.mkdir(...)` with `s: str`; `ensures \result == 0` PROVES at L9, refused at base; CPython returns 1.
- c05 (`b.decode()`), c09 (`q.read_text()`), c12 (`sys.exit(k)`), c14b (`os.path.getsize`): INTRODUCED.
- c06b: PRE-EXISTING twin (explicit raise covers, then `os.path.getsize`).
