import React from 'react';
import { createRoot } from 'react-dom/client';
import ErrorBoundary from './ErrorBoundary';
import StreamlitApp from './StreamlitApp';
import './styles.css';

createRoot(document.getElementById('root') as HTMLElement).render(
  <ErrorBoundary>
    <StreamlitApp />
  </ErrorBoundary>,
);
