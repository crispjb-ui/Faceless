# Funnel — bio link, lead magnet, product, emails

This is the money path. Videos drive viewers to your **bio link (Stan.store)** →
they grab the **free lead magnet** (joining your email list) → the **welcome
emails** nurture them → some buy the **journal**.

```
Shorts/TikTok/Reels  →  bio link (Stan.store)  →  free cheat sheet (email opt-in)
                                                      → welcome emails → Journal ($)
```

## Generate the assets

All offline except the copy step (which uses Claude). `--dry-run` produces real
files with placeholder copy so you can preview layout.

```bash
faceless funnel all                       # everything, real copy (needs ANTHROPIC_API_KEY)
faceless funnel lead-magnet               # output/funnel/lead_magnet.pdf
faceless funnel journal --days 30         # output/funnel/journal.pdf (6x9, KDP/Gumroad-ready)
faceless funnel emails --count 5          # output/funnel/emails/email_0*.md
faceless funnel landing                   # output/funnel/landing/index.html
```

Set `BRAND_NAME` and `STORE_URL` in `.env` first — they're stamped into the
assets and the emails/landing CTA.

## Set up Stan.store (the all-in-one)

1. <https://stan.store/> → sign up → pick your handle (this becomes your bio link).
2. **Add a free product** = the lead magnet. Upload `lead_magnet.pdf`, set price
   to $0, and enable **email collection** (this builds your list).
3. **Add a paid product** = the journal. Upload `journal.pdf`, set your price
   ($7-27). (Or sell the print edition via Amazon KDP and link to it.)
4. **Email automation:** in Stan's email tool, create a welcome sequence and
   paste in the bodies from `output/funnel/emails/` (one per step). Attach the
   cheat sheet to email 1.
5. Copy your Stan.store URL into `.env` as `STORE_URL`, then regenerate emails +
   landing so links are correct: `faceless funnel emails && faceless funnel landing`.
6. Put the Stan.store link in **every** platform bio (YouTube, TikTok, IG, FB).

## Optional: self-hosted landing page

`output/funnel/landing/index.html` is a standalone mobile-first opt-in page. Host
it on Cloudflare Pages or R2 if you want a branded domain in front of Stan. Point
its form `action` at your capture endpoint:

```bash
faceless funnel landing --form-action "https://stan.store/yourhandle"
```

## Notes

- The journal PDF is a 6×9 interior — fine for Gumroad as-is; for Amazon KDP add a
  cover in KDP's tools.
- Keep the lead magnet genuinely useful; it sets the trust that drives the sale.
- Once live, the niche `cta` already tells viewers to grab the cheat sheet — keep
  it consistent with the bio link.
