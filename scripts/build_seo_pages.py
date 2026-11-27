#!/usr/bin/env python3
"""
scripts/build_seo_pages.py

Generates crawlable, zero-JS static HTML pages, category question banks,
AdSense policy pages, paused-language stubs, llms-full.txt, and sitemap.xml
(with image entries) directly from verified Telangana RTA LLR datasets.
"""

from datetime import date
import html
import json
import os
import re
from PIL import Image

BASE_URL = "https://llr.sarvacapital.in"
TODAY = date.today().isoformat()
ASSET_VER = "v=26"
CONTACT_EMAIL = "contact@sarvacapital.in"

# IMPORTANT FOR ALL DEVELOPERS & AI AGENTS:
# Telugu ("te") and Hindi ("hi") are TEMPORARILY DISABLED across public SEO pages
# because 280/412 questions in data/questions/telangana/*.json contain hybrid/incomplete
# English+Telugu/Hindi strings. DO NOT flip ENABLE_MULTILINGUAL_SEO to True without
# explicit user approval.
ENABLE_MULTILINGUAL_SEO = False

_IMG_DIM_CACHE = {}

# Contextual titles for road-signs.json items whose answer option alone lacks question context
SIGN_TITLE_OVERRIDES = {
    "TS_RS_001": "RED TRAFFIC LIGHT — MUST STOP BEHIND WHITE STOP LINE",
    "TS_RS_002": "FLASHING YELLOW LIGHT — SLOW DOWN AND PROCEED WITH CAUTION",
    "TS_RS_003": "FLASHING RED LIGHT — STOP, OBSERVE AND PROCEED WITH CAUTION",
    "TS_RS_004": "CIRCLE SIGN SHAPE — MANDATORY / REGULATORY ROAD SIGNS",
    "TS_RS_005": "TRIANGLE SIGN SHAPE — CAUTIONARY / WARNING ROAD SIGNS",
    "TS_RS_006": "RECTANGLE SIGN SHAPE — INFORMATORY / GUIDE ROAD SIGNS",
    "TS_RS_009": "ONE-WAY STREET RULE — CONTINUE TO THE END OF THE ROAD",
    "TS_RS_065": "Y-INTERSECTION (SYMMETRIC FORK)",
    "TS_RS_066": "Y-INTERSECTION (RIGHT BRANCH AHEAD)",
    "TS_RS_083": "POLICE OFFICER SIGNAL (ONCOMING) — STOP",
    "TS_RS_084": "POLICE OFFICER SIGNAL (JUNCTION) — STOP BEFORE THE STOP LINE",
    "TS_RS_085": "DRIVER HAND SIGNAL (RIGHT TURN) — EXTEND RIGHT PALM OUTWARD",
    "TS_RS_086": "DRIVER HAND SIGNAL — TURN LEFT",
    "TS_RS_087": "DRIVER HAND SIGNAL — TURN RIGHT",
    "TS_RS_088": "DRIVER HAND SIGNAL — INTENDS TO STOP",
    "TS_RS_089": "DRIVER HAND SIGNAL — INTENDS TO SLOW DOWN",
    "TS_RS_090": "DRIVER HAND SIGNAL — GIVE WAY TO BE OVERTAKEN",
    "TS_RS_091": "BROKEN WHITE LINE — CAN CHANGE LANE WITH CAUTION",
    "TS_RS_092": "CONTINUOUS WHITE OR YELLOW LINE — CHANGING OF LANE PROHIBITED",
    "TS_RS_093": "BROKEN + ADJACENT SOLID LINE — OVERTAKE FROM BROKEN LINE SIDE ONLY",
    "TS_RS_094": "TWO SOLID YELLOW LINES — MUST NOT CROSS TO OVERTAKE OR U-TURN",
}


def esc(val):
    return html.escape(str(val or ""), quote=True)


def clean_text(val):
    return re.sub(r"\s+", " ", str(val or "")).strip()


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_file(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {path} ({len(content.encode('utf-8'))} bytes)")


def get_img_dims(rel_path):
    if rel_path in _IMG_DIM_CACHE:
        return _IMG_DIM_CACHE[rel_path]
    dims = (120, 120)
    if rel_path and os.path.exists(rel_path):
        if rel_path.lower().endswith(".svg"):
            try:
                txt = open(rel_path, encoding="utf-8", errors="ignore").read(2048)
                vb = re.search(r'viewBox="0\s+0\s+(\d+)\s+(\d+)"', txt)
                if vb:
                    dims = (int(vb.group(1)), int(vb.group(2)))
            except Exception:
                pass
        else:
            try:
                with Image.open(rel_path) as im:
                    dims = im.size
            except Exception:
                pass
    _IMG_DIM_CACHE[rel_path] = dims
    return dims


def ad_slot_html(slot_key, fmt="leaderboard"):
    return f"""
<aside class="ad-slot-wrapper ad-format-{fmt} is-hidden no-print" data-ad-slot="{slot_key}" aria-label="Advertisement">
  <span class="ad-label">Advertisement</span>
  <div class="ad-slot-inner"></div>
</aside>"""


def render_faq_block_html(faq_items, heading="Frequently Asked Questions"):
    cards = "".join(
        f"""<details class="footer-faq-item">
  <summary>{esc(q)}</summary>
  <p>{esc(a)}</p>
</details>"""
        for q, a in faq_items
    )
    return f"""
<section class="guide-section-anchor" style="margin-top:28px;">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">{esc(heading)}</h2>
  <div class="footer-faq-grid">{cards}</div>
</section>"""


def faq_json_ld(faq_items):
    return {
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": q,
                "acceptedAnswer": {"@type": "Answer", "text": a},
            }
            for q, a in faq_items
        ],
    }


def render_shell(
    *,
    lang="en",
    rel_root="../",
    canonical_path="",
    title="",
    description="",
    keywords="",
    h1="",
    subtitle="",
    breadcrumb_label="",
    breadcrumb_parent=None,
    active_nav="",
    json_ld=None,
    hreflang_links=None,
    robots="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1",
    body_html="",
    extra_scripts="",
    include_hero_cta=True,
):
    canonical_url = f"{BASE_URL}/{canonical_path}"
    is_noindex = "noindex" in robots.lower()
    canonical_link_html = "" if is_noindex else f'  <link rel="canonical" href="{esc(canonical_url)}">\n'
    og_url_html = "" if is_noindex else f'  <meta property="og:url" content="{esc(canonical_url)}">\n'
    twitter_url_html = "" if is_noindex else f'  <meta name="twitter:url" content="{esc(canonical_url)}">\n'
    hreflang_html = ""
    if hreflang_links and ENABLE_MULTILINGUAL_SEO:
        hreflang_html = "\n".join(
            f'  <link rel="alternate" hreflang="{esc(hl)}" href="{esc(url)}">'
            for hl, url in hreflang_links
        )

    ld_script = ""
    if json_ld is not None:
        ld_json = json.dumps(json_ld, ensure_ascii=False, indent=2)
        ld_script = f'  <script type="application/ld+json">\n{ld_json}\n  </script>'

    nav_items = [
        ("", "STALL Simulator", "home"),
        ("road-signs/", "94 Road Signs", "road-signs"),
        ("question-bank/", "412 Q&amp;A Bank", "question-bank"),
        ("online-llr-test/", "Online LLR Test", "online-llr-test"),
        ("rto-guide/", "RTO Guide", "rto-guide"),
        ("dl-test-guide/", "DL Track Test", "dl-test-guide"),
        ("traffic-fines/", "Fines &amp; Signals", "traffic-fines"),
        ("telangana-rto-codes/", "TS/TG Codes", "telangana-rto-codes"),
        ("cheatsheet/", "Cheatsheet", "cheatsheet"),
    ]
    if ENABLE_MULTILINGUAL_SEO:
        nav_items.extend([("te/", "తెలుగు", "te"), ("hi/", "हिन्दी", "hi")])

    nav_links_html = "\n".join(
        f'<a href="{rel_root}{href}" class="seo-nav-link{" active" if key == active_nav else ""}">{label}</a>'
        for href, label, key in nav_items
    )

    hero_cta_html = ""
    if include_hero_cta:
        hero_cta_html = f"""
      <div class="seo-cta-row">
        <a href="{rel_root}" class="seo-cta-primary">Take Official 20-Question STALL Mock Test</a>
        <a href="{rel_root}?tab=practice" class="seo-cta-secondary">Practice All 412 Questions Interactively</a>
      </div>"""

    breadcrumb_html = ""
    if breadcrumb_label:
        parent_crumb = ""
        if breadcrumb_parent:
            p_href, p_label = breadcrumb_parent
            parent_crumb = f'<a href="{rel_root}{esc(p_href)}">{esc(p_label)}</a>\n      <span aria-hidden="true">/</span>'
        breadcrumb_html = f"""
    <nav class="seo-breadcrumb" aria-label="Breadcrumb">
      <a href="{rel_root}">Home</a>
      <span aria-hidden="true">/</span>
      {parent_crumb}
      <span>{breadcrumb_label}</span>
    </nav>"""

    cur_og_locale = "te_IN" if (ENABLE_MULTILINGUAL_SEO and lang == "te") else ("hi_IN" if (ENABLE_MULTILINGUAL_SEO and lang == "hi") else "en_IN")
    alt_locale_meta = ""
    if ENABLE_MULTILINGUAL_SEO:
        alt_locales = [loc for loc in ("en_IN", "te_IN", "hi_IN") if loc != cur_og_locale]
        alt_locale_meta = "\n" + "\n".join(
            f'  <meta property="og:locale:alternate" content="{loc}">' for loc in alt_locales
        )

    font_families = "Plus+Jakarta+Sans:wght@400;500;600;700;800"
    if ENABLE_MULTILINGUAL_SEO:
        font_families = "Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600;700&family=" + font_families

    header_lang_html = ""
    if ENABLE_MULTILINGUAL_SEO:
        header_lang_html = f"""
        <div class="header-lang-links" aria-label="Language versions">
          <a href="{rel_root}" class="header-lang-link{' active' if lang == 'en' else ''}">EN</a>
          <a href="{rel_root}te/" class="header-lang-link{' active' if lang == 'te' else ''}">తెలుగు</a>
          <a href="{rel_root}hi/" class="header-lang-link{' active' if lang == 'hi' else ''}">हिन्दी</a>
        </div>"""

    return f"""<!DOCTYPE html>
<html lang="{esc(lang)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <link rel="icon" type="image/png" sizes="192x192" href="{rel_root}assets/icons/icon-192.png">
  <link rel="apple-touch-icon" href="{rel_root}assets/icons/icon-192.png">
{canonical_link_html}  <meta name="theme-color" content="#0B2545">
  <meta name="author" content="Sarva Capital">
  <meta name="robots" content="{esc(robots)}">
  <meta name="description" content="{esc(description)}">
  <meta name="keywords" content="{esc(keywords)}">
{hreflang_html}
  <link rel="alternate" type="text/plain" title="LLM Context Summary (llms.txt)" href="{BASE_URL}/llms.txt">
  <link rel="alternate" type="text/plain" title="Complete LLM Reference (llms-full.txt)" href="{BASE_URL}/llms-full.txt">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Telangana LLR Practice • Sarva Capital">
{og_url_html}  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{BASE_URL}/assets/images/og-preview.png?{ASSET_VER}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Telangana RTA Learner Licence Practice STALL Simulator">
  <meta property="og:locale" content="{cur_og_locale}">{alt_locale_meta}

  <meta name="twitter:card" content="summary_large_image">
{twitter_url_html}  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{BASE_URL}/assets/images/og-preview.png?{ASSET_VER}">

{ld_script}

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family={font_families}&display=swap" rel="stylesheet">
  <script>
    (function () {{
      try {{
        var pref = localStorage.getItem("TS_LLR_THEME") || "system";
        var dark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
        var resolved = pref === "system" ? (dark ? "dark" : "light") : pref;
        document.documentElement.dataset.theme = resolved;
        document.documentElement.dataset.themePreference = pref;
        document.documentElement.style.colorScheme = resolved;
      }} catch (e) {{}}
    }})();
  </script>
  <link rel="stylesheet" href="{rel_root}css/styles.css?{ASSET_VER}">
  <!-- AdSense verification & Auto Ads snippet: MUST remain in <head> during review & live operation -->
  <script id="google-adsense-script" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6573213692692289" crossorigin="anonymous"></script>
</head>
<body>
  <header class="app-header">
    <div class="header-container">
      <div class="brand-section">
        <a href="{rel_root}" class="brand-link">
          <div class="gov-emblem" aria-hidden="true">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="6" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="12" cy="18" r="1.5"/><rect x="7" y="2" width="10" height="20" rx="3"/></svg>
          </div>
          <div class="brand-titles">
            <span class="brand-title-text">Telangana RTA Learner's Licence Practice</span>
            <span class="subtitle">{esc(subtitle)}</span>
          </div>
        </a>
      </div>
      <div class="header-actions">{header_lang_html}
        <button type="button" class="control-btn theme-toggle-btn" id="btn-theme-toggle" title="Theme: Auto (matches system). Click to switch to Light" aria-label="Toggle theme">
          <span class="theme-icon" aria-hidden="true">◐</span>
          <span class="theme-label">Auto</span>
        </button>
        <a href="{rel_root}" class="control-btn" style="background:var(--cta-gold-bg); color:var(--cta-gold-text); border-color:var(--cta-gold-bg); font-weight:800;">
          Launch STALL Simulator
        </a>
      </div>
    </div>
  </header>

  <nav class="seo-nav-bar" aria-label="Study Guides Navigation">
    <div class="seo-nav-inner">
      {nav_links_html}
    </div>
  </nav>

  <main class="seo-main">
    {breadcrumb_html}
    <section class="seo-hero">
      <h1 style="font-size: 1.6rem; color: var(--primary-navy); font-weight: 800; line-height: 1.25; margin-bottom: 10px;">{h1}</h1>
      <p style="color: var(--text-secondary); font-size: 0.98rem; line-height: 1.6; max-width: 72ch;">{esc(description)}</p>
      {hero_cta_html}
    </section>
    {body_html}
  </main>

  <footer class="app-footer">
    <nav class="footer-directory-grid" aria-label="Study Resources and Compliance Links">
      <div>
        <h3 class="footer-col-title">Practice &amp; Study Tools</h3>
        <ul class="footer-link-list">
          <li><a href="{rel_root}">STALL Mock Test Simulator</a></li>
          <li><a href="{rel_root}?tab=practice">Interactive 412 Question Practice</a></li>
          <li><a href="{rel_root}?tab=flashcards">Road Sign Flip Flashcards</a></li>
          <li><a href="{rel_root}?tab=twins">Tricky Twins Comparisons</a></li>
          <li><a href="{rel_root}cheatsheet/">Printable Rapid Cheatsheet</a></li>
        </ul>
      </div>
      <div>
        <h3 class="footer-col-title">Question Banks &amp; Signs</h3>
        <ul class="footer-link-list">
          <li><a href="{rel_root}road-signs/">All 94 Road Signs &amp; Meanings</a></li>
          <li><a href="{rel_root}question-bank/">Complete 412 LLR Q&amp;A Bank</a></li>
          <li><a href="{rel_root}question-bank/road-signs/">Road Signs Q&amp;A Bank (94)</a></li>
          <li><a href="{rel_root}question-bank/traffic-rules/">Traffic Rules Q&amp;A Bank (159)</a></li>
          <li><a href="{rel_root}question-bank/driving-principles/">Driving Principles Bank (159)</a></li>
        </ul>
      </div>
      <div>
        <h3 class="footer-col-title">RTO &amp; Online Guides</h3>
        <ul class="footer-link-list">
          <li><a href="{rel_root}online-llr-test/">Online LLR &amp; Sarathi Test Guide</a></li>
          <li><a href="{rel_root}rto-guide/">Hyderabad RTO Guide &amp; Fees</a></li>
          <li><a href="{rel_root}dl-test-guide/">Permanent DL 8 &amp; H Track Guide</a></li>
          <li><a href="{rel_root}traffic-fines/">Traffic Fines &amp; Hand Signals</a></li>
          <li><a href="{rel_root}telangana-rto-codes/">All Telangana RTO Codes (01–38)</a></li>
        </ul>
      </div>
      <div>
        <h3 class="footer-col-title">About &amp; Legal</h3>
        <ul class="footer-link-list">
          <li><a href="{rel_root}about/">About, Disclaimer &amp; Contact</a></li>
          <li><a href="{rel_root}privacy-policy/">Privacy &amp; Cookie Policy</a></li>
          <li><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></li>
          <li><a href="https://transport.telangana.gov.in" target="_blank" rel="noopener">Official Telangana Transport ↗</a></li>
        </ul>
      </div>
    </nav>

    <div class="footer-bottom-bar">
      <div>
        <a href="{BASE_URL}/" style="color:var(--accent-blue); font-weight:700; text-decoration:none;">llr.sarvacapital.in</a> • Free Educational Resource by <a href="https://sarvacapital.in" target="_blank" rel="noopener" style="color:var(--accent-blue);">Sarva Capital</a>
      </div>
      <div>
        <a href="{rel_root}llms.txt" style="color:var(--text-secondary);">llms.txt</a> • <a href="{rel_root}llms-full.txt" style="color:var(--text-secondary);">llms-full.txt</a> • <a href="{rel_root}sitemap.xml" style="color:var(--text-secondary);">sitemap.xml</a>
      </div>
    </div>
  </footer>

  <button type="button" id="btn-back-to-top" class="back-to-top-btn no-print" aria-label="Back to top">↑ Top</button>

  <script type="module" src="{rel_root}js/theme-engine.js?{ASSET_VER}"></script>
  <script type="module" src="{rel_root}js/ad-manager.js?{ASSET_VER}"></script>
  <script>
    (() => {{
      const topBtn = document.getElementById("btn-back-to-top");
      if (topBtn) {{
        window.addEventListener("scroll", () => {{
          topBtn.classList.toggle("visible", window.scrollY > 420);
        }}, {{ passive: true }});
        topBtn.addEventListener("click", () => window.scrollTo({{ top: 0, behavior: "smooth" }}));
      }}
    }})();
  </script>
  {extra_scripts}
</body>
</html>
"""


