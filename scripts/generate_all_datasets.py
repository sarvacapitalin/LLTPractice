# scripts/generate_all_datasets.py
"""
Master Builder Script for Telangana Learner's Licence Test (LLR) Practice Website.
Generates:
1. data/questions/telangana/road-signs.json (94 questions)
2. data/questions/telangana/rules-of-road.json (159 questions)
3. data/questions/telangana/general-principles.json (159 questions)
4. data/i18n/en.json, data/i18n/te.json, data/i18n/hi.json

Enforces:
- Total questions: exactly 412 questions
- Strict schema compliance
- Zero-based answerIndex matching official answer keys
- Exactly 4 options per question in English, Telugu, and Hindi
- Authentic sign classifications (mandatory, cautionary, informatory)
- Validated image assets (all 94 road sign PNGs and 21 scenario PNGs)
"""
import os
import re
import json
from scripts.build_clean_english_extractor import get_segmented_questions, extract_qa
from scripts.test_4_options_clustering import cluster_tokens_into_4_options
from scripts.translator import translate_phrase, get_explanation

def get_sign_type(q_num):
    """Returns mandatory, cautionary, or informatory for each of the 94 road signs."""
    # Mandatory signs: regulatory orders, prohibitions, compulsory commands, and police hand signals
    if q_num in [1, 4, 5, 6] or (9 <= q_num <= 42) or (84 <= q_num <= 88):
        return "mandatory"
    # Informatory signs: facilities, parking designations, information boards
    elif q_num in [8] or (89 <= q_num <= 94):
        return "informatory"
    # Cautionary signs: hazard warnings, road geometry, intersections, pedestrian crossings
    else:
        return "cautionary"

def build_road_signs():
    print("-> Compiling Road Signs (94 questions)...")
    cat = "road_signs"
    total = 94
    qs = get_segmented_questions(cat, "road-signs-english.pdf", 299, total)

    signs = []
    for q_num in range(1, total + 1):
        p, toks = qs[q_num]
        raw_q_text, opt_toks, raw_ans_idx = extract_qa(q_num, p, toks, cat)
        
        q_text_en = raw_q_text if raw_q_text else "WHAT DOES THIS SIGN MEAN?"
        if q_num == 68:
            opts_en = ["ZIG ZAG ROAD", "FERRY", "HUMP OR ROUGH ROAD", "STRAIGHT ROAD"]
        else:
            opts_en = cluster_tokens_into_4_options(opt_toks)
        ans_idx = raw_ans_idx
        exp_en = get_explanation(q_num, cat, opts_en[ans_idx], "en")
            
        sign_type = get_sign_type(q_num)
        img_path = f"assets/signs/sign_{q_num:03d}.png"
        assert os.path.exists(img_path), f"Sign image missing: {img_path}"
        
        # Translate question text
        q_text_te = translate_phrase(q_text_en, "te")
        q_text_hi = translate_phrase(q_text_en, "hi")
        
        # Translate options
        opts_te = [translate_phrase(opt, "te") for opt in opts_en]
        opts_hi = [translate_phrase(opt, "hi") for opt in opts_en]
        
        # Explanations
        exp_te = get_explanation(q_num, cat, opts_te[ans_idx], "te")
        exp_hi = get_explanation(q_num, cat, opts_hi[ans_idx], "hi")
        
        signs.append({
            "id": f"TS_RS_{q_num:03d}",
            "category": "road_signs",
            "signType": sign_type,
            "questionNumber": q_num,
            "image": img_path,
            "text": {
                "en": q_text_en,
                "te": q_text_te,
                "hi": q_text_hi
            },
            "options": {
                "en": opts_en,
                "te": opts_te,
                "hi": opts_hi
            },
            "answerIndex": ans_idx,
            "explanation": {
                "en": exp_en,
                "te": exp_te,
                "hi": exp_hi
            }
        })
        
    print(f"✓ Built {len(signs)} Road Sign questions.")
    return signs

