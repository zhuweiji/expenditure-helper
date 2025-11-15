import { useNavigate } from 'react-router-dom';
import { Header } from '../../components/layout/Header';
import { ConfirmationStep } from '../../components/ConfirmationStep';
import { StageProgress } from './StageProgress';
import { useUploadFlow } from '../../hooks/useUploadFlow';
import { apiClient, getCurrentUserId, type ApiError } from '../../lib/api';
import type { CreateTransactionRequest } from '../../lib/types';
import { AlertCircle } from 'lucide-react';
import { useState } from 'react';

export function ConfirmationStage() {
  const navigate = useNavigate();
  const { state, setCreatedCounts, clearState } = useUploadFlow();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const userId = getCurrentUserId();

  if (!state.preview) {
    return (
      <div className="min-h-screen bg-background">
        <Header title="Upload Statement" />
        <div className="max-w-4xl mx-auto px-4 py-6 md:px-6 md:py-8">
          <p className="text-error">No preview data found. Please start over.</p>
          <button
            onClick={() => {
              clearState();
              navigate('/upload');
            }}
            className="mt-4 px-4 py-2 bg-accent text-white rounded hover:bg-accent/90"
          >
            Start Over
          </button>
        </div>
      </div>
    );
  }

  const handleConfirm = async () => {
    setIsLoading(true);
    setError('');

    try {
      if (!userId || !state.preview) {
        setError('Invalid state - please try again');
        return;
      }

      // Create transactions as-is from preview result
      const preview = state.preview;
      const transactions: CreateTransactionRequest[] = preview.transactions.map(
        (transaction) => ({
          user_id: userId,
          description: transaction.description,
          transaction_date: transaction.transaction_date,
          entries: transaction.entries.map((entry) => ({
            account_id: entry.account_id,
            amount: entry.amount,
            entry_type: entry.entry_type,
            description: entry.description,
          })),
        })
      );

      console.log('transactions to create', transactions);

      // Create all transactions in batch
      await apiClient.batchCreateTransactions(userId, transactions);

      // Calculate counts
      const transactionCount = transactions.length;
      const entryCount = transactions.reduce((sum, tx) => sum + tx.entries.length, 0);

      setCreatedCounts(transactionCount, entryCount);
      navigate('/upload/success');
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to create transactions');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    navigate('/upload/preview');
  };

  const handleStartOver = () => {
    clearState();
    navigate('/upload');
  };

  return (
    <div className="min-h-screen bg-background">
      <Header title="Upload Statement" />

      <div className="max-w-4xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        <StageProgress currentStage="confirmation" onStartOver={handleStartOver} />

        {error && (
          <div className="flex items-start gap-3 p-4 bg-error/10 rounded-lg border border-error/20">
            <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
            <p className="text-sm text-error">{error}</p>
          </div>
        )}

        <ConfirmationStep
          preview={state.preview}
          isCreating={isLoading}
          onConfirm={handleConfirm}
          onCancel={handleCancel}
        />
      </div>
    </div>
  );
}
