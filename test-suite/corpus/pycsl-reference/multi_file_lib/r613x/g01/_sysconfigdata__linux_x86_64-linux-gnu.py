# run #8 u55 witness 10223 (review rt66 g01): a benign stand-in for sysconfig's build data, which
# sysconfig imports by a COMPUTED name (`_sysconfigdata_<abiflags>_<platform>_<multiarch>`).
print("LOCAL _sysconfigdata loaded:", __file__)
build_time_vars = {"TZPATH": "/nonexistent/local-tzpath"}
