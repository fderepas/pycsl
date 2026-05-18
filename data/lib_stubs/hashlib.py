"""PyCSL mock for Python's hashlib module.

Provides trusted stubs for secure hash and message digest algorithms.
Hash object is modelled as a class with digest_size >= 0 and block_size > 0.
"""
_ = 0  # anchor

# ── HashObj class ────────────────────────────────────────────────────

""  # pycsl
#@ class invariant self._digest_size >= 0
#@ class invariant self._block_size >= 1
class HashObj:
    def __init__(self):
        self._digest_size = 1
        self._block_size = 1

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._digest_size
    #@ assigns \nothing
    def digest_size(self) -> int:
        return self._digest_size

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._block_size
    #@ assigns \nothing
    def block_size(self) -> int:
        return self._block_size

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def name(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == 0
    #@ assigns \nothing
    def update(self, data: int) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def digest(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def hexdigest(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def copy(self) -> int:
        return 0

# ── Generic constructor ─────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def new(name: int, data: int) -> int:
    """Mock: generic hash constructor by algorithm name."""
    return 0

# ── Named constructors: MD5, SHA-1, SHA-2 ───────────────────────────

#@ \trusted
#@ ensures \result >= 0
def md5(data: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha1(data: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha224(data: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha256(data: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha384(data: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha512(data: int) -> int:
    return 0

# ── SHA-3 constructors ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def sha3_224(data: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_256(data: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_384(data: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def sha3_512(data: int) -> int:
    return 0

# ── SHAKE constructors ──────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def shake_128(data: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def shake_256(data: int) -> int:
    return 0

# ── BLAKE2 constructors ─────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def blake2b(data: int, digest_size: int, key: int, salt: int, person: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def blake2s(data: int, digest_size: int, key: int, salt: int, person: int) -> int:
    return 0

# ── SHAKE variable-length digest ────────────────────────────────────

#@ \trusted
#@ requires length >= 0
#@ ensures \result >= 0
def shake_digest(h: int, length: int) -> int:
    return 0

#@ \trusted
#@ requires length >= 0
#@ ensures \result >= 0
def shake_hexdigest(h: int, length: int) -> int:
    return 0

# ── Key derivation ──────────────────────────────────────────────────

#@ \trusted
#@ requires iterations >= 1
#@ ensures \result >= 0
def pbkdf2_hmac(hash_name: int, password: int, salt: int, iterations: int, dklen: int) -> int:
    return 0

#@ \trusted
#@ requires n >= 1
#@ requires r >= 1
#@ requires p >= 1
#@ ensures \result >= 0
def scrypt(password: int, salt: int, n: int, r: int, p: int, maxmem: int, dklen: int) -> int:
    return 0

# ── File hashing ────────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def file_digest(fileobj: int, digest: int) -> int:
    return 0

# ── Module data attributes ──────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def algorithms_guaranteed() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def algorithms_available() -> int:
    return 0

# ── BLAKE2 constants ────────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 1
def blake2b_SALT_SIZE() -> int:
    return 1

#@ \trusted
#@ ensures \result >= 1
def blake2s_SALT_SIZE() -> int:
    return 1

#@ \trusted
#@ ensures \result >= 1
def blake2b_PERSON_SIZE() -> int:
    return 1

#@ \trusted
#@ ensures \result >= 1
def blake2s_PERSON_SIZE() -> int:
    return 1

#@ \trusted
#@ ensures \result >= 1
def blake2b_MAX_KEY_SIZE() -> int:
    return 1

#@ \trusted
#@ ensures \result >= 1
def blake2s_MAX_KEY_SIZE() -> int:
    return 1

#@ \trusted
#@ ensures \result >= 1
def blake2b_MAX_DIGEST_SIZE() -> int:
    return 1

#@ \trusted
#@ ensures \result >= 1
def blake2s_MAX_DIGEST_SIZE() -> int:
    return 1
