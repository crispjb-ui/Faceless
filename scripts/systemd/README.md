# Hands-off daily scheduling (systemd timer)

Runs the factory automatically every day with **no manual trigger**. Each run
publishes what you approved since last run, produces a fresh batch into the
review queue, and refreshes analytics. (You still approve in the dashboard —
the *running* is automatic, the *publishing of unapproved videos* never happens.)

## Install on your VM

Assumes the repo is at `/opt/Faceless` with a virtualenv at `/opt/Faceless/.venv`
and a populated `.env`. Adjust paths in the unit file if different.

```bash
sudo useradd -r -s /usr/sbin/nologin faceless || true
sudo chown -R faceless:faceless /opt/Faceless

sudo cp scripts/systemd/faceless-daily.service /etc/systemd/system/
sudo cp scripts/systemd/faceless-daily.timer   /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now faceless-daily.timer
```

## Verify / operate

```bash
systemctl list-timers faceless-daily.timer   # next scheduled run
sudo systemctl start faceless-daily.service   # run once now (manual test)
journalctl -u faceless-daily.service -n 100    # logs from the last run
```

Change the time by editing `OnCalendar` in the timer (UTC), then
`sudo systemctl daemon-reload && sudo systemctl restart faceless-daily.timer`.

## Alternatives

- **Cron**: see `scripts/cron.example` (simpler, no time-of-day catch-up).
- **Prefect**: `python -m faceless.orchestrator.prefect_flow` serves a scheduled
  deployment with retries + a UI.
- **GitHub Actions** (zero-infra) is possible but needs externalized state:
  a hosted Postgres (`DATABASE_URL`), R2 for media, the music library synced from
  R2, and `youtube_token.json` stored as a secret. A VM timer is more reliable
  for a daily content business.
