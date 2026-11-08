SUBS=[('''    fd, path = tempfile.mkstemp(prefix=".pycsl_", suffix=".mlw")
    os.close(fd)
    return path''','''    fd, path = tempfile.mkstemp(prefix=".pycsl_", suffix=".mlw")
    os.close(fd)
    return fd''')]
