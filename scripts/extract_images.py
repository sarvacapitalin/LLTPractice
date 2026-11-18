import os, sys, re, zlib, struct

def extract_pdf_images(pdf_path, output_dir, prefix):
    os.makedirs(output_dir, exist_ok=True)
    with open(pdf_path, 'rb') as f:
        data = f.read()

    obj_matches = list(re.finditer(rb'(\d+)\s+(\d+)\s+obj\b(.*?)\bendobj\b', data, re.DOTALL))
    obj_map = {int(m.group(1)): m.group(3) for m in obj_matches}

    extracted_count = 0
    for obj_id, body in obj_map.items():
        if b'/Subtype /Image' in body or b'/Subtype/Image' in body:
            stream_start = body.find(b'stream\n')
            if stream_start == -1:
                stream_start = body.find(b'stream\r\n')
                if stream_start != -1:
                    stream_start += len(b'stream\r\n')
            else:
                stream_start += len(b'stream\n')
            
            stream_end = body.rfind(b'\nendstream')
            if stream_end == -1:
                stream_end = body.rfind(b'\rendstream')
            if stream_start == -1 or stream_end == -1 or stream_start >= stream_end:
                continue

            raw_stream = body[stream_start:stream_end]
            header = body[:stream_start].decode('latin1', errors='ignore')

            # Width and Height
            w_m = re.search(r'/Width\s+(\d+)', header)
            h_m = re.search(r'/Height\s+(\d+)', header)
            if not w_m or not h_m:
                continue
            width = int(w_m.group(1))
            height = int(h_m.group(1))

            out_png = os.path.join(output_dir, f"{prefix}_{obj_id}.png")

            if '/DCTDecode' in header:
                # Direct JPEG stream
                tmp_jpg = os.path.join(output_dir, f"_tmp_{obj_id}.jpg")
                with open(tmp_jpg, 'wb') as jf:
                    jf.write(raw_stream)
                os.system(f"/usr/bin/sips -s format png '{tmp_jpg}' --out '{out_png}' >/dev/null 2>&1")
                if os.path.exists(tmp_jpg):
                    os.remove(tmp_jpg)
                extracted_count += 1
            elif '/FlateDecode' in header:
                try:
                    decomp = zlib.decompress(raw_stream)
                except Exception:
                    continue

                # Check colorspace
                # 1. DeviceRGB
                if '/DeviceRGB' in header and '/Indexed' not in header:
                    ppm_path = os.path.join(output_dir, f"_tmp_{obj_id}.ppm")
                    with open(ppm_path, 'wb') as pf:
                        pf.write(f"P6\n{width} {height}\n255\n".encode() + decomp[:width*height*3])
                    os.system(f"/usr/bin/sips -s format png '{ppm_path}' --out '{out_png}' >/dev/null 2>&1")
                    if os.path.exists(ppm_path):
                        os.remove(ppm_path)
                    extracted_count += 1
                # 2. DeviceGray
                elif '/DeviceGray' in header and '/Indexed' not in header:
                    pgm_path = os.path.join(output_dir, f"_tmp_{obj_id}.pgm")
                    with open(pgm_path, 'wb') as pf:
                        pf.write(f"P5\n{width} {height}\n255\n".encode() + decomp[:width*height])
                    os.system(f"/usr/bin/sips -s format png '{pgm_path}' --out '{out_png}' >/dev/null 2>&1")
                    if os.path.exists(pgm_path):
                        os.remove(pgm_path)
                    extracted_count += 1
                # 3. Indexed colorspace
                elif '/Indexed' in header or re.search(r'/ColorSpace\s+\d+\s+0\s+R', header):
                    # Find palette object
                    cs_ref = re.search(r'/ColorSpace\s+(\d+)\s+0\s+R', header)
                    palette_bytes = None
                    if cs_ref:
                        cs_id = int(cs_ref.group(1))
                        cs_body = obj_map.get(cs_id, b'').decode('latin1', errors='ignore')
                        # format: [/Indexed /DeviceRGB 255 <HEX>] or [/Indexed /DeviceRGB 255 stream]
                        hex_m = re.search(r'<([0-9A-Fa-f\s]+)>', cs_body)
                        if hex_m:
                            hex_str = re.sub(r'\s+', '', hex_m.group(1))
                            palette_bytes = bytes.fromhex(hex_str)
                    
                    if palette_bytes:
                        # Expand indexed bytes to RGB
                        ppm_path = os.path.join(output_dir, f"_tmp_{obj_id}.ppm")
                        rgb_data = bytearray(width * height * 3)
                        p_len = len(palette_bytes)
                        for i, b_idx in enumerate(decomp[:width*height]):
                            offset = b_idx * 3
                            if offset + 2 < p_len:
                                rgb_data[i*3 : i*3+3] = palette_bytes[offset:offset+3]
                        with open(ppm_path, 'wb') as pf:
                            pf.write(f"P6\n{width} {height}\n255\n".encode() + rgb_data)
                        os.system(f"/usr/bin/sips -s format png '{ppm_path}' --out '{out_png}' >/dev/null 2>&1")
                        if os.path.exists(ppm_path):
                            os.remove(ppm_path)
                        extracted_count += 1

    print(f"Extracted {extracted_count} images from {pdf_path} to {output_dir}")

if __name__ == '__main__':
    extract_pdf_images('road-signs-english.pdf', 'assets/signs', 'rs')
    extract_pdf_images('rules-of-road-regulations-english.pdf', 'assets/scenarios', 'rr')
