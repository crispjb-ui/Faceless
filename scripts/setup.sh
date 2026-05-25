#!/usr/bin/env bash
# One-command setup for the Faceless pipeline.
# Installs deps, prepares config, initializes the DB, and reports readiness.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Installing Python package + extras"
pip install -e ".[assets,storage,funnel,review,dev]"

echo "==> Preparing .env"
if [ ! -f .env ]; then
  cp .env.example .env
  echo "    created .env from .env.example — fill in your keys"
else
  echo "    .env already exists; leaving it untouched"
fi

echo "==> Creating music library folders"
mkdir -p music/cinematic_ambient
echo "    drop commercially-cleared tracks (e.g. Epidemic Sound) into music/cinematic_ambient/"

echo "==> Initializing database"
python -m faceless.cli init-db

echo "==> Remotion render backend (optional)"
if command -v npm >/dev/null 2>&1; then
  (
    cd faceless/render/remotion
    npm install
    # Headless Chromium needed for rendering; safe to re-run.
    npx remotion browser ensure || echo "    WARN: 'remotion browser ensure' failed (network?). Re-run on your VM."
  )
else
  echo "    npm not found; skipping Remotion. The default FFmpeg backend needs only ffmpeg."
fi

echo "==> Readiness check"
python -m faceless.cli doctor || true

echo
echo "Setup complete. Next:"
echo "  1) Edit .env with your API keys"
echo "  2) Smoke test offline:  python -m faceless.cli run --dry-run --limit 2"
echo "  3) Go live:             python -m faceless.cli run --limit 5"
