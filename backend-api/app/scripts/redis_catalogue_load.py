import asyncio
import json
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from redis.commands.search.field import TextField, NumericField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query

# Import corretti dal tuo progetto
from app.core.db_session_manager import DatabaseManager
from app.core.redis_manager import RedisManager
from app.models.db_models import Products

async def setup_search_index(r):
    """This method manage the population and setting of redis index for a fast search and filtering"""
    
    #Here i start the configuration for the redis table by choosing the idx with wich i will identify the table
    index_name = "idx:catalogo"
    
    # Here i "expose" some attributes from the redis content so i can use them for filtering operations, like fitelrging inside a range of prices from 0 to 2. Or for showing products that are from a specific catergoy
    # The tag field allow the redis core to treat the exposed tag as a unit of text as a whole. ex it wont look for mil if the tag is milk he will always look for milk as a whole
    # The numeric field instead allow us to make filtering within a range
    # The text field instead allow us to look for a word a set of character inside a text. 
    # For example milkin inside a description: From the scottish countryside, the best fresh milk. In this contest redis will treath the text as a bundle of token and character and will look inside it the word we were typing in the filter

    schema = (
        TagField("$.sku", as_name="sku"),
        TagField("$.category", as_name="category"),
        NumericField("$.u_price", as_name="u_price"),
        TextField("$.name", as_name="name"),
        TextField("$.description", as_name="description")
    )
    
    try:
        # Here we remove the previous index so we will always have a fresh and consistent index
        try:
            await r.ft(index_name).dropindex(delete_documents=False)
            print("[REDIS] Old index succesfully removed.")
        except Exception:
            print("[REDIS] Unable to remove the old index.")

        # Here i create the phisical index for each product
        await r.ft(index_name).create_index(
            schema, 
            definition=IndexDefinition(prefix=["prod:"], index_type=IndexType.JSON)
        )
        print("[REDIS] New index succesfully created")
        
        # Here we allow a short delay so redis can sync with the new index
        await asyncio.sleep(1) 
        
    except Exception as e:
        print(f"[REDIS] Unable to configure the new index: {e}")

async def load_catalogue():
    """This method manage the reading from the postgres database for populating redis ram database"""
    db_manager = DatabaseManager()
    redis_manager = RedisManager()
    r = redis_manager.client

    try:
        # This call allow us to not block the main process with a syncronous operation, and because we use an asyncronous drive for conneting to the database
        async for session in db_manager.get_session():
            statement = select(Products)
            result = await session.execute(statement)
            products = result.scalars().all()

            print(f"[DEBUG DB] Found {len(products)} records. Loading...")
            
            # Here we are forced to cast the database Decimal type into float so redis and python can work with it. But there are problems, we lose the decimal precision with automatic rounding.
            for product in products:
                p_dict = product.model_dump() 
                p_dict['u_price'] = float(p_dict['u_price'])
                key = f"prod:{product.sku}"
                await r.json().set(key, "$", p_dict)
            
            print(f"[SUCCESS] {len(products)} products loaded on redis.")

        # --- IL PEZZO MANCANTE: LA VERIFICA ---
        print("\n--- Verifying loaded data ---")
        # We search for every key that start with the tag: 'prod:'
        keys = await r.keys("prod:*")
        for k in keys:
            # Here we read the json we just extracted 
            data = await r.json().get(k)
            print(f"VERIFYING -> SKU: {data['sku']} | Nome: {data['name']} | Prezzo: €{data['u_price']}")
        print("---------------------------------------\n")

        # 2. Here we load the index
        await setup_search_index(r)

    except Exception as e:
        print(f"[LOADING ERROR] {e}")

async def find_products(category: Optional[str] = None, max_price: Optional[float] = None, search_term: Optional[str] = None):
    """Search method with Dialect 2."""

    # Dialect 2 allow us to use better searching queries , like filtering with numeric range, vector similarities and a better json handling and better optimization avoid dialect 1 parsing inconsistency
    redis_manager = RedisManager()
    r = redis_manager.client
    
    try:
        query_parts = []
        
        if category:
            query_parts.append(f"@category:{{{category}}}")

        if max_price is not None:
            query_parts.append(f"@u_price:[0 {max_price}]")
            
        if search_term:
            query_parts.append(f"@name:({search_term})")

        final_query = " ".join(query_parts) if query_parts else "*"
        
        print(f"[DEBUG] Executing query: {final_query}")
        
        search_results = await r.ft("idx:catalogo").search(
            Query(final_query).dialect(2)
        )
        
        print(f"\n--- Results ({search_results.total} found) ---")
        for doc in search_results.docs:
            data = json.loads(doc.json)
            print(f"SKU: {data['sku']} | {data['name']} | €{data['u_price']}")
            
    except Exception as e:
        print(f"[SEARCHING ERROR] {e}")
    finally:
        await redis_manager.close()

async def start_worker():
    """This method start the worker and put it in a listening state, wating for an event to be received"""
    manager = RedisManager()
    client = manager.client
    queue_key = "queue:catalogue"
    
    print(f"[*] Worker ready. Checking the queue: {queue_key}")

    while True:
        try:
            # BRPOP: the worker stand here waiting for a message in that specific queue
            result = await client.brpop(queue_key)
            
            if result:
                _, message_text = result
                data = json.loads(message_text)
                print(f"[WORKER] Command received: {data}")
                
                # If the message contain load we procede with the loading of the catalogue
                if data.get("action") == "load":
                    await load_catalogue() 
                
                print("[WORKER] Operation sucesfully completed. Waiting for a new message...")

        except Exception as e:
            print(f"[ERRORE] The worker encountered an error: {e}")
            await asyncio.sleep(2)

if __name__ == "__main__":
    # We run the worker in an async state
    asyncio.run(start_worker())