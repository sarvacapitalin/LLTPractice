import re
import zlib
import json

def parse_cmap(cmap_bytes):
    mapping = {}
    for match in re.finditer(rb"<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>", cmap_bytes):
        src_start = int(match.group(1), 16)
        src_end = int(match.group(2), 16)
        dst_start = int(match.group(3), 16)
        for i in range(src_end - src_start + 1):
            mapping[src_start + i] = chr(dst_start + i)
    for match in re.finditer(rb"<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>", cmap_bytes):
        src = int(match.group(1), 16)
        dst = int(match.group(2), 16)
        if src not in mapping:
            mapping[src] = chr(dst)
    return mapping

def unescape_pdf_bytes(b):
    out = bytearray()
    i = 0
    n = len(b)
    while i < n:
        if b[i:i+1] == b"\\":
            i += 1
            if i >= n: break
            c = b[i:i+1]
            if c == b"n": out.append(0x0a); i += 1
            elif c == b"r": out.append(0x0d); i += 1
            elif c == b"t": out.append(0x09); i += 1
            elif c == b"b": out.append(0x08); i += 1
            elif c == b"f": out.append(0x0c); i += 1
            elif c == b"(": out.append(0x28); i += 1
            elif c == b")": out.append(0x29); i += 1
            elif c == b"\\": out.append(0x5c); i += 1
            elif b"0" <= c <= b"7":
                oct_str = c
                i += 1
                while i < n and len(oct_str) < 3 and b"0" <= b[i:i+1] <= b"7":
                    oct_str += b[i:i+1]
                    i += 1
                out.append(int(oct_str, 8))
            else:
                out.append(c[0])
                i += 1
        else:
            out.append(b[i])
            i += 1
    return bytes(out)

def get_obj_stream(pdf, num):
    m = re.search(rb"\n" + str(num).encode() + rb"\s+0\s+obj\s*<<(.*?)>>\s*stream\r?\n(.*?)\r?\nendstream", pdf, re.DOTALL)
    if not m:
        m = re.search(rb"^" + str(num).encode() + rb"\s+0\s+obj\s*<<(.*?)>>\s*stream\r?\n(.*?)\r?\nendstream", pdf, re.DOTALL)
    if m:
        try:
            return zlib.decompress(m.group(2))
        except:
            return m.group(2)
    return b""

def decode_stream(stream_bytes, cmap):
    cmd_pattern = re.compile(
        rb"(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+(-?[\d\.]+)\s+Tm)|"
        rb"(?:(-?[\d\.]+)\s+(-?[\d\.]+)\s+Td)|"
        rb"(?:\[(.*?)\]\s*TJ)|"
        rb"(?:\(((?:[^()\\]|\\.)*)\)\s*Tj)",
        re.DOTALL
    )
    tx, ty = 0.0, 0.0
    elements = []
    for match in cmd_pattern.finditer(stream_bytes):
        if match.group(1) is not None:
            tx = float(match.group(5))
            ty = float(match.group(6))
        elif match.group(7) is not None:
            tx += float(match.group(7))
            ty += float(match.group(8))
        elif match.group(9) is not None:
            raw_arr = match.group(9)
            parts = re.findall(rb"\(((?:[^()\\]|\\.)*)\)", raw_arr, re.DOTALL)
            text = "".join("".join(cmap.get(b, "") for b in unescape_pdf_bytes(p)) for p in parts)
            text = text.strip()
            if text:
                elements.append((round(tx, 2), round(ty, 2), text))
        elif match.group(10) is not None:
            raw_str = match.group(10)
            text = "".join(cmap.get(b, "") for b in unescape_pdf_bytes(raw_str)).strip()
            if text:
                elements.append((round(tx, 2), round(ty, 2), text))
    return elements

def get_page_contents(pdf):
    kids_block = re.search(rb"/Kids\s*\[(.*?)\]", pdf, re.DOTALL).group(1)
    p_nums = [int(x) for x in re.findall(rb"(\d+)\s+0\s+R", kids_block)]
    contents_list = []
    for p in p_nums:
        m = re.search(rb"\n" + str(p).encode() + rb"\s+0\s+obj(.*?)endobj", pdf, re.DOTALL)
        if m:
            mc = re.search(rb"/Contents\s+(\d+)\s+0\s+R", m.group(1))
            if mc:
                contents_list.append((p, int(mc.group(1))))
    return contents_list

def main():
    with open("general-driving-principles-english.pdf", "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, 128))
    pages = get_page_contents(pdf)
    print("General Driving Principles English pages:", len(pages))
    
    # Let us inspect page 1 and page 2
    for p_idx, (p_id, c_id) in enumerate(pages[:2]):
        stream = get_obj_stream(pdf, c_id)
        elems = decode_stream(stream, cmap)
        print(f"\n--- Page {p_idx+1} (Contents {c_id}): {len(elems)} elements ---")
        for x, y, t in elems[:20]:
            print(f"({x:6.2f}, {y:6.2f}): {t}")

if __name__ == "__main__":
    main()
