from scripts.test_cell_extractor import extract_pdf_cells
from scripts.verify_answers import get_official_pdf_answers
import json, re

ans_signs, det_signs = get_official_pdf_answers('road-signs-english.pdf', 299, 94)

def clean_txt(s):
    return re.sub(r'\s+', ' ', s).strip()

# Let's inspect how options and questions are extracted for each sign
extracted_signs = []
for q_num in range(1, 95):
    q_det = det_signs[q_num]
    ans_digit = q_det['chosen'] # 1, 2, 3, 4
    ans_idx = ans_digit - 1
    
    tokens = q_det['tokens'] # list of (y, c_idx, text)
    # y ranges:
    # 70-95: S.NO
    # 95-245: Question text
    # 245-288: Sign/Figure (S)
    # 288-425: Option 1
    # 425-510: Option 2
    # 510-595: Option 3
    # 595-685: Option 4
    # >=685: Answer
    
    # Or if c_idx > 0 from a single row:
    # Let's group by column:
    # Col 0 (Q text): y < 270 and text != str(q_num)
    # If a row has c_idx:
    
    q_text_parts = []
    opt1_parts = []
    opt2_parts = []
    opt3_parts = []
    opt4_parts = []
    
    for y, c_idx, t in tokens:
        t = t.strip()
        if not t:
            continue
        if 70 <= y <= 95 and c_idx == 0 and t == str(q_num):
            continue
        if y >= 680 and t == str(ans_digit):
            continue
        if c_idx > 0 and t == str(ans_digit) and (y >= 595 or c_idx >= 4):
            continue
            
        # Classify by Y and c_idx
        if c_idx == 0:
            if y < 270:
                q_text_parts.append(t)
            elif 270 <= y < 425:
                opt1_parts.append(t)
            elif 425 <= y < 510:
                opt2_parts.append(t)
            elif 510 <= y < 595:
                opt3_parts.append(t)
            elif 595 <= y < 685:
                opt4_parts.append(t)
        else:
            # c_idx > 0 means horizontal column jump in TJ!
            # Could be:
            # 0: S or Q, 1: Opt1, 2: Opt2, 3: Opt3, 4: Opt4, 5: Ans
            # Or if starting from Opt1: 0: Opt1, 1: Opt2, 2: Opt3, 3: Opt4, 4: Ans
            pass
            
    extracted_signs.append({
        'q_num': q_num,
        'ans': ans_digit,
        'q_text': ' '.join(q_text_parts),
        'opt1': ' '.join(opt1_parts),
        'opt2': ' '.join(opt2_parts),
        'opt3': ' '.join(opt3_parts),
        'opt4': ' '.join(opt4_parts),
    })

print("Sample extracted signs:")
for s in extracted_signs[:12]:
    print(f"Q{s['q_num']} (Ans {s['ans']}): Q: '{s['q_text']}'")
    print(f"  1: '{s['opt1']}'")
    print(f"  2: '{s['opt2']}'")
    print(f"  3: '{s['opt3']}'")
    print(f"  4: '{s['opt4']}'")
