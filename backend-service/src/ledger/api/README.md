# Ledger API Documentation

This is the comprehensive API documentation for the double-entry ledger system. The system provides complete CRUD operations for managing users, accounts, transactions, and entries.

## Table of Contents

1. [User Management API](#user-management-api)
2. [Account Management API](#account-management-api)
3. [Transaction Management API](#transaction-management-api)
4. [Entry Management API](#entry-management-api)
5. [Double-Entry Bookkeeping Concepts](#double-entry-bookkeeping-concepts)
6. [Best Practices](#best-practices)

---

# User Management API

The User API provides complete CRUD operations for managing users in the double-entry ledger system. When a new user is created, a standard chart of accounts is automatically set up.

## User Endpoints

### 1. Create User

**POST** `/users/`

Creates a new user and automatically sets up default accounts for double-entry bookkeeping.

#### Default Accounts Created

- **Assets**: Cash, Bank Account, Accounts Receivable
- **Liabilities**: Accounts Payable, Credit Card
- **Equity**: Owner's Equity, Retained Earnings
- **Revenue**: Sales Revenue, Other Income
- **Expenses**: General Expenses, Food & Dining, Transportation, Utilities

#### Request Body

```json
{
  "username": "john_doe",
  "email": "john.doe@example.com",
  "full_name": "John Doe"
}
```

#### Parameters

- `username` (required): Unique username
- `email` (required): Unique email address (must be valid email format)
- `full_name` (optional): User's full name

#### Response (201 Created)

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-11-04T10:30:00"
}
```

### 2. List Users

**GET** `/users/`

Retrieves a list of all users with optional filtering.

#### Query Parameters

- `skip` (optional, default: 0): Number of records to skip for pagination
- `limit` (optional, default: 100): Maximum number of records to return
- `is_active` (optional): Filter by active status (true/false)

#### Response (200 OK)

```json
[
  {
    "id": 1,
    "username": "john_doe",
    "email": "john.doe@example.com",
    "full_name": "John Doe",
    "is_active": true,
    "created_at": "2025-11-04T10:30:00"
  },
  {
    "id": 2,
    "username": "jane_smith",
    "email": "jane.smith@example.com",
    "full_name": "Jane Smith",
    "is_active": true,
    "created_at": "2025-11-04T11:00:00"
  }
]
```

### 3. Get User by ID

**GET** `/users/{user_id}`

Retrieves a specific user by their ID.

#### Response (200 OK)

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john.doe@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-11-04T10:30:00"
}
```

#### Error Response (404 Not Found)

```json
{
  "detail": "User not found"
}
```

### 4. Get User by Username

**GET** `/users/username/{username}`

Retrieves a specific user by their username.

#### Response (200 OK)

Same as "Get User by ID"

### 5. Update User

**PUT** `/users/{user_id}`

Updates a user's details. Username cannot be changed after creation.

#### Request Body

All fields are optional - only include fields you want to update:

```json
{
  "email": "newemail@example.com",
  "full_name": "John Updated Doe",
  "is_active": false
}
```

#### Response (200 OK)

```json
{
  "id": 1,
  "username": "john_doe",
  "email": "newemail@example.com",
  "full_name": "John Updated Doe",
  "is_active": false,
  "created_at": "2025-11-04T10:30:00"
}
```

### 6. Delete User

**DELETE** `/users/{user_id}`

Permanently deletes a user and all associated data (accounts, transactions, statements).

⚠️ **Warning**: This is a hard delete with cascading effects. All user data will be permanently removed.

#### Response (204 No Content)

No response body on success.

### 7. Get User's Accounts

**GET** `/users/{user_id}/accounts`

Retrieves all accounts belonging to a specific user.

#### Response (200 OK)

```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Cash",
    "account_type": "asset",
    "balance": 1000.50
  },
  {
    "id": 2,
    "user_id": 1,
    "name": "Credit Card",
    "account_type": "liability",
    "balance": 250.00
  }
]
```

### 8. Get User Statistics

**GET** `/users/{user_id}/stats`

Retrieves statistics and summary information for a user.

#### Response (200 OK)

```json
{
  "user_id": 1,
  "username": "john_doe",
  "total_accounts": 22,
  "total_transactions": 150,
  "total_statements": 5,
  "accounts_by_type": {
    "asset": 4,
    "liability": 3,
    "equity": 2,
    "revenue": 3,
    "expense": 10
  }
}
```

---

# Account Management API

The Account API provides CRUD operations for managing accounts within the double-entry ledger system.

## Account Endpoints

### 1. List Accounts by User

**GET** `/accounts/{user_id}`

Retrieves all accounts for a specific user.

#### Response (200 OK)

```json
[
  {
    "id": 1,
    "user_id": 1,
    "name": "Cash",
    "balance": 5000
  },
  {
    "id": 2,
    "user_id": 1,
    "name": "Bank Account",
    "balance": 10000
  }
]
```

### 2. Create Account

**POST** `/accounts/`

Creates a new account for a user.

#### Request Body

```json
{
  "user_id": 1,
  "name": "Savings Account",
  "balance": 0
}
```

#### Parameters

- `user_id` (required): The ID of the user who owns this account
- `name` (required): Account name (must be unique for this user)
- `balance` (required): Initial account balance (in cents/smallest currency unit)

#### Response (200 OK)

```json
{
  "id": 3,
  "user_id": 1,
  "name": "Savings Account",
  "balance": 0
}
```

#### Error Response (400 Bad Request)

```json
{
  "detail": "An account with this name already exists for this user"
}
```

### 3. Get Account by ID

**GET** `/accounts/{account_id}?user_id={user_id}`

Retrieves a specific account by ID.

#### Query Parameters

- `user_id` (required): User ID for authorization

#### Response (200 OK)

```json
{
  "id": 1,
  "user_id": 1,
  "name": "Cash",
  "balance": 5000
}
```

#### Error Response (404 Not Found)

```json
{
  "detail": "Account not found"
}
```

### 4. Update Account

**PUT** `/accounts/{account_id}?user_id={user_id}`

Updates an account's details.

#### Request Body

```json
{
  "name": "Updated Account Name",
  "balance": 15000
}
```

#### Response (200 OK)

```json
{
  "id": 1,
  "user_id": 1,
  "name": "Updated Account Name",
  "balance": 15000
}
```

### 5. Delete Account

**DELETE** `/accounts/{account_id}?user_id={user_id}`

Deletes an account.

#### Response (200 OK)

```json
{
  "id": 1,
  "user_id": 1,
  "name": "Deleted Account",
  "balance": 0
}
```

---

# Transaction Management API

The Transaction API provides CRUD operations for managing transactions and their associated entries.

## Transaction Endpoints

### 1. Create Transaction

**POST** `/transactions/`

Creates a new transaction with optional entries.

#### Request Body

```json
{
  "user_id": 1,
  "description": "Monthly salary",
  "transaction_date": "2025-11-04T10:00:00",
  "reference": "SAL-2025-11",
  "entries": [
    {
      "account_id": 2,
      "amount": 5000.00,
      "entry_type": "debit",
      "description": "Salary received"
    },
    {
      "account_id": 8,
      "amount": 5000.00,
      "entry_type": "credit",
      "description": "Salary income"
    }
  ]
}
```

#### Parameters

- `user_id` (required): ID of the user creating the transaction
- `description` (required): Transaction description
- `transaction_date` (required): Date and time of the transaction
- `reference` (optional): Reference number or code
- `entries` (optional): Array of journal entries

#### Response (200 OK)

```json
{
  "id": 1,
  "user_id": 1,
  "description": "Monthly salary",
  "transaction_date": "2025-11-04T10:00:00",
  "reference": "SAL-2025-11",
  "entries": [
    {
      "id": 1,
      "account_id": 2,
      "amount": 5000.00,
      "entry_type": "debit",
      "description": "Salary received",
      "timestamp": "2025-11-04T10:00:00"
    },
    {
      "id": 2,
      "account_id": 8,
      "amount": 5000.00,
      "entry_type": "credit",
      "description": "Salary income",
      "timestamp": "2025-11-04T10:00:00"
    }
  ]
}
```

### 2. List Transactions

**GET** `/transactions/?user_id={user_id}`

Retrieves all transactions for a specific user.

#### Query Parameters

- `user_id` (required): User ID to filter transactions

#### Response (200 OK)

```json
[
  {
    "id": 1,
    "user_id": 1,
    "description": "Monthly salary",
    "transaction_date": "2025-11-04T10:00:00",
    "reference": "SAL-2025-11",
    "entries": []
  }
]
```

### 3. Get Transaction by ID

**GET** `/transactions/{transaction_id}?user_id={user_id}`

Retrieves a specific transaction with all its entries.

#### Query Parameters

- `user_id` (required): User ID for authorization

#### Response (200 OK)

```json
{
  "id": 1,
  "user_id": 1,
  "description": "Monthly salary",
  "transaction_date": "2025-11-04T10:00:00",
  "reference": "SAL-2025-11",
  "entries": [
    {
      "id": 1,
      "account_id": 2,
      "amount": 5000.00,
      "entry_type": "debit",
      "description": "Salary received",
      "timestamp": "2025-11-04T10:00:00"
    }
  ]
}
```

### 4. Update Transaction

**PUT** `/transactions/{transaction_id}?user_id={user_id}`

Updates a transaction and optionally replaces all its entries.

#### Request Body

```json
{
  "description": "Updated salary transaction",
  "transaction_date": "2025-11-04T10:00:00",
  "reference": "SAL-2025-11-UPDATED",
  "entries": [
    {
      "account_id": 2,
      "amount": 5500.00,
      "entry_type": "debit",
      "description": "Updated salary"
    },
    {
      "account_id": 8,
      "amount": 5500.00,
      "entry_type": "credit",
      "description": "Updated salary income"
    }
  ]
}
```

#### Parameters

- `entries` (optional): If provided, replaces all existing entries. If omitted, existing entries are preserved.

#### Response (200 OK)

Returns the updated transaction with entries.

### 5. Delete Transaction

**DELETE** `/transactions/{transaction_id}?user_id={user_id}`

Deletes a transaction and all associated entries.

#### Response (200 OK)

```json
{
  "detail": "Transaction deleted"
}
```

---

# Entry Management API

The Entry API provides CRUD operations for individual ledger entries (debits and credits).

## Entry Endpoints

### 1. Create Entry

**POST** `/entries/`

Creates a new ledger entry.

#### Request Body

```json
{
  "account_id": 1,
  "amount": 100.50,
  "entry_type": "debit",
  "description": "Coffee purchase"
}
```

#### Parameters

- `account_id` (required): ID of the account
- `amount` (required): Entry amount
- `entry_type` (required): Either "debit" or "credit"
- `description` (optional): Entry description

#### Response (201 Created)

```json
{
  "id": 1,
  "account_id": 1,
  "amount": 100.50,
  "entry_type": "debit",
  "description": "Coffee purchase",
  "timestamp": "2025-11-04T10:30:00"
}
```

### 2. List Entries

**GET** `/entries/`

Retrieves entries with optional filtering.

#### Query Parameters

- `skip` (optional, default: 0): Number of records to skip
- `limit` (optional, default: 100): Maximum records to return
- `account_id` (optional): Filter by specific account

#### Response (200 OK)

```json
[
  {
    "id": 1,
    "account_id": 1,
    "amount": 100.50,
    "entry_type": "debit",
    "description": "Coffee purchase",
    "timestamp": "2025-11-04T10:30:00"
  },
  {
    "id": 2,
    "account_id": 5,
    "amount": 100.50,
    "entry_type": "credit",
    "description": "Coffee purchase",
    "timestamp": "2025-11-04T10:30:00"
  }
]
```

### 3. Get Entry by ID

**GET** `/entries/{entry_id}`

Retrieves a specific entry.

#### Response (200 OK)

```json
{
  "id": 1,
  "account_id": 1,
  "amount": 100.50,
  "entry_type": "debit",
  "description": "Coffee purchase",
  "timestamp": "2025-11-04T10:30:00"
}
```

#### Error Response (404 Not Found)

```json
{
  "detail": "Entry not found"
}
```

### 4. Update Entry

**PUT** `/entries/{entry_id}`

Updates an existing entry.

#### Request Body

```json
{
  "account_id": 1,
  "amount": 125.00,
  "entry_type": "debit",
  "description": "Updated coffee purchase"
}
```

#### Response (200 OK)

```json
{
  "id": 1,
  "account_id": 1,
  "amount": 125.00,
  "entry_type": "debit",
  "description": "Updated coffee purchase",
  "timestamp": "2025-11-04T10:30:00"
}
```

### 5. Delete Entry

**DELETE** `/entries/{entry_id}`

Deletes an entry.

#### Response (204 No Content)

No response body on success.

---

# Usage Examples

## User Management Examples

### Create a New User

```bash
curl -X POST "http://localhost:9110/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john.doe@example.com",
    "full_name": "John Doe"
  }'
```

### List All Active Users

```bash
curl -X GET "http://localhost:9110/users/?is_active=true"
```

### Get User Statistics

```bash
curl -X GET "http://localhost:9110/users/1/stats"
```

## Account Management Examples

### Create a New Account

```bash
curl -X POST "http://localhost:9110/accounts/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "name": "Savings Account",
    "balance": 0
  }'
```

### List User's Accounts

```bash
curl -X GET "http://localhost:9110/accounts/1"
```

### Update Account Balance

```bash
curl -X PUT "http://localhost:9110/accounts/1?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Cash",
    "balance": 10000
  }'
```

## Transaction Management Examples

### Create a Complete Transaction

```bash
curl -X POST "http://localhost:9110/transactions/" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "description": "Grocery shopping",
    "transaction_date": "2025-11-04T14:30:00",
    "reference": "GRO-001",
    "entries": [
      {
        "account_id": 12,
        "amount": 150.00,
        "entry_type": "debit",
        "description": "Food & Dining expense"
      },
      {
        "account_id": 1,
        "amount": 150.00,
        "entry_type": "credit",
        "description": "Paid from cash"
      }
    ]
  }'
```

### List User's Transactions

```bash
curl -X GET "http://localhost:9110/transactions/?user_id=1"
```

## Entry Management Examples

### Create a Single Entry

```bash
curl -X POST "http://localhost:9110/entries/" \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "amount": 50.00,
    "entry_type": "debit",
    "description": "ATM withdrawal"
  }'
```

### List Entries for an Account

```bash
curl -X GET "http://localhost:9110/entries/?account_id=1&limit=50"
```

---

# Error Handling

The API returns standard HTTP status codes:

- `200`: Success (GET, PUT)
- `201`: Created (POST)
- `204`: No Content (DELETE)
- `400`: Bad Request (validation errors, duplicate entries)
- `404`: Not Found (resource doesn't exist)
- `500`: Internal Server Error

## Common Error Responses

### Duplicate Username

```json
{
  "detail": "Username already exists"
}
```

### Duplicate Email

```json
{
  "detail": "Email already exists"
}
```

### Duplicate Account Name

```json
{
  "detail": "An account with this name already exists for this user"
}
```

### Resource Not Found

```json
{
  "detail": "User not found"
}
```

```json
{
  "detail": "Account not found"
}
```

```json
{
  "detail": "Transaction not found"
}
```

```json
{
  "detail": "Entry not found"
}
```

---

# Double-Entry Bookkeeping Concepts

## Account Types

1. **Assets**: Increase with debits, decrease with credits
   - Example: Cash, Bank Account, Accounts Receivable

2. **Liabilities**: Increase with credits, decrease with debits
   - Example: Credit Card, Loans, Accounts Payable

3. **Equity**: Increase with credits, decrease with debits
   - Represents owner's stake in the business

4. **Revenue**: Increase with credits, decrease with debits
   - Example: Salary Income, Interest Income

5. **Expenses**: Increase with debits, decrease with credits
   - Example: Food, Transportation, Utilities

## Basic Equation

```
Assets = Liabilities + Equity
```

## Example Transactions

### Recording a Salary Payment

**Transaction**: Receive $5,000 salary

```json
{
  "description": "Monthly salary",
  "entries": [
    {
      "account": "Bank Account (Asset)",
      "amount": 5000,
      "entry_type": "debit"
    },
    {
      "account": "Salary Income (Revenue)",
      "amount": 5000,
      "entry_type": "credit"
    }
  ]
}
```

### Recording a Credit Card Purchase

**Transaction**: Buy groceries for $50 with credit card

```json
{
  "description": "Grocery shopping",
  "entries": [
    {
      "account": "Food & Dining (Expense)",
      "amount": 50,
      "entry_type": "debit"
    },
    {
      "account": "Credit Card (Liability)",
      "amount": 50,
      "entry_type": "credit"
    }
  ]
}
```

### Paying Off Credit Card

**Transaction**: Pay $50 from bank to credit card

```json
{
  "description": "Credit card payment",
  "entries": [
    {
      "account": "Credit Card (Liability)",
      "amount": 50,
      "entry_type": "debit"
    },
    {
      "account": "Bank Account (Asset)",
      "amount": 50,
      "entry_type": "credit"
    }
  ]
}
```

---

# Best Practices

## User Management

1. **Create users first**: Always create a user before attempting to create accounts or transactions
2. **Use username for lookups**: Usernames are indexed and unique, making them efficient for lookups
3. **Soft delete when possible**: Use `is_active=false` instead of hard deletes to preserve historical data
4. **Check statistics**: Use the `/users/{id}/stats` endpoint to get an overview before performing operations

## Account Management

1. **Use descriptive names**: Give accounts clear, meaningful names
2. **Unique names per user**: Each user can have accounts with the same name, but names must be unique within a user's account set
3. **Balance in smallest units**: Store balances in cents (or smallest currency unit) to avoid floating-point issues

## Transaction Management

1. **Always balance entries**: Total debits must equal total credits in every transaction
2. **Use references**: Add reference numbers for tracking and reconciliation
3. **Descriptive transactions**: Write clear descriptions for audit trails
4. **Transaction date accuracy**: Use accurate transaction dates for proper financial reporting

## Entry Management

1. **Link entries to transactions**: Prefer creating entries as part of transactions rather than standalone
2. **Correct entry types**: Use "debit" to increase assets/expenses, "credit" to increase liabilities/revenue/equity
3. **Detailed descriptions**: Add descriptions to entries for clarity

## General

1. **Backup before deleting**: Hard deletes are permanent and cascade to all related data
2. **Validate balances**: Regularly check that total debits equal total credits
3. **Use pagination**: When listing large datasets, use `skip` and `limit` parameters
4. **Error handling**: Always check for error responses and handle them appropriately

---

# Integration Workflow

## Typical Setup Flow

1. **Create a user**
   ```
   POST /users/
   ```

2. **Verify default accounts were created**
   ```
   GET /users/{id}/accounts
   ```

3. **Create custom accounts (if needed)**
   ```
   POST /accounts/
   ```

4. **Record transactions**
   ```
   POST /transactions/
   ```

5. **Review statistics**
   ```
   GET /users/{id}/stats
   ```

## Multi-User Support

This system supports multiple users, each with their own isolated set of:
- Accounts (enforced by unique constraint on `user_id` + `account_name`)
- Transactions (filtered by `user_id`)
- Credit card statements (associated with `user_id`)

Users cannot access or modify each other's data due to foreign key constraints and proper filtering.

---

# Additional Resources

- Statement Processing API: `/statements/` (see `cc_statement_processing` module)
- Entry Creation from Statements: See statement entry creation API
- Database Migrations: Use Alembic for schema changes
- Logging: Application logs available in `app.log`
