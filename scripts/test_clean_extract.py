import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, decode_stream, get_page_contents

def extract_category_clean(pdf_path, cmap_obj, total_count):
    with open(pdf_path, "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, cmap_obj))
    pages = get_page_contents(pdf)
    
    questions = {}
    
    for p_num, (p_id, c_id) in enumerate(pages, 1):
        stream = get_obj_stream(pdf, c_id)
        elems = decode_stream(stream, cmap)
        
        # Filter table header
        filtered = []
        for x, y, t in elems:
            if t in ["S.NO.QUESTIONS", "RELEVANT FIGURE/SIGN", "IF ANY", "OPTION1OPTION2OPTION3OPTION4", "ANSWER", "OPTION", "12", "S", "34567"]:
                continue
            filtered.append((x, y, t))
            
        # On each page, question numbers are distinct integers from 1..total_count
        # that appear at the beginning of rows
        i = 0
        n = len(filtered)
        while i < n:
            x, y, t = filtered[i]
            # Match question number: either standalone digits or digits followed by text
            m = re.match(r"^(\d{1,3})(.*)$", t)
            if m:
                try:
                    val = int(m.group(1))
                except:
                    val = None
                # Check if val is the next expected question or a valid question number
                if val and 1 <= val <= total_count and val not in questions:
                    # To verify it is a question number and not an answer digit,
                    # look ahead: does it have question text / options following it?
                    q_num = val
                    rest = m.group(2).strip()
                    collected = []
                    if rest:
                        collected.append(rest)
                    j = i + 1
                    while j < n:
                        next_x, next_y, next_t = filtered[j]
                        m_next = re.match(r"^(\d{1,3})(.*)$", next_t)
                        if m_next:
                            try:
                                next_val = int(m_next.group(1))
                                if next_val == q_num + 1:
                                    break
                            except:
                                pass
                        collected.append(next_t)
                        j += 1
                    questions[q_num] = (p_num, collected)
                    i = j - 1
            i += 1
            
    print(f"[{pdf_path}] Extracted: {len(questions)} / {total_count}")
    missing = [q for q in range(1, total_count + 1) if q not in questions]
    if missing:
        print(f"Missing: {missing}")
    return questions

def main():
    q_rules = extract_category_clean("rules-of-road-regulations-english.pdf", 180, 159)
    q_gp = extract_category_clean("general-driving-principles-english.pdf", 128, 159)

if __name__ == "__main__":
    main()
