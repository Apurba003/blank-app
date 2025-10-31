# API Reference - Multi-Factor Authentication System

## Base URL
```
http://localhost:5000/api
```

## Authentication
Most endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### System Endpoints

#### Health Check
```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-30T20:00:00.000000",
  "version": "1.0.0"
}
```

---

### User Management

#### Register User
```http
POST /api/register
```

**Request Body:**
```json
{
  "user_id": "john_doe",
  "password": "secure_password123",
  "email": "john@example.com"
}
```

**Response:**
```json
{
  "message": "User registered successfully",
  "user_id": "john_doe"
}
```

**Rate Limit:** 10 per hour

---

### Biometric Enrollment

#### Enroll Keystroke Biometric
```http
POST /api/enroll/keystroke
```

**Request Body:**
```json
{
  "user_id": "john_doe",
  "sessions": [
    [
      {
        "key": "h",
        "press_time": 0.0,
        "release_time": 0.1,
        "pressure": 0.5
      },
      {
        "key": "e",
        "press_time": 0.15,
        "release_time": 0.25,
        "pressure": 0.6
      }
    ],
    // Additional sessions (minimum 3 required)
  ]
}
```

**Response:**
```json
{
  "message": "Keystroke biometric enrolled successfully",
  "user_id": "john_doe",
  "num_samples": 3
}
```

**Rate Limit:** 20 per hour

---

#### Enroll Face Biometric
```http
POST /api/enroll/face
```

**Request Body:**
```json
{
  "user_id": "john_doe",
  "images": [
    "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
    "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  ]
}
```

**Response:**
```json
{
  "message": "Face biometric enrolled successfully",
  "user_id": "john_doe",
  "num_samples": 3
}
```

**Requirements:**
- Minimum 3 images
- Base64 encoded JPEG format
- Face must be clearly visible

**Rate Limit:** 20 per hour

---

### Authentication

#### Authenticate with Keystroke
```http
POST /api/authenticate/keystroke
```

**Request Body:**
```json
{
  "user_id": "john_doe",
  "keystroke_data": [
    {
      "key": "h",
      "press_time": 0.0,
      "release_time": 0.1,
      "pressure": 0.5
    }
    // More keystrokes...
  ]
}
```

