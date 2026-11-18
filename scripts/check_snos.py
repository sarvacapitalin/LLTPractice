from scripts.test_cell_extractor import extract_pdf_cells

for name, cid, total in [
    ('road-signs-english.pdf', 299, 94),
    ('rules-of-road-regulations-english.pdf', 180, 159),
    ('general-driving-principles-english.pdf', 128, 159)
]:
    pages = extract_pdf_cells(name, cid)
    q_found = {}
    for p_num, elems in pages:
        for x, y, c_idx, text in elems:
            if 70 <= y <= 95 and c_idx == 0:
                # check if integer
                t = text.strip()
                if t.isdigit():
                    num = int(t)
                    if 1 <= num <= total:
                        if num not in q_found:
                            q_found[num] = []
                        q_found[num].append((p_num, x, y, text))
    print(f'{name}: Found {len(q_found)} / {total} question numbers in S.NO column.')
    missing = [i for i in range(1, total + 1) if i not in q_found]
    if missing:
        print(f'  Missing S.NOs: {missing}')
