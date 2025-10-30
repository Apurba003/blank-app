import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  TextField,
  Typography,
  Paper,
  LinearProgress,
  Alert,
} from '@mui/material';

const SAMPLE_TEXT = "The quick brown fox jumps over the lazy dog";
const REQUIRED_SESSIONS = 3;

const KeystrokeCapture = ({ onCapture, sessionCount = REQUIRED_SESSIONS }) => {
  const [currentSession, setCurrentSession] = useState(0);
  const [inputValue, setInputValue] = useState('');
  const [keystrokeEvents, setKeystrokeEvents] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [message, setMessage] = useState('');
  const keyStateRef = useRef({});

  const handleKeyDown = (e) => {
    const key = e.key;
    const timestamp = performance.now();

    // Ignore modifier keys alone
    if (['Shift', 'Control', 'Alt', 'Meta'].includes(key)) {
      return;
    }

    if (!keyStateRef.current[key]) {
      keyStateRef.current[key] = {
        key: key,
        press_time: timestamp / 1000, // Convert to seconds
        pressure: 0.5, // Simulated pressure (web doesn't support real pressure)
      };
    }
  };

  const handleKeyUp = (e) => {
    const key = e.key;
    const timestamp = performance.now();

    if (keyStateRef.current[key]) {
      const keystroke = {
        ...keyStateRef.current[key],
        release_time: timestamp / 1000, // Convert to seconds
      };

      setKeystrokeEvents((prev) => [...prev, keystroke]);
      delete keyStateRef.current[key];
    }
  };

  const handleInputChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);

    // Check if sample text is completed
    if (newValue === SAMPLE_TEXT) {
      completeSession();
    }
  };

  const completeSession = () => {
    if (keystrokeEvents.length < 10) {
      setMessage('Please type more characters to complete the session.');
      return;
    }

    const newSessions = [...sessions, keystrokeEvents];
    setSessions(newSessions);
    setCurrentSession(currentSession + 1);
    setKeystrokeEvents([]);
    setInputValue('');
    keyStateRef.current = {};

    if (currentSession + 1 >= sessionCount) {
      setMessage('All sessions completed!');
      if (onCapture) {
        onCapture(newSessions);
      }
    } else {
      setMessage(`Session ${currentSession + 1} completed. Please continue with the next session.`);
    }
  };

  const progress = (currentSession / sessionCount) * 100;
  const isCompleted = currentSession >= sessionCount;

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Keystroke Dynamics Capture
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Session {currentSession + 1} of {sessionCount}
      </Typography>

      <LinearProgress variant="determinate" value={progress} sx={{ mb: 3 }} />

      {!isCompleted && (
        <>
          <Typography variant="body1" sx={{ mb: 2, fontFamily: 'monospace' }}>
            Type: <strong>{SAMPLE_TEXT}</strong>
          </Typography>

          <TextField
            fullWidth
            multiline
            rows={3}
            value={inputValue}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onKeyUp={handleKeyUp}
            placeholder="Start typing here..."
            disabled={isCompleted}
            autoFocus
            sx={{ mb: 2 }}
          />

          <Typography variant="caption" color="text.secondary">
            Captured keystrokes: {keystrokeEvents.length}
          </Typography>
        </>
      )}

      {message && (
        <Alert severity={isCompleted ? 'success' : 'info'} sx={{ mt: 2 }}>
          {message}
        </Alert>
      )}

      {isCompleted && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Keystroke enrollment data captured successfully! Total sessions: {sessions.length}
        </Alert>
      )}
    </Paper>
  );
};

export default KeystrokeCapture;
