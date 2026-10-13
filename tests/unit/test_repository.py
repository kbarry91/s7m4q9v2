import asyncio

import pytest

from app.persistence.repository import ReadingRepository


class FailingSession:
    def __init__(self):
        self.rollback_called = False

    def add(self, reading):
        pass

    async def commit(self):
        raise RuntimeError("commit failed")

    async def refresh(self, reading):
        raise AssertionError("refresh should not run after commit failure")

    async def rollback(self):
        self.rollback_called = True


def test_add_rolls_back_when_commit_fails():
    session = FailingSession()
    repository = ReadingRepository(session)

    with pytest.raises(RuntimeError, match="commit failed"):
        asyncio.run(repository.add(object()))

    assert session.rollback_called is True
