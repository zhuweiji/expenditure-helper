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

// Statement upload flow types
export interface ProcessingStatus {
  id: number;
  statement_id: number;
  status: 'pending' | 'in_progress' | 'completed' | 'errored';
  error_message: string | null;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
}

export interface StatementDetail {
  id: number;
  filename: string;
  saved_path: string;
  account_id: number | null;
  csv_output: string;
  created_at: string;
  file_hash: string;
}

export interface EntryPreview {
  account_id: number;
  account_name: string;
  entry_type: 'debit' | 'credit';
  amount: number;
  description: string;
}

export interface TransactionPreview {
  description: string;
  transaction_date: string;
  entries: EntryPreview[];
}

export interface PrepareEntriesResponse {
  statement_id: number;
  statement_filename: string;
  transactions: TransactionPreview[];
  total_transactions: number;
  total_debits: number;
  total_credits: number;
  is_balanced: boolean;
}

export interface CreateEntryRequest {
  account_id: number;
  amount: number;
  entry_type: 'debit' | 'credit';
  description: string;
  timestamp?: string;
}

export interface CreateTransactionRequest {
  user_id: number;
  description: string;
  transaction_date: string;
  reference?: string;
  entries: CreateEntryRequest[];
}

export interface CategoryMapping {
  category: string;
  account_id: number;
}

export interface PrepareEntriesRequest {
  statement_id: number;
  user_id: number;
  credit_card_account_id: number;
  default_expense_account_id: number;
  bank_account_id?: number | null;
  category_mappings?: CategoryMapping[];
  dry_run: boolean;
}

export interface Account {
  account_id: number;
  account_name: string;
  credit_total: number;
  debit_total: number;
  balance: number;
}

export interface AccountsByType {
  liability: Account[];
  expense: Account[];
  asset: Account[];
}