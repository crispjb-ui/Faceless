FROM python:3.11-slim

# ffmpeg is required by the render step.
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml README.md ./
COPY faceless ./faceless
RUN pip install --no-cache-dir -e ".[review]"

ENTRYPOINT []
CMD ["faceless", "--help"]
