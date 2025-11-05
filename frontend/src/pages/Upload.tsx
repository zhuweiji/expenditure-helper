import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '../components/layout/Header';
import { UploadZone } from '../components/UploadZone';
import { ArrowLeft } from 'lucide-react';

export function Upload() {
  const navigate = useNavigate();
  const [isUploading, setIsUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [uploadError, setUploadError] = useState('');

  const handleFileSelect = async (file: File) => {
    setIsUploading(true);
    setUploadError('');

    try {
      // Mock upload - in production, call apiClient.uploadStatement(file)
      await new Promise((resolve) => setTimeout(resolve, 2000));
      
      setUploadSuccess(true);
      setTimeout(() => {
        navigate('/transactions');
      }, 2000);
    } catch (error) {
      setUploadError('Failed to upload file. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background">
      <Header title="Upload Statement" />

      <div className="max-w-3xl mx-auto px-4 py-6 md:px-6 md:py-8 space-y-6">
        <button
          onClick={() => navigate(-1)}
          className="flex items-center text-secondary hover:text-primary transition-colors"
        >
          <ArrowLeft className="mr-2 h-5 w-5" />
          Back
        </button>

        <div className="card">
          <h2 className="text-xl font-semibold text-primary mb-2">
            Upload Credit Card Statement
          </h2>
          <p className="text-secondary mb-6">
            Upload your credit card statement in PDF, CSV, XLS, or XLSX format.
            We'll automatically extract and categorize your transactions.
          </p>

          <UploadZone
            onFileSelect={handleFileSelect}
            isUploading={isUploading}
            uploadSuccess={uploadSuccess}
            uploadError={uploadError}
          />
        </div>

        {/* Instructions */}
        <div className="card">
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
              <span>
                Our system automatically extracts transaction details
              </span>
            </li>
            <li className="flex">
              <span className="font-semibold text-accent mr-3">3.</span>
              <span>
                Transactions are categorized and added to your account
              </span>
            </li>
            <li className="flex">
              <span className="font-semibold text-accent mr-3">4.</span>
              <span>
                View insights and analytics on your spending patterns
              </span>
            </li>
          </ol>
        </div>
      </div>
    </div>
  );
}
