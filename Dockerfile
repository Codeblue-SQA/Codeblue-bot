FROM python:3.12-slim

# Chrome + chromedriver deps
RUN apt-get update && apt-get install -y \
    wget gnupg unzip curl \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" \
       > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# selenium-manager (bundled with selenium 4.20+) auto-resolves the
# matching chromedriver at runtime, no separate install step needed.

COPY . .

# Default: standalone loop (hourly + jitter, runs forever).
# For one-shot mode under an external scheduler, override with:
#   docker run -e SCHEDULER_RUN_ONCE=true <image>
CMD ["python", "scheduler.py"]
