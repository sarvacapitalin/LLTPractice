import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, decode_stream, get_page_contents

def extract_road_signs_full():
    with open("road-signs-english.pdf", "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, 299))
    pages = get_page_contents(pdf)
    
    all_rows = []
    for p_num, (p_id, c_id) in enumerate(pages, 1):
        stream = get_obj_stream(pdf, c_id)
        elems = decode_stream(stream, cmap)
        # Filter out table headers
        filtered = []
        for x, y, t in elems:
            if t in ["S.NO.QUESTIONS", "RELEVANT FIGURE/SIGN", "IF ANY", "OPTION1OPTION2OPTION3OPTION4", "ANSWER", "OPTION", "12", "S", "34567"]:
                continue
            filtered.append((x, y, t))
        all_rows.append((p_num, filtered))
        
    print(f"Loaded {len(all_rows)} pages of road signs.")
    
    # Locate all questions by tracking question numbers 1..94
    questions = {}
    for p_num, elems in all_rows:
        i = 0
        n = len(elems)
        while i < n:
            x, y, t = elems[i]
            # Check for question number
            m = re.match(r"^(\d{1,2})(.*)$", t)
            if m:
                q_num = int(m.group(1))
                if 1 <= q_num <= 94 and q_num not in questions:
                    # Gather elements belonging to this question until next question number
                    q_elems = []
                    # group 2 might have initial text
                    if m.group(2).strip():
                        q_elems.append((x, y, m.group(2).strip()))
                    j = i + 1
                    while j < n:
                        next_t = elems[j][2]
                        m_next = re.match(r"^(\d{1,2})(.*)$", next_t)
                        if m_next and 1 <= int(m_next.group(1)) <= 94 and int(m_next.group(1)) == q_num + 1:
                            break
                        q_elems.append(elems[j])
                        j += 1
                    questions[q_num] = (p_num, q_elems)
                    i = j - 1
            i += 1
            
    print(f"Total questions segmented: {len(questions)} / 94")
    missing = [q for q in range(1, 95) if q not in questions]
    if missing:
        print(f"Missing signs questions: {missing}")
    else:
        print("All 94 road sign questions segmented successfully!")
        
    # Print sample of Q1 and Q2
    for q in [1, 2, 10, 94]:
        if q in questions:
            print(f"\n--- Question {q} (Page {questions[q][0]}) ---")
            for item in questions[q][1]:
                print(f"  ({item[0]:6.2f}, {item[1]:6.2f}): {item[2]}")

if __name__ == "__main__":
    extract_road_signs_full()
