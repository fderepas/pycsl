# ROUTE #59 WITNESSES — STAGED, TO LAND **WITH** THE REPAIR, NOT BEFORE

Seven drivers, numbered 1125-1131 (1124 is the highest id in the corpus at staging time).

**THEY MUST NOT BE COPIED INTO THE CORPUS UNTIL A REPAIR LANDS.** Six of them are
`# pycsl-expected: FAIL` negative witnesses, and at HEAD they all **PROVE** — that is the
route. `bin/run-reference-tests.sh` treats an expected-FAIL driver that starts proving as a
finding in its own right, so adding them now would turn the reference suite red for a defect
that is already recorded in the route file. Land the repair, then the witnesses, in that
order.

    1125  dict_alias_local            b = a;  b[1] = 2;  read a          COVERED by staged patch
    1126  dict_alias_symmetric        b = a;  a[1] = 2;  read b          COVERED
    1127  dict_alias_chained          a -> b -> c;  c[1] = 2;  read a    COVERED
    1128  dict_field_into_local       b = self.d;  b[1] = 2              COVERED
    1129  getter_returns_internal     m = self.get();  m[1] = 2          **NOT COVERED**
    1130  field_store_then_mutate     self.d = p;  p[1] = 2              **NOT COVERED**
    1131  list_control_faithful       the LIST twin of 1125 — POSITIVE control,
                                      expected-PASS, PROVES at HEAD and must keep proving

**1131 IS THE ONE THAT MAKES THE SET HONEST.** Without it the six negatives could all be
satisfied by a repair that simply refused every collection binding, and nothing would notice
that lists — which are CORRECT today — had been broken to get there.

If a repair lands that covers only four, land 1125-1128 and 1131 and hold 1129/1130 until
the generalisation, so the suite stays green and the two open carriers stay visible in the
route file rather than as a red test nobody can act on.

## ADDED gen #5 — AN EIGHTH DRIVER, 1132

    1132  one_local_two_fields        p = {1:1}; self.d = p; self.e = p;
                                      self.d[1] = 2; read self.e[1]      **NOT COVERED**

Found by probing the SIXTH carrier's planned repair before building it. That repair watches
for the stored local being mutated afterwards; here the local is never touched again, so the
guard would not fire. Hold it with 1129/1130 until a repair covers the field store as a
COPY (whichever name is written through), not merely as a later-mutated local.
