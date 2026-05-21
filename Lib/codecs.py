"""PyCSL mock for Python's codecs module — Encode and decode data and streams."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def encode(obj: int, encoding: int, errors: int) -> int:
    """Mock: Encodes *obj* using the codec registered for *encoding*. *Errors* may be given to set the desired error handling scheme...."""
    return 0

#@ \trusted
#@ ensures \result == 0
def decode(obj: int, encoding: int, errors: int) -> int:
    """Mock: Decodes *obj* using the codec registered for *encoding*. *Errors* may be given to set the desired error handling scheme...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def charmap_build(string: int) -> int:
    """Mock: Return a mapping suitable for encoding with a custom single-byte encoding. Given a :class:`str` *string* of up to 256 ch..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lookup(encoding: int) -> int:
    """Mock: Looks up the codec info in the Python codec registry and returns a :class:`CodecInfo` object as defined below. This func..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getencoder(encoding: int) -> int:
    """Mock: Look up the codec for the given encoding and return its encoder function. Raises a :exc:`LookupError` in case the encodi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getdecoder(encoding: int) -> int:
    """Mock: Look up the codec for the given encoding and return its decoder function. Raises a :exc:`LookupError` in case the encodi..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getincrementalencoder(encoding: int) -> int:
    """Mock: Look up the codec for the given encoding and return its incremental encoder class or factory function. Raises a :exc:`Lo..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getincrementaldecoder(encoding: int) -> int:
    """Mock: Look up the codec for the given encoding and return its incremental decoder class or factory function. Raises a :exc:`Lo..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getreader(encoding: int) -> int:
    """Mock: Look up the codec for the given encoding and return its :class:`StreamReader` class or factory function. Raises a :exc:`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def getwriter(encoding: int) -> int:
    """Mock: Look up the codec for the given encoding and return its :class:`StreamWriter` class or factory function. Raises a :exc:`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register(search_function: int) -> int:
    """Mock: Register a codec search function. Search functions are expected to take one argument, being the encoding name in all low..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def unregister(search_function: int) -> int:
    """Mock: Unregister a codec search function and clear the registry's cache. If the search function is not registered, do nothing...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def open(filename: int, mode: int, encoding: int, errors: int, buffering: int) -> int:
    """Mock: Open an encoded file using the given *mode* and return an instance of :class:`StreamReaderWriter`, providing transparent..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def EncodedFile(file: int, data_encoding: int, file_encoding: int, errors: int) -> int:
    """Mock: Return a :class:`StreamRecoder` instance, a wrapped version of *file* which provides transparent transcoding. The origin..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iterencode(iterator: int, encoding: int, errors: int) -> int:
    """Mock: Uses an incremental encoder to iteratively encode the input provided by *iterator*. *iterator* must yield :class:`str` o..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def iterdecode(iterator: int, encoding: int, errors: int) -> int:
    """Mock: Uses an incremental decoder to iteratively decode the input provided by *iterator*. *iterator* must yield :class:`bytes`..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def readbuffer_encode(buffer: int, errors: int) -> int:
    """Mock: Return a :class:`tuple` containing the raw bytes of *buffer*, a :ref:`buffer-compatible object <bufferobjects>` or :clas..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def register_error(name: int, error_handler: int) -> int:
    """Mock: Register the error handling function *error_handler* under the name *name*. The *error_handler* argument will be called ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def lookup_error(name: int) -> int:
    """Mock: Return the error handler previously registered under the name *name*. Raises a :exc:`LookupError` in case the handler ca..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def strict_errors(exception_: int) -> int:
    """Mock: Implements the ``'strict'`` error handling. Each encoding or decoding error raises a :exc:`UnicodeError`."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ignore_errors(exception_: int) -> int:
    """Mock: Implements the ``'ignore'`` error handling. Malformed data is ignored; encoding or decoding is continued without further..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def replace_errors(exception_: int) -> int:
    """Mock: Implements the ``'replace'`` error handling. Substitutes ``?`` (ASCII character) for encoding errors or ``�`` (U+FFFD, t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def backslashreplace_errors(exception_: int) -> int:
    """Mock: Implements the ``'backslashreplace'`` error handling. Malformed data is replaced by a backslashed escape sequence. On en..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def xmlcharrefreplace_errors(exception_: int) -> int:
    """Mock: Implements the ``'xmlcharrefreplace'`` error handling (for encoding within :term:`text encoding` only). The unencodable ..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def namereplace_errors(exception_: int) -> int:
    """Mock: Implements the ``'namereplace'`` error handling (for encoding within :term:`text encoding` only). The unencodable charac..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def normalize_encoding(encoding: int) -> int:
    """Mock: Normalize encoding name *encoding*. Normalization works as follows: all non-alphanumeric characters except the dot used ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def search_function(encoding: int) -> int:
    """Mock: Search for the codec module corresponding to the given encoding name *encoding*. This function first normalizes the *enc..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def win32_code_page_search_function(encoding: int) -> int:
    """Mock: Search for a Windows code page encoding *encoding* of the form ``cpXXXX``. If the code page is valid and supported, retu..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def nameprep(label_: int) -> int:
    """Mock: Return the nameprepped version of *label*. The implementation currently assumes query strings, so ``AllowUnassigned`` is..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ToASCII(label_: int) -> int:
    """Mock: Convert a label to ASCII, as specified in :rfc:`3490`. ``UseSTD3ASCIIRules`` is assumed to be false."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def ToUnicode(label_: int) -> int:
    """Mock: Convert a label to Unicode, as specified in :rfc:`3490`."""
    return 0
