import { useState, useCallback } from 'react';
import { apiService, ApiError } from '@/services/api';
import { AnalysisRequest, AnalysisState } from '@/types';
import { ERROR_MESSAGES, LOADING_MESSAGES } from '@/utils/constants';

export const useAnalysis = () => {
  const [state, setState] = useState<AnalysisState>({
    isLoading: false,
    data: null,
    error: null,
  });

  const [loadingMessage, setLoadingMessage] = useState<string>('');
  const [progress, setProgress] = useState<number>(0);

  // Simulate progress during analysis
  const simulateProgress = useCallback(() => {
    const messages = LOADING_MESSAGES;
    let currentStep = 0;
    
    const progressInterval = setInterval(() => {
      if (currentStep < messages.length) {
        setLoadingMessage(messages[currentStep]);
        setProgress(((currentStep + 1) / messages.length) * 100);
        currentStep++;
      } else {
        clearInterval(progressInterval);
      }
    }, 2000); // Change message every 2 seconds

    return progressInterval;
  }, []);

  const analyzeRepository = useCallback(async (request: AnalysisRequest) => {
    setState(prev => ({
      ...prev,
      isLoading: true,
      error: null,
    }));

    setProgress(0);
    setLoadingMessage(LOADING_MESSAGES[0]);
    
    const progressInterval = simulateProgress();

    try {
      const response = await apiService.analyzeRepository(request);
      
      // Clear progress simulation
      clearInterval(progressInterval);
      setProgress(100);
      setLoadingMessage('Analysis complete!');

      // Small delay to show completion
      setTimeout(() => {
        setState({
          isLoading: false,
          data: response,
          error: null,
        });
        setProgress(0);
        setLoadingMessage('');
      }, 500);

    } catch (error) {
      clearInterval(progressInterval);
      setProgress(0);
      setLoadingMessage('');

      let errorMessage: string = ERROR_MESSAGES.unknownError;

      if (error instanceof ApiError) {
        switch (error.status) {
          case 404:
            errorMessage = 'Repository not found. Please check the URL.';
            break;
          case 429:
            errorMessage = 'Too many requests. Please wait a moment and try again.';
            break;
          case 401:
            errorMessage = 'Authentication failed. Please try again.';
            break;
          case 500:
            errorMessage = ERROR_MESSAGES.serverError;
            break;
          default:
            errorMessage = error.message || ERROR_MESSAGES.unknownError;
        }
      } else if (error instanceof TypeError) {
        errorMessage = ERROR_MESSAGES.networkError;
      }

      setState({
        isLoading: false,
        data: null,
        error: errorMessage,
      });
    }
  }, [simulateProgress]);

  const clearError = useCallback(() => {
    setState(prev => ({
      ...prev,
      error: null,
    }));
  }, []);

  const reset = useCallback(() => {
    setState({
      isLoading: false,
      data: null,
      error: null,
    });
    setProgress(0);
    setLoadingMessage('');
  }, []);

  return {
    // State
    isLoading: state.isLoading,
    data: state.data,
    error: state.error,
    loadingMessage,
    progress,
    
    // Actions
    analyzeRepository,
    clearError,
    reset,
  };
};