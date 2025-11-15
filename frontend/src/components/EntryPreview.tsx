import { useState, useMemo, useEffect } from 'react';
import { AlertCircle, ArrowUpDown } from 'lucide-react';
import type {
  PrepareEntriesResponse,
  AccountsByType,
  Transaction,
  TransactionEntry,
} from '../lib/types';
import { TransactionCard } from './TransactionCard';

interface EntryPreviewProps {
  preview: PrepareEntriesResponse;
  accounts: AccountsByType;
  onSelectAccounts: (
    creditCardAccountId: number,
    defaultExpenseAccountId: number,
    bankAccountId?: number | null
  ) => void;
  onConfirmAndCreateEntries?: () => void;
  isLoading?: boolean;
  defaultCreditCardAccountId?: number | null;
  defaultExpenseAccountId?: number | null;
  defaultBankAccountId?: number | null;
}

export function EntryPreview({
  preview,
  accounts,
  onSelectAccounts,
  onConfirmAndCreateEntries,
  isLoading = false,
  defaultCreditCardAccountId = null,
  defaultExpenseAccountId: defaultExpenseAccountIdProp = null,
  defaultBankAccountId = null,
}: EntryPreviewProps) {
  const [creditCardAccountId, setCreditCardAccountId] = useState<number | null>(
    defaultCreditCardAccountId
  );
  const [defaultExpenseAccountId, setDefaultExpenseAccountId] =
    useState<number | null>(defaultExpenseAccountIdProp);
  const [bankAccountId, setBankAccountId] = useState<number | null>(
    defaultBankAccountId
  );
  const [sortBy, setSortBy] = useState<'date' | 'amount'>('date');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [hasInitialized, setHasInitialized] = useState(false);

  // Set default accounts on first load
  useEffect(() => {
    if (!hasInitialized && accounts.liability?.length && accounts.expense?.length) {
      const firstLiabilityId = accounts.liability[0].account_id;
      const firstExpenseId = accounts.expense[0].account_id;
      
      setCreditCardAccountId(firstLiabilityId);
      setDefaultExpenseAccountId(firstExpenseId);
      setHasInitialized(true);
    }
  }, [accounts, hasInitialized]);

  const handleSelectAccountsAndGeneratePreview = () => {
    if (!creditCardAccountId || !defaultExpenseAccountId) {
      alert('Please select both credit card account and default expense account');
      return;
    }
    onSelectAccounts(creditCardAccountId, defaultExpenseAccountId, bankAccountId);
  };

  const handleConfirm = () => {
    if (onConfirmAndCreateEntries) {
      onConfirmAndCreateEntries();
    }
  };

  const liabilityAccounts = accounts.liability || [];
  const expenseAccounts = accounts.expense || [];
  const assetAccounts = accounts.asset || [];

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  // Adapter function to convert TransactionPreview to Transaction format
  const adaptTransaction = (transactionPreview: typeof preview.transactions[0], index: number): Transaction => ({
    id: index,
    description: transactionPreview.description,
    transaction_date: transactionPreview.transaction_date,
    reference: undefined,
    entries: transactionPreview.entries as unknown as TransactionEntry[],
    detailed_entries: transactionPreview.entries as unknown as TransactionEntry[],
  });

  const sortedTransactions = useMemo(() => {
    const sorted = [...preview.transactions];
    sorted.sort((a, b) => {
      let compareValue = 0;

      if (sortBy === 'date') {
        compareValue = new Date(a.transaction_date).getTime() - new Date(b.transaction_date).getTime();
      } else if (sortBy === 'amount') {
        const amountA = a.entries.reduce((sum, entry) => sum + entry.amount, 0);
        const amountB = b.entries.reduce((sum, entry) => sum + entry.amount, 0);
        compareValue = amountA - amountB;
      }

      return sortOrder === 'asc' ? compareValue : -compareValue;
    });

    return sorted;
  }, [preview.transactions, sortBy, sortOrder]);

  return (
    <div className="card space-y-6">
      {/* Summary */}
      <div className="bg-accent/5 rounded-lg p-4 border border-accent/20">
        <h3 className="text-lg font-semibold text-primary mb-4">
          {preview.statement_filename}
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <p className="text-sm text-secondary">Transactions</p>
            <p className="text-2xl font-bold text-primary">
              {preview.total_transactions}
            </p>
          </div>
          <div>
            <p className="text-sm text-secondary">CC Debits (Refunds)</p>
            <p className="text-2xl font-bold text-error">
              {formatCurrency(preview.cc_debit_amount)}
            </p>
            <p className="text-xs text-secondary mt-1">Money returned to card</p>
          </div>
          <div>
            <p className="text-sm text-secondary">CC Credits (Expenses)</p>
            <p className="text-2xl font-bold text-success">
              {formatCurrency(preview.cc_credit_amount)}
            </p>
            <p className="text-xs text-secondary mt-1">Charges on card</p>
          </div>
          <div className="col-span-2 md:col-span-1">
            <p className="text-sm text-secondary">Balanced</p>
            <p
              className={`text-2xl font-bold ${
                preview.is_balanced ? 'text-success' : 'text-error'
              }`}
            >
              {preview.is_balanced ? '✓' : '✗'}
            </p>
          </div>
        </div>

        {!preview.is_balanced && (
          <div className="mt-4 flex items-start gap-2 p-3 bg-error/10 rounded border border-error/20">
            <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
            <p className="text-sm text-error">
              Entries are not balanced. Please review your account selections.
            </p>
          </div>
        )}
      </div>

      {/* Account Selection */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-primary">
          Select Accounts
        </h3>

        <div>
          <label className="block text-sm font-medium text-primary mb-2">
            Credit Card Account <span className="text-error">*</span>
          </label>
          <select
            value={creditCardAccountId?.toString() || ''}
            onChange={(e) => setCreditCardAccountId(e.target.value ? Number(e.target.value) : null)}
            disabled={isLoading}
            className = 'w-full px-3 py-2 border border-secondary/30 rounded-lg text-foreground bg-white dark:bg-neutral-900'

          >
            <option value="">Select a liability account...</option>
            {liabilityAccounts.map((account) => (
              <option key={account.account_id} value={account.account_id.toString()}>
                {account.account_name} ({formatCurrency(account.balance)})
              </option>
            ))}
          </select>
          <p className="text-xs text-secondary mt-1">
            Usually a credit card or loan account
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-primary mb-2">
            Default Expense Account <span className="text-error">*</span>
          </label>
          <select
            value={defaultExpenseAccountId?.toString() || ''}
            onChange={(e) => setDefaultExpenseAccountId(e.target.value ? Number(e.target.value) : null)}
            disabled={isLoading}
            className="w-full px-3 py-2 border border-secondary/30 rounded-lg text-foreground bg-white dark:bg-neutral-900"
          >
            <option  value="">Select an expense account...</option>
            {expenseAccounts.map((account) => (
              <option  key={account.account_id} value={account.account_id.toString()}>
                {account.account_name}
              </option>
            ))}
          </select>
          <p className="text-xs text-secondary mt-1">
            Default category for transactions
          </p>
        </div>

        <div>
          <label className="block text-sm font-medium text-primary mb-2">
            Bank Account (Optional)
          </label>
          <select
            value={bankAccountId?.toString() || ''}
            onChange={(e) => setBankAccountId(e.target.value ? Number(e.target.value) : null)}
            disabled={isLoading}
            className="w-full px-3 py-2 bg-background border border-secondary/30 rounded-lg text-primary focus:outline-none focus:border-accent"
          >
            <option value="">None</option>
            {assetAccounts.map((account) => (
              <option key={account.account_id} value={account.account_id.toString()}>
                {account.account_name} ({formatCurrency(account.balance)})
              </option>
            ))}
          </select>
          <p className="text-xs text-secondary mt-1">
            For payment/refund transactions
          </p>
        </div>

        <button
          onClick={handleSelectAccountsAndGeneratePreview}
          disabled={isLoading}
          className="btn-primary w-full"
        >
          {isLoading ? 'Loading Preview...' : 'Generate Preview'}
        </button>
      </div>

      {/* Transactions Preview */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-primary">
            Transactions Preview
          </h3>
          <div className="flex gap-2">
            <div className="relative">
              <ArrowUpDown className="absolute left-4 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary pointer-events-none" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'date' | 'amount')}
                className="pl-12 pr-4 py-2 bg-background border border-secondary/30 rounded-lg text-primary text-sm focus:outline-none focus:border-accent appearance-none cursor-pointer"
              >
                <option value="date">Sort by Date</option>
                <option value="amount">Sort by Amount</option>
              </select>
            </div>
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="px-3 py-2 bg-background border border-secondary/30 rounded-lg text-primary text-sm hover:bg-secondary/5 transition-colors"
              title={`Currently sorted ${sortOrder === 'asc' ? 'ascending' : 'descending'}`}
            >
              {sortOrder === 'asc' ? '↑ ASC' : '↓ DESC'}
            </button>
          </div>
        </div>

        <div className="max-h-96 md:max-h-[600px] overflow-y-auto border border-secondary/20 rounded-lg">
          <div className="space-y-3 p-3">
            {sortedTransactions.map((transaction, index) => (
              <TransactionCard
                key={index}
                transaction={adaptTransaction(transaction, index)}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      {preview.transactions.length > 0 && (
        <div className="flex gap-3 pt-4 border-t border-secondary/20">
          <button
            onClick={handleConfirm}
            disabled={isLoading}
            className="btn-primary flex-1"
          >
            {isLoading ? 'Processing...' : 'Confirm & Create Entries'}
          </button>
        </div>
      )}
    </div>
  );
}
