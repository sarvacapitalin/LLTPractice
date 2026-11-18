import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, decode_stream, get_page_contents

def extract_monotonic_dataset(pdf_path, cmap_obj, total_count, unlabeled_starts=None):
    if unlabeled_starts is None:
        unlabeled_starts = {}
        
    with open(pdf_path, "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, cmap_obj))
    pages = get_page_contents(pdf)
    
    questions = {}
    expected_q = 1
    
    for p_num, (p_id, c_id) in enumerate(pages, 1):
        stream = get_obj_stream(pdf, c_id)
        elems = decode_stream(stream, cmap)
        
        i = 0
        n = len(elems)
        while i < n:
            x, y, t = elems[i]
            matched_q = None
            rest = ""
            
            # Check normal number match
            m = re.match(r"^(\d{1,3})(.*)$", t)
            if m:
                val = int(m.group(1))
                if val == expected_q:
                    matched_q = val
                    rest = m.group(2).strip()
            elif expected_q in unlabeled_starts and t.startswith(unlabeled_starts[expected_q]):
                matched_q = expected_q
                rest = t
                
            if matched_q is not None:
                q_num = matched_q
                collected = []
                if rest:
                    collected.append((x, y, rest))
                j = i + 1
                while j < n:
                    next_x, next_y, next_t = elems[j]
                    m_next = re.match(r"^(\d{1,3})(.*)$", next_t)
                    if m_next and int(m_next.group(1)) == q_num + 1:
                        break
                    if (q_num + 1) in unlabeled_starts and next_t.startswith(unlabeled_starts[q_num + 1]):
                        break
                    collected.append((next_x, next_y, next_t))
                    j += 1
                questions[q_num] = {
                    "page": p_num,
                    "elements": collected
                }
                expected_q += 1
                i = j - 1
            i += 1
            
    print(f"[{pdf_path}] Extracted: {len(questions)} / {total_count}")
    return questions

def main():
    signs = extract_monotonic_dataset("road-signs-english.pdf", 299, 94)
    with open("scripts/signs_monotonic.json", "w") as f:
        json.dump(signs, f, indent=2)
        
    rules = extract_monotonic_dataset("rules-of-road-regulations-english.pdf", 180, 159)
    with open("scripts/rules_monotonic.json", "w") as f:
        json.dump(rules, f, indent=2)
        
    gp_unlabeled = {
        32: "THE MOST EFFECTIVE DEVICE FOR",
        128: "WHAT WILL HAPPEN IF THE WHEELS",
        144: "ALCOHOL MAY AFFECT ADVERSELY",
        150: "BOARDING AND ALIGHTING WHILE"
    }
    gp = extract_monotonic_dataset("general-driving-principles-english.pdf", 128, 159, gp_unlabeled)
    with open("scripts/gp_monotonic.json", "w") as f:
        json.dump(gp, f, indent=2)

if __name__ == "__main__":
    main()
