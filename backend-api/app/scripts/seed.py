import asyncio
from app.core.db_session_manager import DatabaseManager
from app.models.db_models import Products 

async def add_product():
    products = [Products(sku="mozz-sl",name="Mozzarella senza lattosio",description="Classica mozzarella senza lattosio",category="Latticini",u_price=1.15,stock_qnt=20),
                Products(sku="mozz-m",name="Mozzarella",description="Classica mozzarella",category="Latticini",u_price=0.99,stock_qnt=50),
                Products(sku="gran",name="Pezzo di grana pandano",description="Pezzo di grana padano da 100g",category="Latticini",u_price=3.15,stock_qnt=10)]
    
    db_manager = DatabaseManager()

    try:
        async for session in db_manager.get_session():
            for product in products:
                session.add(product)
            
            await session.commit()

    except Exception as e:
        print(f"\n[ERRORE] Test failed: {e}")
        print("Check database status...")


if __name__ == "__main__":
    asyncio.run(add_product())