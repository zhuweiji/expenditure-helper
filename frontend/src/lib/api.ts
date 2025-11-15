// API Configuration and Service Layer
import { ENABLE_MOCK_DATA, TEST_USER_ID } from './config';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:9110';

console.log(API_BASE_URL)

export interface ApiError {
  message: string;
  status: number;
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

// Helper function to get current user ID from localStorage
export function getCurrentUserId(): number | null {
  const userId = localStorage.getItem('userId');
  return userId ? parseInt(userId, 10) : null;
}

/**
 * Determines if mock data should be used for the current user.
 * Mock data is used if:
 * - ENABLE_MOCK_DATA feature flag is true, OR
 * - The current user ID matches TEST_USER_ID (test user has access to mock data)
 */
export function shouldUseMockData(userId: number | null): boolean {
  if (ENABLE_MOCK_DATA) {
    console.log('This version has mock data enabled via feature flag.');
    return true;
  }
  
  if (TEST_USER_ID !== null && userId === TEST_USER_ID) {
    console.log('This is a test user with access to mock data.');
    return true;
  }
  
  return false;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options?: RequestInit
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    console.log(url)
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
      });

      if (!response.ok) {
        throw {
          message: `API Error: ${response.statusText}`,
          status: response.status,
        } as ApiError;
      }

      return await response.json();
    } catch (error) {
      if ((error as ApiError).status) {
        throw error;
      }
      throw {
        message: 'Network error',
        status: 0,
      } as ApiError;
    }
  }

  // Auth endpoints (using user management since passwords are not implemented)
  async getUserByUsername(username: string): Promise<User> {
    return this.request<User>(`/users/username/${username}`);
  }

  async createUser(username: string, email: string, fullName?: string): Promise<User> {
    return this.request<User>('/users', {
      method: 'POST',
      body: JSON.stringify({ 
        username, 
        email, 
        full_name: fullName 
      }),
    });
  }

  async listUsers(): Promise<User[]> {
    return this.request<User[]>('/users');
  }

  // Transaction endpoints
  async getTransactions(
    userId: number,
    params?: {
      startDate?: string;
      endDate?: string;
      page?: number;
      pageSize?: number;
    }
  ) {
    const queryParams = new URLSearchParams({ user_id: userId.toString() });
    if (params?.startDate) queryParams.append('startDate', params.startDate);
    if (params?.endDate) queryParams.append('endDate', params.endDate);
    if (params?.page) queryParams.append('page', params.page.toString());
    if (params?.pageSize) queryParams.append('page_size', params.pageSize.toString());

    console.log(userId)
    return this.request(`/transactions?${queryParams.toString()}`);
  }

  async getTransaction(id: string, userId: number) {
    return this.request(`/transactions/${id}?user_id=${userId}`);
  }

  async createTransaction(userId: number, data: any) {
    return this.request('/transactions', {
      method: 'POST',
      body: JSON.stringify({ ...data, user_id: userId }),
    });
  }

  async updateTransaction(transactionId: number, userId: number, data: any) {
    return this.request(`/transactions/${transactionId}`, {
      method: 'PUT',
      body: JSON.stringify({ ...data, user_id: userId }),
    });
  }

  async deleteTransaction(transactionId: number, userId: number) {
    return this.request(`/transactions/${transactionId}?user_id=${userId}`, {
      method: 'DELETE',
    });
  }

  async batchCreateTransactions(userId: number, transactions: any[]) {
    const transactionsWithUserId = transactions.map(t => ({
      user_id: userId,
      description: t.description,
      transaction_date: t.transaction_date,
      reference: t.reference,
      entries: t.entries,
    }));
    console.log('transactionsWithUserId', transactionsWithUserId);
    return this.request('/transactions/batch', {
      method: 'POST',
      body: JSON.stringify(transactionsWithUserId),
    });
  }

  // Statement upload
  async uploadStatement(file: File, userId: number) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${this.baseUrl}/statements/upload?user_id=${userId}`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw {
        message: 'Upload failed',
        status: response.status,
      } as ApiError;
    }

    return await response.json();
  }

  async getProcessingStatus(processingId: number, userId: number) {
    return this.request(`/statements/processing/${processingId}?user_id=${userId}`);
  }

  async getStatementDetail(statementId: number, userId: number) {
    return this.request(`/statements/${statementId}?user_id=${userId}`);
  }

  async prepareEntries(request: any) {
    return this.request('/statements/create-entries', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getAccountsByUser(userId: number) {
    return this.request(`/users/${userId}/accounts`);
  }

  // Analytics endpoints
  async getAnalytics(userId: number, params?: { startDate?: string; endDate?: string }) {
    const queryParams = new URLSearchParams({ user_id: userId.toString() });
    if (params?.startDate) queryParams.append('startDate', params.startDate);
    if (params?.endDate) queryParams.append('endDate', params.endDate);
    
    return this.request(`/analytics?${queryParams.toString()}`);
  }

  async getSpendingByCategory(
    userId: number,
    params?: {
      startDate?: string;
      endDate?: string;
      currency?: string;
    }
  ) {
    const queryParams = new URLSearchParams({ user_id: userId.toString() });
    if (params?.startDate) queryParams.append('start_date', params.startDate);
    if (params?.endDate) queryParams.append('end_date', params.endDate);
    if (params?.currency) queryParams.append('currency', params.currency);

    return this.request(`/analytics/spending-by-category?${queryParams.toString()}`);
  }

  async getMonthlySpending(
    userId: number,
    params?: {
      months?: number;
      currency?: string;
    }
  ) {
    const queryParams = new URLSearchParams({ user_id: userId.toString() });
    if (params?.months) queryParams.append('months', params.months.toString());
    if (params?.currency) queryParams.append('currency', params.currency);

    return this.request(`/analytics/monthly-spending?${queryParams.toString()}`);
  }

  async getInsights(
    userId: number,
    params?: {
      startDate?: string;
      endDate?: string;
    }
  ) {
    const queryParams = new URLSearchParams({ user_id: userId.toString() });
    if (params?.startDate) queryParams.append('start_date', params.startDate);
    if (params?.endDate) queryParams.append('end_date', params.endDate);

    return this.request(`/analytics/insights?${queryParams.toString()}`);
  }

  // User profile
  async getProfile(userId: number) {
    return this.request(`/users/${userId}`);
  }

  async updateProfile(userId: number, data: any) {
    return this.request(`/users/${userId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  // Clear all transactions/entries for a user
  async clearAllTransactions(userId: number) {
    return this.request(`/accounts/user/${userId}/clear`, {
      method: 'DELETE',
    });
  }

  // Clear all statements for a user
  async clearAllStatements(userId: number) {
    return this.request(`/statements/user/${userId}/all`, {
      method: 'DELETE',
    });
  }
}

export const apiClient = new ApiClient(API_BASE_URL);
