import { useState, useEffect, useCallback } from 'react';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiOptions {
  immediate?: boolean;
  refreshInterval?: number;
}

export function useApi<T>(
  apiCall: () => Promise<T>,
  options: UseApiOptions = {}
): UseApiState<T> & { refetch: () => Promise<void>; clearError: () => void } {
  const { immediate = true, refreshInterval } = options;
  
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    
    try {
      const result = await apiCall();
      setState({ data: result, loading: false, error: null });
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
      setState({ data: null, loading: false, error: errorMessage });
    }
  }, [apiCall]);

  const clearError = useCallback(() => {
    setState(prev => ({ ...prev, error: null }));
  }, []);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  useEffect(() => {
    if (refreshInterval && refreshInterval > 0) {
      const interval = setInterval(execute, refreshInterval);
      return () => clearInterval(interval);
    }
  }, [execute, refreshInterval]);

  return {
    ...state,
    refetch: execute,
    clearError,
  };
}

export function useAsyncAction<T, Args extends any[]>(
  action: (...args: Args) => Promise<T>
): {
  execute: (...args: Args) => Promise<T | null>;
  loading: boolean;
  error: string | null;
  clearError: () => void;
} {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const execute = useCallback(async (...args: Args): Promise<T | null> => {
    setLoading(true);
    setError(null);

    try {
      const result = await action(...args);
      setLoading(false);
      return result;
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'An error occurred';
      setError(errorMessage);
      setLoading(false);
      return null;
    }
  }, [action]);

  const clearError = useCallback(() => {
    setError(null);
  }, []);

  return {
    execute,
    loading,
    error,
    clearError,
  };
}