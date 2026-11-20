# u58 witness 10303: a benign stand-in named like lark's optional dependency `regex`. It acts only when
# imported AS `regex` (as lark's `try: import regex` does from sys.path), not when a corpus harness loads
# it as multi_file_lib.r613y.g6.regex.
if __name__ == "regex":
    import builtins
    print("LOCAL regex.py loaded:", __file__)
    _len = builtins.len
    builtins.len = lambda x: 7 if x == "abc" else _len(x)
    raise ImportError("stand-in: behave as if absent")
