import re
import zlib
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, unescape_pdf_bytes, get_page_contents

def extract_pdf_cells(pdf_path, cmap_id):
    with open(pdf_path, 'rb') as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, cmap_id))
    pages = get_page_contents(pdf)
    
    cmd_pattern = re.compile(
        rb'(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+Tm)|'
        rb'(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+Td)|'
        rb'(?:\[(.*?)\]\s*TJ)|'
        rb'(?:\(((?:[^()\\]|\\.)*)\)\s*Tj)',
        re.DOTALL
    )
    
    all_pages = []
    
    for p_num, (p_id, c_id) in enumerate(pages, 1):
        stream = get_obj_stream(pdf, c_id)
        tm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        tlm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
        elements = []
        
        for match in cmd_pattern.finditer(stream):
            if match.group(1) is not None:
                a, b, c, d, e, f = [float(match.group(i)) for i in range(1, 7)]
                tm = [a, b, c, d, e, f]
                tlm = [a, b, c, d, e, f]
            elif match.group(7) is not None:
                tx, ty = float(match.group(7)), float(match.group(8))
                a, b, c, d, e, f = tlm
                tlm = [a, b, c, d, tx * a + ty * c + e, tx * b + ty * d + f]
                tm = list(tlm)
            elif match.group(9) is not None:
                raw_arr = match.group(9)
                # Parse TJ array into chunks separated by big negative kerns (<-1000)
                chunks = []
                cur_text = []
                i = 0
                n = len(raw_arr)
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
                        txt = ''.join(cmap.get(b, '') for b in unescape_pdf_bytes(s))
                        cur_text.append(txt)
                    elif raw_arr[i:i+1] in b'0123456789-+':
                        start = i
                        while i < n and raw_arr[i:i+1] in b'0123456789-.+':
                            i += 1
                        val = float(raw_arr[start:i])
                        if val < -1000:
                            w = ''.join(cur_text).strip()
                            if w:
                                chunks.append(w)
                            cur_text = []
                    else:
                        i += 1
                w = ''.join(cur_text).strip()
                if w:
                    chunks.append(w)
                
                # If chunks has multiple items, each chunk is a distinct cell
                # If only 1 chunk, standard element
                for c_idx, chunk in enumerate(chunks):
                    # We can assign approximate column offset
                    # In matrix [0, 1, -1, 0, e, f], horizontal is f (y in user space)
                    elements.append((round(tm[4], 2), round(tm[5], 2), c_idx, chunk))
                    
            elif match.group(10) is not None:
                raw_str = match.group(10)
                txt = ''.join(cmap.get(b, '') for b in unescape_pdf_bytes(raw_str)).strip()
                if txt:
                    elements.append((round(tm[4], 2), round(tm[5], 2), 0, txt))
                    
        all_pages.append((p_num, elements))
    return all_pages

if __name__ == '__main__':
    for name, cid in [
        ('road-signs-english.pdf', 299),
        ('rules-of-road-regulations-english.pdf', 180),
        ('general-driving-principles-english.pdf', 128)
    ]:
        pages = extract_pdf_cells(name, cid)
        total_elems = sum(len(e) for p, e in pages)
        print(f'{name}: {len(pages)} pages, {total_elems} elements extracted.')
        print('Sample from Page 1:')
        for e in pages[0][1][:15]:
            print(' ', e)
