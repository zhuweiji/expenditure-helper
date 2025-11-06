import { CheckCircle, AlertCircle } from 'lucide-react';
import type { PrepareEntriesResponse } from '../lib/types';

interface ConfirmationStepProps {
  preview: PrepareEntriesResponse;
  isCreating?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export function ConfirmationStep({
  preview,
  isCreating = false,
  onConfirm,
  onCancel,
}: ConfirmationStepProps) {
  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
    }).format(amount);
  };

  return (
    <div className="card space-y-6">
      <div className="bg-accent/5 rounded-lg p-4 border border-accent/20">
        <h2 className="text-xl font-semibold text-primary mb-4">
          Ready to Create Entries
        </h2>

        <div className="space-y-4">
          <div className="flex items-start gap-3">
            <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-primary">Statement Loaded</p>
              <p className="text-sm text-secondary">{preview.statement_filename}</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            {preview.is_balanced ? (
              <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
            ) : (
              <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
            )}
            <div>
              <p className="font-medium text-primary">Entries Balanced</p>
              <div className="text-sm text-secondary space-y-1">
                <p>Transactions: {preview.total_transactions}</p>
                <p>
                  Total Debits: {formatCurrency(preview.total_debits)}
                </p>
                <p>
                  Total Credits: {formatCurrency(preview.total_credits)}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-primary/5 rounded-lg p-4 border border-primary/20">
        <p className="text-sm text-secondary">
          Once you confirm, {preview.total_transactions} transaction(s) with{' '}
          {preview.transactions.reduce((sum, t) => sum + t.entries.length, 0)} total
          entries will be created in your ledger. This action cannot be undone.
        </p>
      </div>

      <div className="flex gap-3">
        <button
          onClick={onCancel}
          disabled={isCreating}
          className="btn-secondary flex-1"
        >
          Cancel
        </button>
        <button
          onClick={onConfirm}
          disabled={isCreating || !preview.is_balanced}
          className="btn-primary flex-1"
        >
          {isCreating ? 'Creating...' : 'Confirm & Create'}
        </button>
      </div>
    </div>
  );
}