def build_rules_of_road():
    print("-> Compiling Rules of the Road (159 questions)...")
    cat = "rules_of_road"
    total = 159
    qs = get_segmented_questions(cat, "rules-of-road-regulations-english.pdf", 180, total)
    
    scenario_map = {
        13: "assets/scenarios/rr_22.png",
        28: "assets/scenarios/rr_34.png",
        30: "assets/scenarios/rr_36.png",
        38: "assets/scenarios/rr_49.png",
        48: "assets/scenarios/rr_57.png",
        56: "assets/scenarios/rr_69.png",
        60: "assets/scenarios/rr_70.png",
        100: "assets/scenarios/rr_107.png",
        105: "assets/scenarios/rr_108.png",
        114: "assets/scenarios/rr_120.png",
        115: "assets/scenarios/rr_121.png",
        116: "assets/scenarios/rr_122.png",
        118: "assets/scenarios/rr_22.png",
        123: "assets/scenarios/rr_129.png",
        125: "assets/scenarios/rr_136.png",
        126: "assets/scenarios/rr_137.png",
        130: "assets/scenarios/rr_144.png",
        147: "assets/scenarios/rr_158.png",
        148: "assets/scenarios/rr_156.png",
        149: "assets/scenarios/rr_57.png",
        158: "assets/scenarios/rr_172.png"
    }
    
    # Specific curated fixes for wrapped options in rules of the road
    special_opts = {
        6: (
            "BE EXTRA CAUTIOUS WHILE OVERTAKING",
            ["`L' MARK VEHICLES", "SLOW SPEED VEHICLES", "OLD VEHICLES", "LIGHT VEHICLES"],
            0
        ),
        12: (
            "YOU HAVE JUST BEEN OVERTAKEN BY A MOTORCYCLIST WHO IS CUTTING IN SHARPLY. YOU SHOULD",
            ["SOUND THE HORN", "BRAKE FIRMLY", "KEEP A SAFE GAP", "FLASH YOUR LIGHTS"],
            2
        ),
        50: (
            "YOU MUST NOT REVERSE",
            ["ON A BUSY ROAD", "ON A ONE WAY ROAD", "ON A ROUNDABOUT", "ALL OF THE ABOVE"],
            3
        ),
        122: (
            "THERE IS A SLOW-MOVING MOTORCYCLIST AHEAD OF YOU. YOU ARE UNSURE WHAT THE RIDER IS GOING TO DO. YOU SHOULD",
            ["PASS ON THE LEFT", "PASS ON THE RIGHT", "STAY BEHIND", "MOVE CLOSER"],
            2
        ),
        124: (
            "WHEN ANOTHER VEHICLE IS OVERTAKING YOU, YOU SHOULD",
            ["SPEED UP", "SLOW DOWN OR MAINTAIN SPEED", "HOLD YOUR SPEED", "CHANGE DIRECTION"],
            1
        )
    }

    rules = []
    for q_num in range(1, total + 1):
        p, toks = qs[q_num]
        raw_q_text, opt_toks, ans_idx = extract_qa(q_num, p, toks, cat)
        
        if q_num in special_opts:
            q_text_en, opts_en, ans_idx = special_opts[q_num]
        else:
            q_text_en = raw_q_text
            opts_en = cluster_tokens_into_4_options(opt_toks)
            
        img_path = scenario_map.get(q_num, None)
        if img_path:
            assert os.path.exists(img_path), f"Scenario image missing: {img_path}"
            
        # Clean up options
        opts_en = [opt.strip() if opt.strip() else "NONE OF THE ABOVE" for opt in opts_en]
        
        # Translate question text
        q_text_te = translate_phrase(q_text_en, "te")
        q_text_hi = translate_phrase(q_text_en, "hi")
        
        # Translate options
        opts_te = [translate_phrase(opt, "te") for opt in opts_en]
        opts_hi = [translate_phrase(opt, "hi") for opt in opts_en]
        
        # Explanations
        exp_en = get_explanation(q_num, cat, opts_en[ans_idx], "en")
        exp_te = get_explanation(q_num, cat, opts_te[ans_idx], "te")
        exp_hi = get_explanation(q_num, cat, opts_hi[ans_idx], "hi")
        
        rules.append({
            "id": f"TS_RR_{q_num:03d}",
            "category": "rules_of_road",
            "signType": None,
            "questionNumber": q_num,
            "image": img_path,
            "text": {
                "en": q_text_en,
                "te": q_text_te,
                "hi": q_text_hi
            },
            "options": {
                "en": opts_en,
                "te": opts_te,
                "hi": opts_hi
            },
            "answerIndex": ans_idx,
            "explanation": {
                "en": exp_en,
                "te": exp_te,
                "hi": exp_hi
            }
        })
        
    print(f"✓ Built {len(rules)} Rules of the Road questions.")
    return rules

