# Test 7189 -- route #463 (expected FAIL): driver probe (cc1) -- a file with no def / class / loop: the `#@ assert 1 == 2` above its first statement had no header consumer. Measured on 33f7ac681: PROVED; now REFUSED (route #463). (No docstring: a docstring would be the first statement and the line would attach to it.)
# pycsl-expected: FAIL
#@ assert 1 == 2
x = 1
y = x
