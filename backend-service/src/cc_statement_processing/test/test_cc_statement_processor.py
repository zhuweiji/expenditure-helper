from pathlib import Path
from pprint import pprint

from dotenv import load_dotenv
from src.common.logger import get_logger

from ..services.cc_statement_processor import CreditCardStatementProcessor

log = get_logger(__name__)


load_dotenv()

data = CreditCardStatementProcessor().ai_extract_csv(
    Path(
        r"D:\projects\expenditure-helper\backend-service\src\cc_statement_processing\test\example2.txt"
    ).read_text(encoding="utf-16")
)

pprint(data)
