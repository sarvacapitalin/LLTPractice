import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, decode_stream, get_page_contents

def extract_all_road_signs():
    with open("road-signs-english.pdf", "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, 299))
    pages = get_page_contents(pdf)
    
    print(f"Total pages in road-signs-english.pdf: {len(pages)}")
    
    all_elems = []
    for p_idx, (p_id, c_id) in enumerate(pages):
        stream = get_obj_stream(pdf, c_id)
        elems = decode_stream(stream, cmap)
        all_elems.append((p_idx + 1, elems))
        
    # Let us inspect the text elements on each page
    extracted = []
    for p_num, elems in all_elements if 'all_elements' in locals() else all_elems:
        for x, y, text in elems:
            extracted.append((p_num, x, y, text))
            
    print(f"Total elements extracted: {len(extracted)}")
    # Print sample from page 1 and page 2
    for item in extracted[:30]:
        print(f"P{item[0]} ({item[1]:6.2f}, {item[2]:6.2f}): {item[3]}")

if __name__ == "__main__":
    extract_all_road_signs()
