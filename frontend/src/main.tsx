// Polyfill crypto.subtle for HTTP contexts (must be first import!)
import './crypto-polyfill';

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './services/i18n';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
