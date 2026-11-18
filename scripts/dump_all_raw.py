import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, decode_stream, get_page_contents

def extract_category(pdf_path, cmap_obj, total_count, out_path):
    with open(pdf_path, "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, cmap_obj))
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
        
    results = {}
    for p_num, elems in all_elements:
        i = 0
        n = len(elems)
        while i < n:
            x, y, t = elems[i]
            # Match number at start
            m = re.match(r"^(\d{1,3})(.*)$", t)
            if m:
                try:
                    q_num = int(m.group(1))
                except:
                    q_num = None
                if q_num and 1 <= q_num <= total_count and q_num not in results:
                    q_list = []
                    if m.group(2).strip():
                        q_list.append(m.group(2).strip())
                    j = i + 1
                    while j < n:
                        next_t = elems[j][2]
                        m_next = re.match(r"^(\d{1,3})(.*)$", next_t)
                        if m_next:
                            try:
                                next_num = int(m_next.group(1))
                                if 1 <= next_num <= total_count and (next_num == q_num + 1 or next_num > q_num):
                                    break
                            except:
                                pass
                        q_list.append(next_t)
                        j += 1
                    results[q_num] = (p_num, q_list)
                    i = j - 1
            i += 1
            
    print(f"[{pdf_path}] Extracted {len(results)} / {total_count} questions.")
    missing = [q for q in range(1, total_count + 1) if q not in results]
    if missing:
        print(f"Missing in {pdf_path}: {missing}")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)

def main():
    extract_category("rules-of-road-regulations-english.pdf", 180, 159, "scripts/rules_extracted_raw.json")
    extract_category("general-driving-principles-english.pdf", 128, 159, "scripts/principles_extracted_raw.json")

if __name__ == "__main__":
    main()
