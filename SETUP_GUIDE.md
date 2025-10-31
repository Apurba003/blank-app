# Setup Guide - Multi-Factor Authentication System

This guide will help you set up and run the MFA system on your local machine.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Manual Setup](#manual-setup)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Python 3.12+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **pip** - Python package manager (usually comes with Python)
- **npm** - Node package manager (comes with Node.js)

### System Requirements
- **Operating System**: Linux, macOS, or Windows
- **RAM**: Minimum 4GB (8GB recommended)
- **Webcam**: Required for face recognition
- **Internet**: Required for initial setup to download dependencies

### Optional
- **CMake** - Required for dlib installation on some systems
- **Visual Studio Build Tools** - Required for dlib on Windows

## Quick Start

### Using the Startup Script (Linux/macOS)

1. **Clone the repository:**
   ```bash
   cd /path/to/blank-app
   ```

2. **Run the startup script:**
   ```bash
   ./start.sh
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000

The script will automatically:
- Install Python dependencies
- Install Node dependencies
- Create necessary directories
- Start both backend and frontend services

Press `Ctrl+C` to stop all services.

## Manual Setup

### Backend Setup

1. **Navigate to the project directory:**
   ```bash
   cd /path/to/blank-app
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # Activate on Linux/macOS:
   source venv/bin/activate
   
   # Activate on Windows:
   venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   **Note**: Installing `dlib` and `face_recognition` can be challenging. See [Troubleshooting](#troubleshooting) if you encounter issues.

4. **Create storage directories:**
   ```bash
   mkdir -p storage/templates storage/logs
   ```

5. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and set your own secret keys
   ```

6. **Run the backend:**
   ```bash
   cd backend
   python api/app.py
   ```

   The backend API will be available at http://localhost:5000

### Frontend Setup

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node dependencies:**
   ```bash
   npm install
   ```

3. **Run the development server:**
   ```bash
   npm run dev
   ```

   The frontend will be available at http://localhost:3000

## Configuration

### Backend Configuration

Edit the `.env` file to configure the backend:

```bash
# Security (IMPORTANT: Change these in production!)
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# JWT token expiration
JWT_EXPIRATION_HOURS=24

# Face detection model ('hog' for CPU, 'cnn' for GPU)
FACE_DETECTION_MODEL=hog

# Enable/disable liveness detection
ENABLE_LIVENESS_DETECTION=true
```

### Frontend Configuration

Create `frontend/.env` for frontend-specific settings:

```bash
VITE_API_URL=http://localhost:5000/api
```

## Running the Application

### Development Mode

**Terminal 1 (Backend):**
```bash
cd backend
python api/app.py
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### Production Mode

**Backend:**
```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.api.app:app
```

**Frontend:**
```bash
cd frontend
npm run build

# Serve with a static file server
npx serve -s dist -l 3000
```

## Testing

### Run Demo Script

Test the backend functionality:
```bash
python demo.py
```

This will demonstrate:
- Keystroke dynamics authentication
- Feature optimization with PCA
- Biometric performance metrics
- Multi-modal score fusion

### Test Individual Modules

```bash
# Test imports
python -c "from backend.biometrics.keystroke_dynamics import KeystrokeDynamicsAuth; print('✓ OK')"

# Test encryption
python -c "from backend.utils.encryption import TemplateEncryption; enc = TemplateEncryption(); print('✓ OK')"
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:5000/api/health

# Register user (requires backend running)
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "password": "test123", "email": "test@example.com"}'
```

## Troubleshooting

### Common Issues

#### 1. dlib Installation Fails

**On Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install build-essential cmake
sudo apt-get install libopenblas-dev liblapack-dev
pip install dlib
```

**On macOS:**
```bash
brew install cmake
pip install dlib
```

**On Windows:**
- Install Visual Studio Build Tools
- Or use pre-built wheels: `pip install dlib-binary`

#### 2. face_recognition Installation Fails

If dlib is installed correctly but face_recognition fails:
```bash
pip install --upgrade pip
pip install face_recognition --no-cache-dir
```

Or use alternative:
```bash
pip install opencv-python
# Use OpenCV's face detection instead
```

#### 3. Webcam Not Detected

- Ensure browser has permission to access webcam
- Check webcam is not being used by another application
- Try a different browser (Chrome recommended)

#### 4. Port Already in Use

**Backend (port 5000):**
```bash
# Find process using port 5000
lsof -i :5000
# Kill the process
kill -9 <PID>
```

**Frontend (port 3000):**
```bash
# Find process using port 3000
lsof -i :3000
# Kill the process
kill -9 <PID>
```

#### 5. CORS Errors

Make sure:
- Backend is running on port 5000
- Frontend is running on port 3000
- Flask-CORS is installed and configured

#### 6. Module Not Found Errors

Ensure you're in the correct directory and virtual environment is activated:
```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Reinstall dependencies
pip install -r requirements.txt
```

### Performance Issues

#### Slow Face Recognition

- Use 'hog' model instead of 'cnn' for faster CPU processing
- Reduce image resolution before processing
- Consider using a machine with GPU support

#### High Memory Usage

- Reduce number of PCA components
- Use smaller batch sizes for training
- Clear browser cache and reload

## Additional Resources

- **API Documentation**: See `/api/health` endpoint for API status
- **Demo Script**: Run `python demo.py` for examples
- **Frontend Components**: Check `frontend/src/components/` for React components
- **Backend Modules**: Check `backend/biometrics/` for authentication logic

## Support

For issues and questions:
1. Check this troubleshooting guide
2. Review the main README.md
3. Check browser console for frontend errors
4. Check terminal output for backend errors

## Security Notes

**For Production Deployment:**
1. Change all default secret keys
2. Use HTTPS for all connections
3. Set up proper database (not file-based)
4. Enable rate limiting
5. Set up monitoring and logging
6. Regular security audits
7. Keep dependencies updated

**Never commit:**
- `.env` files
- `storage/` directory
- API keys or secrets
- User biometric data
