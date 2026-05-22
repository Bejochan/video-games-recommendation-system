import React, { useEffect, useState } from 'react';
import { testBackend } from './api/backend';

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    testBackend().then(setMessage);
  }, []);

  return (
    <div>
      <h1>Test Backend Connection</h1>
      <p>{message}</p>
    </div>
  );
}

export default App;