#!/usr/bin/env python3
"""
scripts/build_seo_pages.py

Generates crawlable, zero-JS static HTML pages and llms-full.txt / sitemap.xml
directly from the verified Telangana RTA LLR JSON datasets so both regular
search engines (Google, Bing) and AI/LLM crawlers (ChatGPT Search, Perplexity,
Claude, Gemini) can index every road sign, all 412 Q&As, the Hyderabad RTO
guide, cheatsheet, and Telugu/Hindi localized entry pages.
"""

from datetime import date
import html
import json
import os

BASE_URL = "https://llr.sarvacapital.in"
TODAY = date.today().isoformat()


def esc(val):
    return html.escape(str(val or ""), quote=True)


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_file(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Generated {path} ({len(content.encode('utf-8'))} bytes)")


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
    active_nav="",
    json_ld=None,
    hreflang_links=None,
    body_html="",
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
        ("", "🚦 STALL Simulator", "home"),
        ("road-signs/", "🚸 94 Road Signs", "road-signs"),
        ("question-bank/", "📚 412 Q&amp;A Bank", "question-bank"),
        ("rto-guide/", "🏢 RTO Guide", "rto-guide"),
        ("dl-test-guide/", "🚗 DL Track Test", "dl-test-guide"),
        ("traffic-fines/", "🚨 Fines &amp; Signals", "traffic-fines"),
        ("telangana-rto-codes/", "🗺️ TS/TG Codes", "telangana-rto-codes"),
        ("cheatsheet/", "⚡ Cheatsheet", "cheatsheet"),
        ("te/", "🌐 తెలుగు", "te"),
        ("hi/", "🌐 हिन्दी", "hi"),
    ]
    nav_links_html = "\n".join(
        f'<a href="{rel_root}{href}" class="seo-nav-link{" active" if key == active_nav else ""}">{label}</a>'
        for href, label, key in nav_items
    )

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

  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:url" content="{esc(canonical_url)}">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{BASE_URL}/assets/images/og-preview.png">

