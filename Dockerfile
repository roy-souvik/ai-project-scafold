FROM python:3.12-slim

WORKDIR /workspace

# Add audio dependencies (cached after first build)
RUN apt-get update && apt-get install -y \
    build-essential \
    libsqlite3-dev \
    curl \
    portaudio19-dev \
    espeak \
    espeak-ng-data \
    libespeak-ng1 \
    alsa-utils \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel

# Copy only requirements (small, rarely changes)
COPY requirements.txt .

# Install dependencies (cached unless requirements.txt changes)
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application code last (changes frequently, doesn't re-run pip install)
COPY . .

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]