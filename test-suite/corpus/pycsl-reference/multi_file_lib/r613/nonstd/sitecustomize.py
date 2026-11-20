# route #613 witness: a local module named `sitecustomize`. Not a standard-library name, but one
# the stdlib itself imports (`site.py`: `import sitecustomize`, at interpreter startup), so with
# this root on sys.path CPython runs this file and no model of pycsl assumes it.
MARKER = "local"
print("LOCAL sitecustomize.py loaded:", __file__)
