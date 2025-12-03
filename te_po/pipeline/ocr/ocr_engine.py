import base64

from te_po.utils.openai_client import DEFAULT_VISION_MODEL, client


def run_ocr(image_bytes: bytes) -> str:
    if client is None:
        return "[offline] OCR unavailable (missing OPENAI_API_KEY)."
    b64 = base64.b64encode(image_bytes).decode()
    response = client.chat.completions.create(
        model=DEFAULT_VISION_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "input_image", "image_url": f"data:image/png;base64,{b64}"},
                    {"type": "input_text", "text": "Extract all text from this image."},
                ],
            }
        ],
    )
    return response.choices[0].message["content"]
