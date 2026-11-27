---
name: seo-and-llm-publishing
description: >-
  Builds, verifies, and maintains static SEO subpages, llms.txt/llms-full.txt,
  sitemap.xml, and Open Graph preview assets for LLTPractice. Use when adding
  new static pages, editing scripts/build_seo_pages.py, updating metadata/titles,
  or regenerating assets/images/og-preview.png.
---

# SEO & LLM Publishing Workflow (LLTPractice)

## 1. Authoring Rules for `scripts/build_seo_pages.py`
- **No double-escaping:** `render_shell()` escapes `title`, `description`, `keywords`, and `subtitle` with `esc()`. Always pass plain `&` in those arguments (never `&amp;`). `h1` is inserted raw, so use `&amp;` only in `h1`.
- **Title length:** Keep every page `<title>` **≤ 65 characters** (after entity unescaping) to avoid Bing Site Scan `"Title too long"` warnings.
- **Theme tokens:** Use CSS theme variables (`var(--primary-navy)`, `var(--text-primary)`, `var(--text-secondary)`, `var(--accent-blue)`, `var(--card-bg)`, `var(--cta-gold-bg)`, `var(--cta-gold-text)`, `var(--badge-rto-bg)`, `var(--badge-rto-text)`, `var(--sign-surface)`) rather than hardcoded hex literals in `scripts/build_seo_pages.py`.
- **Locale & hreflang:** `ENABLE_MULTILINGUAL_SEO = False` temporarily pauses `/te/` and `/hi/` (`noindex, follow`, omitted from `sitemap.xml`, navigation, and `hreflang`) because Telugu/Hindi question translations are incomplete. **Do NOT set `ENABLE_MULTILINGUAL_SEO = True` without explicit user approval.** Ensure `og:locale` (`en_IN`) is present on every page.
- **AdSense `<head>` tag:** Keep `<script id="google-adsense-script" ...adsbygoogle.js...>` in `render_shell()` `<head>` for AdSense site review and go-live.
- **LLM discovery:** Keep `llms.txt` as a structured link directory and regenerate `llms-full.txt` from the JSON datasets.

## 2. Regenerating Open Graph Preview (`assets/images/og-preview.png`)
- Do not rely on headless Chrome or `qlmanage` in sandboxed macOS environments.
- Run `python3 scripts/generate_og_image.py` (Pillow) and visually verify `assets/images/og-preview.png` with `read_file`.

## 3. Build & Verification Command
Run after any SEO, dataset, or static page change:
```bash
python3 scripts/build_seo_pages.py && python3 -c "
import html, re, json, xml.etree.ElementTree as ET
ET.parse('sitemap.xml')
pages = [
    'index.html', '404.html', 'road-signs/index.html',
    'question-bank/index.html', 'question-bank/road-signs/index.html',
    'question-bank/traffic-rules/index.html', 'question-bank/driving-principles/index.html',
    'online-llr-test/index.html', 'rto-guide/index.html', 'dl-test-guide/index.html',
    'traffic-fines/index.html', 'telangana-rto-codes/index.html', 'cheatsheet/index.html',
    'about/index.html', 'privacy-policy/index.html'
]
for p in pages:
    txt = open(p, encoding='utf-8').read()
    t = html.unescape(re.search(r'<title>(.*?)</title>', txt).group(1))
    assert len(t) <= 65, f'{p}: title {len(t)} chars'
    assert '&amp;amp;' not in txt, f'{p}: double-escaped &amp;amp;'
    assert 'property=\"og:locale\"' in txt, f'{p}: missing og:locale'
    assert 'pagead2.googlesyndication.com/pagead/js/adsbygoogle.js' in txt, f'{p}: missing AdSense verification script'
    assert not re.search(r'<img\b(?![^>]*width=)[^>]*>', txt), f'{p}: img missing width'
    assert not re.search(r'<img\b(?![^>]*height=)[^>]*>', txt), f'{p}: img missing height'
    for b in re.findall(r'<script type=\"application/ld\\+json\">(.*?)</script>', txt, re.S):
        json.loads(b)
for paused in ['te/index.html', 'hi/index.html']:
    assert 'noindex, follow' in open(paused, encoding='utf-8').read(), f'{paused}: expected noindex, follow'
print('All SEO checks passed!')
" && python3 scripts/validate_workspace.py && python3 scripts/test_runner.py
```
