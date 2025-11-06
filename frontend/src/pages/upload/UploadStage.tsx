import { useNavigate } from 'react-router-dom';
import { Header } from '../../components/layout/Header';
import { UploadZone } from '../../components/UploadZone';
import { apiClient, getCurrentUserId, type ApiError } from '../../lib/api';
import { useUploadFlow } from '../../hooks/useUploadFlow';
import { useState } from 'react';

export function UploadStage() {
  const navigate = useNavigate();
  const { setProcessingId } = useUploadFlow();
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const userId = getCurrentUserId();

  const handleFileSelect = async (file: File) => {
    setIsLoading(true);
    setError('');

    try {
      if (!userId) {
        setError('You must be logged in to upload statements.');
        return;
      }

      const response = await apiClient.uploadStatement(file, userId);
      setProcessingId(response.id);
      navigate('/upload/processing');
    } catch (err) {
      const apiError = err as ApiError;
      setError(apiError.message || 'Failed to upload file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header title="Upload Statement" />

      <div className="max-w-4xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        <div className="card space-y-6">
          <div>
            <h2 className="text-xl font-semibold text-primary mb-2">
              Upload Credit Card Statement
            </h2>
            <p className="text-secondary">
              Upload your credit card statement in PDF, CSV, XLS, or XLSX format.
              We'll automatically extract and categorize your transactions.
            </p>
          </div>

          <UploadZone
            onFileSelect={handleFileSelect}
            isUploading={isLoading}
            uploadSuccess={false}
            uploadError={error}
          />

          {/* Instructions */}
          <div className="border-t border-secondary/20 pt-6">
            <h3 className="text-lg font-semibold text-primary mb-4">
              How it works
            </h3>
            <ol className="space-y-3 text-secondary">
              <li className="flex">
                <span className="font-semibold text-accent mr-3">1.</span>
                <span>Upload your credit card statement in a supported format</span>
              </li>
              <li className="flex">
                <span className="font-semibold text-accent mr-3">2.</span>
                <span>Our system extracts transaction details</span>
              </li>
              <li className="flex">
                <span className="font-semibold text-accent mr-3">3.</span>
                <span>Review and confirm the extracted data</span>
              </li>
              <li className="flex">
                <span className="font-semibold text-accent mr-3">4.</span>
                <span>Transactions are added to your ledger</span>
              </li>
            </ol>
          </div>
        </div>
      </div>
    </div>
  );
}
