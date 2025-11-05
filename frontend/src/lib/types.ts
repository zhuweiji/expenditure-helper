export interface TransactionEntry {
  account_name: string;
  account_type: string;
  amount: number;
  entry_type: 'debit' | 'credit';
  description?: string;
}

export interface Transaction {
  id: number;
  description: string;
  transaction_date: string;
  reference?: string;
  amount: number;
  entries: TransactionEntry[];
  detailed_entries: TransactionEntry[];
}