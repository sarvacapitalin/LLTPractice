#!/usr/bin/env python3
"""
scripts/build_seo_pages.py

Generates crawlable, zero-JS static HTML pages, AdSense policy pages,
llms-full.txt, and sitemap.xml directly from verified Telangana RTA LLR datasets.
"""

from datetime import date
import html
import json
import os
import re

BASE_URL = "https://llr.sarvacapital.in"
TODAY = date.today().isoformat()
ASSET_VER = "v=22"
CONTACT_EMAIL = "contact@sarvacapital.in"


def esc(val):
    return html.escape(str(val or ""), quote=True)


def clean_text(val):
    return re.sub(r"\s+", " ", str(val or "")).strip()


def esc_clean(val):
    return esc(clean_text(val))


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_file(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {path} ({len(content.encode('utf-8'))} bytes)")


def ad_slot_html(slot_key, fmt="leaderboard"):
    return f"""
<aside class="ad-slot-wrapper ad-format-{fmt} is-hidden no-print" data-ad-slot="{slot_key}" aria-label="Advertisement">
  <span class="ad-label">Advertisement</span>
  <div class="ad-slot-inner"></div>
</aside>"""


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
    active_nav="",
    json_ld=None,
    hreflang_links=None,
    body_html="",
    extra_scripts="",
    include_hero_cta=True,
):
    canonical_url = f"{BASE_URL}/{canonical_path}"
    hreflang_html = ""
    if hreflang_links:
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
        ("rto-guide/", "RTO Guide", "rto-guide"),
        ("dl-test-guide/", "DL Track Test", "dl-test-guide"),
        ("traffic-fines/", "Fines &amp; Signals", "traffic-fines"),
        ("telangana-rto-codes/", "TS/TG Codes", "telangana-rto-codes"),
        ("cheatsheet/", "Cheatsheet", "cheatsheet"),
        ("te/", "తెలుగు", "te"),
        ("hi/", "हिन्दी", "hi"),
    ]
    nav_links_html = "\n".join(
        f'<a href="{rel_root}{href}" class="seo-nav-link{" active" if key == active_nav else ""}">{label}</a>'
        for href, label, key in nav_items
    )

    hero_cta_html = ""
    if include_hero_cta:
        mock_label = (
            "తెలుగులో STALL మాక్ టెస్ట్ ప్రారంభించండి"
            if lang == "te"
            else ("हिन्दी में STALL मॉक टेस्ट शुरू करें" if lang == "hi" else "Take Official 20-Question STALL Mock Test")
        )
        prac_label = (
            "412 ప్రశ్నలను ప్రాక్టీస్ చేయండి"
            if lang == "te"
            else ("सभी 412 प्रश्नों का अभ्यास करें" if lang == "hi" else "Practice All 412 Questions Interactively")
        )
        lang_qs = f"?lang={lang}" if lang in ("te", "hi") else ""
        prac_qs = f"?lang={lang}&tab=practice" if lang in ("te", "hi") else "?tab=practice"
        hero_cta_html = f"""
      <div class="seo-cta-row">
        <a href="{rel_root}{lang_qs}" class="seo-cta-primary">{mock_label}</a>
        <a href="{rel_root}{prac_qs}" class="seo-cta-secondary">{prac_label}</a>
      </div>"""

    breadcrumb_html = ""
    if breadcrumb_label:
        breadcrumb_html = f"""
    <nav class="seo-breadcrumb" aria-label="Breadcrumb">
      <a href="{rel_root}">Home</a>
      <span aria-hidden="true">/</span>
      <span>{breadcrumb_label}</span>
    </nav>"""

    return f"""<!DOCTYPE html>
<html lang="{esc(lang)}">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <link rel="icon" type="image/png" sizes="192x192" href="{rel_root}assets/icons/icon-192.png">
  <link rel="apple-touch-icon" href="{rel_root}assets/icons/icon-192.png">
  <link rel="canonical" href="{esc(canonical_url)}">
  <meta name="theme-color" content="#0B2545">
  <meta name="author" content="Sarva Capital">
  <meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">
  <meta name="description" content="{esc(description)}">
  <meta name="keywords" content="{esc(keywords)}">
{hreflang_html}
  <link rel="alternate" type="text/plain" title="LLM Context Summary (llms.txt)" href="{BASE_URL}/llms.txt">
  <link rel="alternate" type="text/plain" title="Complete LLM Reference (llms-full.txt)" href="{BASE_URL}/llms-full.txt">

  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Telangana LLR Practice • Sarva Capital">
  <meta property="og:url" content="{esc(canonical_url)}">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:image" content="{BASE_URL}/assets/images/og-preview.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Telangana RTA Learner Licence Practice STALL Simulator">
  <meta property="og:locale" content="{ 'te_IN' if lang == 'te' else ('hi_IN' if lang == 'hi' else 'en_IN') }">
  <meta property="og:locale:alternate" content="en_IN">
  <meta property="og:locale:alternate" content="te_IN">
  <meta property="og:locale:alternate" content="hi_IN">

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="{esc(canonical_url)}">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{BASE_URL}/assets/images/og-preview.png">

{ld_script}

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;600;700&family=Noto+Sans+Telugu:wght@400;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{rel_root}css/styles.css?{ASSET_VER}">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6573213692692289" crossorigin="anonymous"></script>
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
      <div class="header-actions">
        <div class="header-lang-links" aria-label="Language versions">
          <a href="{rel_root}" class="header-lang-link{' active' if lang == 'en' else ''}">EN</a>
          <a href="{rel_root}te/" class="header-lang-link{' active' if lang == 'te' else ''}">తెలుగు</a>
          <a href="{rel_root}hi/" class="header-lang-link{' active' if lang == 'hi' else ''}">हिन्दी</a>
        </div>
        <a href="{rel_root}{'?lang=' + lang if lang in ('te', 'hi') else ''}" class="control-btn" style="background:#F3CA40; color:#0B2545; border-color:#F3CA40; font-weight:800;">
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
      <h1 style="font-size: 1.6rem; color: #0B2545; font-weight: 800; line-height: 1.25; margin-bottom: 10px;">{h1}</h1>
      <p style="color: #475569; font-size: 0.98rem; line-height: 1.6; max-width: 72ch;">{esc(description)}</p>
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
        <h3 class="footer-col-title">RTO Reference Guides</h3>
        <ul class="footer-link-list">
          <li><a href="{rel_root}road-signs/">All 94 Road Signs &amp; Meanings</a></li>
          <li><a href="{rel_root}question-bank/">412 Official LLR Q&amp;A Bank</a></li>
          <li><a href="{rel_root}rto-guide/">Hyderabad RTO Guide &amp; Fees</a></li>
          <li><a href="{rel_root}dl-test-guide/">Permanent DL 8 &amp; H Track Guide</a></li>
          <li><a href="{rel_root}traffic-fines/">Traffic Fines &amp; Hand Signals</a></li>
          <li><a href="{rel_root}telangana-rto-codes/">All Telangana RTO Codes (01–38)</a></li>
        </ul>
      </div>
      <div>
        <h3 class="footer-col-title">Regional Languages</h3>
        <ul class="footer-link-list">
          <li><a href="{rel_root}">English LLR Simulator</a></li>
          <li><a href="{rel_root}te/" hreflang="te">తెలుగు గైడ్ (Telugu Prep)</a></li>
          <li><a href="{rel_root}hi/" hreflang="hi">हिन्दी गाइड (Hindi Prep)</a></li>
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
        <a href="{BASE_URL}/" style="color:var(--secondary-blue); font-weight:700; text-decoration:none;">llr.sarvacapital.in</a> • Free Educational Resource by <a href="https://sarvacapital.in" target="_blank" rel="noopener" style="color:var(--secondary-blue);">Sarva Capital</a>
      </div>
      <div>
        <a href="{rel_root}llms.txt" style="color:#475569;">llms.txt</a> • <a href="{rel_root}llms-full.txt" style="color:#475569;">llms-full.txt</a> • <a href="{rel_root}sitemap.xml" style="color:#475569;">sitemap.xml</a>
      </div>
    </div>
  </footer>

  <button type="button" id="btn-back-to-top" class="back-to-top-btn no-print" aria-label="Back to top">↑ Top</button>

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
        "mandatory": ("Mandatory / Regulatory Road Signs", "Circles (Red border = Prohibition/Order, Blue circle = Compulsory instruction)", "badge-mandatory"),
        "cautionary": ("Cautionary / Warning Road Signs", "Red-bordered Triangles alerting drivers to hazards ahead", "badge-cautionary"),
        "informatory": ("Informatory / Guide Road Signs", "Blue Rectangles indicating directions, facilities, and distances", "badge-informatory"),
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
            ans_te = clean_text(s["options"]["te"][s["answerIndex"]])
            ans_hi = clean_text(s["options"]["hi"][s["answerIndex"]])
            exp_en = clean_text(s["explanation"]["en"])
            search_blob = f"{ans_en} {ans_te} {ans_hi} {s['questionNumber']} {stype}".lower()
            cards.append(
                f"""<article class="seo-card rs-filter-card" id="{esc(s['id'])}" data-type="{esc(stype)}" data-search="{esc(search_blob)}">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
    <span class="seo-badge {badge_cls}">{esc(stype)}</span>
    <span class="tabular-nums" style="font-size:0.78rem; color:#64748B; font-weight:700;">Sign #{s['questionNumber']}</span>
  </div>
  <div style="text-align:center; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:12px; margin-bottom:10px;">
    <img src="../{esc(s['image'])}" alt="{esc(ans_en)} - Telangana RTA Road Sign" loading="lazy" style="max-height:110px; width:auto; object-fit:contain;">
  </div>
  <h3 style="font-size:0.98rem; color:#0B2545; font-weight:700; margin-bottom:6px; letter-spacing:0.01em;">{esc(ans_en)}</h3>
  <p style="font-size:0.84rem; color:#334155; margin-bottom:6px; line-height:1.45;"><strong>తెలుగు:</strong> {esc(ans_te)}<br><strong>हिन्दी:</strong> {esc(ans_hi)}</p>
  <p style="font-size:0.82rem; color:#475569; line-height:1.45;">{esc(exp_en)}</p>
