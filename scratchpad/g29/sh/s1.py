r"""G29 SH1 — a local `def val` FOLLOWED by `from lib import val`: Python binds the import."""
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def val() -> int:
    return 1


from multi_file_lib.shlib import val  # noqa: E402,F811


#@ ensures \result == 1
def probe() -> int:
    return val()


if __name__ == "__main__":
    print("CPython:", probe())
