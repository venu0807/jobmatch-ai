FROM python:3.11-slim

# Install system dependencies, Chromium & fonts for headless PDF rendering
RUN apt-get update && apt-get install -y --no-install-recommends \
    chromium \
    chromium-driver \
    fonts-liberation \
    fontconfig \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set up non-root user for Hugging Face Spaces & security
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    CHROME_BIN=/usr/bin/chromium \
    CHROMIUM_PATH=/usr/bin/chromium \
    PYTHONUNBUFFERED=1

WORKDIR $HOME/app

# Copy dependencies and install
COPY --chown=user:user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy application source code
COPY --chown=user:user . .

# Hugging Face Spaces port
EXPOSE 7860

CMD ["python", "app.py"]
