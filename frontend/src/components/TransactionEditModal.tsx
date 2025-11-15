import { useState, useEffect } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import type { Transaction, TransactionEntry } from '../lib/types';

interface TransactionEditModalProps {
  transaction: Transaction;
  isOpen: boolean;
  onClose: () => void;
  onSave: (transaction: Transaction) => Promise<void>;
  onDelete: (transactionId: number) => Promise<void>;
  availableAccounts: Array<{ account_id: number; account_name: string }>;
}

export function TransactionEditModal({
  transaction,
  isOpen,
  onClose,
  onSave,
  onDelete,
  availableAccounts,
}: TransactionEditModalProps) {
  const [description, setDescription] = useState(transaction.description);
  const [transactionDate, setTransactionDate] = useState(
    transaction.transaction_date.split('T')[0]
  );
  const [entries, setEntries] = useState<TransactionEntry[]>(
    transaction.detailed_entries || []
  );
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Prevent scrolling behind modal on mobile
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      return () => {
        document.body.style.overflow = '';
      };
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const handleUpdateEntry = (
    index: number,
    field: 'account_name' | 'amount',
    value: string | number
  ) => {
    const updatedEntries = [...entries];
    if (field === 'amount') {
      updatedEntries[index].amount = parseFloat(value as string) || 0;
    } else {
      updatedEntries[index].account_name = value as string;
    }
    setEntries(updatedEntries);
  };

  const handleDeleteEntry = (index: number) => {
    setEntries(entries.filter((_, i) => i !== index));
  };

  const handleAddEntry = () => {
    setEntries([
      ...entries,
      {
        account_name: '',
        account_type: 'expense',
        amount: 0,
        entry_type: 'debit',
        description: description,
      },
    ]);
  };

  const handleSave = async () => {
    setError(null);

    // Validation
    if (!description.trim()) {
      setError('Description is required');
      return;
    }

    if (entries.length === 0) {
      setError('At least one entry is required');
      return;
    }

    if (entries.some(e => !e.account_name.trim())) {
      setError('All entries must have an account name');
      return;
    }

    if (entries.some(e => e.amount <= 0)) {
      setError('All amounts must be greater than 0');
      return;
    }

    setIsLoading(true);
    try {
      await onSave({
        ...transaction,
        description,
        transaction_date: transactionDate,
        detailed_entries: entries,
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save transaction');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    setIsLoading(true);
    try {
      await onDelete(transaction.id);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete transaction');
    } finally {
      setIsLoading(false);
      setShowDeleteConfirm(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4 py-10 md:py-4">
      <div className="bg-card/80 backdrop-blur-md rounded-lg shadow-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto border border-secondary/10">
        {/* Header */}
        <div className="top-0 flex items-center justify-between p-6 border-b border-border bg-card/80 backdrop-blur-md">
          <h2 className="text-xl font-semibold text-primary">Edit Transaction</h2>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="text-secondary hover:text-primary transition-colors disabled:opacity-50"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {error && (
            <div className="bg-error/10 border border-error/50 rounded-lg p-4">
              <p className="text-error text-sm">{error}</p>
            </div>
          )}

          {/* Description Section */}
          <div>
            <label className="block text-sm font-medium text-secondary mb-2">
              Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              disabled={isLoading}
              className="input w-full"
              placeholder="Transaction description"
            />
          </div>

          {/* Date Section */}
          <div>
            <label className="block text-sm font-medium text-secondary mb-2">
              Transaction Date
            </label>
            <input
              type="date"
              value={transactionDate}
              onChange={(e) => setTransactionDate(e.target.value)}
              disabled={isLoading}
              className="input w-full"
            />
          </div>

          {/* Entries Section */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <label className="block text-sm font-medium text-secondary">
                Entries ({entries.length})
              </label>
              <button
                onClick={handleAddEntry}
                disabled={isLoading}
                className="flex items-center gap-2 px-3 py-1 bg-primary/10 hover:bg-primary/20 text-primary rounded transition-colors disabled:opacity-50 text-sm"
              >
                <Plus className="h-4 w-4" />
                Add Entry
              </button>
            </div>

            <div className="space-y-3">
              {entries.map((entry, index) => (
                <div
                  key={index}
                  className="card bg-card/50 p-4 space-y-3 border border-border/50"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-medium px-2 py-1 rounded bg-secondary/20 text-secondary">
                      {entry.entry_type.toUpperCase()}
                    </span>
                    <button
                      onClick={() => handleDeleteEntry(index)}
                      disabled={isLoading || entries.length === 1}
                      className="text-error hover:text-error/80 transition-colors disabled:opacity-30"
                      title={entries.length === 1 ? 'At least one entry required' : 'Delete entry'}
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                    {/* Account Name */}
                    <div className="md:col-span-2">
                      <label className="block text-xs font-medium text-secondary mb-1">
                        Account Name
                      </label>
                      <select
                        value={entry.account_name}
                        onChange={(e) =>
                          handleUpdateEntry(index, 'account_name', e.target.value)
                        }
                        disabled={isLoading}
                        className="input w-full text-sm"
                      >
                        <option value="">Select account...</option>
                        {availableAccounts.map((account) => (
                          <option
                            key={account.account_id}
                            value={account.account_name}
                          >
                            {account.account_name}
                          </option>
                        ))}
                      </select>
                      {entry.account_name && !availableAccounts.some(
                        (a) => a.account_name === entry.account_name
                      ) && (
                        <p className="text-xs text-secondary mt-1 italic">
                          Custom: {entry.account_name}
                        </p>
                      )}
                    </div>

                    {/* Amount */}
                    <div>
                      <label className="block text-xs font-medium text-secondary mb-1">
                        Amount
                      </label>
                      <input
                        type="number"
                        value={entry.amount}
                        onChange={(e) =>
                          handleUpdateEntry(index, 'amount', e.target.value)
                        }
                        disabled={isLoading}
                        step="0.01"
                        min="0"
                        className="input w-full text-sm"
                        placeholder="0.00"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="sticky bottom-0 flex items-center justify-between gap-3 p-6 border-t border-border bg-card/80 backdrop-blur-md">
          <button
            onClick={() => setShowDeleteConfirm(true)}
            disabled={isLoading || showDeleteConfirm}
            className="px-4 py-2 bg-error/10 hover:bg-error/20 text-error rounded transition-colors disabled:opacity-50"
          >
            Delete Transaction
          </button>

          <div className="flex gap-3">
            <button
              onClick={onClose}
              disabled={isLoading}
              className="btn-secondary"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isLoading}
              className="btn-primary disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteConfirm && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-card/80 backdrop-blur-md rounded-lg shadow-lg max-w-md w-full p-6 border border-secondary/10">
            <h3 className="text-lg font-semibold text-primary mb-2">
              Delete Transaction?
            </h3>
            <p className="text-secondary mb-6">
              Are you sure you want to delete this transaction? This action cannot be undone.
            </p>
            <div className="flex gap-3 justify-end">
              <button
                onClick={() => setShowDeleteConfirm(false)}
                disabled={isLoading}
                className="btn-secondary"
              >
                Cancel
              </button>
              <button
                onClick={handleDelete}
                disabled={isLoading}
                className="px-4 py-2 bg-error hover:bg-error/80 text-white rounded transition-colors disabled:opacity-50"
              >
                {isLoading ? 'Deleting...' : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
