import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from src.cc_statement_processing.api import create_entries_api, statement_apis
from src.common.logger import get_logger
from src.ledger.api import accounts, entries, transactions, users

load_dotenv()

log = get_logger(__name__)
app = FastAPI()

app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(accounts.router, prefix="/accounts", tags=["accounts"])
app.include_router(entries.router, prefix="/entries", tags=["entries"])
app.include_router(transactions.router, prefix="/transactions", tags=["transactions"])
app.include_router(statement_apis.router, prefix="/statements", tags=["statements"])
app.include_router(
    create_entries_api.router,
    prefix="/import-ledger-entries",
    tags=["import-ledger-entries"],
)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Accounting Service API"}


if __name__ == "__main__":
    port = int(os.getenv("app_port", 9110))
    log.info(f"running on port {port}")
    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=port, reload=True, log_level="info"
    )
