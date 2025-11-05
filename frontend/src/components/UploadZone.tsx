import { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, FileText, CheckCircle, XCircle } from 'lucide-react';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isUploading?: boolean;
  uploadSuccess?: boolean;
  uploadError?: string;
}

export function UploadZone({
  onFileSelect,
  isUploading = false,
  uploadSuccess = false,
  uploadError,
}: UploadZoneProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onFileSelect(acceptedFiles[0]);
      }
    },
    [onFileSelect]
  );

  const { getRootProps, getInputProps, isDragActive, acceptedFiles } =
    useDropzone({
      onDrop,
      accept: {
        'application/pdf': ['.pdf'],
        'text/csv': ['.csv'],
        'application/vnd.ms-excel': ['.xls'],
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': [
          '.xlsx',
        ],
      },
      maxFiles: 1,
      disabled: isUploading,
    });

  return (
    <div className="w-full">
      <div
        {...getRootProps()}
        className={`card border-2 border-dashed cursor-pointer transition-all ${
          isDragActive
            ? 'border-accent bg-accent/5'
            : 'border-secondary/30 hover:border-accent/50'
        } ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center justify-center py-12">
          {uploadSuccess ? (
            <>
              <CheckCircle className="h-16 w-16 text-success mb-4" />
              <p className="text-lg font-medium text-success">Upload Successful!</p>
              <p className="text-sm text-secondary mt-2">
                Your statement has been processed
              </p>
            </>
          ) : uploadError ? (
            <>
              <XCircle className="h-16 w-16 text-error mb-4" />
              <p className="text-lg font-medium text-error">Upload Failed</p>
              <p className="text-sm text-secondary mt-2">{uploadError}</p>
            </>
          ) : isUploading ? (
            <>
              <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-accent mb-4"></div>
              <p className="text-lg font-medium text-primary">Uploading...</p>
              <p className="text-sm text-secondary mt-2">Please wait</p>
            </>
          ) : acceptedFiles.length > 0 ? (
            <>
              <FileText className="h-16 w-16 text-accent mb-4" />
              <p className="text-lg font-medium text-primary">
                {acceptedFiles[0].name}
              </p>
              <p className="text-sm text-secondary mt-2">
                {(acceptedFiles[0].size / 1024).toFixed(2)} KB
              </p>
            </>
          ) : (
            <>
              <Upload className="h-16 w-16 text-secondary mb-4" />
              <p className="text-lg font-medium text-primary">
                {isDragActive
                  ? 'Drop your statement here'
                  : 'Drag & drop your statement'}
              </p>
              <p className="text-sm text-secondary mt-2">
                or click to browse files
              </p>
              <p className="text-xs text-secondary mt-4">
                Supported formats: PDF, CSV, XLS, XLSX
              </p>
            </>
          )}
        </div>
      </div>

      {acceptedFiles.length > 0 && !isUploading && !uploadSuccess && (
        <button
          onClick={() => onFileSelect(acceptedFiles[0])}
          className="btn-primary w-full mt-4"
        >
          Upload Statement
        </button>
      )}
    </div>
  );
}
