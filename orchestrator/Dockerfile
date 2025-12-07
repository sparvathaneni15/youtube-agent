FROM python:3.12-slim

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# App code
COPY agent_runner.py /app/agent_runner.py
COPY start.sh /app/start.sh

# Ensure script is executable
RUN chmod +x /app/start.sh

# Use explicit interpreter to avoid shebang issues
ENTRYPOINT ["sh", "/app/start.sh"]
