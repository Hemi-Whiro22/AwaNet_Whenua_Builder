FROM python:3.12-slim

WORKDIR /app

# Copy proxy files
COPY te_po_proxy/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY te_po_proxy/ .
COPY .env .env.example /app/

EXPOSE 8000

CMD ["python", "main.py"]
