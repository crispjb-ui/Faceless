# Operator Runbook — day 1 to first published video

A concrete checklist to take the Faceless pipeline from a fresh clone to your
first live video, then into daily operation. Estimated effort: ~2-4 focused days
(most of it accounts + branding + quality tuning, not code).

---

## Phase A — Accounts & API keys (~half a day)

Do the two **slow-approval** items first; they can take days.

- [ ] **YouTube Data API** — create a Google Cloud project, enable *YouTube Data
      API v3*, create an **API key** (discovery + analytics) and an **OAuth client
      (Desktop app)** → download `client_secret.json` into the repo root.
- [ ] **File a YouTube quota increase** *(slow — do it now)*. Default 10k units/day
      ≈ 6 uploads/day; you need more for 5-10/day.
- [ ] **TikTok posting** *(slow if using TikTok's official API)* — or use Ayrshare,
      which handles the approval surface for you.
- [ ] **Anthropic** API key → `ANTHROPIC_API_KEY`.
- [ ] **ElevenLabs** key + choose a deep narrator voice → `ELEVENLABS_API_KEY`,
      `ELEVENLABS_VOICE_ID`.
- [ ] **fal.ai** key (Flux images) → `IMAGE_API_KEY`.
- [ ] **Ayrshare** key + connect TikTok / Instagram / Facebook accounts →
      `DISTRIBUTION_API_KEY`.
- [ ] **Cloudflare R2** *(optional but recommended)* — bucket + access keys + a
      public base URL → `STORAGE_*`.

## Phase B — Install & configure (~1-2 hrs)

- [ ] `bash scripts/setup.sh` (installs deps, creates `.env` + music folders,
      inits DB, installs Remotion, runs a readiness check).
- [ ] Fill in `.env` with the keys from Phase A.
- [ ] If using Remotion render: `cd faceless/render/remotion && npx remotion browser ensure`.
      Otherwise ensure `ffmpeg` is on PATH (default backend).
- [ ] Populate the music library: drop ~20-40 commercially-cleared tracks (e.g.
      Epidemic Sound) into `music/cinematic_ambient/`.
- [ ] Verify: `python -m faceless.cli doctor` — every row you need should say OK.

## Phase C — Brand & funnel (~1-2 days, parallelizable)

- [ ] Create the YouTube channel; set name, logo, banner, handle, About.
- [ ] Build the funnel: a free lead magnet (1-page "Discipline Cheat Sheet"), a
      low-ticket journal/planner (Gumroad/Etsy/KDP), and a link-in-bio
      (Stan.store/Linktree). Put the bio link in every platform profile.
- [ ] Update the niche `cta` in `faceless/niches/self_improvement.py` to point at
      the lead magnet.

## Phase D — First real video (~half a day of tuning)

- [ ] Offline smoke: `python -m faceless.cli run --dry-run --limit 2`.
- [ ] First live batch: `python -m faceless.cli run --limit 1`
      (uses real APIs; leaves the job **awaiting review**).
- [ ] Review: `streamlit run faceless/review/app.py` → watch it, read the script,
      check compliance flags. Iterate on voice / `visual.style_prompt` / captions
      until quality is good.
- [ ] Approve, then publish privately: `python -m faceless.cli publish` (uploads
      to YouTube as **private** with Made-for-Kids=false + AI disclosure set).
- [ ] Manually flip it to public on YouTube once you're happy. Confirm captions,
      thumbnail, metadata, and that audio is licensed.

---

## Daily operation

Automated (cron or Prefect) — see `scripts/cron.example`:

```bash
faceless daily --produce-limit 7 --spread-minutes 90
```

Each run: publishes what you approved since last run → produces a fresh batch →
refreshes analytics. **Your only daily task** (~15-30 min): clear the review
queue in the Streamlit dashboard (or `faceless approve-all` once you trust it).

### Weekly (~1 hr)
- Skim analytics; note which hooks/formats win and nudge prompts.
- Refill the music library so tracks stay varied (reused-content hygiene).
- Spot-check compliance flags; respond to comments (allowed — not Made-for-Kids).

---

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `Missing required setting 'X'` | Key not in `.env`; run `faceless doctor`. |
| Uploads stop after ~6/day | YouTube quota cap — use the granted increase or add OAuth projects. |
| Remotion render fails to start | Run `npx remotion browser ensure` on the host (downloads headless Chromium). |
| Compliance `block` on good scripts | Tune `banned_terms` / `extra_rules` in the niche config. |
| Distribution error about media URL | Configure `STORAGE_*` (R2) or let Ayrshare host via its upload flow. |

## Scaling to a second channel

Add a `Niche(...)` (copy `self_improvement.py`), `register()` it, add a render
template — then run `faceless daily --niche <new_id>`. No pipeline changes.
