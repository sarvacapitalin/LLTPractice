#!/usr/bin/env python3
"""Generate a crisp 1200x630 Open Graph / Twitter social preview card at assets/images/og-preview.png."""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630

def load_font(path, size, index=0):
    try:
        return ImageFont.truetype(path, size, index=index)
    except Exception:
        return ImageFont.load_default()

def main():
    base = Image.new("RGBA", (W, H), "#07192F")
    bg_draw = ImageDraw.Draw(base)

    # Diagonal-like navy gradient
    for y in range(H):
        t = y / H
        r = int(7 + (19 - 7) * t)
        g = int(25 + (64 - 25) * t)
        b = int(47 + (116 - 47) * t)
        bg_draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Alpha-composited subtle grid
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ov_draw = ImageDraw.Draw(overlay)
    for x in range(200, W, 200):
        ov_draw.line([(x, 0), (x, H)], fill=(255, 255, 255, 16), width=1)
    for y in range(105, H, 105):
        ov_draw.line([(0, y), (W, y)], fill=(255, 255, 255, 16), width=1)
    img = Image.alpha_composite(base, overlay)
    draw = ImageDraw.Draw(img)

    # Top and bottom gold accent bars
    draw.rectangle([0, 0, W, 8], fill="#F3CA40")
    draw.rectangle([0, H - 8, W, H], fill="#F3CA40")

    avenir = "/System/Library/Fonts/Avenir Next.ttc"
    # 0=Bold, 2=Demi Bold, 5=Medium, 7=Regular, 8=Heavy
    font_pill = load_font(avenir, 15, index=2)
    font_title = load_font(avenir, 50, index=8)
    font_sub_gold = load_font(avenir, 38, index=0)
    font_subtitle = load_font(avenir, 22, index=5)
    font_card_title = load_font(avenir, 22, index=0)
    font_card_body = load_font(avenir, 16, index=7)
    font_card_badge = load_font(avenir, 15, index=2)
    font_footer_url = load_font(avenir, 20, index=0)
    font_footer_note = load_font(avenir, 17, index=7)

    # Top authority pill
    draw.rounded_rectangle([80, 56, 430, 96], radius=20, fill="#1D4E89", outline="#3B82F6", width=1)
    draw.ellipse([98, 70, 110, 82], fill="#10B981")
    draw.text((120, 66), "OFFICIAL STALL 2026 SIMULATOR", font=font_pill, fill="#E2E8F0")

    # Free badge on top-right
    draw.rounded_rectangle([920, 56, 1120, 96], radius=20, fill="#064E3B", outline="#10B981", width=1)
    draw.text((948, 66), "100% FREE • PWA", font=font_pill, fill="#A7F3D0")

    # Main Title & Gold Subtitle
    draw.text((80, 126), "Telangana RTA Learner's Licence", font=font_title, fill="#FFFFFF")
    draw.text((80, 192), "LLR Computerized Mock Exam (STALL)", font=font_sub_gold, fill="#F3CA40")
    draw.text((80, 248), "Authentic Hyderabad & Telangana RTO Practice  |  412 Verified Questions", font=font_subtitle, fill="#CBD5E1")

    # Three feature cards
    cards = [
        ("412 Official Questions", "94 Road Signs • 159 Rules", "159 Driving Principles", "100% Telangana RTA Parity", "#10B981"),
        ("Real STALL Kiosk", "20 Questions • 30s Timer", "8 Signs • 8 Rules • 4 Principles", "Pass Mark: 12 / 20 (60%)", "#F3CA40"),
        ("95% Readiness Gate", "Spaced 2-Streak Mastery", "Tutor Mode + Audio Read-Aloud", "Instant Exam Readiness", "#38BDF8"),
    ]
    card_w = 326
    card_h = 166
    gap = 31
    start_x = 80
    start_y = 308

    for i, (ctitle, l1, l2, badge, badge_color) in enumerate(cards):
        cx = start_x + i * (card_w + gap)
        cy = start_y
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=16, fill="#0F3057", outline="#1D4E89", width=2)
        draw.text((cx + 22, cy + 22), ctitle, font=font_card_title, fill="#FFFFFF")
        draw.text((cx + 22, cy + 62), l1, font=font_card_body, fill="#CBD5E1")
        draw.text((cx + 22, cy + 88), l2, font=font_card_body, fill="#CBD5E1")
        draw.text((cx + 22, cy + 126), badge, font=font_card_badge, fill=badge_color)

    # Footer bar
    draw.line([(80, 518), (1120, 518)], fill="#1E3A5F", width=1)
    draw.text((80, 542), "llr.sarvacapital.in", font=font_footer_url, fill="#F3CA40")
    draw.text((285, 545), "•  Free Public Learning Resource by Sarva Capital  •  No Login Required", font=font_footer_note, fill="#94A3B8")

    os.makedirs("assets/images", exist_ok=True)
    img.convert("RGB").save("assets/images/og-preview.png", format="PNG", optimize=True)
    print("Generated assets/images/og-preview.png (1200x630)")

if __name__ == "__main__":
    main()
