# Quick Start Guide

## Getting Started with TemplateRealm

### 1. Configure Environment

```bash
cp .env.template .env
# Edit .env with your API keys
```

### 2. Upload Documents

Use the DevHub or intake API to add documents to your vector store:

```bash
curl -X POST "https://your-backend/intake/embed" \
  -H "Content-Type: application/json" \
  -d '{"text": "Your document content", "metadata": {"source": "manual"}}'
```

### 3. Query Your Kaitiaki

Ask questions through the chat interface or API:

```bash
curl -X POST "https://your-backend/kitenga/gpt-whisper" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "What do you know about...", "assistant_id": "YOUR_ASSISTANT_ID"}'
```

## Need Help?

Check the main Awa Network documentation or ask Kitenga Whiro!
