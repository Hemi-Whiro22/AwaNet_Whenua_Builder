# Security Hardening Documentation

## Overview
This document outlines the security improvements made to the Kitenga Backend FastAPI server to align with 2025 best practices.

## Security Improvements Implemented

### 1. **Input Validation & Sanitization**
- Added maximum size constraints for all text inputs (10,000 characters)
- Added maximum size for base64 image uploads (10MB)
- Implemented Pydantic field validators for all request models
- Base64 validation to ensure proper encoding
- Language code whitelist for translation endpoint
- Input length validation before processing

### 2. **Error Handling**
- Replaced generic error messages with specific HTTP exceptions
- Prevented information leakage through error responses
- Used HTTPException for proper error codes (400, 500, 503)
- Removed internal error details from client responses

### 3. **CORS Hardening**
- Changed from wildcard `allow_origins=["*"]` to environment-based configuration
- CORS now only enabled when ALLOWED_ORIGINS is set
- Restricted allowed methods to POST only (matching actual endpoints)
- Limited allowed headers to Content-Type and Authorization
- Documented configuration in .env.example

### 4. **Trusted Host Middleware**
- Added TrustedHostMiddleware to prevent host header attacks
- Configurable via TRUSTED_HOSTS environment variable
- Only active when specific hosts are configured

### 5. **API Documentation Security**
- Disabled /docs and /redoc endpoints in production
- Controlled via ENVIRONMENT variable
- Prevents API discovery in production environments

### 6. **External API Security**
- Added timeouts (30s) to all external API calls (OpenAI, ElevenLabs)
- Validates API keys exist before making requests
- Returns 503 (Service Unavailable) when services not configured
- Checks response status codes before processing

### 7. **File System Security**
- Removed hardcoded file paths
- Added directory existence checks with os.makedirs(exist_ok=True)
- Made output directory configurable via OUTPUT_DIR env variable
- Uses os.path.join for cross-platform path handling

### 8. **Dependency Updates**
- Updated requirements.txt with minimum secure versions
- FastAPI >= 0.119.0 (latest stable with security fixes)
- Pydantic >= 2.8.0 (v2 with improved validation)
- Added version constraints to prevent vulnerable versions

### 9. **Import Fixes**
- Added missing import for google.cloud.vision
- Added HTTPException import for proper error handling
- Added Field and field_validator from Pydantic
- Added TrustedHostMiddleware import

### 10. **API Configuration**
- Moved Google Cloud credentials path to environment variable
- Added API title and version metadata
- Centralized configuration through environment variables

## Environment Variables Required

### Required for operation:
- `OPENAI_API_KEY` - OpenAI API authentication
- `ELEVENLABS_API_KEY` - ElevenLabs TTS API key
- `GOOGLE_APPLICATION_CREDENTIALS` - Path to Google Cloud service account JSON

### Recommended for security:
- `ENVIRONMENT` - Set to "production" to disable docs
- `ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins
- `TRUSTED_HOSTS` - Comma-separated list of allowed hostnames
- `OUTPUT_DIR` - Directory for generated files (default: "backend")

### Optional:
- `OPENAI_ORG_ID` - OpenAI organization ID

## Best Practices Not Yet Implemented

The following improvements are recommended but not included to maintain minimal changes:

1. **Rate Limiting** - Use slowapi or similar middleware
2. **Authentication** - Implement API key or OAuth authentication
3. **Request Logging** - Add structured logging for security monitoring
4. **Content Security** - Add security headers (CSP, X-Frame-Options, etc.)
5. **TLS Configuration** - Enforce HTTPS in production
6. **API Versioning** - Add version prefix to endpoints (e.g., /v1/ocr)
7. **Request ID Tracking** - Add correlation IDs for request tracing
8. **Input Sanitization** - Additional HTML/script tag filtering
9. **Database Security** - If persistence is added, use parameterized queries
10. **Secrets Management** - Use proper secrets manager instead of .env files

## Deployment Recommendations

### Production Checklist:
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure specific `ALLOWED_ORIGINS` (no wildcards)
- [ ] Configure specific `TRUSTED_HOSTS`
- [ ] Use secrets manager for API keys (not .env)
- [ ] Deploy behind reverse proxy with HTTPS
- [ ] Implement rate limiting at proxy level
- [ ] Set up monitoring and alerting
- [ ] Regular dependency updates and security scanning
- [ ] Implement authentication/authorization
- [ ] Enable request logging
- [ ] Set up WAF (Web Application Firewall)

### Running the Server:
```bash
# Development
uvicorn kitenga_backend:app --reload --host 0.0.0.0 --port 8000

# Production
uvicorn kitenga_backend:app --host 0.0.0.0 --port 8000 --workers 4 --access-log --log-level warning
```

## Security Testing

Test the security improvements:

1. **CORS**: Try accessing from unauthorized origin
2. **Input Validation**: Send oversized payloads
3. **Error Handling**: Verify no stack traces in responses
4. **Rate Limiting**: Test repeated requests (if implemented)
5. **Authentication**: Verify protected endpoints (if implemented)

## References
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [Pydantic Validation](https://docs.pydantic.dev/latest/concepts/validators/)
