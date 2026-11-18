import re
import zlib
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, unescape_pdf_bytes, get_page_contents

def decode_stream_matrix(stream_bytes, cmap):
    # Match Tm, Td, TJ, Tj
    cmd_pattern = re.compile(
        rb'(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+Tm)|'
        rb'(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+Td)|'
        rb'(?:\[(.*?)\]\s*TJ)|'
        rb'(?:\(((?:[^()\\]|\\.)*)\)\s*Tj)',
        re.DOTALL
    )
    # tm is [a, b, c, d, e, f]
    tm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    tlm = [1.0, 0.0, 0.0, 1.0, 0.0, 0.0]
    elements = []
    
    for match in cmd_pattern.finditer(stream_bytes):
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
            # Find all strings in TJ array
            parts = re.findall(rb'\(((?:[^()\\]|\\.)*)\)', raw_arr, re.DOTALL)
            text = ''.join(''.join(cmap.get(b, '') for b in unescape_pdf_bytes(p)) for p in parts).strip()
            if text:
                elements.append((round(tm[4], 2), round(tm[5], 2), text))
        elif match.group(10) is not None:
            raw_str = match.group(10)
            text = ''.join(cmap.get(b, '') for b in unescape_pdf_bytes(raw_str)).strip()
            if text:
                elements.append((round(tm[4], 2), round(tm[5], 2), text))
    return elements

if __name__ == '__main__':
    with open('rules-of-road-regulations-english.pdf', 'rb') as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, 180))
    pages = get_page_contents(pdf)
    elems = decode_stream_matrix(get_obj_stream(pdf, pages[0][1]), cmap)
    print('Proper matrix decoded count:', len(elems))
    for e in elems[:35]:
        print(f'({e[0]:6.2f}, {e[1]:6.2f}): {e[2]}')
