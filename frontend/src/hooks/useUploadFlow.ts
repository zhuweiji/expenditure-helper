import { useCallback, useEffect, useState } from 'react';
import type {
  PrepareEntriesResponse,
} from '../lib/types';

export type FlowStage =
  | 'upload'
  | 'processing'
  | 'preview'
  | 'confirmation'
  | 'creating'
  | 'success';

const STORAGE_KEY = 'uploadFlow';

interface UploadFlowState {
  processingId: number | null;
  statementId: number | null;
  preview: PrepareEntriesResponse | null;
  selectedCreditCardAccountId: number | null;
  selectedDefaultExpenseAccountId: number | null;
  totalCreatedTransactions: number;
  totalCreatedEntries: number;
}

const defaultState: UploadFlowState = {
  processingId: null,
  statementId: null,
  preview: null,
  selectedCreditCardAccountId: null,
  selectedDefaultExpenseAccountId: null,
  totalCreatedTransactions: 0,
  totalCreatedEntries: 0,
};

export function useUploadFlow() {
  const [state, setState] = useState<UploadFlowState>(defaultState);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        setState(JSON.parse(saved));
      } catch (error) {
        console.error('Failed to parse upload flow state:', error);
        localStorage.removeItem(STORAGE_KEY);
      }
    }
    setIsLoaded(true);
  }, []);

  // Save to localStorage whenever state changes
  useEffect(() => {
    if (isLoaded) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    }
  }, [state, isLoaded]);

  const setProcessingId = useCallback((id: number | null) => {
    setState(prev => ({ ...prev, processingId: id }));
  }, []);

  const setStatementId = useCallback((id: number | null) => {
    setState(prev => ({ ...prev, statementId: id }));
  }, []);

  const setPreview = useCallback((preview: PrepareEntriesResponse | null) => {
    setState(prev => ({ ...prev, preview }));
  }, []);

  const setSelectedAccounts = useCallback(
    (creditCardAccountId: number, defaultExpenseAccountId: number) => {
      setState(prev => ({
        ...prev,
        selectedCreditCardAccountId: creditCardAccountId,
        selectedDefaultExpenseAccountId: defaultExpenseAccountId,
      }));
    },
    []
  );

  const setCreatedCounts = useCallback(
    (transactions: number, entries: number) => {
      setState(prev => ({
        ...prev,
        totalCreatedTransactions: transactions,
        totalCreatedEntries: entries,
      }));
    },
    []
  );

  const clearState = useCallback(() => {
    setState(defaultState);
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  return {
    state,
    isLoaded,
    setProcessingId,
    setStatementId,
    setPreview,
    setSelectedAccounts,
    setCreatedCounts,
    clearState,
  };
}
