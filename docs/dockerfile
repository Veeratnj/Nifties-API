# -------------------------
# 1. Base image
# -------------------------
FROM python:3.11-slim

# -------------------------
# 2. Working directory
# -------------------------
WORKDIR /app

# -------------------------
# 3. Install deps
# -------------------------
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# -------------------------
# 4. Copy project
# -------------------------
COPY . .

# -------------------------
# 5. Run server
# -------------------------
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
