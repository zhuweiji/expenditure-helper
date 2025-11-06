import { useNavigate } from 'react-router-dom';
import { Header } from '../../components/layout/Header';
import { SuccessStep } from '../../components/SuccessStep';
import { useUploadFlow } from '../../hooks/useUploadFlow';
import { useEffect } from 'react';

export function SuccessStage() {
  const navigate = useNavigate();
  const { state, clearState } = useUploadFlow();

  // Clear state after a delay to allow user to see success message
  useEffect(() => {
    const timer = setTimeout(() => {
      clearState();
    }, 5000);

    return () => clearTimeout(timer);
  }, [clearState]);

  // Redirect to upload if no transaction counts (no data to display)
  if (state.totalCreatedTransactions === 0) {
    return (
      <div className="min-h-screen bg-background">
        <Header title="Upload Statement" />
        <div className="max-w-4xl mx-auto px-4 py-6 md:px-6 md:py-8">
          <p className="text-error">No transactions were created.</p>
          <button
            onClick={() => navigate('/upload')}
            className="mt-4 px-4 py-2 bg-accent text-white rounded hover:bg-accent/90"
          >
            Upload Another Statement
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <Header title="Upload Statement" />

      <div className="max-w-4xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        <SuccessStep
          transactionCount={state.totalCreatedTransactions}
          entryCount={state.totalCreatedEntries}
        />
      </div>
    </div>
  );
}
