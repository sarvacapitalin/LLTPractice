from scripts.verify_answers import get_official_pdf_answers
import json, re

def clean_txt(s):
    return re.sub(r'\s+', ' ', s).strip()

def parse_question_tokens(tokens, q_num, ans_digit):
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
            
        # Determine target column
        # Case A: row started at S.NO column (y < 120)
        if y < 120:
            if c_idx == 0:
                if t == str(q_num):
                    continue
                col = 0 # question text on newline
            elif c_idx == 1:
                col = 0 # question text
            elif c_idx == 2:
                col = -1 # Figure/Sign
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
        # Case B: question column continuation (120 <= y < 270)
        elif 120 <= y < 270:
            if c_idx == 0:
                col = 0
            else:
                # c_idx > 0 from question column
                # 0: Q, 1: Fig, 2: Opt1, 3: Opt2, 4: Opt3, 5: Opt4, 6: Ans
                if c_idx == 1: col = -1
                elif c_idx == 2: col = 1
                elif c_idx == 3: col = 2
                elif c_idx == 4: col = 3
                elif c_idx == 5: col = 4
                else: col = 5
        # Case C: options columns (y >= 270)
        elif 270 <= y < 420:
            # starts at Option 1
            # 0: Opt1, 1: Opt2, 2: Opt3, 3: Opt4, 4: Ans
            col = 1 + c_idx
        elif 420 <= y < 500:
            col = 2 + c_idx
        elif 500 <= y < 580:
            col = 3 + c_idx
        elif 580 <= y < 670:
            col = 4 + c_idx
        else:
            col = 5 # Answer
            
        if col == 0:
            if not q_text_parts or q_text_parts[-1] != t:
                q_text_parts.append(t)
        elif 1 <= col <= 4:
            if not options[col] or options[col][-1] != t:
                options[col].append(t)
        elif col == 5:
            ans_tokens.append(t)
            
    q_text = clean_txt(' '.join(q_text_parts))
    if q_text.startswith(str(q_num)):
        q_text = q_text[len(str(q_num)):].strip()
    if q_text.startswith('0') and len(q_text) > 1 and not q_text[1].isdigit():
        q_text = q_text[1:].strip()
        
    opts = [clean_txt(' '.join(options[i])) for i in range(1, 5)]
    
    return q_text, opts, ans_digit - 1

# Test on road signs
ans_signs, det_signs = get_official_pdf_answers('road-signs-english.pdf', 299, 94)
for q in range(1, 20):
    q_text, opts, ans_idx = parse_question_tokens(det_signs[q]['tokens'], q, ans_signs[q])
    print(f"Q{q}: '{q_text}' (Ans: {ans_idx})")
    for i, o in enumerate(opts):
        print(f"   [{i}] '{o}'")
