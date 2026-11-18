import re
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, unescape_pdf_bytes, get_page_contents

with open('general-driving-principles-english.pdf', 'rb') as f:
    pdf = f.read()
cmap = parse_cmap(get_obj_stream(pdf, 128))
pages = get_page_contents(pdf)
stream = get_obj_stream(pdf, pages[0][1])

for m in re.finditer(rb'\[(.*?)\]\s*TJ', stream, re.DOTALL):
    raw_arr = m.group(1)
    parts = re.findall(rb'\(((?:[^()\\]|\\.)*)\)', raw_arr, re.DOTALL)
    text = ''.join(''.join(cmap.get(b, '') for b in unescape_pdf_bytes(p)) for p in parts)
    if 'THINK' in text:
        print('Found TJ for THINK! Total length:', len(raw_arr))
        # Parse tokens in TJ array
        tokens = []
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
                t = ''.join(cmap.get(b, '') for b in unescape_pdf_bytes(s))
                tokens.append(('STR', t))
            elif raw_arr[i:i+1] in b'0123456789-+':
                start = i
                while i < n and raw_arr[i:i+1] in b'0123456789-.+':
                    i += 1
                tokens.append(('NUM', float(raw_arr[start:i])))
            else:
                i += 1
        for tok in tokens:
            print('  ', tok)
        break
