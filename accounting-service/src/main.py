from fastapi import FastAPI
from .api import accounts, entries, transactions

app = FastAPI()

app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(entries.router, prefix="/entries", tags=["entries"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Accounting Service API"}