# Kitenga Backend API

A secure, hardened FastAPI backend service providing OCR, translation, text-to-speech, and AI-powered scribe functionality.

## Features

- **OCR (Optical Character Recognition)**: Extract text from images using Google Cloud Vision
- **Translation**: Multi-language text translation using OpenAI GPT-4
- **Text-to-Speech**: Convert text to speech using ElevenLabs API
- **Scribe**: Intelligent conversation logging with AI-powered insights
- **GPT Whisper**: General-purpose AI conversation endpoint

## Security Enhancements (2025)

This server has been hardened following FastAPI security best practices for 2025:

✅ Input validation with size limits  
✅ Proper error handling without information leakage  
✅ Configurable CORS with origin restrictions  
✅ Trusted host middleware  
✅ Request timeouts on external APIs  
✅ Environment-based configuration  
✅ Production docs disabled by default  
✅ Comprehensive input validation  
✅ No hardcoded credentials  

See [SECURITY.md](SECURITY.md) for complete security documentation.

## Installation

1. **Clone the repository**
```bash
git clone https://github.com/Hemi-Whiro22/Den-Backend.git
cd Den-Backend
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

4. **Set up Google Cloud credentials**
- Download your Google Cloud service account JSON key
- Update `GOOGLE_APPLICATION_CREDENTIALS` in `.env`

## Configuration

### Required Environment Variables

```bash
# API Keys
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
GOOGLE_APPLICATION_CREDENTIALS=path/to/google-credentials.json

# Optional: OpenAI Organization
OPENAI_ORG_ID=your_org_id
```

### Security Configuration

```bash
# Environment (development, staging, production)
ENVIRONMENT=production

# CORS - Comma-separated allowed origins
ALLOWED_ORIGINS=https://yourfrontend.com,https://www.yourfrontend.com

# Trusted Hosts - Comma-separated allowed hostnames
TRUSTED_HOSTS=api.yourdomain.com

# Output Directory
OUTPUT_DIR=backend
```

## Running the Server

### Development
```bash
uvicorn kitenga_backend:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
uvicorn kitenga_backend:app --host 0.0.0.0 --port 8000 --workers 4 --log-level warning
```

## API Endpoints

### POST /ocr
Extract text from base64-encoded images.

**Request:**
```json
{
  "image_base64": "base64_encoded_image_data"
}
```

**Response:**
```json
{
  "status": "success",
  "extracted_text": "Extracted text from image"
}
```

### POST /translate
Translate text to a target language.

**Request:**
```json
{
  "text": "Hello world",
  "target_lang": "es"
}
```

**Response:**
```json
{
  "translation": "Hola mundo"
}
```

**Supported Languages:** en, es, fr, de, it, pt, ru, ja, ko, zh, ar, hi

### POST /speak
Convert text to speech.

**Request:**
```json
{
  "text": "Hello, this is a test"
}
```

**Response:**
```json
{
  "audio_url": "/static/speak.mp3"
}
```

### POST /scribe
Log conversation entries with AI insights.

**Request:**
```json
{
  "speaker": "John",
  "text": "This is interesting",
  "tone": "positive",
  "glyph_id": "glyph-001",
  "translate": false
}
```

**Response:**
```json
{
  "status": "saved",
  "rongo": "AI-generated insight about the text"
}
```

### POST /gpt-whisper
General AI conversation endpoint.

**Request:**
```json
{
  "whisper": "What is the meaning of life?"
}
```

**Response:**
```json
{
  "response": "AI-generated response"
}
```

## API Documentation

When running in development mode, interactive API documentation is available at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Note:** Documentation endpoints are disabled in production for security.

## Input Limits

- **Text fields**: 10,000 characters maximum
- **Base64 images**: 10 MB maximum
- **Speaker names**: 100 characters maximum
- **Language codes**: 10 characters maximum
- **Tone/Glyph fields**: 50-100 characters maximum

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `400`: Bad Request (invalid input)
- `422`: Validation Error (Pydantic validation failed)
- `500`: Internal Server Error
- `503`: Service Unavailable (missing API keys or configuration)

## Security Best Practices

1. **Never commit `.env` files** - They contain sensitive API keys
2. **Use HTTPS in production** - Deploy behind a reverse proxy with SSL
3. **Set specific CORS origins** - Never use wildcards in production
4. **Configure trusted hosts** - Prevent host header attacks
5. **Implement rate limiting** - Use nginx, slowapi, or API gateway
6. **Monitor API usage** - Set up logging and alerting
7. **Rotate API keys regularly** - Follow security best practices
8. **Use secrets management** - Consider AWS Secrets Manager or similar

## Development

### Running Tests
```bash
PYTHONPATH=/path/to/Den-Backend python3 test_validation.py
```

### Code Quality
```bash
# Format code
black kitenga_backend.py

# Lint
pylint kitenga_backend.py

# Type checking
mypy kitenga_backend.py
```

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Changelog

### Version 1.0.0 (2025-10)
- ✅ Security hardening with 2025 best practices
- ✅ Input validation and size limits
- ✅ Proper error handling
- ✅ Configurable CORS and trusted hosts
- ✅ Environment-based configuration
- ✅ Production-ready deployment guide
- ✅ Comprehensive documentation