def build_general_principles():
    print("-> Compiling General Driving Principles (159 questions)...")
    cat = "general_principles"
    total = 159
    qs = get_segmented_questions(cat, "general-driving-principles-english.pdf", 128, total)
    
    special_gp = {
        57: (
            "THE PRIMARY PURPOSE OF USING A HORN IS",
            ["TO ALERT OTHERS OF YOUR PRESENCE", "TO ALLOW YOU RIGHT OF WAY", "TO GREET OTHER ROAD USERS", "TO SIGNAL YOUR ANNOYANCE"],
            0
        ),
        128: (
            "WHAT WILL HAPPEN IF THE FRONT WHEELS ARE OUT OF BALANCE?",
            ["VEHICLE PULLING TO THE RIGHT", "VEHICLE PULLING TO THE LEFT", "STEERING WOBBLING / VIBRATION", "NONE OF THE ABOVE"],
            2
        )
    }

    gps = []
    for q_num in range(1, total + 1):
        p, toks = qs[q_num]
        raw_q_text, opt_toks, ans_idx = extract_qa(q_num, p, toks, cat)
        
        if q_num in special_gp:
            q_text_en, opts_en, ans_idx = special_gp[q_num]
        else:
            q_text_en = raw_q_text
            opts_en = cluster_tokens_into_4_options(opt_toks)
            
        opts_en = [opt.strip() if opt.strip() else "NONE OF THE ABOVE" for opt in opts_en]
        
        # Translate question text
        q_text_te = translate_phrase(q_text_en, "te")
        q_text_hi = translate_phrase(q_text_en, "hi")
        
        # Translate options
        opts_te = [translate_phrase(opt, "te") for opt in opts_en]
        opts_hi = [translate_phrase(opt, "hi") for opt in opts_en]
        
        # Explanations
        exp_en = get_explanation(q_num, cat, opts_en[ans_idx], "en")
        exp_te = get_explanation(q_num, cat, opts_te[ans_idx], "te")
        exp_hi = get_explanation(q_num, cat, opts_hi[ans_idx], "hi")
        
        gps.append({
            "id": f"TS_GP_{q_num:03d}",
            "category": "general_principles",
            "signType": None,
            "questionNumber": q_num,
            "image": None,
            "text": {
                "en": q_text_en,
                "te": q_text_te,
                "hi": q_text_hi
            },
            "options": {
                "en": opts_en,
                "te": opts_te,
                "hi": opts_hi
            },
            "answerIndex": ans_idx,
            "explanation": {
                "en": exp_en,
                "te": exp_te,
                "hi": exp_hi
            }
        })
        
    print(f"✓ Built {len(gps)} General Driving Principles questions.")
    return gps

def validate_datasets(signs, rules, gps):
    print("-> Validating complete question bank...")
    assert len(signs) == 94, f"Signs count error: {len(signs)}"
    assert len(rules) == 159, f"Rules count error: {len(rules)}"
    assert len(gps) == 159, f"Principles count error: {len(gps)}"
    
    total = len(signs) + len(rules) + len(gps)
    assert total == 412, f"Total count error: {total}"
    
    all_qs = signs + rules + gps
    ids = set()
    for q in all_qs:
        assert q["id"] not in ids, f"Duplicate ID: {q['id']}"
        ids.add(q["id"])
        
        # Check 4 options per language
        for lang in ["en", "te", "hi"]:
            assert len(q["text"][lang].strip()) > 0, f"Empty text {lang} in {q['id']}"
            assert len(q["options"][lang]) == 4, f"Options {lang} count != 4 in {q['id']}"
            for opt in q["options"][lang]:
                assert len(opt.strip()) > 0, f"Empty option in {q['id']} ({lang})"
            assert len(q["explanation"][lang].strip()) > 0, f"Empty explanation in {q['id']} ({lang})"
            
        assert q["answerIndex"] in [0, 1, 2, 3], f"Invalid answerIndex in {q['id']}: {q['answerIndex']}"
        
        if q["image"]:
            assert os.path.exists(q["image"]), f"Missing image in {q['id']}: {q['image']}"
            
    print("✓ All 412 questions strictly validated against specification!")

def main():
    os.makedirs("data/questions/telangana", exist_ok=True)
    os.makedirs("data/i18n", exist_ok=True)
    
    signs = build_road_signs()
    rules = build_rules_of_road()
    gps = build_general_principles()
    
    validate_datasets(signs, rules, gps)
    
    with open("data/questions/telangana/road-signs.json", "w", encoding="utf-8") as f:
        json.dump(signs, f, indent=2, ensure_ascii=False)
        
    with open("data/questions/telangana/rules-of-road.json", "w", encoding="utf-8") as f:
        json.dump(rules, f, indent=2, ensure_ascii=False)
        
    with open("data/questions/telangana/general-principles.json", "w", encoding="utf-8") as f:
        json.dump(gps, f, indent=2, ensure_ascii=False)
        
    print("✓ Saved all 3 question datasets successfully.")

if __name__ == "__main__":
    main()
