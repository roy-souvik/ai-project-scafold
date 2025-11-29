# 📘 AI Project Scafold

AI project scafold.

🚀 Project Setup

🧩 Requirements

Python 3.12+

Docker & Docker Compose (optional, for containerized runs)


🐍 Run Locally (without Docker)

# 1. Clone the repo
git clone https://github.com/roy-souvik/ai-project-scafold.git
cd ai-project-scafold

# 2. (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -e .

# 4. Run test script
python scripts/setup_db.py


Expected output:

[LOG] Handling user: Alice
Hello, Alice!

🐳 Run via Docker
# 1. Build and start the container
docker compose up --build

# 2. Stop the container
docker compose down

To open a shell inside the container:

docker compose run app bash

⚙️ Environment Variables

You can define project-level environment variables in .env:

APP_ENV=development
LOG_LEVEL=debug

📦 Project Structure
project-wrapper/
├── src/epoch_explorer/          # Core package code
├── scripts/                  # Entry point scripts
├── pyproject.toml            # Editable install config
├── Dockerfile                # Container build
├── docker compose.yml        # Multi-container orchestration
├── requirements.txt          # Optional pinned dependencies
├── .env                      # Local environment variables
└── .gitignore

4️⃣ requirements.txt location and usage

✅ Keep it in the project root (same level as pyproject.toml and Dockerfile).

requirements.txt

Use it when you don’t want editable installs, e.g., for production builds:

pip install -r requirements.txt

In Dockerfile, you could optionally replace:

RUN pip install -e .

with:

COPY requirements.txt .
RUN pip install -r requirements.txt