# Faceless

A niche-agnostic, faceless **short-form video automation factory**. Every day it
finds trending videos in a niche, generates an *original, differentiated* version,
and publishes to YouTube Shorts + TikTok + Reels — with a fast human approval gate
so it stays clear of YouTube's mass-produced / reused-content demonetization.

Primary niche: **self-improvement / motivation**. A niche is just config, so
adding a second channel (finance, facts, etc.) is a new `Niche(...)` + a template.

## Pipeline

```
discover → ideate → script → compliance gate → assets → render →
  [human approval] → publish (YouTube) → distribute (TikTok/Reels) → analytics ↺
```

Each stage is a module under `faceless/`. The whole pipeline reads the active
niche config (`faceless/niches/`). State for every video flows through the DB
(`faceless/db/models.py`): `Candidate → Idea → VideoJob (+ Script) → Upload → Metric`.

## Quickstart

```bash
pip install -e ".[review,dev]"        # core + Streamlit + test deps
cp .env.example .env                  # then fill in keys

# Exercise the entire pipeline offline (writes placeholder media):
faceless run --dry-run --limit 2
faceless review                       # list jobs awaiting approval
faceless approve 1                    # approve a job
faceless publish --dry-run            # simulate upload + distribution

pytest                                # smoke tests (all dry-run)
```

Review UI: `streamlit run faceless/review/app.py` → http://localhost:8501

## Daily operation (automation)

One cycle = publish what you approved since last run → produce a fresh batch for
review → refresh analytics. The human approval gate sits between runs.

```bash
faceless daily --produce-limit 7 --spread-minutes 90   # one cycle (for cron)
```

Run it **hands-off, no manual trigger** with a systemd timer (recommended — see
`scripts/systemd/README.md`), cron (`scripts/cron.example`), or Prefect:

```bash
# systemd (always-on VM): runs daily at 14:00 UTC, catches up if the box was off
sudo cp scripts/systemd/faceless-daily.* /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now faceless-daily.timer

# or Prefect (with a UI + retries)
pip install -e ".[orchestration]"
python -m faceless.orchestrator.prefect_flow   # serves a daily 14:00 UTC schedule
```

Day-to-day you only touch the **review queue**: open the Streamlit dashboard (or
run `faceless approve-all`), approve/reject, and approvals go live on the next
run. `--spread-minutes` staggers each video's scheduled publish time so a batch
trickles out instead of dropping at once.

## Configuration

Copy `.env.example` to `.env`. Keys are optional until a stage needs one:

| Stage | Needs |
|---|---|
| Discovery | `YOUTUBE_API_KEY` (read-only) |
| Ideation / Script / Compliance | `ANTHROPIC_API_KEY` |
| Voiceover | `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` |
| Images / Motion / Music | `IMAGE_API_KEY` / `VIDEO_API_KEY` / `MUSIC_API_KEY` |
| Upload | YouTube OAuth (`client_secret.json`) |
| Distribution | `DISTRIBUTION_API_KEY` (multi-platform posting SaaS) |
| Object storage (optional) | `STORAGE_*` (Cloudflare R2 / S3) |

New here? Get every credential with **[docs/SETUP_ACCOUNTS.md](docs/SETUP_ACCOUNTS.md)** (click-by-click), then follow **[docs/RUNBOOK.md](docs/RUNBOOK.md)** — the day-1 → first-published-video checklist.

## Implemented vs. wire-up-required

**Implemented:** niche registry + config, DB models/session, discovery (YouTube
Data API), ideation + scripting + compliance (Claude, with prompt caching),
ElevenLabs voiceover, FFmpeg slideshow render + thumbnail, YouTube resumable
upload (with Made-for-Kids + synthetic-content disclosure flags), CLI,
Streamlit review dashboard, dry-run for the whole pipeline.

**Provider-agnostic stubs (pick a provider, then implement):**
`assets/images.py`, `assets/music.py`, `assets/captions.py` (Whisper alignment),
`distribution/fanout.py`, `analytics/collect.py`. Each raises a clear
`NotImplementedError` pointing at the env var to set. A branded Remotion render
project can replace the FFmpeg slideshow under `faceless/render/`.

## Operating notes

- **YouTube upload quota:** `videos.insert` ≈ 1600 units; the default 10k/day cap
  allows ~6 uploads/day. Request a quota increase (or use multiple OAuth projects)
  to sustain 5-10/day.
- **Compliance is enforced, not optional:** the gate hard-blocks banned IP terms
  and runs an LLM policy review; the human approval gate is the last line against
  reused/repetitious-content demonetization. Keep it.
- **Music must be commercially cleared** so one render is safe on every platform.

## Adding a niche

Add a `Niche(...)` (copy `faceless/niches/self_improvement.py`), `register()` it
in `faceless/niches/registry.py`, add a render template — no pipeline changes.
