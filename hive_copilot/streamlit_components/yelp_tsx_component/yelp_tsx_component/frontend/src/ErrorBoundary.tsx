import React from 'react';

type Props = {
  children: React.ReactNode;
};

type State = {
  error: Error | null;
};

export default class ErrorBoundary extends React.Component<Props, State> {
  state: State = {
    error: null,
  };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error) {
    console.error('Custom component render failed:', error);
  }

  render() {
    if (this.state.error) {
      return (
        <div
          style={{
            minHeight: '100vh',
            padding: '24px',
            background: '#f9f8f6',
            color: '#1a1a1a',
            fontFamily: 'Inter, sans-serif',
          }}
        >
          <h1 style={{ margin: 0, fontSize: '20px' }}>Hive Copilot UI failed to render</h1>
          <pre
            style={{
              marginTop: '16px',
              padding: '16px',
              borderRadius: '12px',
              background: '#1a1a1a',
              color: '#f9f8f6',
              overflowX: 'auto',
              whiteSpace: 'pre-wrap',
            }}
          >
            {this.state.error.stack || this.state.error.message}
          </pre>
        </div>
      );
    }

    return this.props.children;
  }
}
