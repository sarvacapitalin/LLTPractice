#!/usr/bin/env python3
"""
scripts/rebuild_rules_and_gp_clean.py

End-to-end audit and clean rebuild of:
1. data/questions/telangana/rules-of-road.json (159 questions)
2. data/questions/telangana/general-principles.json (159 questions)

Uses robust PDF stream parsing, exact coordinate column separation,
official answer keys, and trilingual translation.
"""

import os, sys, re, json
from scripts.test_robust_extractor import decode_stream_robust
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, get_page_contents
from scripts.verify_answers import get_official_pdf_answers
from scripts.translator import translate_phrase, get_explanation

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_JSON_PATH = os.path.join(WORKSPACE_ROOT, "data", "questions", "telangana", "rules-of-road.json")
GP_JSON_PATH = os.path.join(WORKSPACE_ROOT, "data", "questions", "telangana", "general-principles.json")

SCENARIO_MAP_RULES = {
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

def extract_tokens_from_pdf(pdf_path, cmap_id):
    full_path = os.path.join(WORKSPACE_ROOT, pdf_path)
    with open(full_path, "rb") as f:
        pdf_bytes = f.read()
    cmap = parse_cmap(get_obj_stream(pdf_bytes, cmap_id))
    pages = get_page_contents(pdf_bytes)
    
    all_elems = []
    for p_idx, (p_id, c_id) in enumerate(pages):
        stream = get_obj_stream(pdf_bytes, c_id)
        elems = decode_stream_robust(stream, cmap)
        for x, y, t in elems:
            all_elems.append((p_idx + 1, x, y, t.strip()))
            
    header_words = {
        "S.NO.", "QUESTIONS", "RELEVANT FIGURE/SIGN", "OPTION1", "OPTION2",
        "OPTION3", "OPTION4", "ANSWER", "S.NO.QUESTIONS", "OPTION1OPTION2OPTION3OPTION4",
        "ANSWER ", "IF ANY", "RELEVANT", "FIGURE/SIGN", "S"
    }
    filtered = []
    for p, x, y, t in all_elems:
        if not t or t in header_words:
            continue
        filtered.append((p, x, y, t))
    return filtered

def segment_into_questions(tokens, total_count):
    q_ranges = {}
    current_q = 1
    
    # Custom markers for questions whose number is in same token or special layout
    for i, (p, x, y, t) in enumerate(tokens):
        m = re.match(r"^(\d{1,3})$", t)
        if m:
            num = int(m.group(1))
            if num == current_q:
                q_ranges[current_q] = i
                current_q += 1
                if current_q > total_count:
                    break
        elif t.startswith(str(current_q)) and len(t) > len(str(current_q)):
            # e.g. "128WHAT WILL HAPPEN..."
            q_ranges[current_q] = i
            current_q += 1
            if current_q > total_count:
                break
                
    result = {}
    for q in range(1, total_count + 1):
        if q not in q_ranges:
            continue
        start_idx = q_ranges[q]
        end_idx = q_ranges[q + 1] if q + 1 in q_ranges else len(tokens)
        result[q] = tokens[start_idx:end_idx]
    return result

def parse_question_tokens(q_num, tokens, official_ans, category):
    # tokens[0] is the S.No token (or S.No + start of question)
    first_tok = tokens[0]
    toks = list(tokens)
    
    m = re.match(r"^" + str(q_num) + r"(.*)$", first_tok[3])
    if m and m.group(1).strip():
        # First token had question text attached
        toks[0] = (first_tok[0], first_tok[1], first_tok[2], m.group(1).strip())
    else:
        # First token was just the question number
        toks = toks[1:]
        
    # Remove trailing answer token (digit 1-4)
    if toks and toks[-1][3] in ["1", "2", "3", "4"]:
        toks = toks[:-1]
    elif toks and re.search(r"[1-4]$", toks[-1][3]):
        # e.g. "NONE OF THE ABOVE2"
        last_t = toks[-1][3]
        clean_last = last_t[:-1].strip()
        toks[-1] = (toks[-1][0], toks[-1][1], toks[-1][2], clean_last)
        
    # Filter out figure indicator "0"
    content_toks = [t for t in toks if t[3] != "0"]
    
    # Separate into Question Text vs Options
    # Use column coordinate boundaries
    # Notice: In Rules, Option 1 starts at x >= 350 (no figure) or x >= 550 (with figure)
    # In GP, Option 1 starts at x >= 270
    
    q_words = []
    opt_words = []
    
    if category == "rules_of_road":
        # Check if this question row has figure (options shifted to x > 550)
        has_fig_col = any(t[1] > 550 for t in content_toks) and any(t[1] < 450 for t in content_toks)
        opt_start_x = 550.0 if has_fig_col else 350.0
    else: # general_principles
        opt_start_x = 270.0
        
    for p, x, y, t in content_toks:
        if x < opt_start_x:
            q_words.append(t)
        else:
            opt_words.append((x, y, t))
            
    q_text = " ".join(q_words).strip()
    
    # Clean up question text spacing
    q_text = re.sub(r"\s+", " ", q_text)
    
    # Cluster option words into 4 options based on X coordinate
    if not opt_words:
        options = ["", "", "", ""]
    elif len(opt_words) == 4:
        options = [t[2] for t in opt_words]
    else:
        # Sort by x
        min_x = min(t[0] for t in opt_words)
        max_x = max(t[0] for t in opt_words)
        span = max_x - min_x
        
        if span < 30: # fallback
            k = len(opt_words)
            step = k / 4.0
            options = [" ".join(opt_words[int(round(i*step)):int(round((i+1)*step))][j][2] for j in range(len(opt_words[int(round(i*step)):int(round((i+1)*step))]))) for i in range(4)]
        else:
            # 4 bins
            bins = [[], [], [], []]
            for x, y, t in opt_words:
                col = int(round((x - min_x) / (span / 3.0)))
                col = max(0, min(3, col))
                bins[col].append(t)
            options = [" ".join(b).strip() for b in bins]
            
            # If any bin is empty, fallback to sequential 4-split
            if any(len(o) == 0 for o in options):
                k = len(opt_words)
                step = k / 4.0
                options = []
                for i in range(4):
                    sub = opt_words[int(round(i*step)):int(round((i+1)*step))]
                    options.append(" ".join(t[2] for t in sub).strip())
                    
    # Clean up option texts
    options = [re.sub(r"\s+", " ", opt).strip() for opt in options]
    
    # Zero-based answer index
    ans_idx = official_ans - 1
    
    return q_text, options, ans_idx

def test_dry_run():
    print("Testing extraction dry run...")
    rules_ans, _ = get_official_pdf_answers("rules-of-road-regulations-english.pdf", 180, 159)
    rules_toks = extract_tokens_from_pdf("rules-of-road-regulations-english.pdf", 180)
    rules_qs = segment_into_questions(rules_toks, 159)
    print(f"Segmented {len(rules_qs)} Rules questions.")
    
    gp_ans, _ = get_official_pdf_answers("general-driving-principles-english.pdf", 128, 159, {
        32: "THE MOST EFFECTIVE",
        128: "WHAT WILL HAPPEN",
        144: "ALCOHOL MAY AFFECT",
        150: "BOARDING AND ALIGHTING"
    })
    gp_toks = extract_tokens_from_pdf("general-driving-principles-english.pdf", 128)
    gp_qs = segment_into_questions(gp_toks, 159)
    print(f"Segmented {len(gp_qs)} GP questions.")
    
    # Inspect Q116, Q133, Q156, Q157 in Rules
    for qn in [116, 133, 156, 157]:
        qt, opts, aidx = parse_question_tokens(qn, rules_qs[qn], rules_ans[qn], "rules_of_road")
        print(f"\n--- Rules Q{qn} ---")
        print("  Q:", qt)
        print("  Options:", opts)
        print("  AnswerIndex:", aidx, "->", opts[aidx] if aidx < len(opts) else "ERR")
        
    # Inspect GP Q11, Q14, Q18, Q25, Q32
    for qn in [11, 14, 18, 25, 32]:
        qt, opts, aidx = parse_question_tokens(qn, gp_qs[qn], gp_ans[qn], "general_principles")
        print(f"\n--- GP Q{qn} ---")
        print("  Q:", qt)
        print("  Options:", opts)
        print("  AnswerIndex:", aidx, "->", opts[aidx] if aidx < len(opts) else "ERR")

if __name__ == "__main__":
    test_dry_run()
