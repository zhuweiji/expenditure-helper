# README.md

# Accounting Service

This is a minimal double entry accounting system built with FastAPI and SQLAlchemy. The service provides APIs for managing accounts, entries, and transactions, adhering to the principles of double entry accounting.

## Project Structure

```
accounting-service
├── src
│   ├── api
│   ├── models
│   ├── schemas
│   ├── database.py
│   └── main.py
├── tests
├── requirements.txt
└── pyproject.toml
```

## Features

- Manage accounts: Create, retrieve, update, and delete accounts.
- Manage entries: Create, retrieve, update, and delete journal entries.
- Manage transactions: Create, retrieve, update, and delete transactions.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd accounting-service
   ```

2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:

```
uvicorn src.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## Testing

To run the tests, use the following command:

```
pytest
```

## License

This project is licensed under the MIT License.