def build_road_signs_page(signs):
    grouped = {"mandatory": [], "cautionary": [], "informatory": []}
    for s in signs:
        grouped.setdefault(s.get("signType", "mandatory"), []).append(s)

    labels = {
        "mandatory": ("Mandatory / Regulatory Road Signs", "Circles (Red border = Prohibition/Order, Blue circle = Compulsory instruction) plus STOP/GIVE WAY", "badge-mandatory"),
        "cautionary": ("Cautionary / Warning Road Signs", "Red-bordered Triangles alerting drivers to hazards ahead", "badge-cautionary"),
        "informatory": ("Informatory / Guide Road Signs", "Blue Rectangles indicating directions, facilities, distances, and road markings", "badge-informatory"),
    }

    sections = []
    item_list = []
    pos = 1
    for stype in ["mandatory", "cautionary", "informatory"]:
        items = grouped.get(stype, [])
        heading, sub, badge_cls = labels[stype]
        cards = []
        for s in items:
            ans_en = clean_text(s["options"]["en"][s["answerIndex"]])
            card_title = SIGN_TITLE_OVERRIDES.get(s["id"], ans_en)
            exp_en = clean_text(s["explanation"]["en"])
            w, h = get_img_dims(s["image"])
            search_blob = f"{card_title} {ans_en} {s['questionNumber']} {stype}".lower()
            cards.append(
                f"""<article class="seo-card rs-filter-card" id="{esc(s['id'])}" data-type="{esc(stype)}" data-search="{esc(search_blob)}">
  <div class="rs-card-head">
    <span class="seo-badge {badge_cls}">{esc(stype)}</span>
    <span class="tabular-nums rs-card-num">Sign #{s['questionNumber']}</span>
  </div>
  <div class="rs-img-wrap">
    <img class="rs-img" src="../{esc(s['image'])}?{ASSET_VER}" alt="{esc(card_title)} — Official Indian &amp; Telangana Road Sign" width="{w}" height="{h}" loading="lazy">
  </div>
  <h3 class="rs-card-title">{esc(card_title)}</h3>
  <p class="rs-card-desc">{esc(exp_en)}</p>
</article>"""
            )
            item_list.append({
                "@type": "ListItem",
                "position": pos,
                "name": card_title,
                "url": f"{BASE_URL}/road-signs/#{s['id']}",
                "image": f"{BASE_URL}/{s['image']}",
            })
            pos += 1

        sections.append(
            f"""<section id="{stype}" class="rs-section" data-section-type="{esc(stype)}" style="margin-bottom: 32px;">
  <h2 class="seo-section-heading">{esc(heading)} ({len(items)})</h2>
  <p class="seo-section-sub">{esc(sub)}</p>
  <div class="seo-grid">
    {"".join(cards)}
  </div>
</section>"""
        )

    m_cnt = len(grouped.get("mandatory", []))
    c_cnt = len(grouped.get("cautionary", []))
    i_cnt = len(grouped.get("informatory", []))
    total_cnt = len(signs)

    toolbar = f"""
<div class="seo-sticky-tools no-print">
  <div style="display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
    <button type="button" class="pill-btn active" data-rs-filter="all">All ({total_cnt})</button>
    <button type="button" class="pill-btn" data-rs-filter="mandatory">Mandatory ({m_cnt})</button>
    <button type="button" class="pill-btn" data-rs-filter="cautionary">Cautionary ({c_cnt})</button>
    <button type="button" class="pill-btn" data-rs-filter="informatory">Informatory ({i_cnt})</button>
    <a href="../?tab=flashcards" class="pill-btn">Practice Flashcards ↗</a>
    <a href="../question-bank/road-signs/" class="pill-btn">Road Signs Q&amp;As ↗</a>
  </div>
  <div style="display:flex; align-items:center; gap:8px; flex:1; max-width:360px; min-width:220px;">
    <input type="text" id="rs-search-input" class="seo-input" placeholder="Search sign name or #..." style="flex:1;" aria-label="Search road signs">
    <span id="rs-match-count" class="spec-pill">{total_cnt} signs</span>
  </div>
</div>
<p id="rs-empty-msg" class="seo-empty-msg">No road signs matched your filter. Try clearing the search box.</p>
"""

    faq_items = [
        ("How many road sign questions appear in the Telangana LLR STALL test?", "Exactly 8 out of the 20 test questions (40% of the exam) are Road Signs and Traffic Signal questions drawn from this official 94-sign curriculum."),
        ("How can I tell Mandatory, Cautionary, and Informatory signs apart?", "Mandatory signs are mostly circles (red border for prohibitions, blue circle for compulsory actions) plus STOP and GIVE WAY. Cautionary warning signs are red triangles. Informatory guide signs are blue rectangles."),
        ("Are these Telangana road signs valid for Parivahan Sarathi LLR exams across India?", "Yes. All traffic signs follow the national IRC:67 and Motor Vehicles Act standard used across Parivahan Sarathi learner licence tests throughout India."),
    ]

    body_html = (
        toolbar
        + sections[0]
        + ad_slot_html("seo_in_content", "leaderboard")
        + sections[1]
        + sections[2]
        + render_faq_block_html(faq_items, "Road Signs Exam FAQ")
        + ad_slot_html("seo_multiplex", "multiplex")
    )

    extra_scripts = """
  <script>
    (() => {
      const searchInput = document.getElementById("rs-search-input");
      const countEl = document.getElementById("rs-match-count");
      const emptyEl = document.getElementById("rs-empty-msg");
      let activeType = "all";

      function applyFilter() {
        const q = (searchInput?.value || "").trim().toLowerCase();
        let totalShown = 0;
        document.querySelectorAll(".rs-section").forEach(sec => {
          const secType = sec.getAttribute("data-section-type");
          let secShown = 0;
          sec.querySelectorAll(".rs-filter-card").forEach(card => {
            const typeMatch = activeType === "all" || card.getAttribute("data-type") === activeType;
            const hay = card.getAttribute("data-search") || "";
            const textMatch = !q || hay.includes(q);
            const show = typeMatch && textMatch;
            card.style.display = show ? "" : "none";
            if (show) { secShown++; totalShown++; }
          });
          sec.style.display = (secShown > 0 && (activeType === "all" || activeType === secType)) ? "" : "none";
        });
        if (countEl) countEl.textContent = `${totalShown} signs`;
        if (emptyEl) emptyEl.style.display = totalShown === 0 ? "block" : "none";
      }

      document.querySelectorAll("[data-rs-filter]").forEach(btn => {
        btn.addEventListener("click", () => {
          document.querySelectorAll("[data-rs-filter]").forEach(b => b.classList.remove("active"));
          btn.classList.add("active");
          activeType = btn.getAttribute("data-rs-filter");
          applyFilter();
        });
      });

      searchInput?.addEventListener("input", applyFilter);
    })();
  </script>"""

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Telangana Road Signs", "item": f"{BASE_URL}/road-signs/"},
                ],
            },
            {
                "@type": "ItemList",
                "name": "All 94 Telangana RTA Learner's Licence Road Signs",
                "numberOfItems": len(signs),
                "itemListElement": item_list,
            },
            faq_json_ld(faq_items),
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="road-signs/",
        title="All 94 Telangana Road Signs & Meanings • LLR 2026",
        description="Visual directory of all 94 official Telangana RTA & Indian road signs (Mandatory, Cautionary, Informatory) with meanings & exam explanations.",
        keywords="Telangana road signs with meaning, Indian traffic signs LLR, mandatory cautionary informatory signs India, Hyderabad RTO road signs list",
        h1="All 94 Telangana RTA Road Signs &amp; Official Meanings",
        subtitle="Complete Visual Reference for STALL & Parivahan LLR Exam (40% Exam Weightage)",
        breadcrumb_label="94 Road Signs",
        active_nav="road-signs",
        json_ld=json_ld,
        body_html=body_html,
        extra_scripts=extra_scripts,
    )
    write_file("road-signs/index.html", html_doc)


