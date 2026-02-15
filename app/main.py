from fastapi import FastAPI
from app.endpoints import router

app = FastAPI(
    title="Aegis Agent Marketplace POC",
    description="A proof-of-concept for a decentralized agent marketplace.",
)

app.include_router(router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Aegis Agent Marketplace POC"}
