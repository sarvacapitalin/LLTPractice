import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, decode_stream, get_page_contents

def extract_general_principles():
    with open("general-driving-principles-english.pdf", "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, 128))
    pages = get_page_contents(pdf)
    
    all_elements = []
    for p_idx, (p_id, c_id) in enumerate(pages):
        stream = get_obj_stream(pdf, c_id)
        elems = decode_stream(stream, cmap)
        all_elements.append((p_idx + 1, elems))
        
    found_questions = {}
    for p_num, elems in all_elements:
        for idx, (x, y, text) in enumerate(elems):
            m = re.match(r"^(\d{1,3})(?:$|\s+|(?=[A-Za-z]))", text)
            if m:
                q_num = int(m.group(1))
                if 1 <= q_num <= 159 and q_num not in found_questions:
                    found_questions[q_num] = (p_num, idx, x, y, text)
                    
    print(f"Total question numbers located: {len(found_questions)} / 159")
    missing = [i for i in range(1, 160) if i not in found_questions]
    if missing:
        print(f"Missing question numbers: {missing}")
    else:
        print("All 159 question numbers found!")

if __name__ == "__main__":
    extract_general_principles()
