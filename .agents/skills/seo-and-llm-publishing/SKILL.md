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
- **Locale & hreflang:** Ensure `og:locale` (`en_IN`, `te_IN`, `hi_IN`) is set, localized pages (`/te/`, `/hi/`) link CTAs with `?lang=te` / `?lang=hi`, and `hreflang` is bidirectional across `/`, `/te/`, `/hi/`, and `sitemap.xml`.
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
pages = ['index.html', 'road-signs/index.html', 'question-bank/index.html', 'rto-guide/index.html', 'dl-test-guide/index.html', 'traffic-fines/index.html', 'telangana-rto-codes/index.html', 'cheatsheet/index.html', 'te/index.html', 'hi/index.html', 'about/index.html', 'privacy-policy/index.html']
for p in pages:
    txt = open(p, encoding='utf-8').read()
    t = html.unescape(re.search(r'<title>(.*?)</title>', txt).group(1))
    assert len(t) <= 65, f'{p}: title {len(t)} chars'
    assert '&amp;amp;' not in txt, f'{p}: double-escaped &amp;amp;'
    assert 'property=\"og:locale\"' in txt, f'{p}: missing og:locale'
    for b in re.findall(r'<script type=\"application/ld\\+json\">(.*?)</script>', txt, re.S):
        json.loads(b)
print('All SEO checks passed!')
" && python3 scripts/validate_workspace.py && python3 scripts/test_runner.py
```