</article>"""
            )
            item_list.append({
                "@type": "ListItem",
                "position": pos,
                "name": ans_en,
                "url": f"{BASE_URL}/road-signs/#{s['id']}",
            })
            pos += 1

        sections.append(
            f"""<section id="{stype}" class="rs-section" data-section-type="{esc(stype)}" style="margin-bottom: 32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:4px;">{esc(heading)} ({len(items)})</h2>
  <p style="color:#475569; font-size:0.92rem; margin-bottom:16px;">{esc(sub)}</p>
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
    <a href="../?tab=flashcards" class="pill-btn" style="background:#EFF6FF; color:#134074; border-color:#BFDBFE;">Practice Flashcards ↗</a>
  </div>
  <div style="display:flex; align-items:center; gap:8px; flex:1; max-width:360px; min-width:220px;">
    <input type="text" id="rs-search-input" placeholder="Search sign name, Telugu/Hindi, or #..." style="flex:1; padding:8px 12px; border:1px solid #CBD5E1; border-radius:8px; font-size:0.86rem;">
    <span id="rs-match-count" class="spec-pill">{total_cnt} signs</span>
  </div>
</div>
<p id="rs-empty-msg" style="display:none; text-align:center; padding:32px; color:#64748B; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px;">No road signs matched your filter. Try clearing the search box.</p>
"""

    body_html = (
        toolbar
        + sections[0]
        + ad_slot_html("seo_in_content", "leaderboard")
        + sections[1]
        + sections[2]
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
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="road-signs/",
        title="All 94 Telangana RTA Road Signs & Meanings (English, Telugu, Hindi) • LLR 2026",
        description="Complete visual directory of all 94 official Telangana RTA Learner's Licence road signs (Mandatory, Cautionary, Informatory) with English, Telugu & Hindi meanings for the STALL exam.",
        keywords="Telangana road signs with meaning, Hyderabad RTO traffic signs, mandatory cautionary informatory signs India, Telangana LLR road signs list, traffic symbols Telugu Hindi English",
        h1="All 94 Telangana RTA Road Signs &amp; Official Meanings",
        subtitle="Complete Trilingual Visual Reference for STALL LLR Exam (40% Exam Weightage)",
        breadcrumb_label="94 Road Signs",
        active_nav="road-signs",
        json_ld=json_ld,
        body_html=body_html,
        extra_scripts=extra_scripts,
    )
    write_file("road-signs/index.html", html_doc)


def build_question_bank_page(signs, rules, gp):
    categories = [
        ("road-signs", "Section 1: Road Signs & Signals (94 Questions)", signs),
        ("rules-of-road", "Section 2: Rules of the Road Regulations (159 Questions)", rules),
        ("general-principles", "Section 3: General Driving Principles & Safety (159 Questions)", gp),
    ]

    toolbar = """
<div class="seo-sticky-tools no-print">
  <div style="display:flex; flex-wrap:wrap; gap:6px; align-items:center;">
    <button type="button" class="pill-btn active" data-qb-cat="all">All (412)</button>
    <button type="button" class="pill-btn" data-qb-cat="road-signs">Road Signs (94)</button>
    <button type="button" class="pill-btn" data-qb-cat="rules-of-road">Rules (159)</button>
    <button type="button" class="pill-btn" data-qb-cat="general-principles">Principles (159)</button>
  </div>
  <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center;">
    <input type="text" id="qb-search-input" placeholder="Search question keyword or #..." style="padding:7px 12px; border:1px solid #CBD5E1; border-radius:8px; font-size:0.85rem; min-width:210px;">
    <button type="button" id="btn-qb-quiz-mode" class="btn-secondary-light" style="font-size:0.8rem; min-height:34px; padding:5px 10px;">Quiz Mode (Hide Answers)</button>
    <button type="button" id="btn-qb-case-toggle" class="btn-secondary-light" style="font-size:0.8rem; min-height:34px; padding:5px 10px;">Aa Easy-Read</button>
    <span id="qb-match-count" class="spec-pill">412 Qs</span>
  </div>
