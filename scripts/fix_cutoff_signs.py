import zlib, re, os, struct, subprocess

with open("road-signs-english.pdf", "rb") as f:
    pdf_bytes = f.read()

def decode_png_predictor(data, width, height, colors=3, bpc=8):
    bpp = colors * (bpc // 8)
    row_len = 1 + width * bpp
    out = bytearray(width * height * bpp)
    prev_row = bytearray(width * bpp)
    for y in range(height):
        row_start = y * row_len
        if row_start >= len(data): break
        filter_type = data[row_start]
        curr_row = bytearray(width * bpp)
        raw_row = data[row_start + 1 : row_start + row_len]
        for x in range(min(len(raw_row), width * bpp)):
            raw = raw_row[x]
            a = curr_row[x - bpp] if x >= bpp else 0
            b = prev_row[x]
            c = prev_row[x - bpp] if x >= bpp else 0
            if filter_type == 0: val = raw
            elif filter_type == 1: val = (raw + a) & 0xFF
            elif filter_type == 2: val = (raw + b) & 0xFF
            elif filter_type == 3: val = (raw + ((a + b) >> 1)) & 0xFF
            elif filter_type == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pr = a if pa <= pb and pa <= pc else (b if pb <= pc else c)
                val = (raw + pr) & 0xFF
            else: val = raw
            curr_row[x] = val
        out[y * width * bpp : (y + 1) * width * bpp] = curr_row
        prev_row = curr_row
    return out

def read_bmp(path):
    with open(path, "rb") as f:
        data = f.read()
    offset = struct.unpack("<I", data[10:14])[0]
    w, h = struct.unpack("<ii", data[18:26])
    bpp = struct.unpack("<H", data[28:30])[0]
    row_size = ((w * bpp + 31) // 32) * 4
    
    rgb = bytearray(w * abs(h) * 3)
    for y in range(abs(h)):
        src_y = (abs(h) - 1 - y) if h > 0 else y
        row = data[offset + src_y * row_size : offset + (src_y + 1) * row_size]
        for x in range(w):
            b, g, r = row[x*3 : x*3 + 3]
            dst_idx = (y * w + x) * 3
            rgb[dst_idx : dst_idx + 3] = bytes([r, g, b])
    return w, abs(h), rgb

def get_raw_rgb(oid):
    m = re.search(rf"\n{oid}\s+0\s+obj(.*?)endobj", pdf_bytes.decode("latin1", errors="ignore"), re.DOTALL)
    body = m.group(1)
    w = int(re.search(r"/Width\s+(\d+)", body).group(1))
    h = int(re.search(r"/Height\s+(\d+)", body).group(1))
    
    stream_m = re.search(r"stream\r?\n(.*?)endstream", body, re.DOTALL)
    raw_stream = stream_m.group(1).encode("latin1")
    
    if "DCTDecode" in body:
        tmp_jpg = f"/tmp/_tmp_{oid}.jpg"
        tmp_bmp = f"/tmp/_tmp_{oid}.bmp"
        with open(tmp_jpg, "wb") as jf: jf.write(raw_stream)
        subprocess.run(f"/usr/bin/sips -s format bmp {tmp_jpg} --out {tmp_bmp} >/dev/null 2>&1", shell=True)
        w, h, rgb = read_bmp(tmp_bmp)
        if os.path.exists(tmp_jpg): os.remove(tmp_jpg)
        if os.path.exists(tmp_bmp): os.remove(tmp_bmp)
        return w, h, rgb

    decomp = zlib.decompress(raw_stream)
    colors = 1 if "/DeviceGray" in body and "/Indexed" not in body else 3
    if "/Predictor" in body:
        decomp = decode_png_predictor(decomp, w, h, colors=colors)

    cs_ref = re.search(r"/ColorSpace\s+(\d+)\s+0\s+R", body)
    if cs_ref:
        cs_id = int(cs_ref.group(1))
        csm = re.search(rf"\n{cs_id}\s+0\s+obj(.*?)endobj", pdf_bytes.decode("latin1", errors="ignore"), re.DOTALL)
        hex_m = re.search(r"<([0-9A-Fa-f\s]+)>", csm.group(1))
        if hex_m:
            palette_bytes = bytes.fromhex(re.sub(r"\s+", "", hex_m.group(1)))
            rgb = bytearray(w * h * 3)
            p_len = len(palette_bytes)
            for i, b in enumerate(decomp[:w*h]):
                off = b * 3
                if off + 2 < p_len:
                    rgb[i*3:i*3+3] = palette_bytes[off:off+3]
            return w, h, rgb

    if colors == 1:
        rgb = bytearray(w * h * 3)
        for i, g in enumerate(decomp[:w*h]):
            rgb[i*3] = rgb[i*3+1] = rgb[i*3+2] = g
        return w, h, rgb
    return w, h, decomp[:w*h*3]

split_map = {
    4: (12, 17),
    10: (32, 39),
    17: (54, 56),
    24: (71, 79),
    31: (96, 102),
    38: (121, 129),
    45: (146, 148),
    52: (169, 171),
    59: (192, 194),
    66: (215, 217),
    71: (233, 235),
    75: (248, 250),
    87: (276, 277),
    94: (289, 291)
}

if __name__ == "__main__":
    print("-> Repairing and stitching 14 cut-off signs...")
    for q, (o1, o2) in split_map.items():
        w1, h1, rgb1 = get_raw_rgb(o1)
        w2, h2, rgb2 = get_raw_rgb(o2)
        tot_h = h1 + h2
        rgb = rgb1 + rgb2
        ppm = f"P6\n{w1} {tot_h}\n255\n".encode() + rgb
        out_ppm = f"/tmp/stitched_sign_{q:03d}.ppm"
        out_png = f"assets/signs/sign_{q:03d}.png"
        with open(out_ppm, "wb") as pf: pf.write(ppm)
        subprocess.run(f"/usr/bin/sips -s format png {out_ppm} --out {out_png} >/dev/null 2>&1", shell=True)
        if os.path.exists(out_ppm): os.remove(out_ppm)
        print(f"✓ Stitched Q{q:02d}: {w1}x{tot_h} -> {out_png}")

    print("All cut-off signs repaired successfully.")
