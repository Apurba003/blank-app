import React, { useState, useRef, useCallback } from 'react';
import Webcam from 'react-webcam';
import {
  Box,
  Button,
  Typography,
  Paper,
  Grid,
  Alert,
  Card,
  CardMedia,
  IconButton,
} from '@mui/material';
import {
  Camera as CameraIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckIcon,
} from '@mui/icons-material';

const REQUIRED_IMAGES = 3;

const FaceCapture = ({ onCapture, imageCount = REQUIRED_IMAGES }) => {
  const webcamRef = useRef(null);
  const [capturedImages, setCapturedImages] = useState([]);
  const [message, setMessage] = useState('');
  const [isWebcamReady, setIsWebcamReady] = useState(false);

  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: 'user',
  };

  const captureImage = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      const newImages = [...capturedImages, imageSrc];
      setCapturedImages(newImages);

      if (newImages.length >= imageCount) {
        setMessage(`Captured ${newImages.length} images successfully!`);
        if (onCapture) {
          onCapture(newImages);
        }
      } else {
        setMessage(`Captured ${newImages.length} of ${imageCount} images`);
      }
    }
  }, [capturedImages, imageCount, onCapture]);

  const removeImage = (index) => {
    const newImages = capturedImages.filter((_, i) => i !== index);
    setCapturedImages(newImages);
    setMessage(
      newImages.length >= imageCount
        ? `Captured ${newImages.length} images successfully!`
        : `Captured ${newImages.length} of ${imageCount} images`
    );
  };

  const isCompleted = capturedImages.length >= imageCount;

  return (
    <Paper elevation={3} sx={{ p: 3, maxWidth: 800, mx: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Face Recognition Capture
      </Typography>

      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Capture {imageCount} photos of your face from slightly different angles
      </Typography>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Box
            sx={{
              position: 'relative',
              borderRadius: 1,
              overflow: 'hidden',
              bgcolor: 'black',
            }}
          >
            <Webcam
              audio={false}
              ref={webcamRef}
              screenshotFormat="image/jpeg"
              videoConstraints={videoConstraints}
              onUserMedia={() => setIsWebcamReady(true)}
              onUserMediaError={() => setMessage('Error accessing webcam')}
              style={{ width: '100%', height: 'auto' }}
            />
          </Box>

          <Button
            fullWidth
            variant="contained"
            startIcon={<CameraIcon />}
            onClick={captureImage}
            disabled={!isWebcamReady || isCompleted}
            sx={{ mt: 2 }}
          >
            Capture Photo ({capturedImages.length}/{imageCount})
          </Button>
        </Grid>

        <Grid item xs={12} md={6}>
          <Typography variant="subtitle2" gutterBottom>
            Captured Images:
          </Typography>

          <Box sx={{ maxHeight: 400, overflow: 'auto' }}>
            {capturedImages.length === 0 ? (
              <Alert severity="info">No images captured yet</Alert>
            ) : (
              <Grid container spacing={1}>
                {capturedImages.map((image, index) => (
                  <Grid item xs={6} key={index}>
                    <Card>
                      <CardMedia
                        component="img"
                        image={image}
                        alt={`Captured ${index + 1}`}
                      />
                      <Box
                        sx={{
                          position: 'absolute',
                          top: 0,
                          right: 0,
                          bgcolor: 'rgba(0, 0, 0, 0.5)',
                        }}
                      >
                        <IconButton
                          size="small"
                          onClick={() => removeImage(index)}
                          sx={{ color: 'white' }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            )}
          </Box>
        </Grid>
      </Grid>

      {message && (
        <Alert
          severity={isCompleted ? 'success' : 'info'}
          icon={isCompleted ? <CheckIcon /> : undefined}
          sx={{ mt: 2 }}
        >
          {message}
        </Alert>
      )}

      {!isWebcamReady && (
        <Alert severity="warning" sx={{ mt: 2 }}>
          Waiting for webcam access...
        </Alert>
      )}
    </Paper>
  );
};

export default FaceCapture;
