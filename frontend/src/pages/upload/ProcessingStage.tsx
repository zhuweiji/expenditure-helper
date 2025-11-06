import { useNavigate } from 'react-router-dom';
import { Header } from '../../components/layout/Header';
import { ProcessingStatusComponent } from '../../components/ProcessingStatus';
import { StageProgress } from './StageProgress';
import { useUploadFlow } from '../../hooks/useUploadFlow';
import { AlertCircle } from 'lucide-react';
import { useState } from 'react';

export function ProcessingStage() {
  const navigate = useNavigate();
  const { state, setStatementId, clearState } = useUploadFlow();
  const [error, setError] = useState('');

  if (!state.processingId) {
    return (
      <div className="min-h-screen bg-background">
        <Header title="Upload Statement" />
        <div className="max-w-4xl mx-auto px-4 py-6 md:px-6 md:py-8">
          <p className="text-error">No processing ID found. Please start over.</p>
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

  const handleProcessingComplete = async (newStatementId: number) => {
    setStatementId(newStatementId);
    navigate('/upload/preview');
  };

  const handleProcessingError = (errorMsg: string) => {
    setError(errorMsg);
  };

  const handleStartOver = () => {
    clearState();
    navigate('/upload');
  };

  return (
    <div className="min-h-screen bg-background">
      <Header title="Upload Statement" />

      <div className="max-w-4xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        <StageProgress currentStage="processing" onStartOver={handleStartOver} />

        {error && (
          <div className="flex items-start gap-3 p-4 bg-error/10 rounded-lg border border-error/20">
            <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
            <p className="text-sm text-error">{error}</p>
          </div>
        )}

        <ProcessingStatusComponent
          processingId={state.processingId}
          onCompleted={handleProcessingComplete}
          onError={handleProcessingError}
        />
      </div>
    </div>
  );
}
