"""PyCSL mock for Python's http.client module — HTTP and HTTPS protocol client (requires sockets)."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def parse_headers(fp: int) -> int:
    """Mock: Parse the headers from a file pointer *fp* representing a HTTP request/response. The file has to be a :class:`~io.Buffer..."""
    return 0
