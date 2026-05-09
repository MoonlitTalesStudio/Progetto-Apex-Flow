from fastapi import FastAPI

app = FastAPI(title="Moonlit Tales - Apex Flow")


@app.get("/")
def read_root():
    return {
        "status": "online", 
        "brand": "moonlit tales studio",
        "message": "Benvenuto nel sistema Apex-Flow"
    }

