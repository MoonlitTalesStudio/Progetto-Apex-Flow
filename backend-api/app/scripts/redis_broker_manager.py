import asyncio
import json
from typing import Dict, Any
from app.core.redis_manager import RedisManager

# Method for pushing an event
async def send_event(queue_name: str, data: Dict[str, Any]) -> None:

    manager = RedisManager()
    client = manager.client 
    
    # Since redis manage only strings we dump the dict as plain text
    payload = json.dumps(data)
    
    # LPUSH: allow us to push the event in the queue with name 'queue:channel_name'
    await client.lpush(f"queue:{queue_name}", payload)
    print(f"[PRODUCER] Event appended in the queue {queue_name}: {payload}")


async def run_test():
    print("[TEST] Pushing events...")
    
    # Messaggio 1
    await send_event("catalogue", {"action": "load", "info": "First event"})
    # Messaggio 2
    await send_event("catalogue", {"action": "load", "info": "Second event"})
    
    print("[TEST] Events sent, now the listener will react")

if __name__ == "__main__":
    asyncio.run(run_test())