</div>
<p id="qb-empty-msg" style="display:none; text-align:center; padding:32px; color:#64748B; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:12px;">No questions matched your search filter.</p>
"""

    sections = []
    for sec_id, heading, items in categories:
        cards = []
        for idx, q in enumerate(items, 1):
            img_html = ""
            if q.get("image"):
                img_html = f'<div style="margin:10px 0;"><img src="../{esc(q["image"])}" alt="Question diagram for {esc(q["id"])}" loading="lazy" style="max-height:110px; border-radius:8px; border:1px solid #E2E8F0; padding:4px; background:#FFFFFF;"></div>'
            opts_html = []
            for oi, opt in enumerate(q["options"]["en"]):
                is_ans = oi == q["answerIndex"]
                cls = "qa-option correct" if is_ans else "qa-option"
                mark = '<span class="qa-answer-mark"> ✓ (Correct)</span>' if is_ans else ""
                cleaned_opt = clean_text(opt)
                opts_html.append(f'<li class="{cls}"><span class="qb-case-target" data-raw="{esc(cleaned_opt)}">{oi + 1}. {esc(cleaned_opt)}</span>{mark}</li>')
            exp = clean_text(q.get("explanation", {}).get("en", ""))
            q_text = clean_text(q["text"]["en"])
            search_blob = f"{q['id']} {idx} {q_text}".lower()
            cards.append(
                f"""<article class="qa-card qb-card" id="{esc(q['id'])}" data-cat="{esc(sec_id)}" data-search="{esc(search_blob)}">
  <div style="font-size:0.78rem; color:#64748B; font-weight:700; margin-bottom:4px;">{esc(q['id'])} • Question #{idx}</div>
  <h3 class="qb-case-target" data-raw="{esc(q_text)}" style="font-size:1.02rem; color:#0B2545; font-weight:600; line-height:1.48; letter-spacing:0.012em; margin-bottom:8px;">{esc(q_text)}</h3>
  {img_html}
  <ol class="qa-options">{"".join(opts_html)}</ol>
  <p class="qa-explanation-box" style="font-size:0.86rem; color:#334155; background:#F8FAFC; padding:10px; border-radius:8px; margin-top:8px;"><strong>Explanation:</strong> {esc(exp)}</p>
</article>"""
            )
        sections.append(
            f"""<section id="{sec_id}" class="qb-section" data-sec="{esc(sec_id)}" style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:14px;">{esc(heading)}</h2>
  {"".join(cards)}
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

    extra_scripts = """
  <script type="module">
    import { toEasyReadCase, cleanPdfText } from "../js/text-formatter.js?v=22";
    const searchInput = document.getElementById("qb-search-input");
    const countEl = document.getElementById("qb-match-count");
    const emptyEl = document.getElementById("qb-empty-msg");
    const quizBtn = document.getElementById("btn-qb-quiz-mode");
    const caseBtn = document.getElementById("btn-qb-case-toggle");
    let activeCat = "all";
    let easyRead = false;

    function applyFilter() {
      const q = (searchInput?.value || "").trim().toLowerCase();
      let shown = 0;
      document.querySelectorAll(".qb-section").forEach(sec => {
        const secId = sec.getAttribute("data-sec");
        let secShown = 0;
        sec.querySelectorAll(".qb-card").forEach(card => {
          const catOk = activeCat === "all" || card.getAttribute("data-cat") === activeCat;
          const hay = card.getAttribute("data-search") || "";
          const qOk = !q || hay.includes(q);
          const show = catOk && qOk;
          card.style.display = show ? "" : "none";
          if (show) { secShown++; shown++; }
        });
        sec.style.display = (secShown > 0 && (activeCat === "all" || activeCat === secId)) ? "" : "none";
      });
      if (countEl) countEl.textContent = `${shown} Qs`;
      if (emptyEl) emptyEl.style.display = shown === 0 ? "block" : "none";
    }

    document.querySelectorAll("[data-qb-cat]").forEach(btn => {
      btn.addEventListener("click", () => {
        document.querySelectorAll("[data-qb-cat]").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        activeCat = btn.getAttribute("data-qb-cat");
        applyFilter();
      });
    });

    searchInput?.addEventListener("input", applyFilter);

    quizBtn?.addEventListener("click", () => {
      const on = document.body.classList.toggle("qb-quiz-mode");
      quizBtn.textContent = on ? "Show Answers" : "Quiz Mode (Hide Answers)";
      quizBtn.style.background = on ? "#EFF6FF" : "";
      quizBtn.style.color = on ? "#134074" : "";
    });

    caseBtn?.addEventListener("click", () => {
      easyRead = !easyRead;
      caseBtn.textContent = easyRead ? "AA Official Caps" : "Aa Easy-Read";
      document.querySelectorAll(".qb-case-target").forEach(el => {
        const raw = el.getAttribute("data-raw") || "";
        const prefixMatch = el.parentElement?.tagName === "LI" ? el.textContent.match(/^(\d+\.\s)/) : null;
        const prefix = prefixMatch ? prefixMatch[1] : "";
        el.textContent = prefix + (easyRead ? toEasyReadCase(raw, "en") : cleanPdfText(raw));
      });
    });
  </script>"""

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
                "educationalLevel": "Learner's Licence Applicant",
                "learningResourceType": "Question Bank",
                "isAccessibleForFree": True,
                "inLanguage": ["en", "te", "hi"],
            },
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="question-bank/",
        title="Telangana LLR Question Bank 2026 • All 412 Official Questions & Answers",
        description="Study all 412 official Telangana RTA Learner's Licence (LLR / STALL) questions and answers across Road Signs (94), Rules of the Road (159), and Driving Principles (159).",
        keywords="Telangana LLR question bank 412 questions, Hyderabad RTO LLR questions and answers, STALL exam question bank pdf, Telangana RTA test questions",
        h1="Complete Telangana RTA LLR Question Bank (412 Questions &amp; Answers)",
        subtitle="100% Verified Master Curriculum from Telangana Transport Department",
        breadcrumb_label="412 Question Bank",
        active_nav="question-bank",
        json_ld=json_ld,
        body_html=body_html,
        extra_scripts=extra_scripts,
    )
    write_file("question-bank/index.html", html_doc)


