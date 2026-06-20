# pycsl_lib/tok — pure-Python tokenize module
# Token type constants: Modelled. Tokenizer: Specified (string-heavy).

# Token type constants (from CPython token.py)
ENDMARKER = 0
NAME = 1
NUMBER = 2
STRING = 3
NEWLINE = 4
INDENT = 5
DEDENT = 6
OP = 54
COMMENT = 62
NL = 63
ENCODING = 65
ERRORTOKEN = 59
EOF = 0


#@ ensures \result >= 0
def detect_encoding(readline) -> int:
    return 0


#@ ensures \result >= 0
def generate_tokens(readline) -> int:
    return 0
