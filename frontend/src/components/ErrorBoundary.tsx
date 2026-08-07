import React, { Component, type ErrorInfo, type ReactNode } from 'react';
import { ErrorState } from './ErrorState';

type Props = {
  children: ReactNode;
  fallbackMessage?: string;
};

type State = {
  hasError: boolean;
  message: string;
};

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, message: '' };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, message: error.message };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary:', error, info.componentStack);
  }

  handleRetry = () => {
    this.setState({ hasError: false, message: '' });
  };

  render() {
    if (this.state.hasError) {
      return (
        <ErrorState
          message={this.props.fallbackMessage || this.state.message}
          onRetry={this.handleRetry}
        />
      );
    }
    return this.props.children;
  }
}