def render_qa_cards_html(items, sec_id, rel_root):
    cards = []
    for idx, q in enumerate(items, 1):
        img_html = ""
        if q.get("image"):
            w, h = get_img_dims(q["image"])
            img_html = f'<div class="qa-img-wrap"><img class="qa-img" src="{rel_root}{esc(q["image"])}?{ASSET_VER}" alt="Question diagram for {esc(q["id"])}" width="{w}" height="{h}" loading="lazy"></div>'
        opts_html = []
        for oi, opt in enumerate(q["options"]["en"]):
            is_ans = oi == q["answerIndex"]
            cls = "qa-option correct" if is_ans else "qa-option"
            mark = '<span class="qa-answer-mark"> ✓ (Correct)</span>' if is_ans else ""
            cleaned_opt = clean_text(opt)
            opts_html.append(f'<li class="{cls}"><span class="qb-case-target" data-raw="{esc(cleaned_opt)}">{oi + 1}. {esc(cleaned_opt)}</span>{mark}</li>')
        exp = clean_text(q.get("explanation", {}).get("en", ""))
        q_text = clean_text(q["text"]["en"])
        opts_text = " ".join(clean_text(o) for o in q["options"]["en"])
        search_blob = f"{q['id']} {idx} {q_text} {opts_text} {exp}".lower()
        cards.append(
            f"""<article class="qa-card qb-card" id="{esc(q['id'])}" data-cat="{esc(sec_id)}" data-search="{esc(search_blob)}">
  <div class="qa-meta">{esc(q['id'])} • Question #{idx}</div>
  <h3 class="qa-question-title qb-case-target" data-raw="{esc(q_text)}">{esc(q_text)}</h3>
  {img_html}
  <ol class="qa-options">{"".join(opts_html)}</ol>
  <p class="qa-explanation-box"><strong>Explanation:</strong> {esc(exp)}</p>
</article>"""
        )
    return "".join(cards)


def qb_subnav_html(rel_root, active_slug):
    links = [
        ("question-bank/", "All 412 Questions", "all"),
        ("question-bank/road-signs/", "Road Signs (94)", "road-signs"),
        ("question-bank/traffic-rules/", "Traffic Rules (159)", "traffic-rules"),
        ("question-bank/driving-principles/", "Driving Principles (159)", "driving-principles"),
    ]
    pills = "".join(
        f'<a href="{rel_root}{href}" class="pill-btn{" active" if slug == active_slug else ""}">{label}</a>'
        for href, label, slug in links
    )
    return f'<nav class="qb-subnav-pills no-print" aria-label="Question Bank Categories">{pills}</nav>'


def qb_toolbar_script(rel_root):
    return f"""
  <script type="module">
    import {{ toEasyReadCase, cleanPdfText }} from "{rel_root}js/text-formatter.js?{ASSET_VER}";
    const searchInput = document.getElementById("qb-search-input");
    const countEl = document.getElementById("qb-match-count");
    const emptyEl = document.getElementById("qb-empty-msg");
    const quizBtn = document.getElementById("btn-qb-quiz-mode");
    const caseBtn = document.getElementById("btn-qb-case-toggle");
    let activeCat = "all";
    let easyRead = false;

    function applyFilter() {{
      const q = (searchInput?.value || "").trim().toLowerCase();
      let shown = 0;
      document.querySelectorAll(".qb-section").forEach(sec => {{
        const secId = sec.getAttribute("data-sec");
        let secShown = 0;
        sec.querySelectorAll(".qb-card").forEach(card => {{
          const catOk = activeCat === "all" || card.getAttribute("data-cat") === activeCat;
          const hay = card.getAttribute("data-search") || "";
          const qOk = !q || hay.includes(q);
          const show = catOk && qOk;
          card.style.display = show ? "" : "none";
          if (show) {{ secShown++; shown++; }}
        }});
        sec.style.display = (secShown > 0 && (activeCat === "all" || activeCat === secId)) ? "" : "none";
      }});
      if (countEl) countEl.textContent = `${{shown}} Qs`;
      if (emptyEl) emptyEl.style.display = shown === 0 ? "block" : "none";
    }}

    document.querySelectorAll("[data-qb-cat]").forEach(btn => {{
      btn.addEventListener("click", () => {{
        document.querySelectorAll("[data-qb-cat]").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        activeCat = btn.getAttribute("data-qb-cat");
        applyFilter();
      }});
    }});

    searchInput?.addEventListener("input", applyFilter);

    quizBtn?.addEventListener("click", () => {{
      const on = document.body.classList.toggle("qb-quiz-mode");
      quizBtn.textContent = on ? "Show Answers" : "Quiz Mode (Hide Answers)";
      quizBtn.classList.toggle("active", on);
    }});

    caseBtn?.addEventListener("click", () => {{
      easyRead = !easyRead;
      caseBtn.textContent = easyRead ? "AA Official Caps" : "Aa Easy-Read";
      document.querySelectorAll(".qb-case-target").forEach(el => {{
        const raw = el.getAttribute("data-raw") || "";
        const prefixMatch = el.parentElement?.tagName === "LI" ? el.textContent.match(/^(\\d+\\.\\s)/) : null;
        const prefix = prefixMatch ? prefixMatch[1] : "";
        el.textContent = prefix + (easyRead ? toEasyReadCase(raw, "en") : cleanPdfText(raw));
      }});
    }});
  </script>"""


def build_question_bank_page(signs, rules, gp):
    categories = [
        ("road-signs", "Section 1: Road Signs & Signals (94 Questions)", signs),
        ("rules-of-road", "Section 2: Rules of the Road Regulations (159 Questions)", rules),
        ("general-principles", "Section 3: General Driving Principles & Safety (159 Questions)", gp),
    ]

    toolbar = qb_subnav_html("../", "all") + """
<div class="seo-sticky-tools no-print">
  <div style="display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
    <button type="button" class="pill-btn active" data-qb-cat="all">All (412)</button>
    <button type="button" class="pill-btn" data-qb-cat="road-signs">Road Signs (94)</button>
    <button type="button" class="pill-btn" data-qb-cat="rules-of-road">Rules (159)</button>
    <button type="button" class="pill-btn" data-qb-cat="general-principles">Principles (159)</button>
  </div>
  <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center;">
    <input type="text" id="qb-search-input" class="seo-input" placeholder="Search question keyword or #..." style="min-width:210px;" aria-label="Search questions">
    <button type="button" id="btn-qb-quiz-mode" class="btn-secondary-light" style="font-size:0.8rem; min-height:34px; padding:5px 10px;">Quiz Mode (Hide Answers)</button>
    <button type="button" id="btn-qb-case-toggle" class="btn-secondary-light" style="font-size:0.8rem; min-height:34px; padding:5px 10px;">Aa Easy-Read</button>
    <span id="qb-match-count" class="spec-pill">412 Qs</span>
  </div>
</div>
<p id="qb-empty-msg" class="seo-empty-msg">No questions matched your search filter.</p>
"""

    sections = []
    for sec_id, heading, items in categories:
        cards_html = render_qa_cards_html(items, sec_id, "../")
        sections.append(
            f"""<section id="{sec_id}" class="qb-section" data-sec="{esc(sec_id)}" style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:14px;">{esc(heading)}</h2>
  {cards_html}
</section>"""
        )

    body_html = (
        toolbar
        + sections[0]
        + ad_slot_html("seo_in_content", "leaderboard")
        + sections[1]
        + ad_slot_html("seo_in_content", "leaderboard")
        + sections[2]
        + ad_slot_html("seo_multiplex", "multiplex")
    )

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "412 LLR Question Bank", "item": f"{BASE_URL}/question-bank/"},
                ],
            },
            {
                "@type": "LearningResource",
                "name": "Telangana RTA LLR Complete 412 Question Bank with Answers",
                "description": "All 412 official Telangana Transport Department STALL Learner's Licence questions, options, verified answers, and explanations.",
                "url": f"{BASE_URL}/question-bank/",
                "learningResourceType": "Practice Question Bank",
                "about": {"@type": "Thing", "name": "Telangana RTA Learner's Licence (LLR / STALL) Exam"},
                "educationalLevel": "Learner's Licence Applicant",
                "isAccessibleForFree": True,
                "inLanguage": ["en"],
            },
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="question-bank/",
        title="Telangana LLR Question Bank 2026 • 412 Q&As",
        description="Study all 412 official Telangana RTA LLR (STALL) questions and answers across Road Signs (94), Rules of the Road (159), and Driving Principles (159).",
        keywords="Telangana LLR question bank 412 questions, Hyderabad RTO LLR questions and answers, STALL exam question bank, Parivahan LLR questions",
        h1="Complete Telangana RTA LLR Question Bank (412 Questions &amp; Answers)",
        subtitle="100% Verified Master Curriculum from Telangana Transport Department (Official Exam Text)",
        breadcrumb_label="412 Question Bank",
        active_nav="question-bank",
        json_ld=json_ld,
        body_html=body_html,
        extra_scripts=qb_toolbar_script("../"),
    )
    write_file("question-bank/index.html", html_doc)


