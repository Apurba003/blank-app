import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Webcam from 'react-webcam';
import {
  Container,
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Alert,
  Grid,
  Tabs,
  Tab,
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';

const AuthenticationPage = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const webcamRef = useRef(null);

  const [tabValue, setTabValue] = useState(0);
  const [userId, setUserId] = useState('');
  const [inputValue, setInputValue] = useState('');
  const [keystrokeEvents, setKeystrokeEvents] = useState([]);
  const [faceImage, setFaceImage] = useState(null);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const keyStateRef = useRef({});

  const handleKeyDown = (e) => {
    const key = e.key;
    const timestamp = performance.now();

    if (['Shift', 'Control', 'Alt', 'Meta'].includes(key)) {
      return;
    }

    if (!keyStateRef.current[key]) {
      keyStateRef.current[key] = {
        key: key,
        press_time: timestamp / 1000,
        pressure: 0.5,
      };
    }
  };

  const handleKeyUp = (e) => {
    const key = e.key;
    const timestamp = performance.now();

    if (keyStateRef.current[key]) {
      const keystroke = {
        ...keyStateRef.current[key],
        release_time: timestamp / 1000,
      };

      setKeystrokeEvents((prev) => [...prev, keystroke]);
      delete keyStateRef.current[key];
    }
  };

  const captureFace = () => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      setFaceImage(imageSrc);
      setSuccess('Face captured successfully');
    }
  };

  const handleAuthenticateKeystroke = async () => {
    setError('');
    setSuccess('');

    if (!userId) {
      setError('Please enter your username');
      return;
    }

    if (keystrokeEvents.length < 10) {
      setError('Please type more characters');
      return;
    }

    setLoading(true);

    try {
      const response = await authAPI.authenticateKeystroke(userId, keystrokeEvents);

      if (response.authenticated && response.token) {
        login(response.token);
        navigate('/dashboard');
      } else {
        setError('Authentication failed. Please try again.');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleAuthenticateFace = async () => {
    setError('');
    setSuccess('');

    if (!userId) {
      setError('Please enter your username');
      return;
    }

    if (!faceImage) {
      setError('Please capture your face');
      return;
    }

    setLoading(true);

    try {
      const response = await authAPI.authenticateFace(userId, faceImage);

      if (response.authenticated && response.token) {
        login(response.token);
        navigate('/dashboard');
      } else {
        setError('Authentication failed. Please try again.');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  const handleAuthenticateMFA = async () => {
    setError('');
    setSuccess('');

    if (!userId) {
      setError('Please enter your username');
      return;
    }

    if (keystrokeEvents.length < 10) {
      setError('Please type more characters');
      return;
    }

    if (!faceImage) {
      setError('Please capture your face');
      return;
    }

    setLoading(true);

    try {
      const response = await authAPI.authenticateMFA(
        userId,
        keystrokeEvents,
        faceImage,
        'weighted_sum'
      );

      if (response.authenticated && response.token) {
        login(response.token);
        navigate('/dashboard');
      } else {
        setError('Authentication failed. Please try again.');
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Authentication failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 4 }}>
          <Typography variant="h4" component="h1" gutterBottom align="center">
            Authenticate
          </Typography>

          <TextField
            fullWidth
            label="Username"
            value={userId}
            onChange={(e) => setUserId(e.target.value)}
            margin="normal"
            required
          />

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mt: 2 }}>
              {success}
            </Alert>
          )}

          <Tabs value={tabValue} onChange={(e, v) => setTabValue(v)} sx={{ mt: 3, mb: 2 }}>
            <Tab label="Keystroke" />
            <Tab label="Face" />
            <Tab label="Multi-Factor" />
          </Tabs>

          {tabValue === 0 && (
            <Box>
              <Typography variant="body2" sx={{ mb: 2 }}>
                Type naturally in the field below:
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={4}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                onKeyUp={handleKeyUp}
                placeholder="Start typing here..."
                autoFocus
              />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                Captured keystrokes: {keystrokeEvents.length}
              </Typography>
              <Button
                fullWidth
                variant="contained"
                onClick={handleAuthenticateKeystroke}
                disabled={loading || keystrokeEvents.length < 10}
                sx={{ mt: 2 }}
              >
                {loading ? 'Authenticating...' : 'Authenticate with Keystroke'}
              </Button>
            </Box>
          )}

          {tabValue === 1 && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Webcam
                    audio={false}
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    videoConstraints={{ facingMode: 'user' }}
                    style={{ width: '100%', borderRadius: 8 }}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    fullWidth
                    variant="outlined"
                    onClick={captureFace}
                    sx={{ mb: 2 }}
                  >
                    Capture Face
                  </Button>
                  <Button
                    fullWidth
                    variant="contained"
                    onClick={handleAuthenticateFace}
                    disabled={loading || !faceImage}
                  >
                    {loading ? 'Authenticating...' : 'Authenticate with Face'}
                  </Button>
                </Grid>
              </Grid>
            </Box>
          )}

          {tabValue === 2 && (
            <Box>
              <Typography variant="body2" sx={{ mb: 2 }}>
                1. Type naturally in the field below:
              </Typography>
              <TextField
                fullWidth
                multiline
                rows={3}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                onKeyUp={handleKeyUp}
                placeholder="Start typing here..."
                sx={{ mb: 2 }}
              />
              <Typography variant="caption" color="text.secondary" sx={{ mb: 2, display: 'block' }}>
                Captured keystrokes: {keystrokeEvents.length}
              </Typography>

              <Typography variant="body2" sx={{ mb: 2 }}>
                2. Capture your face:
              </Typography>
              <Webcam
                audio={false}
                ref={webcamRef}
                screenshotFormat="image/jpeg"
                videoConstraints={{ facingMode: 'user' }}
                style={{ width: '100%', borderRadius: 8, marginBottom: 16 }}
              />
              <Button
                fullWidth
                variant="outlined"
                onClick={captureFace}
                sx={{ mb: 2 }}
              >
                Capture Face
              </Button>

              <Button
                fullWidth
                variant="contained"
                onClick={handleAuthenticateMFA}
                disabled={loading || keystrokeEvents.length < 10 || !faceImage}
              >
                {loading ? 'Authenticating...' : 'Authenticate with MFA'}
              </Button>
            </Box>
          )}

          <Button
            fullWidth
            variant="text"
            onClick={() => navigate('/')}
            sx={{ mt: 2 }}
          >
            Back to Home
          </Button>
        </Paper>
      </Box>
    </Container>
  );
};

export default AuthenticationPage;