{ld_script}

  <link rel="stylesheet" href="{rel_root}css/styles.css?v=20">
  <style>
    .seo-nav-bar {{ background: #FFFFFF; border-bottom: 1px solid #E2E8F0; }}
    .seo-nav-inner {{ max-width: 1200px; margin: 0 auto; padding: 10px 16px; display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .seo-nav-link {{ text-decoration: none; font-size: 0.88rem; font-weight: 600; color: #334155; padding: 7px 12px; border-radius: 8px; background: #F8FAFC; border: 1px solid #E2E8F0; transition: all 0.15s ease; }}
    .seo-nav-link:hover {{ background: #EFF6FF; color: #134074; border-color: #93C5FD; }}
    .seo-nav-link.active {{ background: #134074; color: #FFFFFF; border-color: #134074; }}
    .seo-main {{ max-width: 1200px; width: 100%; margin: 24px auto; padding: 0 16px; flex: 1; }}
    .seo-hero {{ background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 16px; padding: 24px; margin-bottom: 24px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
    .seo-cta-row {{ display: flex; flex-wrap: wrap; gap: 12px; margin-top: 16px; }}
    .seo-cta-primary {{ display: inline-flex; align-items: center; gap: 8px; background: #134074; color: #FFFFFF; text-decoration: none; font-weight: 700; padding: 12px 18px; border-radius: 10px; font-size: 0.95rem; }}
    .seo-cta-secondary {{ display: inline-flex; align-items: center; gap: 8px; background: #FFF8E7; color: #92400E; border: 1px solid #FCD34D; text-decoration: none; font-weight: 700; padding: 12px 18px; border-radius: 10px; font-size: 0.95rem; }}
    .seo-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
    .seo-card {{ background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }}
    .seo-badge {{ display: inline-block; font-size: 0.72rem; font-weight: 700; padding: 3px 8px; border-radius: 999px; text-transform: uppercase; letter-spacing: 0.03em; }}
    .badge-mandatory {{ background: #FEE2E2; color: #991B1B; }}
    .badge-cautionary {{ background: #FEF3C7; color: #92400E; }}
    .badge-informatory {{ background: #DBEAFE; color: #1E40AF; }}
    .qa-card {{ background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 18px; margin-bottom: 14px; }}
    .qa-options {{ list-style: none; padding: 0; margin: 10px 0; display: grid; gap: 6px; }}
    .qa-option {{ padding: 8px 12px; border-radius: 8px; background: #F8FAFC; border: 1px solid #E2E8F0; font-size: 0.9rem; }}
    .qa-option.correct {{ background: #ECFDF5; border-color: #6EE7B7; color: #065F46; font-weight: 700; }}
    .toc-bar {{ display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 20px; }}
    .toc-pill {{ text-decoration: none; background: #FFFFFF; border: 1px solid #CBD5E1; color: #0B2545; padding: 8px 14px; border-radius: 999px; font-size: 0.85rem; font-weight: 700; }}
    .seo-footer {{ max-width: 1200px; width: 100%; margin: 32px auto 20px; padding: 20px 16px; border-top: 1px solid #E2E8F0; color: #64748B; font-size: 0.85rem; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 12px; }}
  </style>
</head>
<body>
  <header class="app-header">
    <div class="header-container">
      <div class="brand-section">
        <a href="{rel_root}" style="text-decoration:none; display:flex; align-items:center; gap:12px;">
          <div class="gov-emblem" aria-hidden="true">🏛️</div>
          <div class="brand-titles">
            <span style="font-size:1.1rem; font-weight:700; color:#FFFFFF; display:block;">Telangana RTA Learner's Licence Practice</span>
            <span class="subtitle">{esc(subtitle)}</span>
          </div>
        </a>
      </div>
      <div class="header-actions">
        <a href="{rel_root}" class="control-btn" style="background:#F3CA40; color:#0B2545; text-decoration:none; font-weight:800;">
          🚦 Launch STALL Simulator
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
    <section class="seo-hero">
      <h1 style="font-size: 1.65rem; color: #0B2545; font-weight: 800; line-height: 1.25; margin-bottom: 10px;">{h1}</h1>
      <p style="color: #475569; font-size: 1rem; line-height: 1.6;">{esc(description)}</p>
      <div class="seo-cta-row">
        <a href="{rel_root}" class="seo-cta-primary">🚦 Take Official 20-Question STALL Mock Test</a>
        <a href="{rel_root}?tab=practice" class="seo-cta-secondary">📚 Practice All 412 Questions Interactively</a>
      </div>
    </section>
    {body_html}
  </main>

  <footer class="seo-footer">
    <div>
      <a href="{BASE_URL}/" style="color:#134074; font-weight:700; text-decoration:none;">llr.sarvacapital.in</a> • Free Telangana RTA LLR Resource by <a href="https://sarvacapital.in" target="_blank" rel="noopener" style="color:#134074;">Sarva Capital</a>
    </div>
    <div>
      <a href="{rel_root}llms.txt" style="color:#475569;">llms.txt</a> • <a href="{rel_root}llms-full.txt" style="color:#475569;">llms-full.txt</a> • <a href="{rel_root}sitemap.xml" style="color:#475569;">sitemap.xml</a>
    </div>
  </footer>
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
            ans_en = s["options"]["en"][s["answerIndex"]]
            ans_te = s["options"]["te"][s["answerIndex"]]
            ans_hi = s["options"]["hi"][s["answerIndex"]]
            exp_en = s["explanation"]["en"]
            cards.append(
                f"""<article class="seo-card" id="{esc(s['id'])}">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
    <span class="seo-badge {badge_cls}">{esc(stype)}</span>
    <span style="font-size:0.78rem; color:#64748B; font-weight:700;">Sign #{s['questionNumber']}</span>
  </div>
  <div style="text-align:center; background:#F8FAFC; border-radius:8px; padding:12px; margin-bottom:10px;">
    <img src="../{esc(s['image'])}" alt="{esc(ans_en)} - Telangana RTA Road Sign" loading="lazy" style="max-height:110px; width:auto; object-fit:contain;">
  </div>
  <h3 style="font-size:1rem; color:#0B2545; font-weight:700; margin-bottom:6px;">{esc(ans_en)}</h3>
  <p style="font-size:0.84rem; color:#334155; margin-bottom:6px;"><strong>తెలుగు:</strong> {esc(ans_te)}<br><strong>हिन्दी:</strong> {esc(ans_hi)}</p>
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
            f"""<section id="{stype}" style="margin-bottom: 36px;">
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:4px;">{esc(heading)} ({len(items)})</h2>
  <p style="color:#475569; font-size:0.92rem; margin-bottom:16px;">{esc(sub)}</p>
  <div class="seo-grid">
    {"".join(cards)}
  </div>
</section>"""
        )

    toc = """<div class="toc-bar">
  <a href="#mandatory" class="toc-pill">🔴 Mandatory Signs (42)</a>
  <a href="#cautionary" class="toc-pill">⚠️ Cautionary Signs (38)</a>
  <a href="#informatory" class="toc-pill">ℹ️ Informatory Signs (14)</a>
  <a href="../?tab=flashcards" class="toc-pill" style="background:#EFF6FF; color:#134074;">🗂️ Practice Flashcards</a>
</div>"""

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
        active_nav="road-signs",
        json_ld=json_ld,
        body_html=toc + "\n".join(sections),
    )
    write_file("road-signs/index.html", html_doc)


def build_question_bank_page(signs, rules, gp):
    categories = [
        ("road-signs", "Section 1: Road Signs & Signals (94 Questions)", signs),
        ("rules-of-road", "Section 2: Rules of the Road Regulations (159 Questions)", rules),
        ("general-principles", "Section 3: General Driving Principles & Safety (159 Questions)", gp),
    ]

    toc = """<div class="toc-bar">
  <a href="#road-signs" class="toc-pill">🚸 Road Signs (94)</a>
  <a href="#rules-of-road" class="toc-pill">🛑 Rules of the Road (159)</a>
  <a href="#general-principles" class="toc-pill">🚗 Driving Principles (159)</a>
  <a href="../?tab=practice" class="toc-pill" style="background:#EFF6FF; color:#134074;">🎯 Interactive Practice Mode</a>
</div>"""

    sections = []
    for sec_id, heading, items in categories:
        cards = []
        for idx, q in enumerate(items, 1):
            img_html = ""
            if q.get("image"):
                img_html = f'<div style="margin:10px 0;"><img src="../{esc(q["image"])}" alt="Question diagram for {esc(q["id"])}" loading="lazy" style="max-height:110px; border-radius:8px;"></div>'
            opts_html = []
            for oi, opt in enumerate(q["options"]["en"]):
                is_ans = oi == q["answerIndex"]
                cls = "qa-option correct" if is_ans else "qa-option"
                mark = " ✓ (Correct)" if is_ans else ""
                opts_html.append(f'<li class="{cls}">{oi + 1}. {esc(opt)}{mark}</li>')
            exp = q.get("explanation", {}).get("en", "")
            cards.append(
                f"""<article class="qa-card" id="{esc(q['id'])}">
  <div style="font-size:0.78rem; color:#64748B; font-weight:700; margin-bottom:4px;">{esc(q['id'])} • Question #{idx}</div>
  <h3 style="font-size:1.02rem; color:#0B2545; font-weight:700; margin-bottom:8px;">{esc(q['text']['en'])}</h3>
  {img_html}
  <ol class="qa-options">{"".join(opts_html)}</ol>
  <p style="font-size:0.86rem; color:#334155; background:#F8FAFC; padding:10px; border-radius:8px; margin-top:8px;"><strong>Explanation:</strong> {esc(exp)}</p>
</article>"""
            )
        sections.append(
            f"""<section id="{sec_id}" style="margin-bottom:36px;">
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:14px;">{esc(heading)}</h2>
  {"".join(cards)}
</section>"""
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
        active_nav="question-bank",
        json_ld=json_ld,
        body_html=toc + "\n".join(sections),
    )
    write_file("question-bank/index.html", html_doc)


def build_rto_guide_page(guide):
    checklist_html = "".join(
        f"""<li class="seo-card" style="list-style:none;">
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
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
  <td style="padding:10px; border-bottom:1px solid #E2E8F0; font-weight:800; color:#047857;">{esc(f['amount'])}</td>
</tr>"""
        for f in guide["feeRules"]["fees"]
    )

    tips_html = "".join(
        f"""<article class="seo-card" style="background:#FFFBEB; border-color:#FDE68A;">
  <h3 style="font-size:0.98rem; color:#92400E; font-weight:700; margin-bottom:6px;">💡 {esc(t['title']['en'])}</h3>
  <p style="font-size:0.88rem; color:#78350F;">{esc(t['desc']['en'])}</p>
</article>"""
        for t in guide["topTips"]
    )

    body_html = f"""
<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">1. Required Documents Checklist for Telangana LLR Test</h2>
  <ul class="seo-grid" style="padding:0;">{checklist_html}</ul>
</section>

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">2. Test-Day 5-Step Walkthrough at Hyderabad RTO</h2>
  <ol style="padding:0;">{steps_html}</ol>
</section>

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">3. Hyderabad &amp; Telangana RTO Testing Centers Directory</h2>
  <div class="seo-grid">{centers_html}</div>
</section>

<section style="margin-bottom:32px;">
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

<section>
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">5. Top Tips to Pass on Your First Attempt</h2>
  <div class="seo-grid">{tips_html}</div>
</section>
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
        subtitle="Documents Checklist, RTO Center Addresses (TS-07 to TS-12), Fees &amp; Test-Day Steps",
        active_nav="rto-guide",
        json_ld=json_ld,
        body_html=body_html,
    )
    write_file("rto-guide/index.html", html_doc)


def build_cheatsheet_page(cheatsheet, twins, popular):
    rules_html = "".join(
        f"""<li class="qa-card" style="list-style:decimal inside;">
  <strong style="color:#0B2545;">{esc(gr['rule']['en'])}</strong>
  <p style="margin-top:6px; font-size:0.86rem; color:#475569;"><strong>తెలుగు:</strong> {esc(gr['rule']['te'])}<br><strong>हिन्दी:</strong> {esc(gr['rule']['hi'])}</p>
</li>"""
        for gr in cheatsheet["goldenRules"]
    )

    hs = popular["handSignals"]
    hs_html = "".join(
        f"""<article class="seo-card" style="display:flex; gap:12px; align-items:center;">
  <img src="../{esc(item['image'])}" alt="{esc(item['name']['en'])}" loading="lazy" style="width:72px; height:72px; object-fit:contain; background:#F8FAFC; border-radius:8px; padding:4px;">
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
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
    <div style="background:#F8FAFC; padding:10px; border-radius:8px; text-align:center;">
      <img src="../{esc(p['signA']['image'])}" alt="{esc(p['signA']['name']['en'])}" loading="lazy" style="max-height:80px;">
      <strong style="display:block; font-size:0.85rem; margin:6px 0;">{esc(p['signA']['name']['en'])}</strong>
      <p style="font-size:0.8rem; color:#475569; text-align:left;">{esc(p['signA']['rule']['en'])}</p>
    </div>
    <div style="background:#F8FAFC; padding:10px; border-radius:8px; text-align:center;">
      <img src="../{esc(p['signB']['image'])}" alt="{esc(p['signB']['name']['en'])}" loading="lazy" style="max-height:80px;">
      <strong style="display:block; font-size:0.85rem; margin:6px 0;">{esc(p['signB']['name']['en'])}</strong>
      <p style="font-size:0.8rem; color:#475569; text-align:left;">{esc(p['signB']['rule']['en'])}</p>
    </div>
  </div>
  <p style="font-size:0.84rem; color:#92400E; background:#FFFBEB; padding:8px 10px; border-radius:8px;"><strong>Memory Hook:</strong> {esc(p['memoryHook']['en'])}</p>
</article>"""
        for p in twins
    )

    body_html = f"""
<div class="no-print" style="margin-bottom:20px; display:flex; gap:10px; flex-wrap:wrap;">
  <button onclick="window.print()" class="seo-cta-primary" style="border:none; cursor:pointer;">🖨️ Print / Save PDF Revision Sheet</button>
  <a href="../road-signs/" class="seo-cta-secondary">🚸 View All 94 Road Signs</a>
</div>

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:12px;">⚡ Top 10 Golden Rules (10-Minute Pre-Exam Revision)</h2>
  <ol style="padding:0;">{rules_html}</ol>
</section>

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:12px;">👮 {esc(hs['title']['en'])}</h2>
  <div class="seo-grid">{hs_html}</div>
</section>

<section>
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:12px;">🔍 Tricky Twins: Commonly Confused Road Signs</h2>
  <div class="seo-grid" style="grid-template-columns:repeat(auto-fill, minmax(340px, 1fr));">{twins_html}</div>
</section>
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
        subtitle="Printable Last-Minute Revision Rules, Hand Signals &amp; Confusing Sign Comparisons",
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
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:12px;">1. {esc(slot['title']['en'])}</h2>
  <ol style="padding:0;">{slot_html}</ol>
</section>

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:8px;">2. {esc(dl['title']['en'])}</h2>
  <p style="color:#475569; margin-bottom:14px;">{esc(dl['eligibility']['en'])} {esc(dl['automatedTracksNote']['en'])}</p>
  <div class="seo-grid" style="grid-template-columns:repeat(auto-fit, minmax(320px, 1fr));">{tracks_html}</div>
</section>

<section>
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:12px;">3. Documents &amp; Test Vehicle Checklist for DL Track Day</h2>
  <div class="seo-card" style="background:#F0FDF4; border-color:#BBF7D0;">
    <ul style="padding-left:18px; color:#14532D; font-size:0.94rem; line-height:1.55;">{docs_html}</ul>
  </div>
</section>
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
        subtitle="Two-Wheeler '8' Track, Car 'H' Track, Automated RTA Tracks &amp; Digital LLR Download",
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
  <img src="../{esc(item['image'])}" alt="{esc(item['name']['en'])}" loading="lazy" style="width:76px; height:76px; object-fit:contain; background:#F8FAFC; border-radius:8px; padding:4px;">
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
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:12px;">🚨 {esc(fines['title']['en'])}</h2>
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

<section>
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:12px;">👮 {esc(hs['title']['en'])}</h2>
  <div class="seo-grid">{hs_html}</div>
</section>
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
        subtitle="Motor Vehicles Act Penalty Schedule &amp; Visual Police / Driver Hand Signals",
        active_nav="traffic-fines",
        json_ld=json_ld,
        body_html=body_html,
    )
    write_file("traffic-fines/index.html", html_doc)


def build_district_rto_codes_page(popular):
    cards = "".join(
        f"""<article class="seo-card" style="display:flex; align-items:center; gap:12px;">
  <span style="background:#0B2545; color:#F3CA40; font-weight:800; font-size:0.82rem; padding:6px 10px; border-radius:6px; flex-shrink:0;">TS / TG-{esc(d['code'])}</span>
  <div>
    <h3 style="font-size:0.98rem; color:#0B2545; font-weight:700;">{esc(d['district'])}</h3>
    <p style="font-size:0.78rem; color:#64748B;">Telangana RTA Office Code {esc(d['code'])}</p>
  </div>
</article>"""
        for d in popular["districtRtoCodes"]
    )

    body_html = f"""
<section>
  <h2 style="font-size:1.35rem; color:#0B2545; font-weight:800; margin-bottom:8px;">Complete District-Wise Telangana RTA Office Codes (01 to 38)</h2>
  <p style="color:#475569; margin-bottom:16px;">Telangana transitioned vehicle registration prefixes from <strong>TS</strong> to <strong>TG</strong>, while keeping the exact same district numerical codes (01–38). All STALL Learner's Licence tests across every Telangana district follow the same 412-question bank and 20-question (12/20 pass) computerized exam format.</p>
  <div class="seo-grid">{cards}</div>
</section>
"""

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
        subtitle="Complete State-Wide District Transport Office Directory for LLR &amp; DL Applicants",
        active_nav="telangana-rto-codes",
        json_ld=json_ld,
        body_html=body_html,
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
        f'<li class="qa-card" style="list-style:decimal inside;">{esc(gr["rule"][lang_code])}</li>'
        for gr in cheatsheet["goldenRules"]
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
  <strong style="display:block; color:#0B2545; font-size:0.92rem;">{esc(s['options'][lang_code][s['answerIndex']])}</strong>
</article>"""
        for s in signs[:12]
    )

    if lang_code == "te":
        title = "తెలంగాణ RTA లెర్నర్స్ లైసెన్స్ (LLR) మాక్ టెస్ట్ 2026 • STALL ప్రాక్టీస్ తెలుగులో"
        desc = "హైదరాబాద్ మరియు తెలంగాణ RTA లెర్నర్స్ లైసెన్స్ (LLR) కంప్యూటర్ పరీక్ష (STALL) కోసం 412 అధికారిక ప్రశ్నలతో తెలుగులో ఉచిత మాక్ టెస్ట్, రోడ్డు సంకేతాలు మరియు RTO గైడ్."
        kw = "Telangana LLR mock test Telugu, తెలుగు LLR ప్రాక్టీస్ టెస్ట్, Hyderabad RTO test Telugu, రోడ్డు సంకేతాలు తెలుగు"
        h1 = "తెలంగాణ RTA లెర్నర్స్ లైసెన్స్ (LLR) తెలుగు ప్రాక్టీస్ &amp; మాక్ టెస్ట్"
        sub = "అధికారిక STALL కంప్యూటర్ పరీక్ష సిమ్యులేటర్ • 412 ప్రశ్నలు తెలుగులో ఆడియోతో"
        cta_label = "🚦 తెలుగులో STALL మాక్ టెస్ట్ ప్రారంభించండి"
        rules_h2 = "⚡ పరీక్షకు ముందు 10 ముఖ్య నియమాలు (Golden Rules)"
        centers_h2 = "🏢 హైదరాబాద్ RTO పరీక్షా కేంద్రాలు"
        signs_h2 = "🚸 ముఖ్యమైన రోడ్డు సంకేతాలు (నమూనా)"
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
        cta_label = "🚦 हिन्दी में STALL मॉक टेस्ट शुरू करें"
        rules_h2 = "⚡ परीक्षा से पहले 10 सुनहरे नियम (Golden Rules)"
        centers_h2 = "🏢 हैदराबाद आरटीओ परीक्षा केंद्र"
        signs_h2 = "🚸 प्रमुख सड़क संकेत (उदाहरण)"
        faq_items = [
            ("तेलंगाना LLR कंप्यूटर परीक्षा में कितने प्रश्न पूछे जाते हैं?", "कुल 20 बहुविकल्पीय प्रश्न पूछे जाते हैं: 8 सड़क संकेत, 8 यातायात नियम और 4 सामान्य ड्राइविंग सिद्धांत।"),
            ("तेलंगाना LLR परीक्षा में पास होने के लिए कितने अंक चाहिए?", "20 में से कम से कम 12 सही उत्तर (60%) आवश्यक हैं। कोई नेगेटिव मार्किंग नहीं है।"),
            ("प्रत्येक प्रश्न के लिए कितना समय मिलता है?", "प्रत्येक प्रश्न के लिए 30 सेकंड मिलते हैं। जैसे ही 12 उत्तर सही होते हैं, परीक्षा तुरंत PASS दिखाकर समाप्त हो जाती है।"),
        ]

    faq_html = "".join(
        f"""<details class="qa-card" style="cursor:pointer;">
  <summary style="font-weight:700; color:#0B2545;">{esc(q)}</summary>
  <p style="margin-top:8px; color:#475569;">{esc(a)}</p>
</details>"""
        for q, a in faq_items
    )

    body_html = f"""
<div style="margin-bottom:24px;">
  <a href="../?lang={lang_code}" class="seo-cta-primary" style="font-size:1.05rem;">{cta_label}</a>
</div>

<section style="margin-bottom:32px;">
  <h2 style="font-size:1.3rem; color:#0B2545; font-weight:800; margin-bottom:12px;">{rules_h2}</h2>
  <ol style="padding:0;">{rules_list}</ol>
</section>

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
  {faq_html}
</section>
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
        active_nav=lang_code,
        json_ld=json_ld,
        hreflang_links=hreflang_links,
        body_html=body_html,
    )
    write_file(f"{lang_code}/index.html", html_doc)


def build_llms_full(signs, rules, gp, guide, cheatsheet, twins, popular):
    lines = [
        "# Telangana RTA Learner's Licence (LLR) Practice & STALL Simulator — Complete Knowledge Reference",
        "",
        f"> Authoritative, free, offline-capable (PWA) preparation guide and complete 412-question bank for the Telangana Transport Department STALL computerized Learner's Licence test at {BASE_URL}/.",
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
            ans = q["options"]["en"][q["answerIndex"]]
            lines.append(f"- **{q['id']}**: {q['text']['en']} -> **Answer: {ans}**")

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
    build_llms_full(signs, rules, gp, guide, cheatsheet, twins, popular)
    build_sitemap()


if __name__ == "__main__":
    main()
