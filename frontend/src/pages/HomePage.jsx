import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Box,
  Typography,
  Button,
  Paper,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  Fingerprint as FingerprintIcon,
  Face as FaceIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';

const HomePage = () => {
  const navigate = useNavigate();

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 8 }}>
        <Paper elevation={3} sx={{ p: 4, textAlign: 'center', mb: 6 }}>
          <SecurityIcon sx={{ fontSize: 80, color: 'primary.main', mb: 2 }} />
          <Typography variant="h2" component="h1" gutterBottom>
            Multi-Factor Authentication System
          </Typography>
          <Typography variant="h6" color="text.secondary" paragraph>
            Advanced biometric authentication using keystroke dynamics and face recognition
          </Typography>
          <Box sx={{ mt: 4 }}>
            <Button
              variant="contained"
              size="large"
              onClick={() => navigate('/register')}
              sx={{ mr: 2 }}
            >
              Get Started
            </Button>
            <Button
              variant="outlined"
              size="large"
              onClick={() => navigate('/authenticate')}
            >
              Sign In
            </Button>
          </Box>
        </Paper>

        <Typography variant="h4" gutterBottom sx={{ mb: 3 }}>
          Features
        </Typography>

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <FingerprintIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  Keystroke Dynamics
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Analyze your unique typing patterns including dwell time, flight time,
                  and pressure to create a behavioral biometric profile.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <FaceIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  Face Recognition
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Real-time face detection with liveness detection to prevent spoofing.
                  Captures facial landmarks and embeddings for secure authentication.
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <SecurityIcon sx={{ fontSize: 60, color: 'primary.main', mb: 2 }} />
                <Typography variant="h5" gutterBottom>
                  Advanced Security
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Template encryption, secure storage, rate limiting, and comprehensive
                  audit logging for enterprise-grade security.
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        <Box sx={{ mt: 6, p: 3, bgcolor: 'background.paper', borderRadius: 1 }}>
          <Typography variant="h5" gutterBottom>
            How It Works
          </Typography>
          <Typography variant="body1" paragraph>
            1. <strong>Register:</strong> Create your account with a username and password
          </Typography>
          <Typography variant="body1" paragraph>
            2. <strong>Enroll:</strong> Capture your keystroke patterns and face samples
          </Typography>
          <Typography variant="body1" paragraph>
            3. <strong>Authenticate:</strong> Sign in using both biometric factors
          </Typography>
          <Typography variant="body1">
            4. <strong>Access:</strong> Enjoy secure access to your account
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default HomePage;
