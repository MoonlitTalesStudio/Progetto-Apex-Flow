import redis.asyncio as redis
from typing import Optional
import os

class RedisManager:
    _instance: Optional["RedisManager"] = None
    _client: Optional[redis.Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisManager, cls).__new__(cls)

            cls._client = redis.from_url("redis://redis:6379",decode_responses=True, encoding="utf-8")
        
        return cls._instance
    
    @property
    def client(self) -> redis.Redis:
        return self._client

    async def close(self):
        if self._client:
            await self._client.aclose()
            print("[REDIS] Connection correctly closed.")