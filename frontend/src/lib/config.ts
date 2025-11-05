/**
 * Feature Flags and Configuration
 * 
 * These settings control app behavior. Can be controlled via environment variables.
 */

// Feature flag to enable mock data - set to false to disable mock data for all users
// Can be overridden per user by setting a test user with ID that matches TEST_USER_ID
export const ENABLE_MOCK_DATA = import.meta.env.VITE_ENABLE_MOCK_DATA === 'true';

// Test user ID that should have access to mock data when ENABLE_MOCK_DATA is false
// This allows demo/test users to view mock transactions while regular users see real data only
export const TEST_USER_ID = import.meta.env.VITE_TEST_USER_ID 
  ? parseInt(import.meta.env.VITE_TEST_USER_ID, 10) 
  : null;

export const config = {
  ENABLE_MOCK_DATA,
  TEST_USER_ID,
};
