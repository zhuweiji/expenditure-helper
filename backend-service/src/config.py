"""
Feature Flags and Configuration

Controls app behavior via environment variables.
"""

import os
from typing import Optional

# Feature flag to enable mock data - set to 'true' to enable mock data for all users
ENABLE_MOCK_DATA = os.getenv("ENABLE_MOCK_DATA", "false").lower() == "true"

# Test user ID that should have access to mock data when ENABLE_MOCK_DATA is False
# This allows demo/test users to view mock transactions while regular users see real data only
TEST_USER_ID: Optional[int] = None
if test_user_id_str := os.getenv("TEST_USER_ID"):
    try:
        TEST_USER_ID = int(test_user_id_str)
    except ValueError:
        pass


def should_use_mock_data(user_id: Optional[int] = None) -> bool:
    """
    Determines if mock data should be used for the given user.

    Mock data is used if:
    - ENABLE_MOCK_DATA feature flag is true, OR
    - The user ID matches TEST_USER_ID (test user has access to mock data)

    Args:
        user_id: The user ID to check

    Returns:
        True if mock data should be used, False otherwise
    """
    if ENABLE_MOCK_DATA:
        return True

    if TEST_USER_ID is not None and user_id == TEST_USER_ID:
        return True

    return False
