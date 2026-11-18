import re
import json
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, unescape_pdf_bytes, get_page_contents

def decode_stream_robust(stream_bytes, cmap):
    cmd_pattern = re.compile(
        rb"(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+Tm)|"
        rb"(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+Td)|"
        rb"(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+TD)|"
        rb"(?:(-?[\d\.]+)\s+TL)|"
        rb"(?:T\*)|"
        rb"(?:\[(.*?)\]\s*TJ)|"
        rb"(?:\(((?:[^()\\]|\\.)*)\)\s*Tj)|"
        rb"(?:\(((?:[^()\\]|\\.)*)\)\s*\')|"
        rb"(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+\(((?:[^()\\]|\\.)*)\)\s*\")",
        re.DOTALL
    )

    tx, ty = 0.0, 0.0
    line_tx, line_ty = 0.0, 0.0
    leading = 12.0
    elements = []

    for m in cmd_pattern.finditer(stream_bytes):
        if m.group(1) is not None:
            tx = float(m.group(5))
            ty = float(m.group(6))
            line_tx, line_ty = tx, ty
        elif m.group(7) is not None:
            tx += float(m.group(7))
            ty += float(m.group(8))
            line_tx, line_ty = tx, ty
        elif m.group(9) is not None:
            tx += float(m.group(9))
            ty += float(m.group(10))
            leading = -float(m.group(10))
            line_tx, line_ty = tx, ty
        elif m.group(11) is not None:
            leading = float(m.group(11))
        elif m.group(0) == b"T*":
            ty -= leading
            tx = line_tx
        elif m.group(12) is not None: # TJ
            raw_arr = m.group(12)
            i = 0
            n = len(raw_arr)
            current_str = []
            cur_x = tx
            while i < n:
                if raw_arr[i:i+1] == b"(":
                    i += 1
                    start = i
                    depth = 1
                    while i < n and depth > 0:
                        if raw_arr[i:i+1] == b"\\":
                            i += 2
                            continue
                        if raw_arr[i:i+1] == b"(": depth += 1
                        elif raw_arr[i:i+1] == b")": depth -= 1
                        i += 1
                    s = raw_arr[start:i-1]
                    t = "".join(cmap.get(b, "") for b in unescape_pdf_bytes(s))
                    current_str.append(t)
                elif raw_arr[i:i+1] in b"0123456789-+":
                    start = i
                    while i < n and raw_arr[i:i+1] in b"0123456789-.+":
                        i += 1
                    num = float(raw_arr[start:i])
                    if num < -1000: # large column gap -> emit element
                        txt = "".join(current_str).strip()
                        if txt:
                            elements.append((round(cur_x, 2), round(ty, 2), txt))
                        current_str = []
                        cur_x += (-num / 1000.0) * 10.0
                    elif num < -180: # word space
                        current_str.append(" ")
                else:
                    i += 1
            txt = "".join(current_str).strip()
            if txt:
                elements.append((round(cur_x, 2), round(ty, 2), txt))
        elif m.group(13) is not None: # Tj
            raw_str = m.group(13)
            text = "".join(cmap.get(b, "") for b in unescape_pdf_bytes(raw_str)).strip()
            if text: elements.append((round(tx, 2), round(ty, 2), text))
        elif m.group(14) is not None: # single quote (next line and show)
            ty -= leading
            tx = line_tx
            raw_str = m.group(14)
            text = "".join(cmap.get(b, "") for b in unescape_pdf_bytes(raw_str)).strip()
            if text: elements.append((round(tx, 2), round(ty, 2), text))

    return elements

if __name__ == "__main__":
    with open("general-driving-principles-english.pdf", "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, 128))
    stream = get_obj_stream(pdf, get_page_contents(pdf)[1][1]) # page 2
    elems = decode_stream_robust(stream, cmap)
    print(f"Total elements: {len(elems)}")
    for el in elems:
        if any(w in el[2] for w in ["OBJECTS", "MIRROR", "RESTRICT", "DISTRACT", "CONCENTRATION", "11"]):
            print("  ", el)
