# Use official Python 3.13.7 image for compatibility
FROM python:3.13.7-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install only the minimal tools needed before Playwright takes over
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl ca-certificates ffmpeg \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file first (improves build caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright's own Chromium + all required OS-level dependencies.
# --with-deps replaces every manual apt-get library install above.
RUN playwright install --with-deps chromium

# Copy project files
COPY . /app

# Default command — run all tests headlessly
CMD ["pytest", "-vvv", "-m", "pta or heroku", \
     "-n", "4", \
     "--html=output/reports/report.html", "--self-contained-html", \
     "--capture=tee-sys", \
     "--alluredir=output/allure-results", \
     "tests"]
