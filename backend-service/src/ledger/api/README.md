# User Management API

The User API provides complete CRUD operations for managing users in the double-entry ledger system. When a new user is created, a standard chart of accounts is automatically set up.

## Endpoints

### 1. Create User

**POST** `/users/`

Creates a new user and automatically sets up default accounts for double-entry bookkeeping.

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

#### Default Accounts Created

When a user is created, the following accounts are automatically set up:

**Assets** (Things you own):
- Cash
- Bank Account
- Savings Account
- Accounts Receivable

**Liabilities** (Things you owe):
- Credit Card
- Accounts Payable
- Loans Payable

**Equity** (Net worth):
- Owner's Equity
- Retained Earnings

**Revenue** (Income):
- Salary Income
- Interest Income
- Other Income

**Expenses** (Money spent):
- General Expenses
- Food & Dining
- Groceries
- Transportation
- Utilities
- Entertainment
- Healthcare
- Shopping
- Housing/Rent
- Insurance

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

## Usage Examples

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

### Get User by Username

```bash
curl -X GET "http://localhost:9110/users/username/john_doe"
```

### Update User Email

```bash
curl -X PUT "http://localhost:9110/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.new@example.com"
  }'
```

### Deactivate User (Soft Delete)

```bash
curl -X PUT "http://localhost:9110/users/1" \
  -H "Content-Type: application/json" \
  -d '{
    "is_active": false
  }'
```

### Get User's Accounts

```bash
curl -X GET "http://localhost:9110/users/1/accounts"
```

### Get User Statistics

```bash
curl -X GET "http://localhost:9110/users/1/stats"
```

### Delete User (Hard Delete)

```bash
curl -X DELETE "http://localhost:9110/users/1"
```

## Error Handling

The API returns standard HTTP status codes:

- `200`: Success (GET, PUT)
- `201`: Created (POST)
- `204`: No Content (DELETE)
- `400`: Bad Request (validation errors, duplicate username/email)
- `404`: Not Found (user doesn't exist)
- `500`: Internal Server Error

### Common Error Responses

#### Duplicate Username

```json
{
  "detail": "Username already exists"
}
```

#### Duplicate Email

```json
{
  "detail": "Email already exists"
}
```

#### User Not Found

```json
{
  "detail": "User not found"
}
```

## Double-Entry Bookkeeping Concepts

### Account Types

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

### Basic Equation

```
Assets = Liabilities + Equity
```

### Example Transactions

**Recording a salary payment:**
```
Debit:  Bank Account (Asset)        $5,000
Credit: Salary Income (Revenue)     $5,000
```

**Recording a credit card purchase:**
```
Debit:  Food & Dining (Expense)     $50
Credit: Credit Card (Liability)     $50
```

**Paying off credit card:**
```
Debit:  Credit Card (Liability)     $50
Credit: Bank Account (Asset)        $50
```

## Integration with Other APIs

After creating a user, you can:

1. **Create custom accounts** using `/accounts/` endpoints
2. **Record transactions** using `/transactions/` endpoints
3. **Upload credit card statements** using `/statements/upload`
4. **Process statements into ledger entries** using the statement entry creation API

## Best Practices

1. **Create users first**: Always create a user before attempting to create accounts or transactions
2. **Use username for lookups**: Usernames are indexed and unique, making them efficient for lookups
3. **Soft delete when possible**: Use `is_active=false` instead of hard deletes to preserve historical data
4. **Check statistics**: Use the `/users/{id}/stats` endpoint to get an overview before performing operations
5. **Backup before deleting**: Hard deletes are permanent and cascade to all related data

## Multi-User Support

This system supports multiple users, each with their own isolated set of:
- Accounts
- Transactions
- Credit card statements

Users cannot access or modify each other's data due to the foreign key constraints and unique constraints on `(user_id, account_name)`.
