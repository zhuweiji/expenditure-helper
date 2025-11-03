# Statement Entry Creation API

This API provides endpoints to create ledger entries from processed credit card statements.

## Endpoints

### 1. Prepare Entries (Preview)

**POST** `/api/statements/{statement_id}/prepare-entries`

Preview the ledger entries that will be created from a statement without persisting them to the database.

#### Request Body

```json
{
  "statement_id": 1,
  "credit_card_account_id": 10,
  "default_expense_account_id": 20,
  "bank_account_id": 5,
  "category_mappings": [
    {
      "category": "Food",
      "account_id": 21
    },
    {
      "category": "Transport",
      "account_id": 22
    }
  ]
}
```

#### Parameters

- `statement_id` (required): ID of the statement to process
- `credit_card_account_id` (required): Account ID for the credit card liability account
- `default_expense_account_id` (required): Default account ID for expenses when category is not specified
- `bank_account_id` (optional): Account ID for bank account (used for payments/refunds)
- `category_mappings` (optional): List of category-to-account mappings for categorized expenses

#### Response

```json
{
  "statement_id": 1,
  "statement_filename": "SEP 2025_20251104005515228.pdf",
  "transactions": [
    {
      "description": "PAYPAL *YAOHUBA666 4029357733",
      "transaction_date": "2025-08-06",
      "entries": [
        {
          "account_id": 20,
          "account_name": "General Expenses",
          "entry_type": "debit",
          "amount": 24.31,
          "description": "PAYPAL *YAOHUBA666 4029357733"
        },
        {
          "account_id": 10,
          "account_name": "UOB Credit Card",
          "entry_type": "credit",
          "amount": 24.31,
          "description": "PAYPAL *YAOHUBA666 4029357733"
        }
      ]
    },
    {
      "description": "UOB ONE CASH REBATE BILL REDEMPTION",
      "transaction_date": "2025-09-12",
      "entries": [
        {
          "account_id": 10,
          "account_name": "UOB Credit Card",
          "entry_type": "debit",
          "amount": 100.0,
          "description": "UOB ONE CASH REBATE BILL REDEMPTION"
        },
        {
          "account_id": 5,
          "account_name": "Bank Account",
          "entry_type": "credit",
          "amount": 100.0,
          "description": "UOB ONE CASH REBATE BILL REDEMPTION"
        }
      ]
    }
  ],
  "total_transactions": 2,
  "total_debits": 124.31,
  "total_credits": 124.31,
  "is_balanced": true
}
```

### 2. Create Entries (Persist)

**POST** `/api/statements/{statement_id}/create-entries`

Create and persist ledger entries from a statement to the database.

#### Request Body

Same as the prepare endpoint.

#### Response

```json
{
  "statement_id": 1,
  "transactions_created": 2,
  "message": "Successfully created 2 transactions from statement"
}
```

## Usage Flow

1. **Upload Statement**: Use the `/statements/upload` endpoint to upload a PDF statement
2. **Process Statement**: The statement is automatically processed to extract CSV data
3. **Preview Entries**: Use `/api/statements/{id}/prepare-entries` to preview the ledger entries
4. **Create Entries**: If the preview looks correct, use `/api/statements/{id}/create-entries` to persist them

## Double-Entry Bookkeeping Logic

### Credit Card Purchases (Positive Amounts)
```
Debit:  Expense Account             $XX.XX  (increases expense)
Credit: Credit Card Liability       $XX.XX  (increases liability)
```

### Payments/Refunds (Negative Amounts)
```
Debit:  Credit Card Liability       $XX.XX  (decreases liability)
Credit: Bank Account/Expense        $XX.XX  (decreases asset/reverses expense)
```

## Example: Processing a Statement

### Step 1: Get the statement ID
After uploading and processing a statement, you'll have a statement ID.

### Step 2: Prepare your account IDs
You need to identify:
- Your credit card liability account (e.g., "UOB Credit Card")
- Your default expense account (e.g., "General Expenses")
- Your bank account for payments (e.g., "DBS Bank Account")
- Any category-specific expense accounts

### Step 3: Preview the entries
```bash
curl -X POST "http://localhost:9110/api/statements/1/prepare-entries" \
  -H "Content-Type: application/json" \
  -d '{
    "statement_id": 1,
    "credit_card_account_id": 10,
    "default_expense_account_id": 20,
    "bank_account_id": 5,
    "category_mappings": [
      {"category": "Food", "account_id": 21},
      {"category": "Transport", "account_id": 22}
    ]
  }'
```

### Step 4: Create the entries
If the preview looks good, use the same request but call `/create-entries`:
```bash
curl -X POST "http://localhost:9110/api/statements/1/create-entries" \
  -H "Content-Type: application/json" \
  -d '{
    "statement_id": 1,
    "credit_card_account_id": 10,
    "default_expense_account_id": 20,
    "bank_account_id": 5,
    "category_mappings": [
      {"category": "Food", "account_id": 21},
      {"category": "Transport", "account_id": 22}
    ]
  }'
```

## Error Handling

The API will return appropriate HTTP status codes:

- `400`: Bad request (e.g., statement not processed, unbalanced transactions)
- `404`: Statement or account not found
- `500`: Internal server error

## Notes

- The statement must be processed (have CSV output) before entries can be created
- All account IDs must exist in the database
- Category mappings are optional - unmapped categories will use the default expense account
- The prepare endpoint uses a database savepoint to preview entries without persisting them
- All transactions are validated to ensure debits equal credits
