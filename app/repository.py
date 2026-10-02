"""Data-access layer: the only place that talks to the database."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Reading


class ReadingRepository:
    """Persists and retrieves Reading rows."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, reading: Reading) -> Reading:
        self.session.add(reading)
        await self.session.commit()
        await self.session.refresh(reading)
        
        return reading
