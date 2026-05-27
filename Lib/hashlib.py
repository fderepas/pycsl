"""PyCSL mock for Python's hashlib module — Secure hash and message digest algorithms."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def new(name: int, data: int, usedforsecurity: int) -> int:
    """Mock: Is a generic constructor that takes the string *name* of the desired algorithm as its first parameter.  It also exists t..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def md5(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: md5"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha1(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: sha1"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha224(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: sha224"""
    return 0

#@ \trusted
#@ ensures True
def sha256(data: int, usedforsecurity: int) -> int:
    """Mock: Return a SHA-256 hash object for computing a cryptographic digest of data."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha384(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: sha384"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha512(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: sha512"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_224(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: sha3_224"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_256(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: sha3_256"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_384(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: sha3_384"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_512(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: sha3_512"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shake_128(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: shake_128"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def shake_256(data: int, usedforsecurity: int) -> int:
    """Mock: Mock: shake_256"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def file_digest(fileobj: int, digest: int) -> int:
    """Mock: Return a digest object that has been updated with contents of file object. *fileobj* must be a file-like object opened f..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def pbkdf2_hmac(hash_name: int, password: int, salt: int, iterations: int, dklen: int) -> int:
    """Mock: The function provides PKCS#5 password-based key derivation function 2. It uses HMAC as pseudorandom function. The string..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def scrypt(password: int, salt: int, n: int, r: int, p: int, maxmem: int, dklen: int) -> int:
    """Mock: The function provides scrypt password-based key derivation function as defined in :rfc:`7914`. *password* and *salt* mus..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2b(data: int, digest_size: int, key: int, salt: int, __person: int, fanout: int, depth: int) -> int:
    """Mock: Mock: blake2b"""
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2s(data: int, digest_size: int, key: int, salt: int, __person: int, fanout: int, depth: int) -> int:
    """Mock: Mock: blake2s"""
    return 0
