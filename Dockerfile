FROM python:3.12-slim

# use a dedicated build dir so runtime /workspace isn't overwritten/ambiguous
WORKDIR /tmp/project

RUN apt-get update && apt-get install -y build-essential libsqlite3-dev curl portaudio19-dev \
    espeak espeak-ng-data libespeak-ng1 alsa-utils && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip setuptools wheel

# copy requirements if you use one
COPY requirements.txt .

# copy project for editable install
COPY pyproject.toml /tmp/project/pyproject.toml
COPY src /tmp/project/src

# install requirements first (if present) then package
RUN if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
RUN pip install -e /tmp/project

# switch to runtime workspace (this is where your volume will mount)
WORKDIR /workspace

CMD ["bash", "-c", "uvicorn api:app --host 0.0.0.0 --port 8001 & streamlit run app.py --server.port=8501"]