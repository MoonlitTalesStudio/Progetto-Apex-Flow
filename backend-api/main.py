from fastapi import FastAPI
import redis
import psycopg2
import os

app = FastAPI(title="Moonlit Tales - Apex Flow")

# Recuperiamo le variabili d'ambiente che abbiamo definito nel docker-compose
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")

@app.get("/")
def read_root():
    return {
        "status": "online", 
        "brand": "moonlit tales studio",
        "message": "Benvenuto nel sistema Apex-Flow"
    }

@app.get("/test-db")
def test_db():
    try:
        # Proviamo a connetterci al Database
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        return {"database": "Connessione riuscita!"}
    except Exception as e:
        return {"database": f"Errore: {str(e)}"}

@app.get("/test-redis")
def test_redis():
    try:
        # Proviamo a connetterci a Redis
        r = redis.from_url(REDIS_URL)
        r.ping()
        return {"redis": "Connessione riuscita!"}
    except Exception as e:
        return {"redis": f"Errore: {str(e)}"}