def build_question_bank_category_page(
    *,
    slug,
    cat_key,
    heading,
    title,
    h1,
    subtitle,
    description,
    keywords,
    breadcrumb_label,
    items,
):
    rel_root = "../../"
    total = len(items)
    toolbar = qb_subnav_html(rel_root, slug) + f"""
<div class="seo-sticky-tools no-print">
  <div style="display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
    <a href="{rel_root}?tab=practice&cat={esc(cat_key)}" class="pill-btn active">Practice This Category Interactively ↗</a>
    <a href="{rel_root}?tab=exam" class="pill-btn">Take 20-Q STALL Mock Test ↗</a>
  </div>
  <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center;">
    <input type="text" id="qb-search-input" class="seo-input" placeholder="Search {total} questions..." style="min-width:210px;" aria-label="Search questions">
    <button type="button" id="btn-qb-quiz-mode" class="btn-secondary-light" style="font-size:0.8rem; min-height:34px; padding:5px 10px;">Quiz Mode (Hide Answers)</button>
    <button type="button" id="btn-qb-case-toggle" class="btn-secondary-light" style="font-size:0.8rem; min-height:34px; padding:5px 10px;">Aa Easy-Read</button>
    <span id="qb-match-count" class="spec-pill">{total} Qs</span>
  </div>
</div>
<p id="qb-empty-msg" class="seo-empty-msg">No questions matched your search filter.</p>
"""
    mid = total // 2
    part1 = render_qa_cards_html(items[:mid], slug, rel_root)
    part2 = render_qa_cards_html(items[mid:], slug, rel_root)
    body_html = (
        toolbar
        + f"""<section id="{esc(slug)}" class="qb-section" data-sec="{esc(slug)}" style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:14px;">{esc(heading)}</h2>
  {part1}
  {ad_slot_html("seo_in_content", "leaderboard")}
  {part2}
</section>"""
        + ad_slot_html("seo_multiplex", "multiplex")
    )

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Question Bank", "item": f"{BASE_URL}/question-bank/"},
                    {"@type": "ListItem", "position": 3, "name": breadcrumb_label, "item": f"{BASE_URL}/question-bank/{slug}/"},
                ],
            },
            {
                "@type": "LearningResource",
                "name": title,
                "description": description,
                "url": f"{BASE_URL}/question-bank/{slug}/",
                "learningResourceType": "Practice Question Bank",
                "about": {"@type": "Thing", "name": f"Telangana RTA LLR — {breadcrumb_label}"},
                "educationalLevel": "Learner's Licence Applicant",
                "isAccessibleForFree": True,
                "inLanguage": ["en"],
            },
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root=rel_root,
        canonical_path=f"question-bank/{slug}/",
        title=title,
        description=description,
        keywords=keywords,
        h1=h1,
        subtitle=subtitle,
        breadcrumb_label=breadcrumb_label,
        breadcrumb_parent=("question-bank/", "412 Question Bank"),
        active_nav="question-bank",
        json_ld=json_ld,
        body_html=body_html,
        extra_scripts=qb_toolbar_script(rel_root),
    )
    write_file(f"question-bank/{slug}/index.html", html_doc)


def build_online_llr_test_page(guide, popular):
    slot = popular["slotAndDownloadGuide"]
    steps_html = "".join(
        f"""<li class="qa-card" style="list-style:none;">
  <strong style="color:var(--accent-blue); font-size:1.02rem;">Step {s['step']}: {esc(s['title']['en'])}</strong>
  <p style="margin-top:6px; color:var(--text-primary); font-size:0.92rem;">{esc(s['detail']['en'])}</p>
</li>"""
        for s in slot["steps"]
    )
    faq_items = [
        ("Can I take the Telangana LLR test online from home without visiting the RTO?", "Yes. Applicants using Aadhaar e-KYC authentication on the Parivahan Sarathi portal (sarathi.parivahan.gov.in) can take the contactless online LLR test from a webcam-equipped laptop or desktop using AI facial recognition and Safe Exam Browser."),
        ("When is an in-person visit to the Hyderabad or Telangana RTO still required?", "You must visit your designated RTO STALL booth if you apply without Aadhaar e-KYC, have name/date-of-birth mismatches on Aadhaar, do not have a webcam-equipped computer, or encounter facial-liveness verification failures."),
        ("Does this simulator prepare me for both Sarathi online LLR and physical RTO STALL tests?", "Yes. Both modes test the same core Motor Vehicles Act / Central Motor Vehicles Rules (CMVR) road signs, traffic rules, and safe driving principles with 30 seconds per question and a 60% pass requirement. Our 412 questions are sourced directly from the official Telangana Transport Department bank."),
        ("How fast do I get my Learner's Licence after passing online?", "Upon passing, your digitally signed QR-coded Learner's Licence PDF is generated immediately (typically via SMS link within 15 minutes) and can be fetched in DigiLocker or NextGen mParivahan."),
    ]

    body_html = f"""
<section style="margin-bottom:28px;">
  <h2 class="seo-section-heading">Contactless Aadhaar Online LLR Test vs RTO STALL Booth</h2>
  <p class="seo-section-sub">Compare taking the Learner's Licence screening test from home on Parivahan Sarathi versus appearing in person at your district RTA office.</p>
  <div class="seo-card" style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; text-align:left;">
      <thead>
        <tr style="background:var(--surface-subtle);">
          <th style="padding:11px; border-bottom:2px solid var(--border-color);">Feature</th>
          <th style="padding:11px; border-bottom:2px solid var(--border-color);">Contactless Online Test (Home PC)</th>
          <th style="padding:11px; border-bottom:2px solid var(--border-color);">RTO STALL Computer Booth</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:10px; border-bottom:1px solid var(--border-color); font-weight:700;">Verification</td>
          <td style="padding:10px; border-bottom:1px solid var(--border-color);">Aadhaar OTP e-KYC + AI facial liveness check</td>
          <td style="padding:10px; border-bottom:1px solid var(--border-color);">MVI physical Aadhaar check + live biometric counter</td>
        </tr>
        <tr>
          <td style="padding:10px; border-bottom:1px solid var(--border-color); font-weight:700;">Requirements</td>
          <td style="padding:10px; border-bottom:1px solid var(--border-color);">Laptop/PC with webcam, microphone &amp; Safe Exam Browser</td>
          <td style="padding:10px; border-bottom:1px solid var(--border-color);">Printed Form 2, Slot Slip, original Aadhaar &amp; age proof</td>
        </tr>
        <tr>
          <td style="padding:10px; border-bottom:1px solid var(--border-color); font-weight:700;">Exam Pattern</td>
          <td style="padding:10px; border-bottom:1px solid var(--border-color);">Timed MCQs (60% pass mark, road signs &amp; MV Act rules)</td>
          <td style="padding:10px; border-bottom:1px solid var(--border-color);">20 MCQs (8 Signs + 8 Rules + 4 Principles), 12/20 to pass</td>
        </tr>
        <tr>
          <td style="padding:10px; font-weight:700;">Licence Delivery</td>
          <td style="padding:10px;">Instant signed digital LLR PDF + DigiLocker / mParivahan</td>
          <td style="padding:10px;">SMS link within 15 minutes + DigiLocker / mParivahan</td>
        </tr>
      </tbody>
    </table>
  </div>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section style="margin-bottom:28px;">
  <h2 class="seo-section-heading">Step-by-Step Online LLR Application &amp; Test Flow</h2>
  <ol style="padding:0;">{steps_html}</ol>
</section>

<section class="seo-card" style="background:var(--surface-subtle);">
  <h2 class="seo-section-heading">Curriculum Scope &amp; Authoritative Source</h2>
  <p style="color:var(--text-primary); font-size:0.92rem; line-height:1.6;">
    All <strong>412 practice questions</strong> in this simulator are verified directly from the official <strong>Government of Telangana Transport Department</strong> question bank. Because Indian traffic symbols (IRC:67) and the <em>Rules of the Road Regulations, 1989</em> under the Motor Vehicles Act apply uniformly across states, practicing our <a href="../road-signs/" style="color:var(--accent-blue); font-weight:700;">94 Road Signs</a> and <a href="../question-bank/traffic-rules/" style="color:var(--accent-blue); font-weight:700;">159 Traffic Rules</a> builds exam-ready accuracy for both Telangana STALL and Parivahan Sarathi learners.
  </p>
</section>
{render_faq_block_html(faq_items, "Online LLR Test FAQ")}
{ad_slot_html("seo_multiplex", "multiplex")}
"""

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Online LLR Test Guide", "item": f"{BASE_URL}/online-llr-test/"},
                ],
            },
            {
                "@type": "HowTo",
                "name": "How to Take the Online Learner's Licence (LLR) Test via Parivahan Sarathi",
                "description": "Apply online with Aadhaar e-KYC, complete proctored webcam verification, and pass your LLR test from home or an RTO kiosk.",
                "step": [
                    {"@type": "HowToStep", "position": s["step"], "name": s["title"]["en"], "text": s["detail"]["en"]}
                    for s in slot["steps"]
                ],
            },
            faq_json_ld(faq_items),
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="online-llr-test/",
        title="Online LLR Test & Parivahan Sarathi Mock 2026",
        description="Complete guide to taking the Telangana & Parivahan Sarathi contactless Aadhaar online LLR test from home vs RTO STALL booth, plus free 412-Q mock practice.",
        keywords="online LLR test Telangana, contactless Aadhaar LLR test, Parivahan Sarathi learner licence mock test, online LL test webcam rules, Telangana RTA online test",
        h1="Online LLR Test Guide (Parivahan Sarathi &amp; Telangana STALL)",
        subtitle="Contactless Aadhaar e-KYC Exam from Home vs RTO Booth + Verified Practice Syllabus",
        breadcrumb_label="Online LLR Test Guide",
        active_nav="online-llr-test",
        json_ld=json_ld,
        body_html=body_html,
    )
    write_file("online-llr-test/index.html", html_doc)


