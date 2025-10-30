import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Stepper,
  Step,
  StepLabel,
  Button,
  Paper,
  Alert,
} from '@mui/material';
import KeystrokeCapture from '../components/KeystrokeCapture';
import FaceCapture from '../components/FaceCapture';
import { authAPI } from '../services/api';

const steps = ['Keystroke Dynamics', 'Face Recognition', 'Complete'];

const EnrollmentPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const userId = location.state?.userId || '';

  const [activeStep, setActiveStep] = useState(0);
  const [keystrokeSessions, setKeystrokeSessions] = useState(null);
  const [faceImages, setFaceImages] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleKeystrokeCapture = (sessions) => {
    setKeystrokeSessions(sessions);
  };

  const handleFaceCapture = (images) => {
    setFaceImages(images);
  };

  const handleNext = async () => {
    setError('');

    if (activeStep === 0) {
      // Enroll keystroke
      if (!keystrokeSessions || keystrokeSessions.length < 3) {
        setError('Please complete all keystroke sessions');
        return;
      }

      setLoading(true);
      try {
        await authAPI.enrollKeystroke(userId, keystrokeSessions);
        setActiveStep(1);
      } catch (err) {
        setError(err.response?.data?.error || 'Keystroke enrollment failed');
      } finally {
        setLoading(false);
      }
    } else if (activeStep === 1) {
      // Enroll face
      if (!faceImages || faceImages.length < 3) {
        setError('Please capture all required face images');
        return;
      }

      setLoading(true);
      try {
        await authAPI.enrollFace(userId, faceImages);
        setActiveStep(2);
      } catch (err) {
        setError(err.response?.data?.error || 'Face enrollment failed');
      } finally {
        setLoading(false);
      }
    } else if (activeStep === 2) {
      // Complete - redirect to authentication
      navigate('/authenticate');
    }
  };

  const handleBack = () => {
    setActiveStep((prev) => prev - 1);
  };

  const getStepContent = (step) => {
    switch (step) {
      case 0:
        return (
          <KeystrokeCapture
            onCapture={handleKeystrokeCapture}
            sessionCount={3}
          />
        );
      case 1:
        return (
          <FaceCapture
            onCapture={handleFaceCapture}
            imageCount={3}
          />
        );
      case 2:
        return (
          <Paper elevation={3} sx={{ p: 4, textAlign: 'center' }}>
            <Typography variant="h5" gutterBottom>
              Enrollment Complete!
            </Typography>
            <Typography variant="body1" color="text.secondary" paragraph>
              Your biometric profiles have been successfully created.
              You can now authenticate using both keystroke dynamics and face recognition.
            </Typography>
            <Alert severity="success" sx={{ mt: 2 }}>
              Both keystroke and face biometrics enrolled successfully
            </Alert>
          </Paper>
        );
      default:
        return 'Unknown step';
    }
  };

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Biometric Enrollment
        </Typography>

        <Typography variant="body1" color="text.secondary" paragraph align="center">
          User: <strong>{userId}</strong>
        </Typography>

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Box sx={{ mb: 4 }}>{getStepContent(activeStep)}</Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            disabled={activeStep === 0}
            onClick={handleBack}
          >
            Back
          </Button>

          <Button
            variant="contained"
            onClick={handleNext}
            disabled={
              loading ||
              (activeStep === 0 && !keystrokeSessions) ||
              (activeStep === 1 && !faceImages)
            }
          >
            {loading
              ? 'Processing...'
              : activeStep === steps.length - 1
              ? 'Go to Sign In'
              : 'Next'}
          </Button>
        </Box>
      </Box>
    </Container>
  );
};

export default EnrollmentPage;