def build_rto_guide_page(guide):
    checklist_html = "".join(
        f"""<li class="seo-card" style="list-style:none;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px; gap:8px;">
    <strong style="color:#0B2545;">{esc(c['item']['en'])}</strong>
    <span class="seo-badge {'badge-mandatory' if c['mandatory'] else 'badge-informatory'}">{'Mandatory' if c['mandatory'] else 'Optional'}</span>
  </div>
  <p style="font-size:0.88rem; color:#475569;">{esc(c['desc']['en'])}</p>
</li>"""
        for c in guide["checklist"]
    )

    steps_html = "".join(
        f"""<li class="qa-card" style="list-style:none;">
  <strong style="color:#134074; font-size:1.02rem;">Step {s['step']}: {esc(s['title']['en'])}</strong>
  <p style="margin-top:6px; color:#334155; font-size:0.92rem;">{esc(s['detail']['en'])}</p>
</li>"""
        for s in guide["steps"]
    )

    centers_html = "".join(
        f"""<article class="seo-card">
  <span class="seo-badge badge-informatory" style="margin-bottom:8px;">{esc(c['code'])}</span>
  <h3 style="font-size:1rem; color:#0B2545; font-weight:700; margin-bottom:4px;">{esc(c['name']['en'])}</h3>
  <p style="font-size:0.84rem; color:#134074; font-weight:600; margin-bottom:6px;">Areas: {esc(c['area']['en'])}</p>
  <p style="font-size:0.84rem; color:#475569; margin-bottom:6px;">{esc(c['address']['en'])}</p>
  <p style="font-size:0.8rem; color:#047857; font-weight:600;">Hours: {esc(c['hours'])}</p>
</article>"""
        for c in guide["centers"]
    )

    fees_html = "".join(
        f"""<tr>
  <td style="padding:10px; border-bottom:1px solid #E2E8F0; font-weight:600;">{esc(f['category']['en'])}</td>
  <td style="padding:10px; border-bottom:1px solid #E2E8F0; color:#475569;">{esc(f['breakup']['en'])}</td>
  <td class="tabular-nums" style="padding:10px; border-bottom:1px solid #E2E8F0; font-weight:800; color:#047857;">{esc(f['amount'])}</td>
</tr>"""
        for f in guide["feeRules"]["fees"]
    )

    tips_html = "".join(
        f"""<article class="seo-card" style="background:#FFFBEB; border-color:#FDE68A;">
  <h3 style="font-size:0.98rem; color:#92400E; font-weight:700; margin-bottom:6px;">{esc(tip['title']['en'])}</h3>
  <p style="font-size:0.88rem; color:#78350F;">{esc(tip['desc']['en'])}</p>
</article>"""
        for tip in guide["topTips"]
    )

    body_html = f"""
<nav class="toc-bar no-print" aria-label="RTO Guide Sections">
  <a href="#sec-docs" class="toc-pill">1. Documents Checklist</a>
  <a href="#sec-steps" class="toc-pill">2. Test-Day Steps</a>
  <a href="#sec-centers" class="toc-pill">3. Hyderabad RTO Centers</a>
  <a href="#sec-fees" class="toc-pill">4. Fees &amp; Validity</a>
  <a href="#sec-tips" class="toc-pill">5. High-Scorer Tips</a>
</nav>

<section id="sec-docs" class="guide-section-anchor" style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">1. Required Documents Checklist for Telangana LLR Test</h2>
  <ul class="seo-grid" style="padding:0;">{checklist_html}</ul>
</section>

<section id="sec-steps" class="guide-section-anchor" style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">2. Test-Day 5-Step Walkthrough at Hyderabad RTO</h2>
  <ol style="padding:0;">{steps_html}</ol>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section id="sec-centers" class="guide-section-anchor" style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">3. Hyderabad &amp; Telangana RTO Testing Centers Directory</h2>
  <div class="seo-grid">{centers_html}</div>
</section>

<section id="sec-fees" class="guide-section-anchor" style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">4. Official LLR Fee Structure, Retest &amp; Validity Rules</h2>
  <div class="seo-card" style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; text-align:left;">
      <thead>
        <tr style="background:#F8FAFC;">
          <th style="padding:10px; border-bottom:2px solid #E2E8F0;">Vehicle Class</th>
          <th style="padding:10px; border-bottom:2px solid #E2E8F0;">Fee Breakdown</th>
          <th style="padding:10px; border-bottom:2px solid #E2E8F0;">Total Fee</th>
        </tr>
      </thead>
      <tbody>{fees_html}</tbody>
    </table>
    <p style="margin-top:12px; font-size:0.9rem; color:#334155;"><strong>Retest Policy:</strong> {esc(guide['feeRules']['retestRule']['en'])}</p>
    <p style="margin-top:8px; font-size:0.9rem; color:#334155;"><strong>LLR Validity &amp; Permanent DL Rule:</strong> {esc(guide['feeRules']['validityRule']['en'])}</p>
  </div>
</section>

<section id="sec-tips" class="guide-section-anchor">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">5. Top Tips to Pass on Your First Attempt</h2>
  <div class="seo-grid">{tips_html}</div>
</section>
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
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="rto-guide/",
        title="Hyderabad & Telangana RTO LLR Guide 2026 • Centers, Fees, Documents & Process",
        description="Complete test-day guide for Telangana RTA Learner's Licence (LLR): Aadhaar & Form 2 checklist, TS-07 to TS-12 Hyderabad RTO addresses, ₹200/₹350 fees, 7-day retest rule, and STALL booth walkthrough.",
        keywords="Hyderabad RTO LLR documents, Kondapur RTO TS-07 address, Khairatabad RTO TS-09 LLR test, Telangana LLR fees 2026, Uppal Secunderabad RTO timings",
        h1="Hyderabad &amp; Telangana RTA Learner's Licence (LLR) Guide",
        subtitle="Documents Checklist, RTO Center Addresses (TS-07 to TS-12), Fees & Test-Day Steps",
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
    <strong style="color:#0B2545; display:block; margin-bottom:4px;">{esc(gr['rule']['en'])}</strong>
    <p style="font-size:0.85rem; color:#475569; line-height:1.45;"><strong>తెలుగు:</strong> {esc(gr['rule']['te'])}<br><strong>हिन्दी:</strong> {esc(gr['rule']['hi'])}</p>
  </div>
</article>"""
        for idx, gr in enumerate(cheatsheet["goldenRules"], 1)
    )

    hs = popular["handSignals"]
    hs_html = "".join(
        f"""<article class="seo-card" style="display:flex; gap:12px; align-items:center;">
  <img src="../{esc(item['image'])}" alt="{esc(item['name']['en'])}" loading="lazy" style="width:72px; height:72px; object-fit:contain; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:4px; flex-shrink:0;">
  <div>
    <span class="seo-badge badge-informatory" style="margin-bottom:4px;">{esc(item['kind'])}</span>
    <h3 style="font-size:0.95rem; color:#0B2545; font-weight:700; margin-bottom:4px;">{esc(item['name']['en'])}</h3>
    <p style="font-size:0.82rem; color:#475569;">{esc(item['desc']['en'])}</p>
  </div>
</article>"""
        for item in hs["items"]
    )

    twins_html = "".join(
        f"""<article class="seo-card">
  <h3 style="font-size:1.05rem; color:#0B2545; font-weight:800; margin-bottom:12px;">{esc(p['title']['en'])}</h3>
  <div class="twins-comparison-grid">
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:10px; border-radius:8px; text-align:center;">
      <img src="../{esc(p['signA']['image'])}" alt="{esc(p['signA']['name']['en'])}" loading="lazy" style="max-height:80px;">
      <strong style="display:block; font-size:0.85rem; margin:6px 0;">{esc(p['signA']['name']['en'])}</strong>
      <p style="font-size:0.8rem; color:#475569; text-align:left;">{esc(p['signA']['rule']['en'])}</p>
    </div>
    <div style="background:#F8FAFC; border:1px solid #E2E8F0; padding:10px; border-radius:8px; text-align:center;">
      <img src="../{esc(p['signB']['image'])}" alt="{esc(p['signB']['name']['en'])}" loading="lazy" style="max-height:80px;">
      <strong style="display:block; font-size:0.85rem; margin:6px 0;">{esc(p['signB']['name']['en'])}</strong>
      <p style="font-size:0.8rem; color:#475569; text-align:left;">{esc(p['signB']['rule']['en'])}</p>
    </div>
  </div>
  <div class="twins-memory-hook"><strong>Memory Hook:</strong> {esc(p['memoryHook']['en'])}</div>
</article>"""
        for p in twins
    )

    body_html = f"""
<div class="no-print" style="margin-bottom:20px; display:flex; gap:10px; flex-wrap:wrap;">
  <button onclick="window.print()" class="seo-cta-primary" style="border:none; cursor:pointer;">Print / Save PDF Revision Sheet</button>
  <a href="../road-signs/" class="seo-cta-secondary">View All 94 Road Signs</a>
</div>

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">Top 10 Golden Rules (10-Minute Pre-Exam Revision)</h2>
  <div class="cheatsheet-rules-grid">{rules_html}</div>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">{esc(hs['title']['en'])}</h2>
  <div class="seo-grid">{hs_html}</div>
</section>

<section>
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">Tricky Twins: Commonly Confused Road Signs</h2>
  <div class="seo-grid" style="grid-template-columns:repeat(auto-fill, minmax(320px, 1fr));">{twins_html}</div>
</section>
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
                "inLanguage": ["en", "te", "hi"],
            },
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="cheatsheet/",
        title="Telangana LLR Rapid Cheatsheet, Hand Signals & Printable Revision Sheet 2026",
        description="Printable 10-minute morning-of-the-test revision cheatsheet for Telangana RTA LLR: pass mark, sign shapes, hand signals, emergency numbers, and Tricky Twins comparisons.",
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
  <strong style="color:#134074; font-size:1.02rem;">Step {s['step']}: {esc(s['title']['en'])}</strong>
  <p style="margin-top:6px; color:#334155; font-size:0.92rem;">{esc(s['detail']['en'])}</p>
</li>"""
        for s in slot["steps"]
    )

    tracks_html = "".join(
        f"""<article class="seo-card">
  <span class="seo-badge badge-informatory" style="margin-bottom:8px;">{esc(tr['badge'])}</span>
  <h3 style="font-size:1.05rem; color:#0B2545; font-weight:800; margin-bottom:10px;">{esc(tr['title']['en'])}</h3>
  <ul style="padding-left:18px; color:#334155; font-size:0.9rem; line-height:1.5;">
    {"".join(f'<li style="margin-bottom:6px;">{esc(pt)}</li>' for pt in tr['points']['en'])}
  </ul>
</article>"""
        for tr in dl["tracks"]
    )

    docs_html = "".join(
        f'<li style="margin-bottom:6px;">{esc(d)}</li>' for d in dl["documents"]["en"]
    )

    body_html = f"""
<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">1. {esc(slot['title']['en'])}</h2>
  <ol style="padding:0;">{slot_html}</ol>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:8px;">2. {esc(dl['title']['en'])}</h2>
  <p style="color:#475569; margin-bottom:14px;">{esc(dl['eligibility']['en'])} {esc(dl['automatedTracksNote']['en'])}</p>
  <div class="seo-grid" style="grid-template-columns:repeat(auto-fit, minmax(300px, 1fr));">{tracks_html}</div>
</section>

<section>
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">3. Documents &amp; Test Vehicle Checklist for DL Track Day</h2>
  <div class="seo-card" style="background:#F0FDF4; border-color:#BBF7D0;">
    <ul style="padding-left:18px; color:#14532D; font-size:0.94rem; line-height:1.55;">{docs_html}</ul>
  </div>
</section>
{ad_slot_html("seo_multiplex", "multiplex")}
"""

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
                "step": [
                    {"@type": "HowToStep", "position": s["step"], "name": s["title"]["en"], "text": s["detail"]["en"]}
                    for s in slot["steps"]
                ],
            },
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="dl-test-guide/",
        title="Telangana Permanent Driving Licence (DL) 8-Track & H-Track Test Guide 2026",
        description="Complete Telangana RTA Permanent Driving Licence guide: Two-Wheeler 8-Track & Car H-Track rules, automated sensor tracks (Kondapur, Uppal, Medchal), slot booking, and DigiLocker LLR download.",
        keywords="Telangana driving licence track test, Hyderabad 8 track bike test, Kondapur H track car test, transport.telangana.gov.in DL slot booking, digital LLR download DigiLocker",
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
  <td style="padding:12px; border-bottom:1px solid #E2E8F0; font-weight:600; color:#0B2545;">{esc(item['offence']['en'])}</td>
  <td style="padding:12px; border-bottom:1px solid #E2E8F0; font-weight:700; color:#B91C1C;">{esc(item['fine'])}</td>
  <td style="padding:12px; border-bottom:1px solid #E2E8F0; color:#475569;">{esc(item['section'])}</td>
