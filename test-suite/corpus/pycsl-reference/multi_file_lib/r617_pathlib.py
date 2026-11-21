"""Route #617 helper (lvZ, run #8): imported Path-returning / Path-taking functions and a Path
type alias, for witnesses 10246-10251."""
from pathlib import Path
from typing import TypeAlias

Fp: TypeAlias = Path


def mk(s: str) -> Path:
    return Path(s)


def ident(p: Path) -> Path:
    return p


def keep(x: str) -> str:
    return x


def name_of(p: Path) -> str:
    return p.name
