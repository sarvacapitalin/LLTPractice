#!/usr/bin/env python3
"""
scripts/build_clean_datasets_v2.py

Robust extractor for Rules of the Road (159) and General Principles (159).
Handles multi-line questions, multi-line options, scenario images,
official government answer keys, and trilingual translations.
"""

import os, sys, re, json
from scripts.test_robust_extractor import decode_stream_robust
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, get_page_contents
from scripts.verify_answers import get_official_pdf_answers
from scripts.translator import translate_phrase, get_explanation

WORKSPACE_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def extract_clean_stream(pdf_filename, cmap_id, header_len):
    pdf_path = os.path.join(WORKSPACE_ROOT, pdf_filename)
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()
    cmap = parse_cmap(get_obj_stream(pdf_bytes, cmap_id))
    pages = get_page_contents(pdf_bytes)
    
    all_elems = []
    for p_idx, (p_id, c_id) in enumerate(pages):
        raw = decode_stream_robust(get_obj_stream(pdf_bytes, c_id), cmap)
        cur = raw[header_len:] if p_idx == 0 else raw
        for x, y, t in cur:
            all_elems.append((p_idx + 1, x, y, t.strip()))
            
    header_words = {
        "S.NO.", "QUESTIONS", "RELEVANT FIGURE/SIGN", "OPTION1", "OPTION2",
        "OPTION3", "OPTION4", "ANSWER", "S.NO.QUESTIONS", "OPTION1OPTION2OPTION3OPTION4",
        "ANSWER ", "IF ANY", "RELEVANT", "FIGURE/SIGN", "S"
    }
    filtered = [e for e in all_elems if e[3] and e[3] not in header_words]
    return filtered

def segment_questions(tokens, total):
    q_ranges = {}
    current_q = 1
    for i, (p, x, y, t) in enumerate(tokens):
        m = re.match(r"^(\d{1,3})$", t)
        if m and int(m.group(1)) == current_q:
            q_ranges[current_q] = i
            current_q += 1
            if current_q > total: break
        elif t.startswith(str(current_q)) and len(t) > len(str(current_q)):
            q_ranges[current_q] = i
            current_q += 1
            if current_q > total: break
            
    assert len(q_ranges) == total, f"Only found {len(q_ranges)} / {total} questions!"
    return q_ranges

def cluster_options_robust(opt_toks):
    if not opt_toks:
        return ["", "", "", ""]
    if len(opt_toks) == 4:
        return [t[2] for t in opt_toks]
        
    # Cluster tokens by X coordinate
    # Find distinct columns
    min_x = min(t[0] for t in opt_toks)
    max_x = max(t[0] for t in opt_toks)
    span = max_x - min_x
    
    if span < 30: # fallback
        k = len(opt_toks)
        step = k / 4.0
        return [" ".join(opt_toks[int(round(i*step)):int(round((i+1)*step))][j][2] for j in range(len(opt_toks[int(round(i*step)):int(round((i+1)*step))]))) for i in range(4)]
        
    bins = [[], [], [], []]
    for x, y, t in opt_toks:
        col = int(round((x - min_x) / (span / 3.0)))
        col = max(0, min(3, col))
        bins[col].append(t)
        
    res = [" ".join(b).strip() for b in bins]
    if any(len(o) == 0 for o in res):
        # Fallback to sequential 4-split
        k = len(opt_toks)
        step = k / 4.0
        res = []
        for i in range(4):
            sub = opt_toks[int(round(i*step)):int(round((i+1)*step))]
            res.append(" ".join(t[2] for t in sub).strip())
    return [re.sub(r"\s+", " ", o).strip() for o in res]

if __name__ == "__main__":
    print("Testing stream extraction...")
    rules_toks = extract_clean_stream("rules-of-road-regulations-english.pdf", 180, 18)
    rules_qr = segment_questions(rules_toks, 159)
    print(f"Rules tokens: {len(rules_toks)}, questions: {len(rules_qr)}")
    
    gp_toks = extract_clean_stream("general-driving-principles-english.pdf", 128, 19)
    gp_qr = segment_questions(gp_toks, 159)
    print(f"GP tokens: {len(gp_toks)}, questions: {len(gp_qr)}")