</tr>"""
        for item in fines["items"]
    )

    hs_html = "".join(
        f"""<article class="seo-card" style="display:flex; gap:12px; align-items:center;">
  <img src="../{esc(item['image'])}" alt="{esc(item['name']['en'])}" loading="lazy" style="width:76px; height:76px; object-fit:contain; background:#FFFFFF; border:1px solid #E2E8F0; border-radius:8px; padding:4px; flex-shrink:0;">
  <div>
    <span class="seo-badge badge-informatory" style="margin-bottom:4px;">{esc(item['kind'])}</span>
    <h3 style="font-size:0.95rem; color:#0B2545; font-weight:700; margin-bottom:4px;">{esc(item['name']['en'])}</h3>
    <p style="font-size:0.84rem; color:#475569;">{esc(item['desc']['en'])}</p>
  </div>
</article>"""
        for item in hs["items"]
    )

    body_html = f"""
<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">{esc(fines['title']['en'])}</h2>
  <p style="color:#475569; margin-bottom:12px;">{esc(fines['subtitle']['en'])} Digital Driving Licence &amp; RC stored in <strong>DigiLocker</strong> or <strong>mParivahan</strong> are legally valid across Telangana and India.</p>
  <div class="seo-card" style="overflow-x:auto;">
    <table style="width:100%; border-collapse:collapse; text-align:left;">
      <thead>
        <tr style="background:#F8FAFC;">
          <th style="padding:12px; border-bottom:2px solid #E2E8F0;">Traffic Offence</th>
          <th style="padding:12px; border-bottom:2px solid #E2E8F0;">Penalty / Fine</th>
          <th style="padding:12px; border-bottom:2px solid #E2E8F0;">MV Act Section</th>
        </tr>
      </thead>
      <tbody>{rows_html}</tbody>
    </table>
  </div>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section>
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">{esc(hs['title']['en'])}</h2>
  <div class="seo-grid">{hs_html}</div>
