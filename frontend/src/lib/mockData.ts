// Mock data for demonstration purposes

export interface Transaction {
  id: string;
  date: string;
  description: string;
  amount: number;
  category: string;
  type: 'credit' | 'debit';
  merchant?: string;
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
    id: '1',
    date: '2025-11-03',
    description: 'Grocery Store',
    amount: -85.50,
    category: 'Groceries',
    type: 'debit',
    merchant: 'Whole Foods',
  },
  {
    id: '2',
    date: '2025-11-02',
    description: 'Salary Deposit',
    amount: 3500.00,
    category: 'Income',
    type: 'credit',
    merchant: 'Employer Inc',
  },
  {
    id: '3',
    date: '2025-11-02',
    description: 'Coffee Shop',
    amount: -4.75,
    category: 'Dining',
    type: 'debit',
    merchant: 'Starbucks',
  },
  {
    id: '4',
    date: '2025-11-01',
    description: 'Gas Station',
    amount: -65.00,
    category: 'Transportation',
    type: 'debit',
    merchant: 'Shell',
  },
  {
    id: '5',
    date: '2025-10-31',
    description: 'Online Shopping',
    amount: -129.99,
    category: 'Shopping',
    type: 'debit',
    merchant: 'Amazon',
  },
  {
    id: '6',
    date: '2025-10-30',
    description: 'Restaurant',
    amount: -67.80,
    category: 'Dining',
    type: 'debit',
    merchant: 'The Bistro',
  },
  {
    id: '7',
    date: '2025-10-29',
    description: 'Gym Membership',
    amount: -49.99,
    category: 'Health',
    type: 'debit',
    merchant: 'FitLife Gym',
  },
  {
    id: '8',
    date: '2025-10-28',
    description: 'Electric Bill',
    amount: -95.30,
    category: 'Utilities',
    type: 'debit',
    merchant: 'Electric Co',
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
