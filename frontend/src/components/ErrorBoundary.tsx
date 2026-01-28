import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    // 향후 에러 로깅 서비스 연동 가능 (예: Sentry)
    // if (window.Sentry) {
    //   window.Sentry.captureException(error, {
    //     contexts: {
    //       react: {
    //         componentStack: errorInfo.componentStack,
    //       },
    //     },
    //   });
    // }
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: undefined });
  };

  public render() {
    if (this.state.hasError) {
      const { error } = this.state;
      const message = error?.message ?? '알 수 없는 오류가 발생했습니다.';

      return (
        <div className="min-h-screen flex items-center justify-center bg-white p-6">
          <div className="text-center max-w-md">
            <h1 className="text-2xl font-semibold text-black mb-4 ibm-plex-sans-kr-bold">
              오류가 발생했습니다
            </h1>
            <p className="text-sm text-black/80 mb-2 ibm-plex-sans-kr-regular" style={{ letterSpacing: '-0.42px' }}>
              {message}
            </p>
            <p className="text-xs text-black/60 mb-6 ibm-plex-sans-kr-regular" style={{ letterSpacing: '-0.36px' }}>
              페이지를 새로고침하거나 다시 시도해주세요.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                type="button"
                onClick={this.handleRetry}
                className="px-4 py-2 text-sm font-medium text-white bg-black border border-black rounded-lg hover:bg-gray-800 ibm-plex-sans-kr-medium transition-colors"
              >
                다시 시도
              </button>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="px-4 py-2 text-sm font-medium text-black bg-white border border-black rounded-lg hover:bg-black hover:text-white ibm-plex-sans-kr-medium transition-colors"
              >
                새로고침
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
