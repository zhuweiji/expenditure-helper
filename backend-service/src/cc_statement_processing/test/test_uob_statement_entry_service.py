from pathlib import Path
from pprint import pprint

from src.common.logger import get_logger
from src.ledger.models import Transaction

from ..api.create_entries_utilities import _build_transaction_previews
from ..models.statement_models import Statement, StatementProcessing
from ..services.uob_statement_entry_service import UOBStatementEntryService

log = get_logger(__name__)


def test_build_ledger_entries_data():
    data = UOBStatementEntryService.build_ledger_entries_data(
        csv_content=Path(
            r"D:\projects\expenditure-helper\backend-service\src\cc_statement_processing\test\test_data.csv"
        ).read_text(encoding="utf-8"),
        bank_account_id=1,
        credit_card_account_id=2,
        default_expense_account_id=3,
    )

    pprint(data)

    transactions = UOBStatementEntryService.create_ledger_objects(
        user_id=2, transactions_data=data
    )

    _build_transaction_previews()

    pprint([i.__dict__ for i in transactions])


test_build_ledger_entries_data()
