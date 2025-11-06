import { CheckCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface SuccessStepProps {
  transactionCount: number;
  entryCount: number;
}

export function SuccessStep({ transactionCount, entryCount }: SuccessStepProps) {
  const navigate = useNavigate();

  return (
    <div className="card space-y-6 text-center py-8">
      <div className="flex justify-center">
        <div className="relative">
          <div className="absolute inset-0 bg-success/20 rounded-full blur-xl"></div>
          <CheckCircle className="relative w-20 h-20 text-success" />
        </div>
      </div>

      <div>
        <h2 className="text-2xl font-bold text-primary mb-2">
          Success!
        </h2>
        <p className="text-secondary">
          Your statement has been processed and entries created
        </p>
      </div>

      <div className="bg-accent/5 rounded-lg p-6 space-y-4">
        <div>
          <p className="text-sm text-secondary">Transactions Created</p>
          <p className="text-3xl font-bold text-primary">{transactionCount}</p>
        </div>
        <div>
          <p className="text-sm text-secondary">Total Entries</p>
          <p className="text-3xl font-bold text-primary">{entryCount}</p>
        </div>
      </div>

      <div className="flex flex-col gap-3">
        <button
          onClick={() => navigate('/transactions')}
          className="btn-primary w-full"
        >
          View Transactions
        </button>
        <button
          onClick={() => window.location.reload()}
          className="btn-secondary w-full"
        >
          Upload Another Statement
        </button>
      </div>
    </div>
  );
}
