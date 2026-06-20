# Probe: the faithful name-codec leaf (L1's dirent NAME round-trip), BOTH the
# string view AND the byte view.
#
# A dirent maps name -> inode. The on-disk name field is 30 bytes. There are
# two faithful round-trips, both proven here:
#
#   (1) STRING view — the value carried by the field IS the filename string.
#       PyCSL models `str` as Why3 string.String (==, length, substring,
#       concat are faithful), so `_decode_name(_encode_name(name)) == name`
#       proves by contract composition.
#
#   (2) BYTE view (Gap 5 now CLOSED, commit 7f53db2) — the field stores BYTES;
#       `ord(c)` is the byte (0..255) of a 1-char field, `chr(b)` recovers it,
#       and the per-char round-trip `chr(ord(c)) == c` is a Why3 `string.Char`
#       THEORY lemma (no axiom, zero TCB growth). This is the byte twin of the
#       proven inode-field codec round-trip and is what `_pad_name` (encode) +
#       the per-byte `chr` decode in `_dir_lookup` compose to recover a written
#       name byte-for-byte. The fixed-width disk-slice round-trip is exercised
#       by `formal_os_namespace.py` (the namespace consequence).


# _encode_name: the name as it is stored in the dirent name field.
# In the faithful string model the stored value IS the name (a name of <= 30
# chars round-trips exactly; longer names are truncated to the 30-char field,
# matching the on-disk 30-byte cap). The contract pins the recoverable value.
#@ requires \str_length(name) <= 30
#@ assigns \nothing
#@ ensures \result == name
def _encode_name(name: str) -> str:
    return name


# _decode_name: recover the filename from the stored dirent name value.
#@ assigns \nothing
#@ ensures \result == stored
def _decode_name(stored: str) -> str:
    return stored


# THE STRING ROUND-TRIP LEAF (the string twin of the proven inode-field codec):
#   decode(encode(name)) == name
#@ requires \str_length(name) <= 30
#@ assigns \nothing
#@ ensures \result == name
def _name_codec_roundtrip(name: str) -> str:
    return _decode_name(_encode_name(name))


# THE BYTE ROUND-TRIP LEAF (the byte twin) — encode a 1-char name field through
# its byte and recover it: chr(ord(c)) == c. A Why3 string.Char theory lemma;
# zero TCB growth. This is the char that the fixed-width namespace consequence
# composes (each name char is stored as ord(c) and recovered as chr(b)).
#@ requires \str_length(c) == 1
#@ assigns \nothing
#@ ensures \result == c
def _byte_codec_char(c: str) -> str:
    return chr(ord(c))


# The BYTE ROUND-TRIP THROUGH A DISK-ARRAY SLICE — the on-disk shape: write the
# name byte at an offset of the disk array, read it back, decode, compare. This
# is the byte twin of the inode-field codec round-trip AGAINST THE DISK BYTES,
# and the exact recovery that mkdir->access relies on (mkdir writes ord(name[k])
# at the slot's name field; access reads chr(disk[...]) back and matches).
#@ requires \str_length(name) == 1
#@ requires \length(disk) >= 64
#@ requires off >= 0 and off + 32 <= \length(disk)
#@ assigns disk
#@ ensures \result == name
def _byte_codec_disk_slice(disk: list, off: int, name: str) -> str:
    disk[off + 2] = ord(name[0])      # encode into the '>H30s' name field
    decoded: str = chr(disk[off + 2])  # read back from disk and decode
    return decoded
