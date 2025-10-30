import React, { useState, useEffect } from 'react';
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
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import { useAuth } from '../contexts/AuthContext';
import { authAPI } from '../services/api';

const DashboardPage = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [userStatus, setUserStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusData, metricsData] = await Promise.all([
          authAPI.getUserStatus(user.userId),
          authAPI.getSystemMetrics(),
        ]);

        setUserStatus(statusData);
        setMetrics(metricsData);
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to load dashboard data');
      } finally {
        setLoading(false);
      }
    };

    if (user?.userId) {
      fetchData();
    }
  }, [user]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box
          display="flex"
          justifyContent="center"
          alignItems="center"
          minHeight="80vh"
        >
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Paper elevation={3} sx={{ p: 3, mb: 4 }}>
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            flexWrap="wrap"
          >
            <Box>
              <Typography variant="h4" component="h1" gutterBottom>
                Dashboard
              </Typography>
              <Typography variant="body1" color="text.secondary">
                Welcome, <strong>{user?.userId}</strong>
              </Typography>
            </Box>
            <Button variant="outlined" onClick={handleLogout}>
              Logout
            </Button>
          </Box>
        </Paper>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
          Your Enrollment Status
        </Typography>

        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  {userStatus?.keystroke_enrolled ? (
                    <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                  ) : (
                    <CancelIcon color="error" sx={{ mr: 1 }} />
                  )}
                  <Typography variant="h6">Keystroke Dynamics</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {userStatus?.keystroke_enrolled
                    ? 'Enrolled and active'
                    : 'Not enrolled'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  {userStatus?.face_enrolled ? (
                    <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                  ) : (
                    <CancelIcon color="error" sx={{ mr: 1 }} />
                  )}
                  <Typography variant="h6">Face Recognition</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {userStatus?.face_enrolled ? 'Enrolled and active' : 'Not enrolled'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={4}>
            <Card>
              <CardContent>
                <Box display="flex" alignItems="center" mb={2}>
                  {userStatus?.mfa_enabled ? (
                    <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                  ) : (
                    <CancelIcon color="warning" sx={{ mr: 1 }} />
                  )}
                  <Typography variant="h6">MFA Status</Typography>
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {userStatus?.mfa_enabled
                    ? 'Multi-factor authentication enabled'
                    : 'Partial enrollment'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {metrics && (
          <>
            <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
              System Metrics
            </Typography>

            <Grid container spacing={3}>
              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h4" color="primary">
                      {metrics.total_users || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Users
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h4" color="primary">
                      {metrics.total_authentications || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Total Authentications
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h4" color="success.main">
                      {metrics.successful_authentications || 0}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Successful
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              <Grid item xs={12} md={3}>
                <Card>
                  <CardContent>
                    <Typography variant="h4" color="primary">
                      {metrics.success_rate
                        ? `${(metrics.success_rate * 100).toFixed(1)}%`
                        : '0%'}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Success Rate
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>

            <Box sx={{ mt: 4, p: 3, bgcolor: 'background.paper', borderRadius: 1 }}>
              <Typography variant="h6" gutterBottom>
                Enrollment Statistics
              </Typography>
              <Typography variant="body2">
                Keystroke Enrollments:{' '}
                {metrics.enrollments?.keystroke || 0}
              </Typography>
              <Typography variant="body2">
                Face Enrollments: {metrics.enrollments?.face || 0}
              </Typography>
            </Box>
          </>
        )}
      </Box>
    </Container>
  );
};

export default DashboardPage;
