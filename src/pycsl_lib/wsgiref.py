"""PyCSL mock for Python's wsgiref module — WSGI Utilities and Reference Implementation."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def guess_scheme(environ: int) -> int:
    """Mock: Return a guess for whether ``wsgi.url_scheme`` should be 'http' or 'https', by checking for a ``HTTPS`` environment vari..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def request_uri(environ: int, include_query: int) -> int:
    """Mock: Return the full request URI, optionally including the query string, using the algorithm found in the 'URL Reconstruction..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def application_uri(environ: int) -> int:
    """Mock: Similar to :func:`request_uri`, except that the ``PATH_INFO`` and ``QUERY_STRING`` variables are ignored.  The result is..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shift_path_info(environ: int) -> int:
    """Mock: Shift a single name from ``PATH_INFO`` to ``SCRIPT_NAME`` and return the name. The *environ* dictionary is *modified* in..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def setup_testing_defaults(environ: int) -> int:
    """Mock: Update *environ* with trivial defaults for testing purposes. This routine adds various parameters required for WSGI, inc..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def is_hop_by_hop(header_name: int) -> int:
    """Mock: Return ``True`` if 'header_name' is an HTTP/1.1 'Hop-by-Hop' header, as defined by :rfc:`2616`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def make_server(host: int, port: int, app: int, server_class: int, handler_class: int) -> int:
    """Mock: Create a new WSGI server listening on *host* and *port*, accepting connections for *app*.  The return value is an instan..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def demo_app(environ: int, start_response: int) -> int:
    """Mock: This function is a small but complete WSGI application that returns a text page containing the message 'Hello world!' an..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def validator(application: int) -> int:
    """Mock: Wrap *application* and return a new WSGI application object.  The returned application will forward all requests to the ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def read_environ() -> int:
    """Mock: Transcode CGI variables from ``os.environ`` to :pep:`3333` 'bytes in unicode' strings, returning a new dictionary.  This..."""
    return 0
