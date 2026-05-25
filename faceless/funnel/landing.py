from __future__ import annotations

import html
import os

from faceless.config import get_settings

# Mobile-first single-page opt-in. Traffic arrives from Shorts/TikTok on phones,
# so it's one screen: promise -> email field -> button. The form posts to your
# capture endpoint (Stan.store / ESP form action); the CTA also links to STORE_URL.
_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{brand} — Free Discipline Cheat Sheet</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family: system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
          background:#0e0e10; color:#fff; min-height:100vh; display:flex;
          align-items:center; justify-content:center; padding:24px; }}
  .card {{ width:100%; max-width:440px; text-align:center; }}
  h1 {{ font-size:30px; line-height:1.15; margin:0 0 12px; }}
  p.sub {{ color:#b8b8bf; font-size:17px; line-height:1.5; margin:0 0 28px; }}
  form {{ display:flex; flex-direction:column; gap:12px; }}
  input {{ padding:16px; border-radius:12px; border:1px solid #2a2a30; background:#17171b;
           color:#fff; font-size:16px; }}
  button {{ padding:16px; border:0; border-radius:12px; background:#c0392b; color:#fff;
            font-size:17px; font-weight:700; cursor:pointer; }}
  a.alt {{ display:inline-block; margin-top:18px; color:#b8b8bf; font-size:14px; }}
  .fine {{ color:#6b6b6b; font-size:12px; margin-top:16px; }}
</style>
</head>
<body>
  <main class="card">
    <h1>{headline}</h1>
    <p class="sub">{subhead}</p>
    <form action="{form_action}" method="post">
      <input type="email" name="email" placeholder="Your best email" required>
      <button type="submit">Send me the cheat sheet</button>
    </form>
    <a class="alt" href="{store_url}">Or see the full Discipline Journal &rarr;</a>
    <p class="fine">No spam. Unsubscribe anytime.</p>
  </main>
</body>
</html>
"""


def generate_landing_page(
    out_path: str,
    *,
    form_action: str | None = None,
    headline: str | None = None,
    subhead: str | None = None,
) -> str:
    """Write a self-contained mobile-first opt-in page. Host it on Cloudflare
    Pages/R2, or just use your Stan.store page directly. Returns the path."""
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    s = get_settings()
    store_url = s.store_url or "#"
    page = _TEMPLATE.format(
        brand=html.escape(s.brand_name),
        headline=html.escape(headline or "Stop relying on motivation."),
        subhead=html.escape(
            subhead or "Get the free Discipline Cheat Sheet — 5 systems to do it anyway."
        ),
        form_action=html.escape(form_action or store_url),
        store_url=html.escape(store_url),
    )
    with open(out_path, "w") as f:
        f.write(page)
    return out_path
