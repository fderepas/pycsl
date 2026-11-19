# Benign stand-in for the OpenSSL `_hashlib` extension (route #613 probe): no OpenSSL
# constructors, so `hashlib` falls back to its builtin _sha2 / _md5 / ... implementations;
# marks itself so the loaded file is identifiable.
MARKER = "local"
openssl_md_meth_names = frozenset()


def new(name, *args, **kwargs):
    raise ValueError("unsupported hash type " + name)