**Response:**
```json
{
  "authenticated": true,
  "score": 0.85,
  "modality": "keystroke",
  "details": {
    "score": 0.85,
    "threshold": 3.0,
    "num_keystrokes": 15,
    "timestamp": "2025-10-30T20:00:00.000000"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Rate Limit:** 50 per hour

---

#### Authenticate with Face
```http
POST /api/authenticate/face
```

**Request Body:**
```json
{
  "user_id": "john_doe",
  "image": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
}
```

**Response:**
```json
{
  "authenticated": true,
  "score": 0.92,
  "modality": "face",
  "details": {
    "score": 0.92,
    "tolerance": 0.6,
    "liveness_check": true,
    "texture_score": 0.78,
    "liveness_score": 0.85,
    "timestamp": "2025-10-30T20:00:00.000000"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Rate Limit:** 50 per hour

---

#### Authenticate with Multi-Factor (MFA)
```http
POST /api/authenticate/mfa
```

**Request Body:**
```json
{
  "user_id": "john_doe",
  "keystroke_data": [
    {
      "key": "h",
      "press_time": 0.0,
      "release_time": 0.1,
      "pressure": 0.5
    }
    // More keystrokes...
  ],
  "face_image": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
  "fusion_method": "weighted_sum"
}
```

**Fusion Methods:**
- `weighted_sum` (default) - Weighted combination (40% keystroke, 60% face)
- `product` - Product of scores
- `mean` - Average of scores

**Response:**
```json
{
  "authenticated": true,
  "fused_score": 0.88,
  "individual_scores": [0.85, 0.92],
  "details": [
    {
      "modality": "keystroke",
      "score": 0.85,
      "threshold": 3.0,
      "num_keystrokes": 15
    },
    {
      "modality": "face",
      "score": 0.92,
      "tolerance": 0.6,
      "liveness_score": 0.85
    }
  ],
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Rate Limit:** 30 per hour

---

### User Status (Protected)

#### Get User Enrollment Status
```http
GET /api/user/<user_id>/status
```

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "user_id": "john_doe",
  "keystroke_enrolled": true,
  "face_enrolled": true,
  "mfa_enabled": true
}
```

---

#### Get System Metrics (Protected)
```http
GET /api/metrics
```

**Headers:**
```
Authorization: Bearer <jwt-token>
```

**Response:**
```json
{
  "total_users": 42,
  "total_authentications": 1250,
  "successful_authentications": 1175,
  "failed_authentications": 75,
  "success_rate": 0.94,
  "enrollments": {
    "keystroke": 38,
    "face": 40
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "user_id and sessions required"
}
```

### 401 Unauthorized
```json
{
  "error": "Token is missing"
}
```

### 403 Forbidden
```json
{
  "error": "Unauthorized"
}
```

### 404 Not Found
```json
{
  "error": "User not enrolled"
}
```

### 409 Conflict
```json
{
  "error": "User already exists"
}
```

### 429 Too Many Requests
```json
{
  "error": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error message"
}
```

---

## Data Formats

### Keystroke Event
```json
{
  "key": "string",           // Key pressed
  "press_time": 0.0,         // Timestamp when key pressed (seconds)
  "release_time": 0.1,       // Timestamp when key released (seconds)
  "pressure": 0.5            // Simulated pressure (0.0-1.0)
}
```

### Image Format
- **Encoding:** Base64
- **Format:** JPEG
- **Size:** Recommended 640x480 or higher
- **Quality:** Clear, well-lit face image
- **Prefix:** Can include `data:image/jpeg;base64,` prefix

---

## Rate Limits

| Endpoint | Limit |
|----------|-------|
| `/register` | 10/hour |
| `/enroll/*` | 20/hour |
| `/authenticate/*` | 30-50/hour |
| `/metrics`, `/user/*/status` | 100/hour |

---

## Authentication Flow

### New User Flow
1. **Register** → `POST /api/register`
2. **Enroll Keystroke** → `POST /api/enroll/keystroke`
3. **Enroll Face** → `POST /api/enroll/face`
4. **Authenticate** → `POST /api/authenticate/mfa`

### Returning User Flow
1. **Authenticate** → `POST /api/authenticate/mfa`
2. **Access Protected Resources** → Use JWT token

---

## JWT Token

### Token Structure
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJ1c2VyX2lkIjoiam9obl9kb2UiLCJleHAiOjE2OTg2ODQwMDAsImlhdCI6MTY5ODU5NzYwMH0.
signature
```

### Token Payload
```json
{
  "user_id": "john_doe",
  "exp": 1698684000,  // Expiration timestamp
  "iat": 1698597600   // Issued at timestamp
}
```

### Using the Token
```javascript
// In headers
headers: {
  'Authorization': `Bearer ${token}`
}

// Or
headers: {
  'Authorization': 'Bearer ' + token
}
```

---

## Example: Complete User Registration & Authentication

### 1. Register
```bash
curl -X POST http://localhost:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "password": "secure123",
    "email": "alice@example.com"
  }'
```

### 2. Enroll Keystroke
```bash
curl -X POST http://localhost:5000/api/enroll/keystroke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "sessions": [[
      {"key": "h", "press_time": 0.0, "release_time": 0.1, "pressure": 0.5},
      {"key": "e", "press_time": 0.15, "release_time": 0.25, "pressure": 0.6}
    ]]
  }'
```

### 3. Authenticate
```bash
curl -X POST http://localhost:5000/api/authenticate/keystroke \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "keystroke_data": [
      {"key": "h", "press_time": 0.0, "release_time": 0.1, "pressure": 0.5},
      {"key": "e", "press_time": 0.15, "release_time": 0.25, "pressure": 0.6}
    ]
  }'
```

### 4. Access Protected Resource
```bash
TOKEN="<jwt-token-from-step-3>"

curl -X GET http://localhost:5000/api/user/alice/status \
  -H "Authorization: Bearer $TOKEN"
```

---

## Best Practices

1. **Always use HTTPS in production**
2. **Store JWT tokens securely** (httpOnly cookies or secure storage)
3. **Handle token expiration** (refresh or re-authenticate)
4. **Validate input** on client side before sending
5. **Handle errors gracefully** with appropriate user feedback
6. **Respect rate limits** to avoid being blocked
7. **Clear sensitive data** after use
8. **Use environment variables** for API URLs

---

## Support

For issues or questions about the API:
- Check the error message in the response
- Review the main README.md
- Check the SETUP_GUIDE.md for troubleshooting
- Verify all required fields are included
- Ensure data formats match specifications
