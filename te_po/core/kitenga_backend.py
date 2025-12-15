from fastapi import FastAPI, Request, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator, Field
from google.cloud import vision
import openai
import json, base64, os
import requests
from typing import Optional

app = FastAPI(
    title="Kitenga Backend API",
    version="1.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)

# Security: Restrict CORS to specific origins from environment variable
allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
if allowed_origins and allowed_origins != [""]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["POST"],
        allow_headers=["Content-Type", "Authorization"],
    )

# Security: Add trusted host middleware
trusted_hosts = os.getenv("TRUSTED_HOSTS", "*").split(",")
if trusted_hosts != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=trusted_hosts)

# Security: Use environment variable for Google credentials path
google_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "the-den-faa84-39e2d1939316.json")
if os.path.exists(google_creds_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_creds_path

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORG_ID")


scribe_entries = []

# Security: Maximum sizes for inputs
MAX_BASE64_SIZE = 10 * 1024 * 1024  # 10MB
MAX_TEXT_LENGTH = 10000  # 10K characters

class OCRPayload(BaseModel):
    image_base64: str = Field(..., max_length=MAX_BASE64_SIZE)
    
    @field_validator('image_base64')
    @classmethod
    def validate_base64(cls, v):
        try:
            # Validate it's proper base64
            base64.b64decode(v)
            return v
        except Exception:
            raise ValueError("Invalid base64 encoded image")

@app.post("/ocr")
async def ocr(payload: OCRPayload):
    try:
        client = vision.ImageAnnotatorClient()
        image_data = base64.b64decode(payload.image_base64)
        image = vision.Image(content=image_data)
        response = client.text_detection(image=image)
        
        # Check for errors in response
        if response.error.message:
            raise HTTPException(status_code=500, detail="OCR processing failed")
        
        texts = response.text_annotations

        if not texts:
            return {"status": "success", "extracted_text": "No text found."}

        return {
            "status": "success",
            "extracted_text": texts[0].description
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# Translate
class TranslateRequest(BaseModel):
    text: str = Field(..., max_length=MAX_TEXT_LENGTH)
    target_lang: str = Field(default="en", max_length=10)
    
    @field_validator('target_lang')
    @classmethod
    def validate_lang(cls, v):
        # Allow only common language codes
        allowed_langs = ['en', 'es', 'fr', 'de', 'it', 'pt', 'ru', 'ja', 'ko', 'zh', 'ar', 'hi']
        if v not in allowed_langs:
            raise ValueError(f"Language '{v}' not supported")
        return v

@app.post("/translate")
async def translate_text(req: TranslateRequest):
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=503, detail="Service not configured")
        
        prompt = f"Translate to {req.target_lang}:\n{req.text}"
        res = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            timeout=30
        )
        return {"translation": res.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Translation failed")

# TTS
class SpeakRequest(BaseModel):
    text: str = Field(..., max_length=MAX_TEXT_LENGTH)

@app.post("/speak")
async def speak_text(req: SpeakRequest):
    try:
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise HTTPException(status_code=503, detail="Service not configured")
        
        headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        body = {
            "text": req.text,
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
        }
        url = "https://api.elevenlabs.io/v1/text-to-speech/TxGEqnHWrfWFTfGW9XjX"
        response = requests.post(url, headers=headers, json=body, timeout=30)
        
        if response.status_code != 200:
            raise HTTPException(status_code=500, detail="TTS service failed")
        
        # Ensure directory exists
        output_dir = os.getenv("OUTPUT_DIR", "backend")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "speak.mp3")
        
        with open(output_path, "wb") as f:
            f.write(response.content)
        return {"audio_url": "/static/speak.mp3"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="TTS processing failed")

# Scribe Log
class ScribeEntry(BaseModel):
    speaker: str = Field(..., max_length=100)
    text: str = Field(..., max_length=MAX_TEXT_LENGTH)
    tone: str = Field(default="neutral", max_length=50)
    glyph_id: str = Field(default="glyph-auto", max_length=100)
    translate: bool = False

@app.post("/scribe")
async def scribe(entry: ScribeEntry):
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=503, detail="Service not configured")
        
        scribe_entries.append(entry.model_dump())
        
        # Ensure directory exists
        output_dir = os.getenv("OUTPUT_DIR", "backend")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "scribe_entries.json")
        
        with open(output_path, "w") as f:
            json.dump(scribe_entries, f, indent=2)
        
        # Rongo Whisper
        rongo_prompt = f"What does this mean: {entry.text}"
        res = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": rongo_prompt}],
            max_tokens=1000,
            timeout=30
        )
        whisper = res.choices[0].message.content.strip()
        return {"status": "saved", "rongo": whisper}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Scribe processing failed")

@app.post("/gpt-whisper")
async def gpt_whisper(request: Request):
    try:
        if not os.getenv("OPENAI_API_KEY"):
            raise HTTPException(status_code=503, detail="Service not configured")
        
        data = await request.json()
        whisper = data.get("whisper", "")
        
        # Validate input
        if not whisper or len(whisper) > MAX_TEXT_LENGTH:
            raise HTTPException(status_code=400, detail="Invalid whisper text")

        res = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": whisper}
            ],
            max_tokens=2000,
            timeout=30
        )
        reply = res.choices[0].message.content.strip()
        return {"response": reply}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Processing failed")
