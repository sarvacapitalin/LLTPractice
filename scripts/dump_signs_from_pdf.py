import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, decode_stream, get_page_contents

def clean_text(t):
    t = re.sub(r"\s+", " ", t).strip()
    return t

def parse_all_signs():
    with open("road-signs-english.pdf", "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, 299))
    pages = get_page_contents(pdf)
    
    all_elements = []
    for p_num, (p_id, c_id) in enumerate(pages, 1):
        stream = get_obj_stream(pdf, c_id)
        elems = decode_stream(stream, cmap)
        filtered = []
        for x, y, t in elems:
            if t in ["S.NO.QUESTIONS", "RELEVANT FIGURE/SIGN", "IF ANY", "OPTION1OPTION2OPTION3OPTION4", "ANSWER", "OPTION", "12", "S", "34567"]:
                continue
            filtered.append((x, y, t))
        all_elements.append((p_num, filtered))
        
    # We will build a structured dictionary of question data
    results = {}
    for p_num, elems in all_elements:
        i = 0
        n = len(elems)
        while i < n:
            x, y, t = elems[i]
            m = re.match(r"^(\d{1,2})(.*)$", t)
            if m:
                q_num = int(m.group(1))
                if 1 <= q_num <= 94 and q_num not in results:
                    q_list = []
                    if m.group(2).strip():
                        q_list.append(m.group(2).strip())
                    j = i + 1
                    while j < n:
                        next_t = elems[j][2]
                        m_next = re.match(r"^(\d{1,2})(.*)$", next_t)
                        if m_next and 1 <= int(m_next.group(1)) <= 94 and int(m_next.group(1)) == q_num + 1:
                            break
                        q_list.append(next_t)
                        j += 1
                    results[q_num] = (p_num, q_list)
                    i = j - 1
            i += 1
            
    print(f"Extracted {len(results)} signs from PDF.")
    with open("scripts/signs_extracted_raw.json", "w") as f:
        json.dump(results, f, indent=2)
    print("Saved to scripts/signs_extracted_raw.json")

if __name__ == "__main__":
    parse_all_signs()
