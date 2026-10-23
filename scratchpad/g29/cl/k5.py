r"""G29 CL-K5 — closure / late binding (claim != truth; CPython 2)."""
_ = 0  # anchor


#@ ensures \result != 2
def probe() -> int:
    xs = [1]
    def app() -> None:
        xs.append(2)
    app()
    return len(xs)


if __name__ == "__main__":
    print("CPython:", probe())
