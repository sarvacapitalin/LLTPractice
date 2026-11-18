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

def extract_tokens_from_stream(stream_bytes, cmap):
    # Regex to capture Tm, Td, TD, T*, TJ, Tj
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

def get_page_contents_ids(pdf):
    # Find all Page objects
    page_ids = []
    # Find /Pages root
    m_root = re.search(rb"/Type\s*/Pages\b.*?/Kids\s*\[(.*?)\]", pdf, re.DOTALL)
    if m_root:
        kids_str = m_root.group(1)
        page_nums = [int(p) for p in re.findall(rb"(\d+)\s+0\s+R", kids_str)]
        for pnum in page_nums:
            m_p = re.search(rb"\n" + str(pnum).encode() + rb"\s+0\s+obj\s*<<(.*?)>>", pdf, re.DOTALL)
            if m_p:
                m_c = re.search(rb"/Contents\s+(\d+)\s+0\s+R", m_p.group(1))
                if m_c:
                    page_ids.append((pnum, int(m_c.group(1))))
    return page_ids

def main():
    for fname, cmap_obj in [
        ("general-driving-principles-english.pdf", 128),
        ("rules-of-road-regulations-english.pdf", 180),
        ("road-signs-english.pdf", 299)
    ]:
        with open(fname, "rb") as f:
            pdf = f.read()
        cmap = parse_cmap(get_obj_stream(pdf, cmap_obj))
        pages = get_page_contents_ids(pdf)
        print(f"\n======================================")
        print(f"File: {fname} -> Found {len(pages)} pages")
        total_elems = 0
        for pnum, c_id in pages:
            stream = get_obj_stream(pdf, c_id)
            elems = extract_tokens_from_stream(stream, cmap)
            total_elems += len(elems)
        print(f"Total text tokens across all pages: {total_elems}")

if __name__ == "__main__":
    main()