</section>
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
                "inLanguage": ["en", "te", "hi"],
            },
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="traffic-fines/",
        title="Telangana Traffic Fines 2026, E-Challan Rules & Driver Hand Signals Guide",
        description="Updated Telangana & Hyderabad traffic challan fines (helmet, drunk driving, overspeeding, no licence, seatbelt) under the Motor Vehicles Act plus visual driver and police hand signals.",
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
        f"""<article class="seo-card rto-code-card" data-search="{esc((d['code'] + ' ts-' + d['code'] + ' tg-' + d['code'] + ' ' + d['district']).lower())}" style="display:flex; align-items:center; gap:12px;">
  <span class="tabular-nums" style="background:#0B2545; color:#F3CA40; font-weight:800; font-size:0.82rem; padding:6px 10px; border-radius:6px; flex-shrink:0;">TS / TG-{esc(d['code'])}</span>
  <div>
    <h3 style="font-size:0.98rem; color:#0B2545; font-weight:700;">{esc(d['district'])}</h3>
    <p style="font-size:0.78rem; color:#64748B;">Telangana RTA Office Code {esc(d['code'])}</p>
  </div>
</article>"""
        for d in popular["districtRtoCodes"]
    )

    body_html = f"""
<section>
  <div style="display:flex; justify-content:space-between; align-items:flex-end; flex-wrap:wrap; gap:12px; margin-bottom:16px;">
    <div>
      <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:6px;">Complete District-Wise Telangana RTA Office Codes (01 to 38)</h2>
      <p style="color:#475569; max-width:68ch;">Telangana transitioned vehicle registration prefixes from <strong>TS</strong> to <strong>TG</strong>, while keeping the exact same district numerical codes (01–38). All STALL Learner's Licence tests follow the same 412-question bank.</p>
    </div>
    <input type="text" id="rto-codes-search" placeholder="Search district or code (e.g. Warangal, 07)..." style="padding:9px 14px; border:1px solid #CBD5E1; border-radius:8px; font-size:0.88rem; min-width:250px;">
  </div>
  <div class="seo-grid">{cards}</div>
  <p id="rto-codes-empty" style="display:none; text-align:center; padding:24px; color:#64748B;">No Telangana district matched your search.</p>
</section>
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
                    {"@type": "ListItem", "position": i, "name": f"TS-{d['code']} / TG-{d['code']} {d['district']}"}
                    for i, d in enumerate(popular["districtRtoCodes"], 1)
                ],
            },
        ],
    }

    html_doc = render_shell(
        lang="en",
        rel_root="../",
        canonical_path="telangana-rto-codes/",
        title="All Telangana RTO / RTA District Codes List (TS-01 to TS-38 / TG-01 to TG-38)",
        description="Complete list of all 38 Telangana Regional Transport Authority (RTA / RTO) district codes from TS/TG-01 Adilabad to TS/TG-38 Narayanpet including Hyderabad, Warangal, Karimnagar, Nizamabad, Khammam & Rangareddy.",
        keywords="Telangana RTO codes list, TG 01 to TG 38 districts, TS 07 Kondapur TS 09 Khairatabad, Warangal Karimnagar Nizamabad RTA code",
        h1="All Telangana District RTO / RTA Codes (TS &amp; TG 01–38)",
        subtitle="Complete State-Wide District Transport Office Directory for LLR & DL Applicants",
        breadcrumb_label="TS / TG RTO Codes",
        active_nav="telangana-rto-codes",
        json_ld=json_ld,
        body_html=body_html,
        extra_scripts=extra_scripts,
    )
    write_file("telangana-rto-codes/index.html", html_doc)


def build_localized_page(lang_code, guide, cheatsheet, signs):
    hreflang_links = [
        ("en", f"{BASE_URL}/"),
        ("te", f"{BASE_URL}/te/"),
        ("hi", f"{BASE_URL}/hi/"),
        ("x-default", f"{BASE_URL}/"),
    ]

    rules_list = "".join(
        f'<article class="cheatsheet-rule-card"><span class="rule-num-badge">{idx}</span><p style="font-size:0.94rem; color:#0F172A; line-height:1.5;">{esc(gr["rule"][lang_code])}</p></article>'
        for idx, gr in enumerate(cheatsheet["goldenRules"], 1)
    )
    centers_list = "".join(
        f"""<article class="seo-card">
  <span class="seo-badge badge-informatory" style="margin-bottom:6px;">{esc(c['code'])}</span>
  <h3 style="font-size:1rem; color:#0B2545; font-weight:700;">{esc(c['name'][lang_code])}</h3>
  <p style="font-size:0.85rem; color:#475569; margin-top:4px;">{esc(c['address'][lang_code])}</p>
</article>"""
        for c in guide["centers"]
    )
    sample_signs = "".join(
        f"""<article class="seo-card" style="text-align:center;">
  <img src="../{esc(s['image'])}" alt="{esc(s['options'][lang_code][s['answerIndex']])}" loading="lazy" style="max-height:90px; margin-bottom:8px;">
  <strong style="display:block; color:#0B2545; font-size:0.92rem;">{esc(clean_text(s['options'][lang_code][s['answerIndex']]))}</strong>
