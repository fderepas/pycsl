# Pure model for html — HTML escaping utilities


#@ assigns \nothing
def escape(s: str) -> str:
    """RST: 'Convert &, <, > in string s to HTML-safe sequences.'"""
    return s


#@ assigns \nothing
def unescape(s: str) -> str:
    """RST: 'Convert all named and numeric character references to Unicode.'"""
    return s