def build_rto_guide_page(guide):
    checklist_html = "".join(
        f"""<li class="seo-card" style="list-style:none;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; gap:8px;">
    <strong style="color:var(--primary-navy);">{esc(c['item']['en'])}</strong>
    <span class="seo-badge {'badge-mandatory' if c['mandatory'] else 'badge-informatory'}">{'Mandatory' if c['mandatory'] else 'Optional'}</span>
  </div>
  <p style="font-size:0.88rem; color:var(--text-secondary);">{esc(c['desc']['en'])}</p>
</li>"""
        for c in guide["checklist"]
    )

    steps_html = "".join(
        f"""<li class="qa-card" style="list-style:none;">
  <strong style="color:var(--accent-blue); font-size:1.02rem;">Step {s['step']}: {esc(s['title']['en'])}</strong>
  <p style="margin-top:6px; color:var(--text-primary); font-size:0.92rem;">{esc(s['detail']['en'])}</p>
</li>"""
        for s in guide["steps"]
    )

    centers_html = "".join(
        f"""<article class="seo-card">
  <span class="seo-badge badge-informatory" style="margin-bottom:8px;">{esc(c['code'])}</span>
  <h3 style="font-size:1rem; color:var(--primary-navy); font-weight:700; margin-bottom:4px;">{esc(c['name']['en'])}</h3>
  <p style="font-size:0.84rem; color:var(--accent-blue); font-weight:600; margin-bottom:6px;">Areas: {esc(c['area']['en'])}</p>
  <p style="font-size:0.84rem; color:var(--text-secondary); margin-bottom:6px;">{esc(c['address']['en'])}</p>
  <p style="font-size:0.8rem; color:var(--success-green); font-weight:600;">Hours: {esc(c['hours'])}</p>
</article>"""
        for c in guide["centers"]
    )

    fees_html = "".join(
        f"""<tr>
  <td style="padding:10px; border-bottom:1px solid var(--border-color); font-weight:600;">{esc(f['category']['en'])}</td>
  <td style="padding:10px; border-bottom:1px solid var(--border-color); color:var(--text-secondary);">{esc(f['breakup']['en'])}</td>
  <td class="tabular-nums" style="padding:10px; border-bottom:1px solid var(--border-color); font-weight:800; color:var(--success-green);">{esc(f['amount'])}</td>
</tr>"""
        for f in guide["feeRules"]["fees"]
    )

    tips_html = "".join(
        f"""<article class="seo-card" style="background:var(--accent-gold-light); border-color:var(--accent-gold);">
  <h3 style="font-size:0.98rem; color:var(--warning-amber); font-weight:700; margin-bottom:6px;">{esc(tip['title']['en'])}</h3>
  <p style="font-size:0.88rem; color:var(--text-primary);">{esc(tip['desc']['en'])}</p>
</article>"""
        for tip in guide["topTips"]
    )

    faq_items = [
        ("What is the LLR fee in Telangana for bike and car together?", "For one vehicle class (e.g., MCWG motorcycle), the fee is ₹200 (₹150 test fee + ₹50 service fee). For two classes (e.g., Two-Wheeler + Car LMV), the fee is ₹350 (₹300 + ₹50 service fee)."),
        ("How many days after failing the Telangana LLR test can I book a retest?", "You can book a retest slot after 7 days on transport.telangana.gov.in by paying a ₹150 retest fee."),
        ("How long is a Telangana Learner's Licence valid?", "A Learner's Licence is valid for 6 months (180 days) across India. You become eligible for the Permanent Driving Licence (DL) track test after completing 30 days from LLR issue."),
    ]

    body_html = f"""
<nav class="toc-bar no-print" aria-label="RTO Guide Sections">
  <a href="#sec-docs" class="toc-pill">1. Documents Checklist</a>
  <a href="#sec-steps" class="toc-pill">2. Test-Day Steps</a>
  <a href="#sec-centers" class="toc-pill">3. Hyderabad RTO Centers</a>
  <a href="#sec-fees" class="toc-pill">4. Fees &amp; Validity</a>
  <a href="#sec-tips" class="toc-pill">5. High-Scorer Tips</a>
  <a href="../online-llr-test/" class="toc-pill">Online Aadhaar Test ↗</a>
</nav>

<section id="sec-docs" class="guide-section-anchor" style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">1. Required Documents Checklist for Telangana LLR Test</h2>
  <ul class="seo-grid" style="padding:0;">{checklist_html}</ul>
</section>

<section id="sec-steps" class="guide-section-anchor" style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">2. Test-Day 5-Step Walkthrough at Hyderabad RTO</h2>
  <ol style="padding:0;">{steps_html}</ol>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section id="sec-centers" class="guide-section-anchor" style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">3. Hyderabad &amp; Telangana RTO Testing Centers Directory</h2>
  <div class="seo-grid">{centers_html}</div>
</section>

<section id="sec-fees" class="guide-section-anchor" style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">4. Official LLR Fee Structure, Retest &amp; Validity Rules</h2>
  <div class="seo-card" style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; text-align:left;">
      <thead>
        <tr style="background:var(--surface-subtle);">
          <th style="padding:10px; border-bottom:2px solid var(--border-color);">Vehicle Class</th>
          <th style="padding:10px; border-bottom:2px solid var(--border-color);">Fee Breakdown</th>
          <th style="padding:10px; border-bottom:2px solid var(--border-color);">Total Fee</th>
        </tr>
      </thead>
      <tbody>{fees_html}</tbody>
    </table>
    <p style="margin-top:12px; font-size:0.9rem; color:var(--text-primary);"><strong>Retest Policy:</strong> {esc(guide['feeRules']['retestRule']['en'])}</p>
    <p style="margin-top:8px; font-size:0.9rem; color:var(--text-primary);"><strong>LLR Validity &amp; Permanent DL Rule:</strong> {esc(guide['feeRules']['validityRule']['en'])}</p>
  </div>
</section>

<section id="sec-tips" class="guide-section-anchor">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">5. Top Tips to Pass on Your First Attempt</h2>
  <div class="seo-grid">{tips_html}</div>
</section>
{render_faq_block_html(faq_items, "Hyderabad & Telangana RTO FAQ")}
{ad_slot_html("seo_multiplex", "multiplex")}
"""

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Hyderabad RTO Guide", "item": f"{BASE_URL}/rto-guide/"},
                ],
            },
            {
                "@type": "HowTo",
                "name": guide["title"]["en"],
                "description": guide["subtitle"]["en"],
                "step": [
                    {"@type": "HowToStep", "position": s["step"], "name": s["title"]["en"], "text": s["detail"]["en"]}
                    for s in guide["steps"]
                ],
            },
            faq_json_ld(faq_items),
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="rto-guide/",
        title="Hyderabad & Telangana RTO LLR Guide 2026 • Fees & Centers",
        description="Telangana RTA LLR test-day guide: Aadhaar & Form 2 checklist, TS/TG-07 to 12 Hyderabad RTO addresses, ₹200/₹350 fees, 7-day retest & STALL tips.",
        keywords="Hyderabad RTO LLR documents, Kondapur RTO TS-07 TG-07 address, Khairatabad RTO TS-09 TG-09 LLR test, Telangana LLR fees 2026, Uppal Secunderabad RTO timings",
        h1="Hyderabad &amp; Telangana RTA Learner's Licence (LLR) Guide",
        subtitle="Documents Checklist, RTO Center Addresses (TS/TG 07–12), Fees & Test-Day Steps",
        breadcrumb_label="Hyderabad RTO Guide",
        active_nav="rto-guide",
        json_ld=json_ld,
        body_html=body_html,
    )
    write_file("rto-guide/index.html", html_doc)


def build_cheatsheet_page(cheatsheet, twins, popular):
    rules_html = "".join(
        f"""<article class="cheatsheet-rule-card">
  <span class="rule-num-badge">{idx}</span>
  <div>
    <strong style="color:var(--primary-navy); display:block; margin-bottom:4px;">{esc(gr['rule']['en'])}</strong>
  </div>
</article>"""
        for idx, gr in enumerate(cheatsheet["goldenRules"], 1)
    )

    hs = popular["handSignals"]
    hs_cards = []
    for item in hs["items"]:
        w, h = get_img_dims(item["image"])
        hs_cards.append(
            f"""<article class="seo-card" style="display:flex; gap:12px; align-items:center;">
  <img src="../{esc(item['image'])}?{ASSET_VER}" alt="{esc(item['name']['en'])}" width="{w}" height="{h}" loading="lazy" style="width:72px; height:auto; max-height:72px; object-fit:contain; background:var(--sign-surface); border:1px solid var(--border-color); border-radius:8px; padding:4px; flex-shrink:0;">
  <div>
    <span class="seo-badge badge-informatory" style="margin-bottom:4px;">{esc(item['kind'])}</span>
    <h3 style="font-size:0.95rem; color:var(--primary-navy); font-weight:700; margin-bottom:4px;">{esc(item['name']['en'])}</h3>
    <p style="font-size:0.82rem; color:var(--text-secondary);">{esc(item['desc']['en'])}</p>
  </div>
</article>"""
        )
    hs_html = "".join(hs_cards)

    twin_cards = []
    for p in twins:
        wa, ha = get_img_dims(p["signA"]["image"])
        wb, hb = get_img_dims(p["signB"]["image"])
        twin_cards.append(
            f"""<article class="seo-card">
  <h3 style="font-size:1.05rem; color:var(--primary-navy); font-weight:800; margin-bottom:12px;">{esc(p['title']['en'])}</h3>
  <div class="twins-comparison-grid">
    <div style="background:var(--surface-subtle); border:1px solid var(--border-color); padding:10px; border-radius:8px; text-align:center;">
      <img src="../{esc(p['signA']['image'])}?{ASSET_VER}" alt="{esc(p['signA']['name']['en'])}" width="{wa}" height="{ha}" loading="lazy" style="max-height:80px; width:auto; height:auto;">
      <strong style="display:block; font-size:0.85rem; margin:6px 0;">{esc(p['signA']['name']['en'])}</strong>
      <p style="font-size:0.8rem; color:var(--text-secondary); text-align:left;">{esc(p['signA']['rule']['en'])}</p>
    </div>
    <div style="background:var(--surface-subtle); border:1px solid var(--border-color); padding:10px; border-radius:8px; text-align:center;">
      <img src="../{esc(p['signB']['image'])}?{ASSET_VER}" alt="{esc(p['signB']['name']['en'])}" width="{wb}" height="{hb}" loading="lazy" style="max-height:80px; width:auto; height:auto;">
      <strong style="display:block; font-size:0.85rem; margin:6px 0;">{esc(p['signB']['name']['en'])}</strong>
      <p style="font-size:0.8rem; color:var(--text-secondary); text-align:left;">{esc(p['signB']['rule']['en'])}</p>
    </div>
  </div>
  <div class="twins-memory-hook"><strong>Memory Hook:</strong> {esc(p['memoryHook']['en'])}</div>
</article>"""
        )
    twins_html = "".join(twin_cards)

    faq_items = [
        ("What is the difference between No Parking and No Stopping?", "No Parking (single slash) forbids leaving a vehicle unattended but allows quick passenger drop-off/pick-up. No Stopping (crossed X) strictly forbids stopping even for a second."),
        ("What do flashing red and flashing yellow traffic lights mean?", "Flashing Yellow means slow down and proceed with caution. Flashing Red means treat it like a STOP sign—halt completely, observe traffic, and proceed only when safe."),
        ("What are the emergency numbers tested in the Telangana LLR exam?", "Police = 100, Fire = 101, and Ambulance = 108."),
    ]

    body_html = f"""
<div class="no-print" style="margin-bottom:20px; display:flex; gap:10px; flex-wrap:wrap;">
  <button onclick="window.print()" class="seo-cta-primary" style="border:none; cursor:pointer;">Print / Save PDF Revision Sheet</button>
  <a href="../road-signs/" class="seo-cta-secondary">View All 94 Road Signs</a>
</div>

<section style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">Top 10 Golden Rules (10-Minute Pre-Exam Revision)</h2>
  <div class="cheatsheet-rules-grid">{rules_html}</div>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">{esc(hs['title']['en'])}</h2>
  <div class="seo-grid">{hs_html}</div>
</section>

<section>
  <h2 class="seo-section-heading" style="margin-bottom:12px;">Tricky Twins: Commonly Confused Road Signs</h2>
  <div class="seo-grid" style="grid-template-columns:repeat(auto-fill, minmax(320px, 1fr));">{twins_html}</div>
</section>
{render_faq_block_html(faq_items, "Rapid Revision FAQ")}
{ad_slot_html("seo_multiplex", "multiplex")}
"""

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Cheatsheet & Tricky Twins", "item": f"{BASE_URL}/cheatsheet/"},
                ],
            },
            {
                "@type": "LearningResource",
                "name": "Telangana LLR Rapid Cheatsheet & Confusing Road Signs Guide",
                "description": "Quick 10-minute revision rules and side-by-side comparisons of easily confused road signs for the Telangana STALL exam.",
                "isAccessibleForFree": True,
                "inLanguage": ["en"],
            },
            faq_json_ld(faq_items),
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="cheatsheet/",
        title="Telangana LLR Cheatsheet & Hand Signals 2026",
        description="Printable 10-minute revision cheatsheet for Telangana RTA LLR: pass mark, sign shapes, hand signals, emergency numbers, and Tricky Twins.",
        keywords="Telangana LLR cheatsheet PDF, tricky road signs comparison, driver hand signals India, No Parking vs No Stopping sign, Hyderabad LLR quick tips",
        h1="Telangana LLR Rapid Cheatsheet, Hand Signals &amp; Tricky Twins",
        subtitle="Printable Last-Minute Revision Rules, Hand Signals & Confusing Sign Comparisons",
        breadcrumb_label="Rapid Cheatsheet",
        active_nav="cheatsheet",
        json_ld=json_ld,
        body_html=body_html,
    )
    write_file("cheatsheet/index.html", html_doc)


