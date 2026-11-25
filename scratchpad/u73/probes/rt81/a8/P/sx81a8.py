class K:
    @staticmethod
    def one() -> int:
        return 2


def go() -> None:
    from unittest import mock
    mock.patch("zv81a8.b", K).start()
