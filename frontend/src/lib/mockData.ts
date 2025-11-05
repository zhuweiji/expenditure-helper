// Mock data for demonstration purposes

export interface TransactionEntry {
  account_name: string;
  account_type: string;
  amount: number;
  entry_type: 'debit' | 'credit';
  description?: string;
}

export interface Transaction {
  id: number;
  user_id: number;
  description: string;
  transaction_date: string;
  reference?: string;
  amount: number;
  entries: TransactionEntry[];
  detailed_entries: TransactionEntry[];
}

export interface CategorySpending {
  category: string;
  amount: number;
  percentage: number;
  color: string;
}

export interface MonthlySpending {
  month: string;
  amount: number;
}

export const mockTransactions: Transaction[] = [
  {
    id: 1,
    user_id: 1,
    description: 'Grocery Store',
    transaction_date: '2025-11-03',
    reference: 'WF-001',
    amount: -85.50,
    entries: [
      {
        account_name: 'Groceries',
        account_type: 'user',
        amount: -85.50,
        entry_type: 'debit',
        description: 'Whole Foods purchase',
      },
    ],
    detailed_entries: [
      {
        account_name: 'Groceries',
        account_type: 'user',
        amount: -85.50,
        entry_type: 'debit',
        description: 'Whole Foods purchase',
      },
    ],
  },
  {
    id: 2,
    user_id: 1,
    description: 'Salary Deposit',
    transaction_date: '2025-11-02',
    reference: 'DEPOSIT-001',
    amount: 3500.00,
    entries: [
      {
        account_name: 'Checking Account',
        account_type: 'user',
        amount: 3500.00,
        entry_type: 'credit',
        description: 'Monthly salary',
      },
    ],
    detailed_entries: [
      {
        account_name: 'Checking Account',
        account_type: 'user',
        amount: 3500.00,
        entry_type: 'credit',
        description: 'Monthly salary',
      },
    ],
  },
  {
    id: 3,
    user_id: 1,
    description: 'Coffee Shop',
    transaction_date: '2025-11-02',
    reference: 'SB-001',
    amount: -4.75,
    entries: [
      {
        account_name: 'Dining',
        account_type: 'user',
        amount: -4.75,
        entry_type: 'debit',
        description: 'Coffee purchase',
      },
    ],
    detailed_entries: [
      {
        account_name: 'Dining',
        account_type: 'user',
        amount: -4.75,
        entry_type: 'debit',
        description: 'Coffee purchase',
      },
    ],
  },
  {
    id: 4,
    user_id: 1,
    description: 'Gas Station',
    transaction_date: '2025-11-01',
    reference: 'SHELL-001',
    amount: -65.00,
    entries: [
      {
        account_name: 'Transportation',
        account_type: 'user',
        amount: -65.00,
        entry_type: 'debit',
        description: 'Fuel',
      },
    ],
    detailed_entries: [
      {
        account_name: 'Transportation',
        account_type: 'user',
        amount: -65.00,
        entry_type: 'debit',
        description: 'Fuel',
      },
    ],
  },
  {
    id: 5,
    user_id: 1,
    description: 'Online Shopping',
    transaction_date: '2025-10-31',
    reference: 'AMAZON-001',
    amount: -129.99,
    entries: [
      {
        account_name: 'Shopping',
        account_type: 'user',
        amount: -129.99,
        entry_type: 'debit',
        description: 'Amazon purchase',
      },
    ],
    detailed_entries: [
      {
        account_name: 'Shopping',
        account_type: 'user',
        amount: -129.99,
        entry_type: 'debit',
        description: 'Amazon purchase',
      },
    ],
  },
  {
    id: 6,
    user_id: 1,
    description: 'Restaurant',
    transaction_date: '2025-10-30',
    reference: 'REST-001',
    amount: -67.80,
    entries: [
      {
        account_name: 'Dining',
        account_type: 'user',
        amount: -67.80,
        entry_type: 'debit',
        description: 'Dinner',
      },
    ],
    detailed_entries: [
      {
        account_name: 'Dining',
        account_type: 'user',
        amount: -67.80,
        entry_type: 'debit',
        description: 'Dinner',
      },
    ],
  },
  {
    id: 7,
    user_id: 1,
    description: 'Gym Membership',
    transaction_date: '2025-10-29',
    reference: 'GYM-001',
    amount: -49.99,
    entries: [
      {
        account_name: 'Health',
        account_type: 'user',
        amount: -49.99,
        entry_type: 'debit',
        description: 'Monthly subscription',
      },
    ],
    detailed_entries: [
      {
        account_name: 'Health',
        account_type: 'user',
        amount: -49.99,
        entry_type: 'debit',
        description: 'Monthly subscription',
      },
    ],
  },
  {
    id: 8,
    user_id: 1,
    description: 'Electric Bill',
    transaction_date: '2025-10-28',
    reference: 'ELEC-001',
    amount: -95.30,
    entries: [
      {
        account_name: 'Utilities',
        account_type: 'user',
        amount: -95.30,
        entry_type: 'debit',
        description: 'Monthly bill',
      },
    ],
    detailed_entries: [
      {
        account_name: 'Utilities',
        account_type: 'user',
        amount: -95.30,
        entry_type: 'debit',
        description: 'Monthly bill',
      },
    ],
  },
];

export const mockCategorySpending: CategorySpending[] = [
  { category: 'Groceries', amount: 285.50, percentage: 28, color: '#EAFD60' },
  { category: 'Dining', amount: 245.30, percentage: 24, color: '#27C46B' },
  { category: 'Transportation', amount: 165.00, percentage: 16, color: '#60A5FA' },
  { category: 'Shopping', amount: 159.99, percentage: 16, color: '#F472B6' },
  { category: 'Utilities', amount: 95.30, percentage: 9, color: '#A78BFA' },
  { category: 'Health', amount: 49.99, percentage: 5, color: '#FB923C' },
  { category: 'Other', amount: 20.00, percentage: 2, color: '#9BA0A5' },
];

export const mockMonthlySpending: MonthlySpending[] = [
  { month: 'May', amount: 1250 },
  { month: 'Jun', amount: 1380 },
  { month: 'Jul', amount: 1150 },
  { month: 'Aug', amount: 1420 },
  { month: 'Sep', amount: 1280 },
  { month: 'Oct', amount: 1350 },
  { month: 'Nov', amount: 498.34 },
];

export const mockUserProfile = {
  name: 'John Doe',
  email: 'john.doe@example.com',
  avatar: null,
  currency: 'USD',
  timezone: 'America/New_York',
  joinedDate: '2025-01-15',
};
