import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.cc_statement_processing.api import create_entries_api, statement_apis
from src.common.logger import get_logger
from src.expenditure_analysis import analytics_api
from src.ledger.api import (
    account_management,
    account_views,
    entries_api,
    transactions_api,
    user_management,
    user_views,
)

load_dotenv()

log = get_logger(__name__)
app = FastAPI()

# Get CORS origins from environment variable, fallback to localhost if not set
# CORS_ORIGINS should be a comma-separated list of origins
cors_origins_str = os.getenv("CORS_ORIGINS", "http://localhost,http://localhost:3000")
if not os.getenv("CORS_ORIGINS"):
    log.warning(
        "CORS_ORIGINS environment variable not set. Defaulting to localhost origins http://localhost and http://localhost:3000"
    )
origins = [origin.strip() for origin in cors_origins_str.split(",") if origin.strip()]

log.info(f"Setting CORS allowed origins to: {origins}")


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(user_management.router, prefix="/users", tags=["users"])
app.include_router(user_views.router, prefix="/users", tags=["users"])

app.include_router(account_management.router, prefix="/accounts", tags=["accounts"])
app.include_router(account_views.router, prefix="/accounts", tags=["accounts"])

app.include_router(entries_api.router, prefix="/entries", tags=["entries"])
app.include_router(
    transactions_api.router, prefix="/transactions", tags=["transactions"]
)
app.include_router(statement_apis.router, prefix="/statements", tags=["statements"])
app.include_router(create_entries_api.router, prefix="/statements", tags=["statements"])

app.include_router(analytics_api.router, prefix="/analytics", tags=["analytics"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Accounting Service API"}


if __name__ == "__main__":
    port = int(os.getenv("app_port", 9110))
    log.info(f"running on port {port}")
    uvicorn.run(
        "src.main:app", host="0.0.0.0", port=port, reload=True, log_level="info"
    )