def build_dl_test_guide_page(popular):
    dl = popular["dlTrackGuide"]
    slot = popular["slotAndDownloadGuide"]

    slot_html = "".join(
        f"""<li class="qa-card" style="list-style:none;">
  <strong style="color:var(--accent-blue); font-size:1.02rem;">Step {s['step']}: {esc(s['title']['en'])}</strong>
  <p style="margin-top:6px; color:var(--text-primary); font-size:0.92rem;">{esc(s['detail']['en'])}</p>
</li>"""
        for s in slot["steps"]
    )

    tracks_html = "".join(
        f"""<article class="seo-card">
  <span class="seo-badge badge-informatory" style="margin-bottom:8px;">{esc(tr['badge'])}</span>
  <h3 style="font-size:1.05rem; color:var(--primary-navy); font-weight:800; margin-bottom:10px;">{esc(tr['title']['en'])}</h3>
  <ul style="padding-left:18px; color:var(--text-primary); font-size:0.9rem; line-height:1.5;">
    {"".join(f'<li style="margin-bottom:6px;">{esc(pt)}</li>' for pt in tr['points']['en'])}
  </ul>
</article>"""
        for tr in dl["tracks"]
    )

    docs_html = "".join(
        f'<li style="margin-bottom:6px;">{esc(d)}</li>' for d in dl["documents"]["en"]
    )

    faq_items = [
        ("When can I apply for a Permanent Driving Licence (DL) after passing the LLR test?", "You must hold your valid LLR for at least 30 days and apply before it expires at 180 days (6 months)."),
        ("What causes instant failure on Telangana automated Figure-8 and H tracks?", "Putting a foot down on the bike Figure-8 track, hitting sensor poles/curbs, stalling on gradients, or forgetting helmet/seatbelt and turn indicators."),
        ("Is the online Road Safety Training module mandatory before DL slot booking?", "Telangana Transport provides an online Road Safety Training module at tgtransport.online/llr/—complete it before booking your DL track slot if prompted on your application."),
    ]

    body_html = f"""
<section style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">1. {esc(slot['title']['en'])}</h2>
  <ol style="padding:0;">{slot_html}</ol>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:8px;">2. {esc(dl['title']['en'])}</h2>
  <p style="color:var(--text-secondary); margin-bottom:14px;">{esc(dl['eligibility']['en'])} {esc(dl['automatedTracksNote']['en'])}</p>
  <div class="seo-grid" style="grid-template-columns:repeat(auto-fit, minmax(300px, 1fr));">{tracks_html}</div>
</section>

<section>
  <h2 class="seo-section-heading" style="margin-bottom:12px;">3. Documents &amp; Test Vehicle Checklist for DL Track Day</h2>
  <div class="seo-card" style="background:var(--success-bg); border-color:var(--success-green);">
    <ul style="padding-left:18px; color:var(--text-primary); font-size:0.94rem; line-height:1.55;">{docs_html}</ul>
  </div>
</section>
{render_faq_block_html(faq_items, "Permanent DL Track Test FAQ")}
{ad_slot_html("seo_multiplex", "multiplex")}
"""

    dl_howto_steps = [
        {
            "@type": "HowToStep",
            "position": 1,
            "name": "Check 30-Day LLR Eligibility & Automated Track Readiness",
            "text": f"{dl['eligibility']['en']} {dl['automatedTracksNote']['en']}",
        },
        *[
            {
                "@type": "HowToStep",
                "position": i,
                "name": tr["title"]["en"],
                "text": " ".join(tr["points"]["en"]),
            }
            for i, tr in enumerate(dl["tracks"], 2)
        ],
        {
            "@type": "HowToStep",
            "position": len(dl["tracks"]) + 2,
            "name": "Carry Original Documents & L-Marked Test Vehicle",
            "text": "; ".join(dl["documents"]["en"]),
        },
    ]

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Permanent DL Track Test Guide", "item": f"{BASE_URL}/dl-test-guide/"},
                ],
            },
            {
                "@type": "HowTo",
                "name": dl["title"]["en"],
                "description": dl["subtitle"]["en"],
                "step": dl_howto_steps,
            },
            faq_json_ld(faq_items),
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="dl-test-guide/",
        title="Telangana DL 8-Track & H-Track Test Guide 2026",
        description="Telangana RTA Permanent DL guide: Two-Wheeler 8-Track & Car H-Track rules, automated sensor tracks, Parivahan slot booking & DigiLocker LLR.",
        keywords="Telangana driving licence track test, Hyderabad 8 track bike test, Kondapur H track car test, tgtransport.online llr, digital LLR download DigiLocker",
        h1="Telangana Permanent Driving Licence (DL) Track Test &amp; Slot Booking Guide",
        subtitle="Two-Wheeler '8' Track, Car 'H' Track, Automated RTA Tracks & Digital LLR Download",
        breadcrumb_label="DL Track Test Guide",
        active_nav="dl-test-guide",
        json_ld=json_ld,
        body_html=body_html,
    )
    write_file("dl-test-guide/index.html", html_doc)


def build_traffic_fines_page(popular):
    fines = popular["trafficFines"]
    hs = popular["handSignals"]

    rows_html = "".join(
        f"""<tr>
  <td style="padding:12px; border-bottom:1px solid var(--border-color); font-weight:600; color:var(--primary-navy);">{esc(item['offence']['en'])}</td>
  <td style="padding:12px; border-bottom:1px solid var(--border-color); font-weight:700; color:var(--danger-red);">{esc(item['fine'])}</td>
  <td style="padding:12px; border-bottom:1px solid var(--border-color); color:var(--text-secondary);">{esc(item['section'])}</td>
</tr>"""
        for item in fines["items"]
    )

    hs_cards = []
    for item in hs["items"]:
        w, h = get_img_dims(item["image"])
        hs_cards.append(
            f"""<article class="seo-card" style="display:flex; gap:12px; align-items:center;">
  <img src="../{esc(item['image'])}?{ASSET_VER}" alt="{esc(item['name']['en'])}" width="{w}" height="{h}" loading="lazy" style="width:76px; height:auto; max-height:76px; object-fit:contain; background:var(--sign-surface); border:1px solid var(--border-color); border-radius:8px; padding:4px; flex-shrink:0;">
  <div>
    <span class="seo-badge badge-informatory" style="margin-bottom:4px;">{esc(item['kind'])}</span>
    <h3 style="font-size:0.95rem; color:var(--primary-navy); font-weight:700; margin-bottom:4px;">{esc(item['name']['en'])}</h3>
    <p style="font-size:0.84rem; color:var(--text-secondary);">{esc(item['desc']['en'])}</p>
  </div>
</article>"""
        )
    hs_html = "".join(hs_cards)

    faq_items = [
        ("Are digital Driving Licence and RC in DigiLocker or mParivahan valid in Telangana?", "Yes. Under the Central Motor Vehicles Rules, electronic Driving Licence, Learner's Licence, RC, Insurance, and PUC stored in DigiLocker or NextGen mParivahan are legally valid across India."),
        ("What is the fine for riding without a helmet or driving without a licence in Hyderabad?", "Riding without a helmet carries a ₹1,000 penalty plus 3-month DL suspension (Section 194D). Driving without a valid licence carries a ₹5,000 fine (Section 181)."),
    ]

    body_html = f"""
<section style="margin-bottom:32px;">
  <h2 class="seo-section-heading" style="margin-bottom:12px;">{esc(fines['title']['en'])}</h2>
  <p style="color:var(--text-secondary); margin-bottom:12px;">{esc(fines['subtitle']['en'])} Digital Driving Licence &amp; RC stored in <strong>DigiLocker</strong> or <strong>mParivahan</strong> are legally valid across Telangana and India.</p>
  <div class="seo-card" style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; text-align:left;">
      <thead>
        <tr style="background:var(--surface-subtle);">
          <th style="padding:12px; border-bottom:2px solid var(--border-color);">Traffic Offence</th>
          <th style="padding:12px; border-bottom:2px solid var(--border-color);">Penalty / Fine</th>
          <th style="padding:12px; border-bottom:2px solid var(--border-color);">MV Act Section</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section>
  <h2 class="seo-section-heading" style="margin-bottom:12px;">{esc(hs['title']['en'])}</h2>
  <div class="seo-grid">{hs_html}</div>
</section>
{render_faq_block_html(faq_items, "Traffic Fines & Hand Signals FAQ")}
{ad_slot_html("seo_multiplex", "multiplex")}
"""

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Telangana Traffic Fines & Hand Signals", "item": f"{BASE_URL}/traffic-fines/"},
                ],
            },
            {
                "@type": "LearningResource",
                "name": "Telangana Traffic Fines, E-Challan Penalties & Hand Signals Guide",
                "description": "Motor Vehicles Act traffic fines in Hyderabad & Telangana plus visual driver hand signals and traffic police signals.",
                "isAccessibleForFree": True,
                "inLanguage": ["en"],
            },
            faq_json_ld(faq_items),
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="traffic-fines/",
        title="Telangana Traffic Fines 2026 & Hand Signals",
        description="Updated Telangana & Hyderabad traffic challan fines (helmet, drunk driving, overspeeding, no licence) under the MV Act plus driver & police hand signals.",
        keywords="Hyderabad traffic fines 2026, Telangana e-challan penalty list, drunk driving fine Hyderabad, helmet fine Telangana, driver hand signals traffic police signals",
        h1="Telangana Traffic Fines, E-Challan Penalties &amp; Hand Signals",
        subtitle="Motor Vehicles Act Penalty Schedule & Visual Police / Driver Hand Signals",
        breadcrumb_label="Traffic Fines & Hand Signals",
        active_nav="traffic-fines",
        json_ld=json_ld,
        body_html=body_html,
    )
    write_file("traffic-fines/index.html", html_doc)


def build_district_rto_codes_page(popular):
    cards = "".join(
        f"""<article id="rto-{esc(d['code'])}" class="seo-card rto-code-card" data-search="{esc((d['code'] + ' ts-' + d['code'] + ' tg-' + d['code'] + ' ' + d['district']).lower())}" style="display:flex; align-items:center; gap:12px;">
  <span class="tabular-nums" style="background:var(--badge-rto-bg); color:var(--badge-rto-text); font-weight:800; font-size:0.82rem; padding:6px 10px; border-radius:6px; flex-shrink:0;">TS / TG-{esc(d['code'])}</span>
  <div>
    <h3 style="font-size:0.98rem; color:var(--primary-navy); font-weight:700;">{esc(d['district'])}</h3>
    <p style="font-size:0.78rem; color:var(--text-muted);">Telangana RTA Office Code {esc(d['code'])}</p>
  </div>
</article>"""
        for d in popular["districtRtoCodes"]
    )

    faq_items = [
        ("Did Telangana change RTO codes from TS to TG?", "Yes. Telangana updated new vehicle registration and RTA office prefixes from TS to TG while keeping the same district numbers 01 through 38 (for example, TS-09 / TG-09 for Khairatabad and TS-07 / TG-07 for Ranga Reddy / Kondapur)."),
        ("Is the LLR question bank the same for every Telangana district RTO?", "Yes. Whether you apply at Hyderabad (TG-09), Kondapur (TG-07), Warangal (TG-03/TG-24), Karimnagar (TG-02), Nizamabad (TG-16), or Khammam (TG-04), every district uses the same 412-question Telangana Transport Department STALL curriculum."),
    ]

    body_html = f"""
<section>
  <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:12px; margin-bottom:16px;">
    <div>
      <h2 class="seo-section-heading">Complete District-Wise Telangana RTA Office Codes (01 to 38)</h2>
      <p style="color:var(--text-secondary); max-width:68ch;">Telangana transitioned vehicle registration prefixes from <strong>TS</strong> to <strong>TG</strong>, while keeping the exact same district numerical codes (01–38). All STALL Learner's Licence tests follow the same 412-question bank.</p>
    </div>
    <input type="text" id="rto-codes-search" class="seo-input" placeholder="Search district or code (e.g. Warangal, 07)..." style="min-width:250px;" aria-label="Search Telangana RTO district or code">
  </div>
  <div class="seo-grid">{cards}</div>
  <p id="rto-codes-empty" class="seo-empty-msg">No Telangana district matched your search.</p>
</section>
{render_faq_block_html(faq_items, "Telangana TS / TG RTO Codes FAQ")}
{ad_slot_html("seo_multiplex", "multiplex")}
"""

    extra_scripts = """
  <script>
    (() => {
      const inp = document.getElementById("rto-codes-search");
      const empty = document.getElementById("rto-codes-empty");
      inp?.addEventListener("input", e => {
        const q = e.target.value.trim().toLowerCase();
        let shown = 0;
        document.querySelectorAll(".rto-code-card").forEach(c => {
          const ok = !q || (c.getAttribute("data-search") || "").includes(q);
          c.style.display = ok ? "flex" : "none";
          if (ok) shown++;
        });
        if (empty) empty.style.display = shown === 0 ? "block" : "none";
      });
    })();
  </script>"""

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": "Telangana RTO Codes", "item": f"{BASE_URL}/telangana-rto-codes/"},
                ],
            },
            {
                "@type": "ItemList",
                "name": "All Telangana District RTO / RTA Codes (TS-01 to TS-38 / TG-01 to TG-38)",
                "numberOfItems": len(popular["districtRtoCodes"]),
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": i,
                        "name": f"TS-{d['code']} / TG-{d['code']} {d['district']}",
                        "url": f"{BASE_URL}/telangana-rto-codes/#rto-{d['code']}",
                    }
                    for i, d in enumerate(popular["districtRtoCodes"], 1)
                ],
            },
            faq_json_ld(faq_items),
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="telangana-rto-codes/",
        title="Telangana RTO District Codes (TS / TG 01–38)",
        description="Complete directory of all 38 Telangana RTA/RTO district codes from TS/TG-01 Adilabad to TS/TG-38 Narayanpet, including Hyderabad & Rangareddy.",
        keywords="Telangana RTO codes list, TG 01 to TG 38 districts, TS 07 Kondapur TG 07, TS 09 Khairatabad TG 09, Warangal Karimnagar Nizamabad RTA code",
        h1="All Telangana District RTO / RTA Codes (TS &amp; TG 01–38)",
        subtitle="Complete State-Wide District Transport Office Directory for LLR & DL Applicants",
        breadcrumb_label="TS / TG RTO Codes",
        active_nav="telangana-rto-codes",
        json_ld=json_ld,
        body_html=body_html,
        extra_scripts=extra_scripts,
    )
    write_file("telangana-rto-codes/index.html", html_doc)


