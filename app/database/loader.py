from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

engine = create_async_engine(url=settings.database_url)
sessionmaker = async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
