class K:
    @staticmethod
    def one() -> int:
        return 2


def swap() -> None:
    from unittest import mock
    mock.patch("zv81a10.b", K).start()
