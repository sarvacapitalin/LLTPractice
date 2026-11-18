import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, decode_stream, get_page_contents

def extract_rules_of_road_full():
    with open("rules-of-road-regulations-english.pdf", "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, 180))
    pages = get_page_contents(pdf)
    
    all_rows = []
    for p_num, (p_id, c_id) in enumerate(pages, 1):
        stream = get_obj_stream(pdf, c_id)
        elems = decode_stream(stream, cmap)
        filtered = []
        for x, y, t in elems:
            if t in ["S.NO.QUESTIONS", "RELEVANT FIGURE/SIGN", "IF ANY", "OPTION1OPTION2OPTION3OPTION4", "ANSWER", "OPTION", "12", "S", "34567"]:
                continue
            filtered.append((x, y, t))
        all_rows.append((p_num, filtered))
        
    print(f"Loaded {len(all_rows)} pages of rules of the road.")
    
    questions = {}
    for p_num, elems in all_rows:
        i = 0
        n = len(elems)
        while i < n:
            x, y, t = elems[i]
            m = re.match(r"^(\d{1,3})(.*)$", t)
            if m:
                q_num = int(m.group(1))
                if 1 <= q_num <= 159 and q_num not in questions:
                    q_elems = []
                    if m.group(2).strip():
                        q_elems.append((x, y, m.group(2).strip()))
                    j = i + 1
                    while j < n:
                        next_t = elems[j][2]
                        m_next = re.match(r"^(\d{1,3})(.*)$", next_t)
                        if m_next and 1 <= int(m_next.group(1)) <= 159 and int(m_next.group(1)) == q_num + 1:
                            break
                        q_elems.append(elems[j])
                        j += 1
                    questions[q_num] = (p_num, q_elems)
                    i = j - 1
            i += 1
            
    print(f"Total questions segmented: {len(questions)} / 159")
    missing = [q for q in range(1, 160) if q not in questions]
    if missing:
        print(f"Missing rules questions: {missing}")
    else:
        print("All 159 rules of road questions segmented successfully!")
        
    for q in [1, 50, 100, 159]:
        if q in questions:
            print(f"\n--- Question {q} (Page {questions[q][0]}) ---")
            for item in questions[q][1]:
                print(f"  ({item[0]:6.2f}, {item[1]:6.2f}): {item[2]}")

if __name__ == "__main__":
    extract_rules_of_road_full()
