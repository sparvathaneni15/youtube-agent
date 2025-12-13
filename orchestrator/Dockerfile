FROM python:3.12-slim

WORKDIR /app

# System deps (including Playwright browser dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
    # Playwright dependencies
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libdrm2 libdbus-1-3 libxkbcommon0 libxcomposite1 libxdamage1 \
    libxfixes3 libxrandr2 libgbm1 libasound2 libpango-1.0-0 libcairo2 \
  && rm -rf /var/lib/apt/lists/*

# Python deps
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Install Playwright browsers (chromium only for efficiency)
RUN playwright install chromium --with-deps

# App code
COPY agent_runner.py /app/agent_runner.py
COPY mcp_server.py /app/mcp_server.py


# Use explicit interpreter to avoid shebang issues
ENTRYPOINT ["python", "/app/agent_runner.py"]
