import re
from scripts.test_robust_extractor import decode_stream_robust
from scripts.test_pdf_parse import parse_cmap, get_obj_stream, get_page_contents

def inspect_qa_extraction(pdf_path, cmap_id, total, name):
    with open(pdf_path, "rb") as f:
        pdf = f.read()
    cmap = parse_cmap(get_obj_stream(pdf, cmap_id))
    pages = get_page_contents(pdf)
    all_elems = []
    for p_idx, (p_id, c_id) in enumerate(pages):
        stream = get_obj_stream(pdf, c_id)
        elems = decode_stream_robust(stream, cmap)
        for x, y, t in elems:
            all_elems.append((p_idx + 1, x, y, t))
            
    header_words = {"S.NO.", "QUESTIONS", "RELEVANT FIGURE/SIGN", "OPTION1", "OPTION2", "OPTION3", "OPTION4", "ANSWER", "S.NO.QUESTIONS", "OPTION1OPTION2OPTION3OPTION4", "ANSWER ", "IF ANY", "RELEVANT", "FIGURE/SIGN"}
    filtered = [el for el in all_elems if el[3] not in header_words]
    
    q_indices = {}
    for i, (p, x, y, t) in enumerate(filtered):
        m = re.match(r"^(\d{1,3})$", t.strip())
        if m:
            num = int(m.group(1))
            if 1 <= num <= total and num not in q_indices:
                if num == 1 or (num - 1) in q_indices:
                    q_indices[num] = i
                    
    ans_issues = []
    for q in range(1, total + 1):
        start_idx = q_indices[q] + 1
        end_idx = q_indices[q + 1] if q < total else len(filtered)
        toks = filtered[start_idx:end_idx]
        if not toks:
            print(f"Empty toks for Q{q}")
            continue
        ans_tok = toks[-1]
        m = re.match(r"^([1-4])$", ans_tok[3].strip())
        if not m:
            ans_issues.append((q, [t[3] for t in toks[-3:]]))
            
    print(f"[{name}] Answer token validation: {len(ans_issues)} non-exact single-digit answer tokens out of {total}")
    if ans_issues:
        for it in ans_issues[:10]:
            print("  ", it)

if __name__ == "__main__":
    inspect_qa_extraction("rules-of-road-regulations-english.pdf", 180, 159, "Rules")
    inspect_qa_extraction("general-driving-principles-english.pdf", 128, 159, "GP")
