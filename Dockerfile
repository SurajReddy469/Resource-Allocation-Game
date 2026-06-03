FROM python:3.11-slim

# Prevent Python from writing pyc files to disc and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set default port (7860 is Hugging Face's default port, Render/Railway will override via PORT env var)
ENV PORT=7860
EXPOSE 7860

# Run with Gunicorn
CMD gunicorn --bind 0.0.0.0:$PORT app:app
