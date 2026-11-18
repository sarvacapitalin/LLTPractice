from scripts.verify_answers import get_official_pdf_answers
import json, re

def clean_txt(s):
    return re.sub(r'\s+', ' ', s).strip()

def parse_question_tokens_category(tokens, q_num, ans_digit, category):
    q_text_parts = []
    options = {1: [], 2: [], 3: [], 4: []}
    ans_tokens = []
    
    for y, c_idx, t in tokens:
        t = t.strip()
        if not t:
            continue
            
        # Ignore Question number in col 1
        if 70 <= y <= 95 and c_idx == 0 and t == str(q_num):
            continue
            
        # If starting at y < 120:
        if y < 120:
            if c_idx == 0:
                if t == str(q_num): continue
                col = 0
            elif c_idx == 1:
                col = 0
            elif c_idx == 2:
                col = -1 # Figure
            elif c_idx == 3:
                col = 1
            elif c_idx == 4:
                col = 2
            elif c_idx == 5:
                col = 3
            elif c_idx == 6:
                col = 4
            else:
                col = 5
        elif 120 <= y < (250 if category == 'general_principles' else 310):
            if c_idx == 0:
                col = 0
            elif c_idx == 1:
                col = -1 # Figure
            else:
                col = c_idx - 1 # e.g. c=2 -> col 1
        else:
            # Options area
            if category == 'general_principles':
                if y < 330: base_col = 1
                elif y < 430: base_col = 2
                elif y < 530: base_col = 3
                elif y < 640: base_col = 4
                else: base_col = 5
            else:
                if y < 390: base_col = 1
                elif y < 475: base_col = 2
                elif y < 560: base_col = 3
                elif y < 650: base_col = 4
                else: base_col = 5
            col = base_col + c_idx
            
        if col == 0:
            if not q_text_parts or q_text_parts[-1] != t:
                q_text_parts.append(t)
        elif 1 <= col <= 4:
            if not options[col] or options[col][-1] != t:
                options[col].append(t)
        else:
            ans_tokens.append(t)
            
    q_text = clean_txt(' '.join(q_text_parts))
    if q_text.startswith(str(q_num)):
        q_text = q_text[len(str(q_num)):].strip()
    if q_text.startswith('0') and len(q_text) > 1 and not q_text[1].isdigit():
        q_text = q_text[1:].strip()
        
    opts = [clean_txt(' '.join(options[i])) for i in range(1, 5)]
    
    return q_text, opts, ans_digit - 1

for name, cid, total, missing, cat in [
    ('road-signs-english.pdf', 299, 94, {}, 'road_signs'),
    ('rules-of-road-regulations-english.pdf', 180, 159, {}, 'rules_of_road'),
    ('general-driving-principles-english.pdf', 128, 159, {
        32: "THE MOST EFFECTIVE DEVICE FOR",
        128: "WHAT WILL HAPPEN IF THE WHEELS",
        144: "ALCOHOL MAY AFFECT ADVERSELY",
        150: "BOARDING AND ALIGHTING WHILE"
    }, 'general_principles')
]:
    ans_dict, det_dict = get_official_pdf_answers(name, cid, total, missing)
    empty_q = []
    empty_opt = []
    for q in range(1, total + 1):
        q_text, opts, ans_idx = parse_question_tokens_category(det_dict[q]['tokens'], q, ans_dict[q], cat)
        if not q_text:
            empty_q.append(q)
        for i, o in enumerate(opts):
            if not o:
                empty_opt.append((q, i))
    print(f"{cat}: Empty Qs: {len(empty_q)} {empty_q}, Empty Opts: {len(empty_opt)} {empty_opt}")
