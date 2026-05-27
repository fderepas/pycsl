"""PyCSL mock for Python's urllib.request module — Extensible library for opening URLs."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def urlopen(url: int, data: int, timeout: int, context: int) -> int:
    """Mock: Open *url*, which can be either a string containing a valid, properly encoded URL, or a :class:`Request` object. *data* ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def install_opener(opener: int) -> int:
    """Mock: Install an :class:`OpenerDirector` instance as the default global opener. Installing an opener is only necessary if you ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def build_opener(handler: int, ___: int) -> int:
    """Mock: Return an :class:`OpenerDirector` instance, which chains the handlers in the order given. *handler*\s can be either inst..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pathname2url(path: int, add_scheme: int) -> int:
    """Mock: Convert the given local path to a ``file:`` URL. This function uses :func:`~urllib.parse.quote` function to encode the p..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def url2pathname(url: int, require_scheme: int, resolve_host: int) -> int:
    """Mock: Convert the given ``file:`` URL to a local path. This function uses :func:`~urllib.parse.unquote` to decode the URL. If ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def getproxies() -> int:
    """Mock: This helper function returns a dictionary of scheme to proxy server URL mappings. It scans the environment for variables..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urlretrieve(url: int, filename: int, reporthook: int, data: int) -> int:
    """Mock: Copy a network object denoted by a URL to a local file. If the URL points to a local file, the object will not be copied..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def urlcleanup() -> int:
    """Mock: Cleans up temporary files that may have been left behind by previous calls to :func:`urlretrieve`."""
    return 0

#@ \trusted
#@ ensures True
def Request(url: int, data: int, headers: int, origin_req_host: int, unverifiable: int, method: int) -> int:
    """Mock: Abstraction of a URL request. url is a string containing a valid URL. data may be a bytes object or an iterable of bytes objects. headers is a dict. method is a string for the HTTP method."""
    return 0
