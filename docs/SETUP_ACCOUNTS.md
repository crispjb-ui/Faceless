# Step-by-step: set up every app & access

Click-by-click instructions to obtain every credential the pipeline needs and
drop it into `.env`. Work top to bottom. **Start items marked ⏳ first** — they
involve approval waits.

When done, run `python -m faceless.cli doctor` — every required row should say OK.

---

## 0. Get the code running locally

```bash
git clone <your repo> && cd Faceless
bash scripts/setup.sh        # installs deps, creates .env + music folders, inits DB
```

Open `.env` in an editor; you'll paste credentials into it below.

---

## 1. ⏳ Google / YouTube Data API (discovery + upload)

**A. Create a project & enable the API**
1. Go to <https://console.cloud.google.com/> → top bar → **Select a project** →
   **New Project** → name it (e.g. "faceless") → **Create**.
2. **APIs & Services → Library** → search **YouTube Data API v3** → **Enable**.
3. (For analytics revenue later) also enable **YouTube Analytics API**.

**B. API key (read-only discovery + basic stats)**
4. **APIs & Services → Credentials → Create credentials → API key**.
5. Copy it → `.env`: `YOUTUBE_API_KEY=...`

**C. OAuth client (required for uploading)**
6. **Credentials → Create credentials → OAuth client ID**. If prompted,
   configure the **OAuth consent screen**: User type **External**, fill app name +
   your email, **Add users → your Google account** (keep it in "Testing").
7. Application type **Desktop app** → **Create** → **Download JSON**.
8. Save it in the repo root as `client_secret.json` (matches
   `YOUTUBE_CLIENT_SECRET_FILE`).

**D. Mint the token (one time, on a machine with a browser)**
9. `python -m faceless.cli youtube-auth` → a browser opens → sign in → allow.
   This writes `youtube_token.json`. Copy that file to your server for headless
   scheduled uploads.

**E. ⏳ Request a quota increase** (do now — approval can take days)
10. **APIs & Services → YouTube Data API v3 → Quotas**. Each upload ≈ 1600 units;
    default 10,000/day ≈ 6 uploads/day. Request an increase for 5-10/day, or
    create additional OAuth projects to spread load.

---

## 2. Anthropic (scripting / ideation / compliance)

1. <https://console.anthropic.com/> → sign up → **Settings → Billing** → add
   credit.
2. **API Keys → Create Key** → copy → `.env`: `ANTHROPIC_API_KEY=...`

---

## 3. ElevenLabs (voiceover — your channel's signature voice)

1. <https://elevenlabs.io/> → sign up → pick a paid plan (commercial use +
   enough characters).
2. **Voices**: choose a deep narrator from the library (or design/clone one) and
   **Add to My Voices**.
3. Open the voice → copy its **Voice ID**.
4. **Profile → API key** (or Settings) → copy.
5. `.env`: `ELEVENLABS_API_KEY=...` and `ELEVENLABS_VOICE_ID=...`

---

## 4. fal.ai (Flux images)

1. <https://fal.ai/> → sign up → **Billing** → add credit.
2. **Dashboard → Keys → Add key** → copy.
3. `.env`: `IMAGE_API_KEY=...`  (used as `FAL_KEY`)

---

## 5. ⏳ Ayrshare (multi-platform posting: TikTok / Instagram / Facebook)

1. <https://www.ayrshare.com/> → sign up → choose a plan that allows API +
   the platforms you want.
2. **Dashboard → connect social accounts**: link your TikTok, Instagram
   (Business/Creator), and Facebook Page. (Instagram/Facebook require a
   Facebook Page + a connected IG Business account.)
3. **API Key** page → copy → `.env`: `DISTRIBUTION_API_KEY=...`
4. ⏳ TikTok connection may require app review on TikTok's side — start early.

> Profiles: put your link-in-bio (Stan.store/Linktree → lead magnet) in every
> connected account's bio.

---

## 6. Cloudflare R2 (object storage — recommended)

Hosts rendered videos and provides the public URL used for distribution.

1. <https://dash.cloudflare.com/> → **R2** → **Create bucket** (e.g.
   `faceless-media`).
2. **Manage R2 API Tokens → Create API token** (Object Read & Write) → copy the
   **Access Key ID**, **Secret Access Key**, and the **S3 endpoint**
   (`https://<accountid>.r2.cloudflarestorage.com`).
3. Make objects publicly readable: bucket **Settings → Public access** → either
   enable the **r2.dev** subdomain or attach a **custom domain**
   (e.g. `media.yourdomain.com`). That URL is your public base.
4. `.env`:
   ```
   STORAGE_ENDPOINT_URL=https://<accountid>.r2.cloudflarestorage.com
   STORAGE_BUCKET=faceless-media
   STORAGE_ACCESS_KEY_ID=...
   STORAGE_SECRET_ACCESS_KEY=...
   STORAGE_PUBLIC_BASE_URL=https://media.yourdomain.com   # or the r2.dev URL
   STORAGE_REGION=auto
   ```

---

## 7. Epidemic Sound (licensed music)

1. <https://www.epidemicsound.com/> → subscribe (a plan that licenses your own
   channels).
2. Download ~20-40 tracks that fit the mood (cinematic / ambient).
3. Put the files in `music/cinematic_ambient/` (matches
   `niche.visual.music_library`). Refresh periodically so tracks stay varied.

> Why local files: Epidemic's track API is enterprise-gated, so a local pool is
> the reliable, automatable approach — and keeps the same render safe on YouTube,
> TikTok, and Reels.

---

## 8. (Optional) Hosted Postgres — for servers/CI

SQLite is fine for a single machine. For a server or to share state across
hosts, create a free **Neon** or **Supabase** Postgres and set:
```
DATABASE_URL=postgresql+psycopg://USER:PASS@HOST/DB
```
(Install the driver: `pip install "psycopg[binary]"`.)

---

## 9. Render backend

- **FFmpeg** (default): `sudo apt-get install -y ffmpeg`. Nothing else needed.
- **Remotion** (branded look): `cd faceless/render/remotion && npm install &&
  npx remotion browser ensure`, then set `RENDER_BACKEND=remotion` in `.env`.

---

## 10. Verify & first run

```bash
python -m faceless.cli doctor                 # all required rows OK?
python -m faceless.cli run --dry-run --limit 2  # offline smoke
python -m faceless.cli run --limit 1            # first REAL video -> awaiting review
streamlit run faceless/review/app.py            # review, then approve
python -m faceless.cli publish                  # uploads to YouTube (private)
```

Then set up hands-off scheduling — see `scripts/systemd/README.md`.
```bash
sudo cp scripts/systemd/faceless-daily.* /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now faceless-daily.timer
```
