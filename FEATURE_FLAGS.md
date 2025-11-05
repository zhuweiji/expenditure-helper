# Feature Flags Documentation

This document describes the feature flags used in the Expenditure Helper application.

## Mock Data Feature Flag

### Overview

The mock data feature flag controls whether users see mock/demo data or real data from the API. This is useful for:

- **Disabling mock data by default** to prevent users from seeing example transactions
- **Allowing test/demo users** to view mock data while regular users see real data only
- **Development and testing** when setting the flag to `true` for everyone

### Default Behavior

- **Mock data is DISABLED by default** - users will not see mock transactions unless explicitly configured
- Users without data in the database will see an empty state instead of mock data
- Only test users can view mock data when the flag is disabled globally

### Configuration

#### Frontend Configuration

Set environment variables in your frontend `.env` file:

```env
# Enable mock data for ALL users (default: false)
VITE_ENABLE_MOCK_DATA=false

# Test user ID that can see mock data (optional)
# When set, this user ID will see mock data even if VITE_ENABLE_MOCK_DATA is false
VITE_TEST_USER_ID=999
```

#### Backend Configuration

Set environment variables in your backend `.env` file:

```env
# Enable mock data for ALL users (default: false)
ENABLE_MOCK_DATA=false

# Test user ID that can see mock data (optional)
# When set, this user ID will see mock data even if ENABLE_MOCK_DATA is false
TEST_USER_ID=999
```

### Usage Examples

#### Scenario 1: Development Mode (Everyone Sees Mock Data)

**Frontend `.env`:**
```env
VITE_ENABLE_MOCK_DATA=true
```

**Backend `.env`:**
```env
ENABLE_MOCK_DATA=true
```

All users will see mock data.

#### Scenario 2: Production Mode (No Mock Data)

**Frontend `.env`:**
```env
VITE_ENABLE_MOCK_DATA=false
```

**Backend `.env`:**
```env
ENABLE_MOCK_DATA=false
```

Users will only see their real data from the API. Users without data will see an empty state.

#### Scenario 3: Production with Demo User

**Frontend `.env`:**
```env
VITE_ENABLE_MOCK_DATA=false
VITE_TEST_USER_ID=999
```

**Backend `.env`:**
```env
ENABLE_MOCK_DATA=false
TEST_USER_ID=999
```

- User ID 999 (demo user) sees mock data
- All other users see their real data
- Users without data see an empty state

#### Scenario 4: Hybrid Mode (Everyone Sees Mock Data, but Specific User Sees Real Data)

This scenario is not currently supported. The feature flag assumes:
- If global mock data is enabled, everyone sees mock data
- If global mock data is disabled, only test users see mock data

### Implementation Details

#### Frontend (`src/lib/config.ts`)

The frontend configuration module provides:
- `ENABLE_MOCK_DATA`: Boolean flag from environment
- `TEST_USER_ID`: Optional test user ID from environment
- Helper function available through `api.ts`: `shouldUseMockData(userId)`

#### Frontend Usage in Components

The `shouldUseMockData()` function is used in:
- **Home.tsx** - Determines which data to display on the dashboard
- **Transactions.tsx** - Decides whether to fetch real transactions or use mock data

#### Backend (`src/config.py`)

The backend configuration module provides:
- `ENABLE_MOCK_DATA`: Boolean flag from environment
- `TEST_USER_ID`: Optional test user ID from environment
- `should_use_mock_data(user_id)`: Function to check if mock data should be used

#### Backend Usage in APIs

Currently, the backend can use this configuration to:
- Return mock data from transaction endpoints when appropriate
- Provide a consistent feature flag system between frontend and backend

### Adding New Mock-Data-Aware APIs

When adding new API endpoints that should respect the mock data feature flag:

**Backend:**
```python
from src.config import should_use_mock_data

@router.get("/endpoint")
def my_endpoint(user_id: int, db: Session = Depends(get_db_session)):
    if should_use_mock_data(user_id):
        # Return mock data
        return mock_data
    else:
        # Query real data from database
        return db.query(...).filter(...).all()
```

**Frontend:**
```typescript
import { shouldUseMockData, getCurrentUserId } from '../lib/api';

useEffect(() => {
  const userId = getCurrentUserId();
  if (shouldUseMockData(userId)) {
    // Use mock data from mockData.ts
    setData(mockData);
  } else {
    // Fetch real data from API
    fetchFromAPI(userId);
  }
}, []);
```

### Logging

The system provides informative console messages:

**Development:**
```
Mock data enabled for user ID: 999
```

**Production without user:**
```
No user id found in localStorage. Set `userId` in localStorage to fetch transactions.
```