</article>"""
        for s in signs[:12]
    )

    if lang_code == "te":
        title = "తెలంగాణ RTA లెర్నర్స్ లైసెన్స్ (LLR) మాక్ టెస్ట్ 2026 • STALL ప్రాక్టీస్ తెలుగులో"
        desc = "హైదరాబాద్ మరియు తెలంగాణ RTA లెర్నర్స్ లైసెన్స్ (LLR) కంప్యూటర్ పరీక్ష (STALL) కోసం 412 అధికారిక ప్రశ్నలతో తెలుగులో ఉచిత మాక్ టెస్ట్, రోడ్డు సంకేతాలు మరియు RTO గైడ్."
        kw = "Telangana LLR mock test Telugu, తెలుగు LLR ప్రాక్టీస్ టెస్ట్, Hyderabad RTO test Telugu, రోడ్డు సంకేతాలు తెలుగు"
        h1 = "తెలంగాణ RTA లెర్నర్స్ లైసెన్స్ (LLR) తెలుగు ప్రాక్టీస్ &amp; మాక్ టెస్ట్"
        sub = "అధికారిక STALL కంప్యూటర్ పరీక్ష సిమ్యులేటర్ • 412 ప్రశ్నలు తెలుగులో ఆడియోతో"
        crumb = "తెలుగు గైడ్"
        rules_h2 = "పరీక్షకు ముందు 10 ముఖ్య నియమాలు (Golden Rules)"
        centers_h2 = "హైదరాబాద్ RTO పరీక్షా కేంద్రాలు"
        signs_h2 = "ముఖ్యమైన రోడ్డు సంకేతాలు (నమూనా)"
        faq_items = [
            ("తెలంగాణ LLR కంప్యూటర్ పరీక్షలో ఎన్ని ప్రశ్నలు ఉంటాయి?", "మొత్తం 20 మల్టిపుల్ ఛాయిస్ ప్రశ్నలు ఉంటాయి: 8 రోడ్డు సంకేతాలు, 8 ట్రాఫిక్ నియమాలు, 4 జనరల్ డ్రైవింగ్ నియమాలు."),
            ("తెలంగాణ LLR పరీక్షలో పాస్ మార్కు ఎంత?", "20 ప్రశ్నలకు కనీసం 12 సరైన సమాధానాలు (60%) రావాలి. నెగటివ్ మార్కింగ్ లేదు."),
            ("ఒక్కో ప్రశ్నకు ఎంత సమయం ఉంటుంది?", "ప్రతి ప్రశ్నకు 30 సెకన్ల సమయం ఉంటుంది. 12 సరైన సమాధానాలు రాగానే పరీక్ష వెంటనే పాస్ అని ముగుస్తుంది."),
        ]
    else:
        title = "तेलंगाना RTA लर्नर लाइसेंस (LLR) मॉक टेस्ट 2026 • STALL प्रैक्टिस हिन्दी में"
        desc = "हैदराबाद और तेलंगाना RTA लर्नर लाइसेंस (LLR) कंप्यूटर परीक्षा (STALL) के लिए 412 आधिकारिक प्रश्नों के साथ हिन्दी में मुफ्त मॉक टेस्ट, सड़क संकेत और RTO गाइड।"
        kw = "Telangana LLR mock test Hindi, तेलंगाना LLR प्रैक्टिस टेस्ट हिन्दी, Hyderabad RTO test Hindi, सड़क संकेत हिन्दी"
        h1 = "तेलंगाना RTA लर्नर लाइसेंस (LLR) हिन्दी प्रैक्टिस और मॉक टेस्ट"
        sub = "आधिकारिक STALL कंप्यूटर परीक्षा सिम्युलेटर • 412 प्रश्न हिन्दी ऑडियो के साथ"
        crumb = "हिन्दी गाइड"
        rules_h2 = "परीक्षा से पहले 10 सुनहरे नियम (Golden Rules)"
        centers_h2 = "हैदराबाद आरटीओ परीक्षा केंद्र"
        signs_h2 = "प्रमुख सड़क संकेत (उदाहरण)"
        faq_items = [
            ("तेलंगाना LLR कंप्यूटर परीक्षा में कितने प्रश्न पूछे जाते हैं?", "कुल 20 बहुविकल्पीय प्रश्न पूछे जाते हैं: 8 सड़क संकेत, 8 यातायात नियम और 4 सामान्य ड्राइविंग सिद्धांत।"),
            ("तेलंगाना LLR परीक्षा में पास होने के लिए कितने अंक चाहिए?", "20 में से कम से कम 12 सही उत्तर (60%) आवश्यक हैं। कोई नेगेटिव मार्किंग नहीं है।"),
            ("प्रत्येक प्रश्न के लिए कितना समय मिलता है?", "प्रत्येक प्रश्न के लिए 30 सेकंड मिलते हैं। जैसे ही 12 उत्तर सही होते हैं, परीक्षा तुरंत PASS दिखाकर समाप्त हो जाती है।"),
        ]

    faq_html = "".join(
        f"""<details class="footer-faq-item">
  <summary>{esc(q)}</summary>
  <p>{esc(a)}</p>
</details>"""
        for q, a in faq_items
    )

    body_html = f"""
<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">{rules_h2}</h2>
  <div class="cheatsheet-rules-grid">{rules_list}</div>
</section>

{ad_slot_html("seo_in_content", "leaderboard")}

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">{signs_h2}</h2>
  <div class="seo-grid">{sample_signs}</div>
</section>

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">{centers_h2}</h2>
  <div class="seo-grid">{centers_list}</div>
</section>

<section>
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">FAQ</h2>
  <div class="footer-faq-grid">{faq_html}</div>
</section>
{ad_slot_html("seo_multiplex", "multiplex")}
"""

    json_ld = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{BASE_URL}/"},
                    {"@type": "ListItem", "position": 2, "name": lang_code.upper(), "item": f"{BASE_URL}/{lang_code}/"},
                ],
            },
            {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": a},
                    }
                    for q, a in faq_items
                ],
            },
        ],
    }

    html_doc = render_shell(
        lang=lang_code,
        rel_root="../",
        canonical_path=f"{lang_code}/",
        title=title,
        description=desc,
        keywords=kw,
        h1=h1,
        subtitle=sub,
        breadcrumb_label=crumb,
        active_nav=lang_code,
        json_ld=json_ld,
        hreflang_links=hreflang_links,
        body_html=body_html,
    )
    write_file(f"{lang_code}/index.html", html_doc)


def build_privacy_policy_page():
    body_html = f"""
