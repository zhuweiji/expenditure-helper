import { useEffect, useState } from 'react';
import { AlertCircle, Loader } from 'lucide-react';
import { apiClient, getCurrentUserId, type ApiError } from '../lib/api';
import type { ProcessingStatus } from '../lib/types';

interface ProcessingStatusProps {
  processingId: number;
  onCompleted: (statementId: number) => void;
  onError: (error: string) => void;
}

const POLLING_INTERVAL = 3000; // 3 seconds
const MAX_POLLING_TIME = 5 * 60 * 1000; // 5 minutes

export function ProcessingStatusComponent({
  processingId,
  onCompleted,
  onError,
}: ProcessingStatusProps) {
  const [status, setStatus] = useState<ProcessingStatus | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    const userId = getCurrentUserId();
    if (!userId) {
      onError('User not authenticated');
      return;
    }

    const startTime = Date.now();
    let pollInterval: ReturnType<typeof setInterval>;

    const pollStatus = async () => {
      try {
        const data = await apiClient.getProcessingStatus(processingId, userId);
        const statusData = data as ProcessingStatus;
        setStatus(statusData);

        if (statusData.status === 'completed') {
          setIsPolling(false);
          onCompleted(statusData.statement_id);
        } else if (statusData.status === 'errored') {
          setIsPolling(false);
          onError(statusData.error_message || 'Processing failed');
        } else if (Date.now() - startTime > MAX_POLLING_TIME) {
          setIsPolling(false);
          onError('Processing timeout - please try again');
        }
      } catch (error) {
        const apiError = error as ApiError;
        setIsPolling(false);
        onError(apiError.message || 'Failed to check processing status');
      }
    };

    // Poll immediately, then at intervals
    pollStatus();
    if (isPolling) {
      pollInterval = setInterval(pollStatus, POLLING_INTERVAL);
    }

    return () => {
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [processingId, onCompleted, onError, isPolling]);

  const getStatusLabel = (status: string): string => {
    switch (status) {
      case 'pending':
        return 'Queued';
      case 'in_progress':
        return 'Processing';
      case 'completed':
        return 'Complete';
      case 'errored':
        return 'Error';
      default:
        return status;
    }
  };

  const getProgressPercentage = (status: string): number => {
    switch (status) {
      case 'pending':
        return 25;
      case 'in_progress':
        return 50;
      case 'completed':
        return 100;
      case 'errored':
        return 0;
      default:
        return 0;
    }
  };

  if (!status) {
    return (
      <div className="card space-y-4">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
        </div>
        <p className="text-center text-secondary">Starting process...</p>
      </div>
    );
  }

  return (
    <div className="card space-y-6">
      <div>
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-primary">Processing Statement</h3>
          <span className="text-sm font-medium text-accent">
            {getStatusLabel(status.status)}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-secondary/20 rounded-full h-2 overflow-hidden">
          <div
            className="bg-accent h-full transition-all duration-300"
            style={{ width: `${getProgressPercentage(status.status)}%` }}
          />
        </div>
      </div>

      {/* Status Timeline */}
      <div className="space-y-3">
        {/* Pending */}
        <div className="flex items-start gap-3">
          <div
            className={`w-3 h-3 rounded-full mt-1.5 flex-shrink-0 ${
              status.status !== 'pending' ? 'bg-success' : 'bg-secondary/30'
            }`}
          />
          <div className="flex-1">
            <p className="text-sm font-medium text-primary">Queued</p>
            {status.created_at && (
              <p className="text-xs text-secondary">
                {new Date(status.created_at).toLocaleTimeString()}
              </p>
            )}
          </div>
        </div>

        {/* In Progress */}
        <div className="flex items-start gap-3">
          <div
            className={`w-3 h-3 rounded-full mt-1.5 flex-shrink-0 ${
              status.status === 'completed' || status.status === 'errored'
                ? 'bg-success'
                : status.status === 'in_progress'
                  ? 'bg-accent animate-pulse'
                  : 'bg-secondary/30'
            }`}
          />
          <div className="flex-1">
            <p className="text-sm font-medium text-primary">Processing</p>
            {status.started_at && (
              <p className="text-xs text-secondary">
                {new Date(status.started_at).toLocaleTimeString()}
              </p>
            )}
          </div>
        </div>

        {/* Completed/Error */}
        {(status.status === 'completed' || status.status === 'errored') && (
          <div className="flex items-start gap-3">
            <div
              className={`w-3 h-3 rounded-full mt-1.5 flex-shrink-0 ${
                status.status === 'completed' ? 'bg-success' : 'bg-error'
              }`}
            />
            <div className="flex-1">
              <p className="text-sm font-medium text-primary">
                {status.status === 'completed' ? 'Complete' : 'Error'}
              </p>
              {status.completed_at && (
                <p className="text-xs text-secondary">
                  {new Date(status.completed_at).toLocaleTimeString()}
                </p>
              )}
              {status.error_message && (
                <div className="mt-2 flex items-start gap-2 p-3 bg-error/10 rounded border border-error/20">
                  <AlertCircle className="w-4 h-4 text-error flex-shrink-0 mt-0.5" />
                  <p className="text-sm text-error">{status.error_message}</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Status Message */}
      {status.status === 'in_progress' && (
        <div className="flex items-center justify-center gap-2">
          <Loader className="w-4 h-4 animate-spin text-accent" />
          <p className="text-sm text-secondary">
            This may take a few minutes...
          </p>
        </div>
      )}
    </div>
  );
}
