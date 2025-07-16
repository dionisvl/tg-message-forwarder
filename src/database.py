import os
import asyncio
from typing import List, Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, DateTime, select, delete
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class ExcludedKeyword(Base):
    __tablename__ = "excluded_keywords"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    keyword: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return
            
        db_url = (
            f"postgresql+asyncpg://{os.getenv('DB_USER')}:"
            f"{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:"
            f"{os.getenv('DB_PORT_INTERNAL', '5432')}/{os.getenv('DB_NAME')}"
        )
        
        self.engine = create_async_engine(db_url, echo=False)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
        
        # Create tables if they don't exist
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        self._initialized = True
        logger.info("Database initialized successfully")
    
    async def get_session(self) -> AsyncSession:
        if not self._initialized:
            await self.initialize()
        return self.session_factory()
    
    async def close(self):
        if self.engine:
            await self.engine.dispose()
    
    async def add_keyword(self, keyword: str) -> bool:
        try:
            async with await self.get_session() as session:
                new_keyword = ExcludedKeyword(keyword=keyword.strip())
                session.add(new_keyword)
                await session.commit()
                logger.info(f"Added excluded keyword: {keyword}")
                return True
        except Exception as e:
            logger.error(f"Error adding keyword '{keyword}': {e}")
            return False
    
    async def remove_keyword(self, keyword: str) -> bool:
        try:
            async with await self.get_session() as session:
                stmt = delete(ExcludedKeyword).where(ExcludedKeyword.keyword == keyword.strip())
                result = await session.execute(stmt)
                await session.commit()
                
                if result.rowcount > 0:
                    logger.info(f"Removed excluded keyword: {keyword}")
                    return True
                else:
                    logger.warning(f"Keyword not found: {keyword}")
                    return False
        except Exception as e:
            logger.error(f"Error removing keyword '{keyword}': {e}")
            return False
    
    async def get_all_keywords(self) -> List[str]:
        try:
            async with await self.get_session() as session:
                stmt = select(ExcludedKeyword.keyword).order_by(ExcludedKeyword.created_at)
                result = await session.execute(stmt)
                keywords = result.scalars().all()
                return list(keywords)
        except Exception as e:
            logger.error(f"Error fetching keywords: {e}")
            return []
    
    async def keyword_exists(self, keyword: str) -> bool:
        try:
            async with await self.get_session() as session:
                stmt = select(ExcludedKeyword).where(ExcludedKeyword.keyword == keyword.strip())
                result = await session.execute(stmt)
                return result.first() is not None
        except Exception as e:
            logger.error(f"Error checking keyword existence '{keyword}': {e}")
            return False


# Global database manager instance
db_manager = DatabaseManager()