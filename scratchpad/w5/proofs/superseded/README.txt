These three runs were KILLED, not failed. They were proving mirror content that a later
#32 increment superseded before they finished, so they were terminated (rc=137 / rc=15)
and re-queued against the final tree. Their replacements are the `*_F.log` / `*_G.log`
runs in the parent directory. `module6_whyml_statements_2.log` had in fact already
reported `Verification SUCCESS` (922 goals) for the getattr-scalar capability before the
kill; `module6_whyml_expressions_2.log` likewise (1069 goals).
