import { useState, useMemo } from 'react';
import { AlertCircle, ChevronDown, ChevronUp, ArrowUpDown } from 'lucide-react';
import type {
  PrepareEntriesResponse,
  AccountsByType,
} from '../lib/types';

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
  const [expandedTransactions, setExpandedTransactions] = useState<Set<number>>(
    new Set([0])
  ); // Expand first transaction by default
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

  const toggleTransaction = (index: number) => {
    const newExpanded = new Set(expandedTransactions);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedTransactions(newExpanded);
  };

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

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-sm text-secondary">Transactions</p>
            <p className="text-2xl font-bold text-primary">
              {preview.total_transactions}
            </p>
          </div>
          <div>
            <p className="text-sm text-secondary">Total Debits</p>
            <p className="text-2xl font-bold text-primary">
              {formatCurrency(preview.total_debits)}
            </p>
          </div>
          <div>
            <p className="text-sm text-secondary">Total Credits</p>
            <p className="text-2xl font-bold text-primary">
              {formatCurrency(preview.total_credits)}
            </p>
          </div>
          <div>
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
            className="w-full px-3 py-2 bg-background border border-secondary/30 rounded-lg text-primary focus:outline-none focus:border-accent"
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
            className="w-full px-3 py-2 bg-background border border-secondary/30 rounded-lg text-primary focus:outline-none focus:border-accent"
          >
            <option value="">Select an expense account...</option>
            {expenseAccounts.map((account) => (
              <option key={account.account_id} value={account.account_id.toString()}>
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
          <div key={index} className="border border-secondary/20 rounded-lg overflow-hidden">
            {/* Transaction Header */}
            <button
              onClick={() => toggleTransaction(index)}
              className="w-full px-4 py-3 bg-secondary/5 hover:bg-secondary/10 transition-colors flex items-center justify-between text-left"
            >
              <div className="flex-1">
                <p className="font-medium text-primary">
                  {transaction.description}
                </p>
                <p className="text-sm text-secondary">
                  {new Date(transaction.transaction_date).toLocaleDateString()}
                </p>
              </div>
              <div className="text-right mr-3">
                <p className="font-semibold text-primary">
                  {formatCurrency(
                    transaction.entries.reduce((sum, entry) => sum + entry.amount, 0)
                  )}
                </p>
                <p className='text-sm text-secondary'>{transaction.entries.length} entries</p>

              </div>
              <div className="flex-shrink-0">
                {expandedTransactions.has(index) ? (
                  <ChevronUp className="w-5 h-5 text-secondary" />
                ) : (
                  <ChevronDown className="w-5 h-5 text-secondary" />
                )}
              </div>
            </button>

            {/* Transaction Details */}
            {expandedTransactions.has(index) && (
              <div className="bg-background px-4 py-4 space-y-3 border-t border-secondary/20">
                {transaction.entries.map((entry, entryIndex) => (
                  <div key={entryIndex} className="flex items-center justify-between text-sm">
                    <div>
                      <p className="text-primary">
                        {entry.account_name}
                        <span className="text-secondary ml-2">
                          ({entry.entry_type})
                        </span>
                      </p>
                      {entry.description && (
                        <p className="text-xs text-secondary mt-1">
                          {entry.description}
                        </p>
                      )}
                    </div>
                    <p
                      className={`font-semibold ${
                        entry.entry_type === 'debit'
                          ? 'text-error'
                          : 'text-success'
                      }`}
                    >
                      {entry.entry_type === 'debit' ? '-' : '+'}
                      {formatCurrency(entry.amount)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
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
