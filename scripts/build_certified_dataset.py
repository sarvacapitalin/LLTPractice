import re
import zlib
import json
import os
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, unescape_pdf_bytes, get_page_contents

def extract_tokens_with_jumps(stream_bytes, cmap):
    """
    Extracts text tokens while converting large negative displacements into column breaks (\t)
    """
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
            tokens = re.findall(rb"\(((?:[^()\\]|\\.)*)\)|(-?[\d\.]+)", raw_arr)
            parts = []
            for s, num in tokens:
                if s:
                    t = "".join(cmap.get(b, "") for b in unescape_pdf_bytes(s))
                    parts.append(t)
                elif num:
                    val = float(num)
                    if val < -2000:
                        parts.append(" \t ")
            text = "".join(parts).strip()
            if text:
                elements.append((round(tx, 2), round(ty, 2), text))
        elif match.group(10) is not None:
            raw_str = match.group(10)
            text = "".join(cmap.get(b, "") for b in unescape_pdf_bytes(raw_str)).strip()
            if text:
                elements.append((round(tx, 2), round(ty, 2), text))
                
    return elements

print("Helper ready.")