def build_paused_language_stub(lang_code):
    """
    Generates a clean noindex, follow notice page at /te/ and /hi/ while Telugu & Hindi
    are temporarily disabled due to incomplete translations in data/questions/telangana/*.json.
    """
    lang_name = "Telugu (తెలుగు)" if lang_code == "te" else "Hindi (हिन्दी)"
    body_html = f"""
<article class="card-surface" style="max-width:760px; margin:0 auto;">
  <span class="seo-badge badge-cautionary" style="margin-bottom:10px;">Temporarily Paused</span>
  <h2 class="seo-section-heading">{esc(lang_name)} Practice Mode Is Currently Under Translation Audit</h2>
  <p style="color:var(--text-primary); line-height:1.65; margin:12px 0 18px;">
    To protect learners from incomplete or mixed translations on exam day, we have temporarily paused the {esc(lang_name)} interface while auditing the full 412-question Telangana RTA dataset. Please use our verified English STALL Mock Simulator and Question Bank below.
  </p>
  <div class="seo-cta-row">
    <a href="../" class="seo-cta-primary">Open English STALL Mock Simulator</a>
    <a href="../question-bank/" class="seo-cta-secondary">Browse All 412 Verified Questions</a>
  </div>
</article>"""

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="",
        title="Telangana RTA LLR Practice (English Simulator)",
        description="Telugu and Hindi modes are temporarily paused while translations are audited. Practice the verified 412-question Telangana RTA LLR mock exam in English.",
        keywords="Telangana LLR practice, STALL mock test English",
        h1="Telangana RTA Learner's Licence Practice — English Simulator",
        subtitle="Verified 412-Question STALL Mock Test & Study Reference",
        breadcrumb_label=f"{lang_code.upper()} Mode Paused",
        active_nav="",
        robots="noindex, follow",
        body_html=body_html,
        include_hero_cta=False,
    )
    write_file(f"{lang_code}/index.html", html_doc)


def build_404_page():
    body_html = """
<section class="study-hub-grid" aria-label="Popular LLR Practice Resources">
  <a href="/road-signs/" class="study-hub-card">
    <span class="study-hub-badge">94 Visual Signs</span>
    <span class="study-hub-title">All Road Signs &amp; Meanings</span>
    <span class="study-hub-desc">Mandatory, cautionary, and informatory road signs with official explanations.</span>
  </a>
  <a href="/question-bank/" class="study-hub-card">
    <span class="study-hub-badge">412 Q&amp;As</span>
    <span class="study-hub-title">Complete LLR Question Bank</span>
    <span class="study-hub-desc">Browse and search all 412 official Telangana RTA questions and verified answers.</span>
  </a>
  <a href="/online-llr-test/" class="study-hub-card">
    <span class="study-hub-badge">Sarathi &amp; STALL</span>
    <span class="study-hub-title">Online LLR Test Guide</span>
    <span class="study-hub-desc">Contactless Aadhaar e-KYC online test vs physical RTO STALL booth process.</span>
  </a>
  <a href="/rto-guide/" class="study-hub-card">
    <span class="study-hub-badge">TS / TG 07–13</span>
    <span class="study-hub-title">Hyderabad RTO &amp; Fees Guide</span>
    <span class="study-hub-desc">Document checklist, MVI steps, fees, and Hyderabad RTO center addresses.</span>
  </a>
</section>
"""
    html_doc = render_shell(
        lang="en",
        rel_root="/",
        canonical_path="",
        title="Page Not Found • Telangana RTA LLR Practice",
        description="The requested page could not be found. Jump straight to the STALL Mock Test, 94 Road Signs, or 412-Question Bank.",
        keywords="Telangana LLR practice, STALL mock test, 412 LLR question bank",
        h1="Sorry, that LLR study page could not be found (404).",
        subtitle="Verified 412-Question STALL Mock Test & Study Reference",
        breadcrumb_label="404 Not Found",
        active_nav="",
        robots="noindex, follow",
        body_html=body_html,
        include_hero_cta=True,
    )
    write_file("404.html", html_doc)


def build_privacy_policy_page():
    body_html = f"""
<article class="card-surface" style="max-width:860px; margin:0 auto;">
  <p style="font-size:0.84rem; color:var(--text-muted); margin-bottom:16px;">Last updated: {TODAY} • Domain: <strong>llr.sarvacapital.in</strong></p>

  <h2 style="font-size:1.15rem; color:var(--primary-navy); font-weight:800; margin:18px 0 8px;">1. Overview &amp; Zero-Account Local Practice</h2>
  <p style="color:var(--text-primary); line-height:1.65; margin-bottom:12px;">
    <strong>Telangana RTA Learner's Licence Practice</strong> (operated by Sarva Capital at <code>llr.sarvacapital.in</code>) is a free public educational simulator. We do not require registration, logins, phone numbers, Aadhaar details, or personal profiles to use any practice mode, mock test, or study guide.
  </p>

  <h2 style="font-size:1.15rem; color:var(--primary-navy); font-weight:800; margin:18px 0 8px;">2. Browser Local Storage &amp; Cross-Device QR Sync</h2>
  <p style="color:var(--text-primary); line-height:1.65; margin-bottom:12px;">
    Your quiz streaks, readiness progress, sound settings, and RTO document checklist ticks are stored exclusively inside your own browser's <code>localStorage</code>. None of your study scores are uploaded to any backend database. When you use the optional QR Cross-Device Sync feature, your compact study progress is encoded directly inside the sync URL / JSON export file processed locally in your browser.
  </p>

  <h2 style="font-size:1.15rem; color:var(--primary-navy); font-weight:800; margin:18px 0 8px;">3. Google AdSense &amp; Third-Party Advertising Cookies</h2>
  <p style="color:var(--text-primary); line-height:1.65; margin-bottom:10px;">
    To keep this learning platform 100% free for students and learner drivers, we display non-intrusive advertisements served by <strong>Google AdSense</strong> on study and post-exam summary screens (never inside the active 30-second timed mock test).
  </p>
  <ul style="padding-left:20px; color:var(--text-primary); line-height:1.65; margin-bottom:12px;">
    <li style="margin-bottom:6px;">Third-party vendors, including Google, use cookies to serve ads based on a user's prior visits to this website or other websites.</li>
    <li style="margin-bottom:6px;">Google's use of advertising cookies enables it and its partners to serve ads to users based on their visit to <code>llr.sarvacapital.in</code> and/or other sites on the Internet.</li>
    <li style="margin-bottom:6px;">Users may opt out of personalized advertising by visiting <a href="https://adssettings.google.com/" target="_blank" rel="noopener" style="color:var(--accent-blue); font-weight:600;">Google Ads Settings</a> or opt out of third-party vendor cookie use via <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener" style="color:var(--accent-blue); font-weight:600;">aboutads.info</a>.</li>
  </ul>

  <h2 style="font-size:1.15rem; color:var(--primary-navy); font-weight:800; margin:18px 0 8px;">4. External Official Links</h2>
  <p style="color:var(--text-primary); line-height:1.65; margin-bottom:12px;">
    We link to official government portals such as <a href="https://transport.telangana.gov.in" target="_blank" rel="noopener" style="color:var(--accent-blue); font-weight:600;">transport.telangana.gov.in</a> and <a href="https://sarathi.parivahan.gov.in" target="_blank" rel="noopener" style="color:var(--accent-blue); font-weight:600;">sarathi.parivahan.gov.in</a> for application filing, slot booking, and DigiLocker/mParivahan verification. External sites operate under their own privacy policies.
  </p>

  <h2 style="font-size:1.15rem; color:var(--primary-navy); font-weight:800; margin:18px 0 8px;">5. Contact Us</h2>
  <p style="color:var(--text-primary); line-height:1.65;">
    For privacy questions, ad inquiries, or content corrections, please write to <a href="mailto:{CONTACT_EMAIL}" style="color:var(--accent-blue); font-weight:700;">{CONTACT_EMAIL}</a>.
  </p>
</article>
"""

    json_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "Privacy Policy", "item": f"{BASE_URL}/privacy-policy/"},
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="privacy-policy/",
        title="Privacy Policy & Cookie Notice • Telangana RTA LLR Practice",
        description="Privacy Policy for llr.sarvacapital.in explaining local browser storage, zero personal data collection, and Google AdSense cookie disclosures.",
        keywords="Telangana LLR practice privacy policy, llr.sarvacapital.in cookies, AdSense privacy notice",
        h1="Privacy Policy &amp; Cookie Notice",
        subtitle="Transparent Local-First Storage & Advertising Cookie Disclosures",
        breadcrumb_label="Privacy Policy",
        active_nav="",
        json_ld=json_ld,
        body_html=body_html,
        include_hero_cta=False,
    )
    write_file("privacy-policy/index.html", html_doc)


def build_about_page():
    body_html = f"""
<article class="card-surface" style="max-width:860px; margin:0 auto;">
  <h2 style="font-size:1.15rem; color:var(--primary-navy); font-weight:800; margin-bottom:8px;">1. Mission &amp; Educational Purpose</h2>
  <p style="color:var(--text-primary); line-height:1.65; margin-bottom:14px;">
    <strong>Telangana RTA Learner's Licence Practice</strong> (<a href="{BASE_URL}/" style="color:var(--accent-blue); font-weight:600;">llr.sarvacapital.in</a>) is a free civic-education web application built by <strong>Sarva Capital</strong> to help learner drivers across Hyderabad, all 33+ districts of Telangana, and Parivahan Sarathi applicants prepare thoroughly for their Learner's Licence test and build lifelong road safety habits.
  </p>

  <div style="background:var(--accent-gold-light); border:1px solid var(--accent-gold); border-radius:10px; padding:16px; margin-bottom:18px;">
    <h2 style="font-size:1.05rem; color:var(--warning-amber); font-weight:800; margin-bottom:6px;">2. Non-Government Affiliation Disclaimer</h2>
    <p style="color:var(--text-primary); line-height:1.6; font-size:0.92rem; margin:0;">
      <strong>Independent Practice Tool:</strong> This website is NOT an official website of, nor affiliated with, the Government of Telangana Transport Department (RTA) or Parivahan Sarathi. All official Learner's Licence applications, fee payments, slot bookings, and digital LLR downloads must be completed exclusively on official government portals: <a href="https://transport.telangana.gov.in" target="_blank" rel="noopener" style="color:var(--warning-amber); font-weight:700; text-decoration:underline;">transport.telangana.gov.in</a> and <a href="https://sarathi.parivahan.gov.in" target="_blank" rel="noopener" style="color:var(--warning-amber); font-weight:700; text-decoration:underline;">sarathi.parivahan.gov.in</a>.
    </p>
  </div>

  <h2 style="font-size:1.15rem; color:var(--primary-navy); font-weight:800; margin:18px 0 8px;">3. Official Curriculum &amp; Source Attribution</h2>
  <p style="color:var(--text-primary); line-height:1.65; margin-bottom:14px;">
    The 412 questions (94 Road Signs, 159 Rules of the Road Regulations, and 159 General Driving Principles), 8-8-4 category quota, and 30-second countdown logic are derived directly from the publicly published Telangana Transport Department STALL curriculum under the Motor Vehicles Act, 1988. Question text is kept in official exam casing by default so learners recognize exact test phrasing.
  </p>

  <h2 style="font-size:1.15rem; color:var(--primary-navy); font-weight:800; margin:18px 0 8px;">4. Terms of Use</h2>
  <p style="color:var(--text-primary); line-height:1.65; margin-bottom:14px;">
    While we carefully verify all answer keys, RTO office addresses, and Motor Vehicles Act fine schedules, statutory rules and RTO fees may change over time. Always verify current fee schedules and slot guidelines directly on official government notices.
  </p>

  <h2 style="font-size:1.15rem; color:var(--primary-navy); font-weight:800; margin:18px 0 8px;">5. Contact &amp; Feedback</h2>
  <p style="color:var(--text-primary); line-height:1.65;">
    Found an outdated RTO office detail or want to share feedback? Reach our team at <a href="mailto:{CONTACT_EMAIL}" style="color:var(--accent-blue); font-weight:700;">{CONTACT_EMAIL}</a>.
  </p>
</article>
"""

    json_ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
            {"@type": "ListItem", "position": 2, "name": "About & Disclaimer", "item": f"{BASE_URL}/about/"},
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="about/",
        title="About & Disclaimer • Telangana RTA LLR Practice",
        description="About Telangana RTA LLR Practice by Sarva Capital: free educational mission, official Telangana Transport syllabus, non-affiliation notice & contact.",
        keywords="About Telangana LLR practice, Sarva Capital LLR disclaimer, contact Telangana LLR simulator",
        h1="About, Official Disclaimer &amp; Contact",
        subtitle="Educational Mission, Source Attribution & Non-Government Affiliation Notice",
        breadcrumb_label="About & Disclaimer",
        active_nav="",
        json_ld=json_ld,
        body_html=body_html,
        include_hero_cta=False,
    )
    write_file("about/index.html", html_doc)