<article class="card-surface" style="max-width:860px; margin:0 auto;">
  <p style="font-size:0.84rem; color:#64748B; margin-bottom:16px;">Last updated: {TODAY} • Domain: <strong>llr.sarvacapital.in</strong></p>

  <h2 style="font-size:1.15rem; color:#0B2545; font-weight:800; margin:18px 0 8px;">1. Overview &amp; Zero-Account Local Practice</h2>
  <p style="color:#334155; line-height:1.65; margin-bottom:12px;">
    <strong>Telangana RTA Learner's Licence Practice</strong> (operated by Sarva Capital at <code>llr.sarvacapital.in</code>) is a free public educational simulator. We do not require registration, logins, phone numbers, Aadhaar details, or personal profiles to use any practice mode, mock test, or study guide.
  </p>

  <h2 style="font-size:1.15rem; color:#0B2545; font-weight:800; margin:18px 0 8px;">2. Browser Local Storage &amp; Cross-Device QR Sync</h2>
  <p style="color:#334155; line-height:1.65; margin-bottom:12px;">
    Your quiz streaks, readiness progress, language preference (English, Telugu, or Hindi), sound settings, and RTO document checklist ticks are stored exclusively inside your own browser's <code>localStorage</code>. None of your study scores are uploaded to any backend database. When you use the optional QR Cross-Device Sync feature, your compact study progress is encoded directly inside the sync URL / JSON export file processed locally in your browser.
  </p>

  <h2 style="font-size:1.15rem; color:#0B2545; font-weight:800; margin:18px 0 8px;">3. Google AdSense &amp; Third-Party Advertising Cookies</h2>
  <p style="color:#334155; line-height:1.65; margin-bottom:10px;">
    To keep this learning platform 100% free for students and learner drivers across Telangana, we plan to display non-intrusive advertisements served by <strong>Google AdSense</strong> on study and post-exam summary screens (never inside the active 30-second timed mock test).
  </p>
  <ul style="padding-left:20px; color:#334155; line-height:1.65; margin-bottom:12px;">
    <li style="margin-bottom:6px;">Third-party vendors, including Google, use cookies to serve ads based on a user's prior visits to this website or other websites.</li>
    <li style="margin-bottom:6px;">Google's use of advertising cookies enables it and its partners to serve ads to users based on their visit to <code>llr.sarvacapital.in</code> and/or other sites on the Internet.</li>
    <li style="margin-bottom:6px;">Users may opt out of personalized advertising by visiting <a href="https://adssettings.google.com/" target="_blank" rel="noopener" style="color:#134074; font-weight:600;">Google Ads Settings</a> or opt out of third-party vendor cookie use via <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener" style="color:#134074; font-weight:600;">aboutads.info</a>.</li>
  </ul>

  <h2 style="font-size:1.15rem; color:#0B2545; font-weight:800; margin:18px 0 8px;">4. External Official Links</h2>
  <p style="color:#334155; line-height:1.65; margin-bottom:12px;">
    We link to official government portals such as <a href="https://transport.telangana.gov.in" target="_blank" rel="noopener" style="color:#134074; font-weight:600;">transport.telangana.gov.in</a> for application filing, slot booking, and DigiLocker/mParivahan verification. External sites operate under their own privacy policies.
  </p>

  <h2 style="font-size:1.15rem; color:#0B2545; font-weight:800; margin:18px 0 8px;">5. Contact Us</h2>
  <p style="color:#334155; line-height:1.65;">
    For privacy questions, ad inquiries, or content corrections, please write to <a href="mailto:{CONTACT_EMAIL}" style="color:#134074; font-weight:700;">{CONTACT_EMAIL}</a>.
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
  <h2 style="font-size:1.15rem; color:#0B2545; font-weight:800; margin-bottom:8px;">1. Mission &amp; Educational Purpose</h2>
  <p style="color:#334155; line-height:1.65; margin-bottom:14px;">
    <strong>Telangana RTA Learner's Licence Practice</strong> (<a href="{BASE_URL}/" style="color:#134074; font-weight:600;">llr.sarvacapital.in</a>) is a free civic-education web application built by <strong>Sarva Capital</strong> to help learner drivers across Hyderabad and all 33+ districts of Telangana prepare thoroughly for the computerized <strong>STALL (Screen Test Aid for Learner Licence)</strong> exam and build lifelong road safety habits.
  </p>

  <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:10px; padding:16px; margin-bottom:18px;">
    <h2 style="font-size:1.05rem; color:#92400E; font-weight:800; margin-bottom:6px;">2. Non-Government Affiliation Disclaimer</h2>
    <p style="color:#78350F; line-height:1.6; font-size:0.92rem; margin:0;">
      <strong>Independent Practice Tool:</strong> This website is NOT an official website of, nor affiliated with, the Government of Telangana Transport Department (RTA) or Parivahan Sarathi. All official Learner's Licence applications, fee payments, slot bookings, and digital LLR downloads must be completed exclusively on the official government portal: <a href="https://transport.telangana.gov.in" target="_blank" rel="noopener" style="color:#92400E; font-weight:700; text-decoration:underline;">transport.telangana.gov.in</a>.
    </p>
  </div>

  <h2 style="font-size:1.15rem; color:#0B2545; font-weight:800; margin:18px 0 8px;">3. Official Curriculum &amp; Source Attribution</h2>
  <p style="color:#334155; line-height:1.65; margin-bottom:14px;">
    The 412 questions (94 Road Signs, 159 Rules of the Road Regulations, and 159 General Driving Principles), fixed option sequence, 8-8-4 category quota, and 30-second countdown logic are derived directly from the publicly published Telangana Transport Department STALL curriculum under the Motor Vehicles Act, 1988.
  </p>

  <h2 style="font-size:1.15rem; color:#0B2545; font-weight:800; margin:18px 0 8px;">4. Terms of Use</h2>
  <p style="color:#334155; line-height:1.65; margin-bottom:14px;">
    While we carefully verify all translations, answer keys, RTO office addresses, and Motor Vehicles Act fine schedules, statutory rules and RTO fees may change over time. Always verify current fee schedules and slot guidelines directly on official government notices.
  </p>

  <h2 style="font-size:1.15rem; color:#0B2545; font-weight:800; margin:18px 0 8px;">5. Contact &amp; Feedback</h2>
  <p style="color:#334155; line-height:1.65;">
    Found a typo in Telugu/Hindi text, an outdated RTO office detail, or want to share feedback? Reach our team at <a href="mailto:{CONTACT_EMAIL}" style="color:#134074; font-weight:700;">{CONTACT_EMAIL}</a>.
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
        title="About, Official Disclaimer & Contact • Telangana RTA LLR Practice",
        description="About Telangana RTA LLR Practice by Sarva Capital: free educational mission, official Telangana Transport curriculum attribution, non-affiliation disclaimer, and contact details.",
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
        "- Exam Format: 20 multiple-choice questions per test",
        "- Category Quota: 8 Road Signs (40%) + 8 Rules of the Road (40%) + 4 General Driving Principles (20%)",
        "- Time Limit: 30 seconds per question (maximum 10 minutes)",
        "- Passing Mark: 12 correct out of 20 (60%); zero negative marking",
        "- Early Termination: Test ends immediately as PASSED on reaching 12 correct answers, or FAILED on reaching 9 wrong answers",
        "- Fixed Option Order: Options 1, 2, 3, 4 are never shuffled (matching STALL physical keypad 1-4)",
        "- Languages Supported: English, Telugu (తెలుగు), Hindi (हिन्दी)",
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

    lines.extend(["", "## 7. Permanent DL Track Test Guide (8-Track & H-Track) & Digital LLR Download"])
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


def build_sitemap():
    urls = [
        (f"{BASE_URL}/", "daily", "1.0", True),
        (f"{BASE_URL}/road-signs/", "weekly", "0.9", False),
        (f"{BASE_URL}/question-bank/", "weekly", "0.9", False),
        (f"{BASE_URL}/rto-guide/", "weekly", "0.9", False),
        (f"{BASE_URL}/dl-test-guide/", "weekly", "0.9", False),
        (f"{BASE_URL}/traffic-fines/", "weekly", "0.8", False),
        (f"{BASE_URL}/telangana-rto-codes/", "weekly", "0.8", False),
        (f"{BASE_URL}/cheatsheet/", "weekly", "0.8", False),
        (f"{BASE_URL}/te/", "weekly", "0.9", True),
        (f"{BASE_URL}/hi/", "weekly", "0.9", True),
        (f"{BASE_URL}/about/", "monthly", "0.5", False),
        (f"{BASE_URL}/privacy-policy/", "monthly", "0.5", False),
    ]
    entries = []
    for loc, freq, prio, include_hreflang in urls:
        alt_block = ""
        if include_hreflang:
            alt_block = f"""
    <xhtml:link rel="alternate" hreflang="en" href="{BASE_URL}/" />
    <xhtml:link rel="alternate" hreflang="te" href="{BASE_URL}/te/" />
    <xhtml:link rel="alternate" hreflang="hi" href="{BASE_URL}/hi/" />
    <xhtml:link rel="alternate" hreflang="x-default" href="{BASE_URL}/" />"""
        entries.append(
            f"""  <url>
    <loc>{loc}</loc>
    <lastmod>{TODAY}</lastmod>
    <changefreq>{freq}</changefreq>
    <priority>{prio}</priority>{alt_block}
  </url>"""
        )

    xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
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
    build_rto_guide_page(guide)
    build_dl_test_guide_page(popular)
    build_traffic_fines_page(popular)
    build_district_rto_codes_page(popular)
    build_cheatsheet_page(cheatsheet, twins, popular)
    build_localized_page("te", guide, cheatsheet, signs)
    build_localized_page("hi", guide, cheatsheet, signs)
    build_privacy_policy_page()
    build_about_page()
    build_llms_full(signs, rules, gp, guide, cheatsheet, twins, popular)
    build_sitemap()


if __name__ == "__main__":
    main()
