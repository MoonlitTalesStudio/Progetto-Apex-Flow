import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, text
from app.models.db_models import Products, Orders, Users, OrderItem

class DatabaseManager:
    _instance: Optional["DatabaseManager"] = None
    _engine = None
    _async_session_maker = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            
            # Stringa di connessione per ambiente Docker
            postgresql_url = "postgresql+asyncpg://moonlit:moonlit_tales@db:5432/apex_database"
            
            # 1. Creazione Engine Asincrono
            cls._engine = create_async_engine(
                postgresql_url, 
                echo=True,       # Mostra l'SQL nel terminale (ottimo per debug)
                future=True
            )
            
            # 2. Produttore di sessioni
            cls._async_session_maker = sessionmaker(
                cls._engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
        return cls._instance

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Here we use an asyncronous session generator
        The block 'async with' garant us a safe and automatic session termination.
        """
        if self._async_session_maker is None:
            raise RuntimeError("DatabaseManager not initialized.")
            
        async with self._async_session_maker() as session:
            yield session

    async def create_tables(self):
        """This manage the creation of the tables in the postgres database """
        async with self._engine.begin() as conn:
            # 1. If the schema doesnt exist i create it
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS b2b"))
            
            # 2. Create the tables
            # run_sync will use the models definition that point to the schema 'b2b'
            await conn.run_sync(SQLModel.metadata.create_all)

# --- Test Logic ---
async def test_connection():
    """This method check if the connection get correctly enstablished and that the tables are correctly created"""
    print("\n[TEST] Inizio procedura di verifica...")
    db_manager = DatabaseManager()
    
    try:
        print("[TEST] Attempting table creation...")
        await db_manager.create_tables()
        print("[TEST] Tables correctly created or alredy existent.")

        print("[TEST] Attempt session opening for future queries...")
        async for session in db_manager.get_session():
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            print(f"[TEST] Result: Query (SELECT 1): {value}")
            
        print("[TEST] Everything work as intended")

    except Exception as e:
        print(f"\n[ERRORE] Test failed: {e}")
        print("Check if the database is reachable or that the credentials are correct.")

if __name__ == "__main__":
    asyncio.run(test_connection())