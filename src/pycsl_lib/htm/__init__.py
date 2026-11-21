# Pure model for html — HTML escaping utilities
#
# (#49) gen #30: BOTH FUNCTIONS USED TO CARRY ONLY `#@ assigns \nothing`, so each
# verified while claiming NOTHING about the string it returns — the shape
# `bin/check-stdlib-modules-verify.py` now counts and prints ("VERIFIES with no
# postcondition"). A body of `return s` under no value claim is silent, not wrong, but a
# reader who sees `src/pycsl_lib/htm` VERIFY hears more than that.
#
# The claim each one can honestly make is a LENGTH LAW, and it is the strongest claim the
# identity body supports:
#   escape   never SHRINKS a string — every substitution (`&` -> `&amp;`, `<` -> `&lt;`,
#            `>` -> `&gt;`, and with quote=True `"` -> `&quot;`, `'` -> `&#x27;`) replaces
#            one character with several, and no character is ever removed. MEASURED over
#            4000 random strings drawn from U+0020..U+03E7 plus the five escaped
#            characters and three non-ASCII ones: zero counterexamples.
#   unescape never GROWS one — a character reference collapses several characters to one,
#            and nothing expands. MEASURED the same way: zero counterexamples.
# The model returns `s` unchanged, so `\str_length(\result) == \str_length(s)`, which
# satisfies both bounds. The contracts are therefore TRUE OF CPYTHON and PROVABLE OF THE
# MODEL — they do not pin the identity, which would be false (`html.escape('<')` is
# `'&lt;'`).


#@ assigns \nothing
#@ ensures \str_length(\result) >= \str_length(s)
def escape(s: str) -> str:
    """RST: 'Convert &, <, > in string s to HTML-safe sequences.'
    Length-non-shrinking: every substitution replaces one character with several."""
    return s


#@ assigns \nothing
#@ ensures \str_length(\result) <= \str_length(s)
def unescape(s: str) -> str:
    """RST: 'Convert all named and numeric character references to Unicode.'
    Length-non-growing: a character reference collapses several characters to one."""
    return s