def build_llms_full(signs, rules, gp, guide, cheatsheet, twins, popular):
    lines = [
        "# Telangana RTA Learner's Licence (LLR) Practice & STALL Simulator — Complete Knowledge Reference",
        "",
        f"> Authoritative, free, zero-login preparation guide and complete 412-question bank for the Telangana Transport Department STALL computerized Learner's Licence test at {BASE_URL}/.",
        "",
        "## 1. Official STALL Exam Format & Rules (Telangana RTA)",
        "- Governing Authority: Transport Department, Government of Telangana (Motor Vehicles Act, 1988 & CMVR 1989)",
        "- Exam Format: 20 multiple-choice questions per test (or contactless Aadhaar e-KYC online test via Parivahan Sarathi)",
        "- Category Quota: 8 Road Signs (40%) + 8 Rules of the Road (40%) + 4 General Driving Principles (20%)",
        "- Time Limit: 30 seconds per question (maximum 10 minutes)",
        "- Passing Mark: 12 correct out of 20 (60%); zero negative marking",
        "- Early Termination: Test ends immediately as PASSED on reaching 12 correct answers, or FAILED on reaching 9 wrong answers",
        "- Shuffled Option Order: Answer options 1, 2, 3, 4 are shuffled per question by default to match the latest STALL exam format",
        "- Simulator Language: English active (official RTA exam also supports English, Telugu, Hindi; Telugu & Hindi simulator modes are temporarily paused during translation audit)",
        "",
        "## 2. Official Fees, Retest & Validity",
    ]
    for fee in guide["feeRules"]["fees"]:
        lines.append(f"- {fee['category']['en']}: {fee['amount']} ({fee['breakup']['en']})")
    lines.append(f"- Retest Policy: {guide['feeRules']['retestRule']['en']}")
    lines.append(f"- Validity: {guide['feeRules']['validityRule']['en']}")

    lines.extend(["", "## 3. Required Documents Checklist"])
    for item in guide["checklist"]:
        req = "Mandatory" if item["mandatory"] else "Optional"
        lines.append(f"- [{req}] {item['item']['en']}: {item['desc']['en']}")

    lines.extend(["", "## 4. Test-Day 5-Step Process"])
    for step in guide["steps"]:
        lines.append(f"{step['step']}. **{step['title']['en']}**: {step['detail']['en']}")

    lines.extend(["", "## 5. Hyderabad RTO Testing Centers Directory"])
    for c in guide["centers"]:
        lines.append(f"- **{c['code']} — {c['name']['en']}**: {c['address']['en']} | Areas: {c['area']['en']} | Hours: {c['hours']}")

    lines.extend(["", "## 6. All 38 Telangana District RTO Codes (TS / TG 01–38)"])
    for d in popular["districtRtoCodes"]:
        lines.append(f"- TS-{d['code']} / TG-{d['code']}: {d['district']}")

    lines.extend(["", "## 7. Permanent DL Track Test Guide (8-Track & H-Track) & Online Slot Booking"])
    lines.append(f"- Eligibility: {popular['dlTrackGuide']['eligibility']['en']}")
    for tr in popular["dlTrackGuide"]["tracks"]:
        lines.append(f"- **{tr['title']['en']}**: " + " | ".join(tr["points"]["en"]))
    for s in popular["slotAndDownloadGuide"]["steps"]:
        lines.append(f"- Step {s['step']} ({s['title']['en']}): {s['detail']['en']}")

    lines.extend(["", "## 8. Telangana Traffic Fines (Motor Vehicles Amendment Act)"])
    for fitem in popular["trafficFines"]["items"]:
        lines.append(f"- **{fitem['offence']['en']}**: {fitem['fine']} ({fitem['section']})")

    lines.extend(["", "## 9. Driver Hand Signals & Traffic Police Signals"])
    for hs in popular["handSignals"]["items"]:
        lines.append(f"- **{hs['name']['en']}** ({hs['kind']}): {hs['desc']['en']}")

    lines.extend(["", "## 10. Rapid Cheatsheet (Top 10 Golden Rules)"])
    for i, gr in enumerate(cheatsheet["goldenRules"], 1):
        lines.append(f"{i}. {gr['rule']['en']}")

    lines.extend(["", "## 11. Tricky Twins (Commonly Confused Road Signs)"])
    for p in twins:
        lines.append(f"- **{p['title']['en']}**: {p['signA']['name']['en']} ({p['signA']['rule']['en']}) VS {p['signB']['name']['en']} ({p['signB']['rule']['en']}). Memory hook: {p['memoryHook']['en']}")

    lines.extend(["", "## 12. Complete 412 Official Telangana RTA LLR Questions & Verified Answers"])
    for sec_title, qlist in [
        ("Road Signs (94 Questions)", signs),
        ("Rules of the Road (159 Questions)", rules),
        ("General Driving Principles (159 Questions)", gp),
    ]:
        lines.extend(["", f"### {sec_title}"])
        for q in qlist:
            ans = clean_text(q["options"]["en"][q["answerIndex"]])
            lines.append(f"- **{q['id']}**: {clean_text(q['text']['en'])} -> **Answer: {ans}**")

    write_file("llms-full.txt", "\n".join(lines) + "\n")


def build_sitemap(signs, rules):
    sign_images = [
        (
            f"{BASE_URL}/{s['image']}",
            SIGN_TITLE_OVERRIDES.get(s["id"], clean_text(s["options"]["en"][s["answerIndex"]])),
        )
        for s in signs
        if s.get("image")
    ]
    seen_scen = set()
    scenario_images = []
    for r in rules:
        img = r.get("image")
        if img and img not in seen_scen:
            seen_scen.add(img)
            scenario_images.append((f"{BASE_URL}/{img}", clean_text(r["text"]["en"])[:120]))

    urls = [
        (f"{BASE_URL}/", "daily", "1.0", []),
        (f"{BASE_URL}/road-signs/", "weekly", "0.9", sign_images),
        (f"{BASE_URL}/question-bank/", "weekly", "0.9", []),
        (f"{BASE_URL}/question-bank/road-signs/", "weekly", "0.9", []),
        (f"{BASE_URL}/question-bank/traffic-rules/", "weekly", "0.9", scenario_images),
        (f"{BASE_URL}/question-bank/driving-principles/", "weekly", "0.9", []),
        (f"{BASE_URL}/online-llr-test/", "weekly", "0.9", []),
        (f"{BASE_URL}/rto-guide/", "weekly", "0.9", []),
        (f"{BASE_URL}/dl-test-guide/", "weekly", "0.9", []),
        (f"{BASE_URL}/traffic-fines/", "weekly", "0.8", []),
        (f"{BASE_URL}/telangana-rto-codes/", "weekly", "0.8", []),
        (f"{BASE_URL}/cheatsheet/", "weekly", "0.8", []),
        (f"{BASE_URL}/about/", "monthly", "0.5", []),
        (f"{BASE_URL}/privacy-policy/", "monthly", "0.5", []),
    ]

    entries = []
    for loc, freq, prio, imgs in urls:
        img_block = ""
        if imgs:
            img_lines = [
                f"""    <image:image>
      <image:loc>{esc(img_url)}</image:loc>
      <image:title>{esc(img_title)}</image:title>
    </image:image>"""
                for img_url, img_title in imgs
            ]
            img_block = "\n" + "\n".join(img_lines)
        entries.append(
            f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>{img_block}
  </url>"""
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">
{chr(10).join(entries)}
</urlset>
"""
    write_file("sitemap.xml", xml)


def main():
    signs = load_json("data/questions/telangana/road-signs.json")
    rules = load_json("data/questions/telangana/rules-of-road.json")
    gp = load_json("data/questions/telangana/general-principles.json")
    guide = load_json("data/rto-guide.json")
    cheatsheet = load_json("data/last-minute-cheatsheet.json")
    twins = load_json("data/tricky-twins.json")
    popular = load_json("data/popular-guides.json")

    build_road_signs_page(signs)
    build_question_bank_page(signs, rules, gp)
    build_question_bank_category_page(
        slug="road-signs",
        cat_key="road_signs",
        heading="Section 1: Road Signs & Signals (94 Questions)",
        title="Road Signs Q&As (94) • Telangana LLR 2026",
        h1="Telangana LLR Road Signs &amp; Signals Question Bank (94 Q&amp;As)",
        subtitle="40% of STALL Exam (8 of 20 Questions) • Official Telangana RTA Wordings",
        description="Practice all 94 official Telangana RTA Road Signs, Hand Signals, and Road Markings multiple-choice questions with verified answers and explanations.",
        keywords="road signs questions and answers, Telangana LLR road signs quiz, traffic symbol MCQs India, Parivahan road signs test",
        breadcrumb_label="Road Signs (94 Qs)",
        items=signs,
    )
    build_question_bank_category_page(
        slug="traffic-rules",
        cat_key="rules_of_road",
        heading="Section 2: Rules of the Road Regulations (159 Questions)",
        title="Traffic Rules LLR Questions (159) • 2026",
        h1="Rules of the Road Regulations Question Bank (159 Q&amp;As)",
        subtitle="40% of STALL Exam (8 of 20 Questions) • Junctions, Overtaking & Right-of-Way",
        description="Study all 159 official Telangana RTA & MV Act Rules of the Road questions with intersection diagrams, verified answers, and explanations.",
        keywords="traffic rules LLR questions, rules of the road regulations MCQ, overtaking right of way LLR questions, Telangana RTA rules bank",
        breadcrumb_label="Traffic Rules (159 Qs)",
        items=rules,
    )
    build_question_bank_category_page(
        slug="driving-principles",
        cat_key="general_principles",
        heading="Section 3: General Driving Principles (159 Questions)",
        title="Driving Principles LLR Q&As (159) • 2026",
        h1="General Driving Principles &amp; Road Safety Bank (159 Q&amp;As)",
        subtitle="20% of STALL Exam (4 of 20 Questions) • Defensive Driving, Documents & Safety",
        description="Complete 159-question Telangana RTA General Driving Principles bank covering night driving, fog, braking, documents, and emergency procedures.",
        keywords="driving principles LLR questions, safe driving licence test questions, Telangana RTA general principles Q&A, learner licence exam questions",
        breadcrumb_label="Driving Principles (159 Qs)",
        items=gp,
    )
    build_online_llr_test_page(guide, popular)
    build_rto_guide_page(guide)
    build_dl_test_guide_page(popular)
    build_traffic_fines_page(popular)
    build_district_rto_codes_page(popular)
    build_cheatsheet_page(cheatsheet, twins, popular)

    if not ENABLE_MULTILINGUAL_SEO:
        build_paused_language_stub("te")
        build_paused_language_stub("hi")

    build_privacy_policy_page()
    build_about_page()
    build_404_page()
    build_llms_full(signs, rules, gp, guide, cheatsheet, twins, popular)
    build_sitemap(signs, rules)


if __name__ == "__main__":
    main()
