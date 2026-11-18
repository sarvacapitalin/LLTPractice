import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, unescape_pdf_bytes, get_page_contents

def extract_elements(pdf_path, cmap_obj):
    with open(pdf_path, 'rb') as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, cmap_obj))
    pages = get_page_contents(pdf)
    
    cmd_pattern = re.compile(
        rb"(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+Tm)|"
        rb"(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+Td)|"
        rb"(?:\[(.*?)\]\s*TJ)|"
        rb"(?:\(((?:[^()\\]|\\.)*)\)\s*Tj)",
        re.DOTALL
    )
    
    all_pages = []
    for p_num, (p_id, c_id) in enumerate(pages, 1):
        stream = get_obj_stream(pdf, c_id)
        tx, ty = 0.0, 0.0
        elements = []
        for match in cmd_pattern.finditer(stream):
            if match.group(1) is not None:
                tx = float(match.group(5))
                ty = float(match.group(6))
            elif match.group(7) is not None:
                tx += float(match.group(7))
                ty += float(match.group(8))
            elif match.group(9) is not None:
                raw_arr = match.group(9)
                i = 0
                n = len(raw_arr)
                current_word = []
                while i < n:
                    if raw_arr[i:i+1] == b'(':
                        i += 1
                        start = i
                        depth = 1
                        while i < n and depth > 0:
                            if raw_arr[i:i+1] == b'\\':
                                i += 2
                                continue
                            if raw_arr[i:i+1] == b'(': depth += 1
                            elif raw_arr[i:i+1] == b')': depth -= 1
                            i += 1
                        s = raw_arr[start:i-1]
                        txt = "".join(cmap.get(b, "") for b in unescape_pdf_bytes(s))
                        current_word.append(txt)
                    elif raw_arr[i:i+1] in b'0123456789-+':
                        start = i
                        while i < n and raw_arr[i:i+1] in b'0123456789-.+':
                            i += 1
                        try:
                            num = float(raw_arr[start:i])
                            if num < -500:
                                w = "".join(current_word).strip()
                                if w:
                                    elements.append((round(tx, 2), round(ty, 2), w))
                                current_word = []
                        except:
                            pass
                    else:
                        i += 1
                w = "".join(current_word).strip()
                if w:
                    elements.append((round(tx, 2), round(ty, 2), w))
            elif match.group(10) is not None:
                raw_str = match.group(10)
                txt = "".join(cmap.get(b, "") for b in unescape_pdf_bytes(raw_str)).strip()
                if txt:
                    elements.append((round(tx, 2), round(ty, 2), txt))
        all_pages.append((p_num, elements))
    return all_pages

def filter_header(elements, p_num):
    filtered = []
    # Ignore initial header rows
    for x, y, t in elements:
        if p_num == 1 and t in ["1", "2", "12"] and y > 280:
            continue
        if t in ["S.NO.", "QUESTIONS", "S.NO.QUESTIONS", "RELEVANT FIGURE/SIGN", "IF ANY",
                 "OPTION1", "OPTION2", "OPTION3", "OPTION4", "OPTION1OPTION2OPTION3OPTION4",
                 "ANSWER", "ANSWER ", "OPTION", "S", "3", "4", "5", "6", "7", "34567"]:
            continue
        filtered.append((x, y, t))
    return filtered

if __name__ == "__main__":
    for name, cid, total in [
        ("road-signs-english.pdf", 299, 94),
        ("rules-of-road-regulations-english.pdf", 180, 159),
        ("general-driving-principles-english.pdf", 128, 159)
    ]:
        pages = extract_elements(name, cid)
        total_tokens = sum(len(filter_header(elems, p)) for p, elems in pages)
        print(f"{name}: {len(pages)} pages, {total_tokens} clean content tokens")
